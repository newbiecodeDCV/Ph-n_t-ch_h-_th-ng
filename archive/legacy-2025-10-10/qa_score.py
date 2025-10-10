#!/usr/bin/env python3
import argparse
import json
import math
from pathlib import Path
from typing import Dict, Any, List

try:
    import yaml  # type: ignore
except Exception:  # pragma: no cover
    yaml = None


def load_rules(path: str) -> Dict[str, Any]:
    with open(path, "r", encoding="utf-8") as f:
        if path.endswith(".yaml") or path.endswith(".yml"):
            if yaml is None:
                raise RuntimeError("PyYAML chưa được cài. Hãy: pip install pyyaml")
            return yaml.safe_load(f)
        return json.load(f)


def read_jsonl(path: str) -> List[Dict[str, Any]]:
    if not path:
        return []
    data = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            data.append(json.loads(line))
    return data


def tokens_per_minute(text: str, dur_seconds: float) -> float:
    if dur_seconds <= 0:
        return 0.0
    tokens = len([t for t in text.split() if t])
    return 60.0 * tokens / dur_seconds


def speech_rate_severity(agent_segments: List[Dict[str, Any]], base: float, std: float, th: Dict[str, Any]) -> str:
    # Tính tốc độ theo từng segment của Agent
    rates = []
    for seg in agent_segments:
        dur = max(0.0, float(seg.get("end", 0)) - float(seg.get("start", 0)))
        txt = seg.get("text", "") or ""
        if dur <= 0 or not txt.strip():
            continue
        rates.append(tokens_per_minute(txt, dur))
    if not rates:
        return "OK"

    def ratio_over_sigma(sigma: float) -> float:
        upper = base + sigma * std
        lower = base - sigma * std
        count = sum(1 for r in rates if (r > upper or r < lower))
        return count / len(rates)

    r3 = ratio_over_sigma(th.get("M3", {}).get("sigma", 2.5))
    if r3 >= th.get("M3", {}).get("duration_ratio", 0.40):
        return "M3"
    r2 = ratio_over_sigma(th.get("M2", {}).get("sigma", 2.0))
    if r2 >= th.get("M2", {}).get("duration_ratio", 0.30):
        return "M2"
    r1 = ratio_over_sigma(th.get("M1", {}).get("sigma", 1.0))
    if r1 >= th.get("M1", {}).get("duration_ratio", 0.20):
        return "M1"
    return "OK"


def accent_severity(signals: Dict[str, Any], acc_cfg: Dict[str, Any]) -> str:
    wer_gap = float(signals.get("wer_gap", 0.0) or 0.0)
    repeats = int(signals.get("customer_repeat_count", 0) or 0)

    if wer_gap >= acc_cfg.get("wer_gap_threshold", {}).get("M2", 0.20) or repeats >= acc_cfg.get("customer_repeat_threshold", {}).get("M2", 3):
        return "M2"
    if wer_gap >= acc_cfg.get("wer_gap_threshold", {}).get("M1", 0.10) or repeats >= acc_cfg.get("customer_repeat_threshold", {}).get("M1", 1):
        return "M1"
    return "OK"


def group_penalty(group_points: float, base_group: float, level: str) -> float:
    if level == "M3":
        return 0.0
    if level == "M2":
        return max(0.0, group_points - 0.5 * base_group)
    # M1 xử lý ở tiêu chí con (trừ đúng điểm quy đổi)
    return group_points


def score_call(call: Dict[str, Any], rules: Dict[str, Any], call_type: str, baselines: Dict[str, Any]) -> Dict[str, Any]:
    bases = rules["call_types"][call_type]["base_points"]
    points = dict(bases)

    # --- KNGT: ky_nang_noi ---
    kngt_cfg = rules["criteria"]["KNGT"]["ky_nang_noi"]
    # baseline có thể ghi đè bởi docs/baselines.json
    rate_base = float(baselines.get("speech_rate", {}).get("baseline_rate_wpm", kngt_cfg["speech_rate"]["baseline_rate_wpm"]))
    rate_std = float(baselines.get("speech_rate", {}).get("baseline_std_wpm", kngt_cfg["speech_rate"]["baseline_std_wpm"]))

    agent_segments = [s for s in call.get("segments", []) if s.get("speaker") == "AGENT"]
    sr_sev = speech_rate_severity(agent_segments, rate_base, rate_std, kngt_cfg["speech_rate"]["thresholds"])
    acc_sev = accent_severity(call.get("signals", {}), kngt_cfg.get("accent", {}))

    # Mức lỗi tổng hợp cho ky_nang_noi = mức cao nhất giữa speed & accent
    sev_rank = {"OK": 0, "M1": 1, "M2": 2, "M3": 3}
    combined = sr_sev if sev_rank[sr_sev] >= sev_rank[acc_sev] else acc_sev

    # Áp hình phạt nhóm KNGT trước (M2/M3)
    points["KNGT"] = group_penalty(points["KNGT"], bases["KNGT"], combined)

    # Nếu chỉ M1 → trừ đúng điểm quy đổi tiêu chí con (ky_nang_noi)
    if combined == "M1":
        sub_pts = float(kngt_cfg["points"][call_type])
        points["KNGT"] = max(0.0, points["KNGT"] - sub_pts)

    # --- NTT: CRM ---
    # Nếu call có trường crm_violations (M1/M2/M3) thì áp trực tiếp; nếu không, bỏ qua.
    ntt_cfg = rules["criteria"].get("NTT", {}).get("nhap_he_thong", {})
    if call.get("crm_violations"):
        if "M3" in call["crm_violations"]:
            points["NTT"] = 0.0
        elif "M2" in call["crm_violations"]:
            points["NTT"] = max(0.0, points["NTT"] - ntt_cfg.get("penalties", {}).get("M2_ratio", 0.5) * bases["NTT"])
        elif "M1" in call["crm_violations"]:
            points["NTT"] = max(0.0, points["NTT"] - ntt_cfg.get("penalties", {}).get("M1_ratio", 0.2) * bases["NTT"])

    total = round(points["KNGT"] + points["KNBH"] + points["NTT"], 2)
    label = (
        "Yếu" if total < 5.0 else
        "Trung bình" if total < 7.0 else
        "Khá" if total < 8.0 else
        "Tốt" if total < 9.0 else
        "Xuất sắc"
    )
    return {
        "call_id": call.get("call_id"),
        "call_type": call_type,
        "speech_rate_severity": sr_sev,
        "accent_severity": acc_sev,
        "combined_kngt_severity": combined,
        "points": points,
        "total": total,
        "label": label,
        "passed": total >= 5.0,
    }


def main():
    ap = argparse.ArgumentParser(description="QA Scoring (Pha 1): KNGT tốc độ/giọng + NTT CRM")
    ap.add_argument("--transcripts", required=True, help="Đường dẫn transcripts.jsonl")
    ap.add_argument("--rules", default="docs/QA_RULES.yaml")
    ap.add_argument("--baselines", default="docs/baselines.json")
    ap.add_argument("--call-type", choices=["BH", "CSKH"], required=True)
    ap.add_argument("--crm", default="", help="crm.jsonl (tùy chọn)")
    ap.add_argument("--out", default="scores.jsonl")
    args = ap.parse_args()

    rules = load_rules(args.rules)
    # baselines.json là tùy chọn
    baselines = {}
    try:
        if Path(args.baselines).exists():
            with open(args.baselines, "r", encoding="utf-8") as f:
                baselines = json.load(f)
    except Exception:
        baselines = {}

    calls = read_jsonl(args.transcripts)

    # Nếu có CRM, ghép violations theo call_id
    crm_map: Dict[str, Dict[str, Any]] = {}
    if args.crm:
        for r in read_jsonl(args.crm):
            crm_map[r.get("call_id")] = r

    outputs = []
    for c in calls:
        # Gắn crm_violations nếu có
        if c.get("call_id") in crm_map:
            viols = crm_map[c["call_id"]].get("violations", [])
            if viols:
                c["crm_violations"] = viols
        outputs.append(score_call(c, rules, args.call_type, baselines))

    with open(args.out, "w", encoding="utf-8") as f:
        for o in outputs:
            f.write(json.dumps(o, ensure_ascii=False) + "\n")
    print(f"Đã ghi {len(outputs)} bản ghi điểm vào {args.out}")


if __name__ == "__main__":
    main()
