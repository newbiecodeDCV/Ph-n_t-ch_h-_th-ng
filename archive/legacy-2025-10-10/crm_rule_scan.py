#!/usr/bin/env python3
"""
CRM Rule Scanner - Phát hiện vi phạm CRM compliance
Đọc CRM records, áp dụng rules từ QA_RULES.yaml, sinh violations report
"""
import argparse
import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Any, List, Optional

try:
    import yaml  # type: ignore
except Exception:  # pragma: no cover
    yaml = None


def load_rules(path: str) -> Dict[str, Any]:
    """Load QA rules từ YAML hoặc JSON"""
    with open(path, "r", encoding="utf-8") as f:
        if path.endswith((".yaml", ".yml")):
            if yaml is None:
                raise RuntimeError("PyYAML chưa được cài. Hãy: pip install pyyaml")
            return yaml.safe_load(f)
        return json.load(f)


def read_jsonl(path: str) -> List[Dict[str, Any]]:
    """Đọc file JSONL"""
    data = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            data.append(json.loads(line))
    return data


def check_required_fields(record: Dict[str, Any], call_type: str, rules: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Kiểm tra trường bắt buộc"""
    required = rules.get("CRM_COMPLIANCE", {}).get("required_fields", {}).get(call_type, [])
    missing = []
    
    for field in required:
        value = record.get(field)
        if value is None or (isinstance(value, str) and not value.strip()):
            missing.append(field)
    
    if not missing:
        return None
    
    # Phân loại mức độ
    severity = "M1"  # default
    if len(missing) >= 3 or "ticket_id" in missing:
        severity = "M3"  # thiếu nhiều hoặc thiếu ticket_id quan trọng
    elif len(missing) >= 2:
        severity = "M2"
    
    return {
        "violation_type": "missing_required_fields",
        "severity": severity,
        "evidence": {
            "missing_fields": missing,
            "call_type": call_type
        }
    }


def check_notes_quality(record: Dict[str, Any], call_type: str, rules: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Kiểm tra chất lượng ghi chú"""
    notes_config = rules.get("CRM_COMPLIANCE", {}).get("notes_quality", {})
    notes = record.get("notes", "") or ""
    
    min_length = notes_config.get("min_length", 50)
    must_contain = notes_config.get("must_contain", [])
    
    issues = []
    
    # Check độ dài
    if len(notes) < min_length:
        issues.append(f"Ghi chú quá ngắn ({len(notes)} ký tự, yêu cầu tối thiểu {min_length})")
    
    # Check từ khóa bắt buộc (chỉ cho BH)
    if call_type == "BH":
        missing_keywords = [kw for kw in must_contain if kw.lower() not in notes.lower()]
        if missing_keywords:
            issues.append(f"Thiếu từ khóa: {', '.join(missing_keywords)}")
    
    if not issues:
        return None
    
    severity = "M1" if len(notes) >= min_length * 0.7 else "M2"
    
    return {
        "violation_type": "poor_notes_quality",
        "severity": severity,
        "evidence": {
            "notes_length": len(notes),
            "issues": issues
        }
    }


def check_ticket_creation(record: Dict[str, Any], call_type: str, rules: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Kiểm tra việc tạo ticket/case khi bắt buộc"""
    ticket_config = rules.get("CRM_COMPLIANCE", {}).get("ticket_creation", {}).get(call_type, {})
    required_if_rules = ticket_config.get("required_if", [])
    
    for rule_expr in required_if_rules:
        # Simple eval - trong production nên dùng safe parser
        # Ví dụ: "issue_category in ['complaint', 'bug']"
        try:
            if "issue_category" in rule_expr:
                issue_cat = record.get("issue_category", "")
                if issue_cat in ["complaint", "bug"] and not record.get("ticket_id"):
                    return {
                        "violation_type": "missing_ticket",
                        "severity": "M2",  # M2 vì ảnh hưởng đến process
                        "evidence": {
                            "issue_category": issue_cat,
                            "ticket_id": None,
                            "rule": rule_expr
                        }
                    }
            
            if "opportunity_stage" in rule_expr:
                opp_stage = record.get("opportunity_stage", "")
                if opp_stage == "qualified" and not record.get("ticket_id") and not record.get("opportunity_id"):
                    return {
                        "violation_type": "missing_opportunity",
                        "severity": "M2",
                        "evidence": {
                            "opportunity_stage": opp_stage,
                            "opportunity_id": record.get("opportunity_id"),
                            "rule": rule_expr
                        }
                    }
        except Exception as e:
            print(f"Warning: Cannot evaluate rule '{rule_expr}': {e}")
            continue
    
    return None


def check_sla_compliance(record: Dict[str, Any], rules: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Kiểm tra SLA cập nhật"""
    sla_config = rules.get("CRM_COMPLIANCE", {}).get("sla", {}).get("update_within_minutes", {})
    
    call_time_str = record.get("call_time")
    updated_at_str = record.get("updated_at")
    
    if not call_time_str or not updated_at_str:
        return None  # Không đủ dữ liệu để check
    
    try:
        call_time = datetime.fromisoformat(call_time_str.replace("Z", "+00:00"))
        updated_at = datetime.fromisoformat(updated_at_str.replace("Z", "+00:00"))
        delay_minutes = (updated_at - call_time).total_seconds() / 60
    except Exception:
        return None  # Invalid datetime format
    
    # Xác định severity dựa trên delay
    if delay_minutes > sla_config.get("M3", 30):
        severity = "M3"
    elif delay_minutes > sla_config.get("M2", 60):
        severity = "M2"
    elif delay_minutes > sla_config.get("M1", 120):
        severity = "M1"
    else:
        return None  # OK
    
    return {
        "violation_type": "sla_violation",
        "severity": severity,
        "evidence": {
            "call_time": call_time_str,
            "updated_at": updated_at_str,
            "delay_minutes": round(delay_minutes, 1),
            "threshold_minutes": sla_config.get(severity)
        }
    }


def scan_record(record: Dict[str, Any], call_type: str, rules: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Quét một CRM record và trả về danh sách violations"""
    violations = []
    
    # Check các loại vi phạm
    checks = [
        check_required_fields(record, call_type, rules),
        check_notes_quality(record, call_type, rules),
        check_ticket_creation(record, call_type, rules),
        check_sla_compliance(record, rules)
    ]
    
    for violation in checks:
        if violation:
            # Thêm metadata
            violation.update({
                "call_id": record.get("call_id"),
                "agent_id": record.get("agent_id"),
                "detected_at": datetime.utcnow().isoformat() + "Z"
            })
            violations.append(violation)
    
    return violations


def generate_reminder(violation: Dict[str, Any]) -> Dict[str, Any]:
    """Sinh reminder từ violation"""
    severity = violation.get("severity", "M1")
    
    # SLA cho reminder
    due_hours = {"M1": 4, "M2": 2, "M3": 1}.get(severity, 4)
    due_time = datetime.utcnow() + timedelta(hours=due_hours)
    
    return {
        "reminder_id": f"R-{violation['call_id']}-{violation['violation_type']}",
        "violation_id": f"V-{violation['call_id']}-{violation['violation_type']}",
        "call_id": violation["call_id"],
        "agent_id": violation["agent_id"],
        "severity": severity,
        "message": generate_reminder_message(violation),
        "due_at": due_time.isoformat() + "Z",
        "status": "pending",
        "created_at": datetime.utcnow().isoformat() + "Z"
    }


def generate_reminder_message(violation: Dict[str, Any]) -> str:
    """Sinh nội dung nhắc nhở"""
    vtype = violation.get("violation_type")
    evidence = violation.get("evidence", {})
    
    templates = {
        "missing_required_fields": (
            f"⚠️ Thiếu thông tin bắt buộc trong CRM\n"
            f"Các trường cần bổ sung: {', '.join(evidence.get('missing_fields', []))}"
        ),
        "poor_notes_quality": (
            f"📝 Ghi chú CRM chưa đạt yêu cầu\n"
            f"Vấn đề: {'; '.join(evidence.get('issues', []))}"
        ),
        "missing_ticket": (
            f"🎫 Chưa tạo ticket cho khiếu nại\n"
            f"Loại vấn đề: {evidence.get('issue_category')}\n"
            f"Yêu cầu: Tạo ticket với category '{evidence.get('issue_category')}'"
        ),
        "missing_opportunity": (
            f"💼 Chưa tạo opportunity cho khách hàng qualified\n"
            f"Giai đoạn: {evidence.get('opportunity_stage')}\n"
            f"Yêu cầu: Tạo opportunity trong CRM"
        ),
        "sla_violation": (
            f"⏰ Cập nhật CRM chậm hơn SLA\n"
            f"Thời gian chậm: {evidence.get('delay_minutes')} phút\n"
            f"Ngưỡng cho phép: {evidence.get('threshold_minutes')} phút"
        )
    }
    
    return templates.get(vtype, f"Vi phạm: {vtype}")


def aggregate_report(violations: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Tổng hợp báo cáo từ violations"""
    total = len(violations)
    by_severity = {"M1": 0, "M2": 0, "M3": 0}
    by_type = {}
    by_agent = {}
    
    for v in violations:
        severity = v.get("severity", "M1")
        vtype = v.get("violation_type", "unknown")
        agent = v.get("agent_id", "unknown")
        
        by_severity[severity] = by_severity.get(severity, 0) + 1
        by_type[vtype] = by_type.get(vtype, 0) + 1
        by_agent[agent] = by_agent.get(agent, 0) + 1
    
    return {
        "report_date": datetime.utcnow().isoformat() + "Z",
        "total_violations": total,
        "by_severity": by_severity,
        "by_type": by_type,
        "by_agent": by_agent,
        "top_violations": sorted(by_type.items(), key=lambda x: x[1], reverse=True)[:5]
    }


def main():
    ap = argparse.ArgumentParser(description="CRM Rule Scanner - Phát hiện vi phạm CRM compliance")
    ap.add_argument("--crm", required=True, help="Đường dẫn crm.jsonl")
    ap.add_argument("--rules", default="docs/QA_RULES.yaml", help="QA rules file")
    ap.add_argument("--call-type", choices=["BH", "CSKH"], help="Filter by call type (optional)")
    ap.add_argument("--violations-out", default="violations.jsonl", help="Output violations")
    ap.add_argument("--reminders-out", default="reminders.jsonl", help="Output reminders")
    ap.add_argument("--report-out", default="violations_report.json", help="Output aggregate report")
    args = ap.parse_args()
    
    # Load rules và CRM records
    rules = load_rules(args.rules)
    crm_records = read_jsonl(args.crm)
    
    print(f"Đọc {len(crm_records)} CRM records từ {args.crm}")
    
    # Scan từng record
    all_violations = []
    all_reminders = []
    
    for record in crm_records:
        # Xác định call_type từ record hoặc args
        call_type = record.get("call_type") or args.call_type
        if not call_type:
            print(f"Warning: Record {record.get('call_id')} không có call_type, skip")
            continue
        
        # Scan violations
        violations = scan_record(record, call_type, rules)
        all_violations.extend(violations)
        
        # Generate reminders
        for v in violations:
            reminder = generate_reminder(v)
            all_reminders.append(reminder)
    
    # Xuất violations
    with open(args.violations_out, "w", encoding="utf-8") as f:
        for v in all_violations:
            f.write(json.dumps(v, ensure_ascii=False) + "\n")
    print(f"✅ Ghi {len(all_violations)} violations vào {args.violations_out}")
    
    # Xuất reminders
    with open(args.reminders_out, "w", encoding="utf-8") as f:
        for r in all_reminders:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    print(f"✅ Ghi {len(all_reminders)} reminders vào {args.reminders_out}")
    
    # Tổng hợp báo cáo
    report = aggregate_report(all_violations)
    with open(args.report_out, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    print(f"✅ Ghi báo cáo tổng hợp vào {args.report_out}")
    
    # In summary
    print("\n📊 TÓM TẮT:")
    print(f"   Tổng violations: {report['total_violations']}")
    print(f"   M1: {report['by_severity']['M1']}, M2: {report['by_severity']['M2']}, M3: {report['by_severity']['M3']}")
    print(f"   Top violations: {', '.join([f'{v[0]}({v[1]})' for v in report['top_violations'][:3]])}")


if __name__ == "__main__":
    main()
