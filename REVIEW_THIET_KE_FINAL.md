# REVIEW THIẾT KẾ HỆ THỐNG AI QA CALL SCORING

**Người review:** System Architect  
**Ngày:** 11/10/2025  
**Tài liệu review:** 13_SYSTEM_DESIGN_THEO_CASE_CHUAN.md + các tài liệu liên quan

---

## 1. TỔNG QUAN ĐÁNH GIÁ

### 1.1. Độ phù hợp với yêu cầu

Dựa trên 2 use case chính từ ảnh:
1. **Kiểm tra tuân thủ cập nhật CRM của Sales/CSKH** ✅
2. **Đánh giá chấm điểm cuộc gọi của Sales trao đổi với KH** ✅

**Kết luận:** Thiết kế đã **ĐÁP ỨNG ĐẦY ĐỦ** cả 2 use case với:
- CASE 1: CRM Compliance (Kiểm tra tuân thủ CRM)
- CASE 2: Call Scoring & Coaching (Đánh giá chấm điểm cuộc gọi)

### 1.2. Điểm mạnh của thiết kế

| Tiêu chí | Đánh giá | Chi tiết |
|----------|----------|----------|
| **Tính toàn diện** | ⭐⭐⭐⭐⭐ | Bao phủ đầy đủ 2 CASE, có kiến trúc rõ ràng |
| **Tính chi tiết** | ⭐⭐⭐⭐⭐ | Code mẫu, database schema, API specs đầy đủ |
| **Tính khả thi** | ⭐⭐⭐⭐ | Có giải pháp cold start khi chưa có baseline |
| **Tính mở rộng** | ⭐⭐⭐⭐⭐ | Microservices, horizontal scaling, monitoring |
| **Tính thực tiễn** | ⭐⭐⭐⭐ | Docker compose, deployment guides có sẵn |

---

## 2. MAPPING VỚI YÊU CẦU TỪ ẢNH

### 2.1. Use Case 1: Kiểm tra tuân thủ cập nhật CRM

| Yêu cầu (từ ảnh) | Thiết kế hiện tại | Đánh giá |
|------------------|-------------------|----------|
| **AI tự động phát hiện lỗi & cảnh báo nhắc nhở** | ✅ CASE 1 với Rules Engine phát hiện vi phạm M1/M2/M3 | Đáp ứng |
| **AI tự động quét rules** | ✅ Có hệ thống Rules Engine với thresholds có thể cấu hình | Đáp ứng |
| **Tạo bộ lọc, xuất dữ liệu** | ✅ Database schema hỗ trợ query và filter | Đáp ứng |
| **Ra soát tuân thủ phát hiện lỗi sai** | ✅ Detection rate, False positive <5% | Đáp ứng |
| **Tự động nhắc nhở Sales/CSKH sửa lỗi** | ✅ Reminders system với due_at, status tracking | Đáp ứng |
| **Tổng hợp báo cáo thống kê lỗi** | ✅ Reports aggregation, views for reporting | Đáp ứng |

### 2.2. Use Case 2: Đánh giá chấm điểm cuộc gọi

| Yêu cầu (từ ảnh) | Thiết kế hiện tại | Đánh giá |
|------------------|-------------------|----------|
| **AI chấm điểm & đánh giá cuộc gọi** | ✅ CASE 2 với KNGT + KNBH evaluation (0-10 điểm) | Đáp ứng tốt |
| **Tóm tắt nội dung Voice → Giúp view nhanh** | ✅ Executive summary 3-5 câu + highlights | Đáp ứng tốt |
| **Đánh giá chấm điểm theo checklist** | ✅ 7 criteria KNGT + 7 criteria KNBH với weights rõ ràng | Đáp ứng xuất sắc |
| **Đề xuất cải thiện theo ngữ cảnh** | ✅ Context-aware recommendations với actionable messages | Đáp ứng tốt |
| **Gợi ý kịch bản giao tiếp mẫu để tham khảo** | ✅ Suggested scripts by stage với when_to_use guides | Đáp ứng tốt |

---

## 3. PHÂN TÍCH CHI TIẾT CÁC THÀNH PHẦN

### 3.1. CASE 1: CRM Compliance (NTT - 10% điểm)

**Điểm mạnh:**
- ✅ Tách biệt rõ ràng với CASE 2 (độc lập module)
- ✅ Có hệ thống vi phạm M1/M2/M3 rõ ràng
- ✅ Integration point với CASE 2 để tính điểm tổng

**Cần bổ sung:**
- ⚠️ Chi tiết về Rules Engine cho CRM compliance
- ⚠️ Workflow nhắc nhở và escalation
- ⚠️ Cơ chế filter và export data

**Đề xuất cải thiện:**
```python
class CRMComplianceChecker:
    """
    CASE 1: Kiểm tra tuân thủ CRM
    """
    
    RULES = {
        "update_time": {
            "max_delay_hours": 24,
            "violation_levels": {
                "M1": (24, 48),    # 1-2 ngày
                "M2": (48, 72),    # 2-3 ngày
                "M3": (72, None)   # >3 ngày
            }
        },
        "required_fields": [
            "contact_outcome",
            "next_action",
            "notes"
        ],
        "minimum_note_length": 50
    }
    
    def check_compliance(self, call_id: str, crm_record: Dict) -> Dict:
        violations = []
        
        # Check update time
        delay_hours = self._calculate_delay(call_id, crm_record)
        if delay_hours > self.RULES["update_time"]["max_delay_hours"]:
            violations.append(self._classify_violation(delay_hours))
        
        # Check required fields
        for field in self.RULES["required_fields"]:
            if not crm_record.get(field):
                violations.append({
                    "type": "missing_field",
                    "field": field,
                    "level": "M2"
                })
        
        # Check note quality
        if len(crm_record.get("notes", "")) < self.RULES["minimum_note_length"]:
            violations.append({
                "type": "insufficient_notes",
                "level": "M1"
            })
        
        return {
            "compliant": len(violations) == 0,
            "violations": violations,
            "score_impact": self._calculate_score_impact(violations)
        }
```

### 3.2. CASE 2: Call Scoring (KNGT + KNBH - 90% điểm)

**Điểm mạnh:**
- ✅ Phân chia rõ ràng KNGT (Kỹ năng giao tiếp) và KNBH (Kỹ năng bán hàng)
- ✅ Dynamic weights theo call type (BH/CSKH) 
- ✅ Call Type Detection từ audio (không cần CRM)
- ✅ Speech Rate evaluation chi tiết với cold start strategy
- ✅ Customer Impact ưu tiên cao

**Điểm xuất sắc:**
- 🌟 **Cold Start Strategy:** Giải quyết vấn đề không có baseline ban đầu
- 🌟 **Context-aware:** Không phạt trong ngữ cảnh hợp lý (đọc OTP, KH yêu cầu)
- 🌟 **Evidence Generation:** Timestamps + quotes cụ thể

### 3.3. Speech Rate Evaluation (Tiêu chí SR)

**Phân tích độ sâu:**
Thiết kế Speech Rate đã rất chi tiết với:
- ✅ Segmentation theo speaker + pause (5-15s segments)
- ✅ VAD để xác định pause dài (≥700ms)
- ✅ WPM calculation loại trừ silence
- ✅ Customer Impact detection (yêu cầu nhắc lại)
- ✅ Absolute thresholds khi chưa có baseline

**Ngưỡng cụ thể:**
| Call Type | Quá chậm | Chậm | Tốt | Nhanh | Quá nhanh |
|-----------|----------|------|-----|-------|-----------|
| BH | <100 | 100-130 | 130-180 | 180-220 | >220 wpm |
| CSKH | <90 | 90-120 | 120-170 | 170-210 | >210 wpm |

---

## 4. KIẾN TRÚC & CÔNG NGHỆ

### 4.1. Architecture Review

```
Strengths:
✅ Microservices architecture → Scalable
✅ Message Queue (RabbitMQ) → Async processing
✅ Redis Cache → Performance
✅ PostgreSQL + Views → Reporting ready
✅ S3/MinIO → Audio storage
✅ Prometheus + Grafana → Monitoring

Weaknesses:
⚠️ Không có API Gateway chi tiết (chỉ mention Kong/Nginx)
⚠️ Thiếu Authentication/Authorization details
⚠️ Chưa có CI/CD pipeline
```

### 4.2. Technology Stack

| Layer | Technology | Phù hợp? |
|-------|------------|----------|
| API | FastAPI | ✅ Excellent choice (async, auto-docs) |
| Queue | Celery + RabbitMQ | ✅ Mature, reliable |
| Database | PostgreSQL 14+ | ✅ Perfect for structured data |
| Cache | Redis 7+ | ✅ Standard choice |
| STT | Whisper/Google STT | ✅ Good options |
| VAD | Silero VAD | ✅ Lightweight, CPU-only |
| Monitoring | Prometheus + Grafana | ✅ Industry standard |

---

## 5. GAP ANALYSIS

### 5.1. Những gì đã làm tốt

1. **Comprehensive Design:** Bao phủ đầy đủ 2 use cases
2. **Production Ready:** Có Docker compose, deployment guides
3. **Scalable Architecture:** Microservices, horizontal scaling
4. **Smart Solutions:** Cold start strategy, context-aware rules
5. **Detailed Implementation:** Code mẫu, database schema chi tiết

### 5.2. Những gì cần bổ sung

| Gap | Priority | Đề xuất |
|-----|----------|---------|
| **CRM Rules Engine chi tiết** | High | Thêm module rules configuration |
| **Reminder Workflow** | High | Design notification service |
| **Export/Filter mechanism** | Medium | API endpoints cho export Excel/CSV |
| **Authentication/Authorization** | High | JWT + RBAC implementation |
| **CI/CD Pipeline** | Medium | GitLab CI hoặc GitHub Actions |
| **Load Testing** | Low | Locust test scenarios |
| **Backup & Recovery** | Medium | Database backup strategy |

### 5.3. Đề xuất bổ sung cho Use Case 1

```yaml
# crm-compliance-service.yaml
apiVersion: v1
kind: Service
metadata:
  name: crm-compliance-service
spec:
  components:
    rules-engine:
      description: "Quét và kiểm tra rules tuân thủ"
      features:
        - Configurable rules per team/department
        - Real-time violation detection
        - Batch processing for historical data
    
    reminder-service:
      description: "Tự động nhắc nhở agent"
      features:
        - Email/SMS/In-app notifications
        - Escalation matrix (Agent → Supervisor → Manager)
        - Reminder frequency configuration
        - Snooze/Acknowledge tracking
    
    reporting-service:
      description: "Báo cáo và export"
      features:
        - Daily/Weekly/Monthly aggregation
        - Export to Excel/CSV/PDF
        - Drill-down by team/agent/time
        - Trend analysis and predictions
```

---

## 6. RISK ASSESSMENT

### 6.1. Technical Risks

| Risk | Impact | Likelihood | Mitigation |
|------|--------|------------|------------|
| **STT accuracy cho tiếng Việt** | High | Medium | Dùng multiple STT engines, ensemble |
| **False positive cao** | Medium | Medium | Customer Impact priority, human review |
| **Latency vượt 5s** | Medium | Low | Caching, parallel processing |
| **Baseline drift** | Low | Medium | Weekly baseline update (đã có) |

### 6.2. Business Risks

| Risk | Impact | Mitigation |
|------|--------|------------|
| **Agent resistance** | High | Training, gradual rollout, feedback loop |
| **Over-reliance on AI** | Medium | Human QA sampling 10-20% |
| **Privacy concerns** | High | Data encryption, access control, audit logs |

---

## 7. KẾT LUẬN & KHUYẾN NGHỊ

### 7.1. Tổng quan đánh giá

**Điểm số tổng thể: 8.5/10** 🌟

Thiết kế đã:
- ✅ **Đáp ứng đầy đủ** cả 2 use cases từ yêu cầu
- ✅ **Chi tiết và khả thi** cho implementation
- ✅ **Có giải pháp thông minh** cho các vấn đề thực tế (cold start, context-aware)
- ✅ **Production-ready** với monitoring, deployment guides

### 7.2. Khuyến nghị triển khai

#### Phase 1: MVP (Sprint 1-2)
1. **CASE 2 - Core Scoring:** KNGT + KNBH evaluation
2. **Speech Rate với cold start:** Dùng absolute thresholds
3. **Basic API:** Score submission + result retrieval

#### Phase 2: Enhancement (Sprint 3-4)  
1. **CASE 1 - CRM Compliance:** Rules engine + reminders
2. **Summary & Recommendations:** LLM integration
3. **Dashboard:** Real-time monitoring

#### Phase 3: Optimization (Sprint 5-6)
1. **Baseline calculation:** Từ dữ liệu tích lũy
2. **Export/Reporting:** Advanced analytics
3. **Performance tuning:** Caching, optimization

### 7.3. Success Metrics

| Metric | Target | Measure |
|--------|--------|---------|
| **Scoring Accuracy** | MAE ≤ 1.0 | Weekly validation vs manual QA |
| **Processing Speed** | <5s per call | P95 latency monitoring |
| **CRM Compliance Rate** | >85% | Daily compliance reports |
| **False Positive Rate** | <5% | Agent feedback tracking |
| **System Availability** | 99.9% | Uptime monitoring |

### 7.4. Final Recommendation

**✅ APPROVE thiết kế với điều kiện:**

1. Bổ sung chi tiết CRM Rules Engine (CASE 1)
2. Thêm Reminder/Notification service design
3. Clarify Authentication/Authorization strategy
4. Document data export/filter APIs

**Thiết kế này đã sẵn sàng cho development phase với các bổ sung nhỏ nêu trên.**

---

## 8. NEXT STEPS

1. **Immediate (Week 1):**
   - [ ] Finalize CRM Rules Engine specification
   - [ ] Setup development environment (Docker)
   - [ ] Create project structure and repositories

2. **Short-term (Week 2-4):**
   - [ ] Implement CASE 2 core (KNGT + KNBH)
   - [ ] Develop Speech Rate evaluator with cold start
   - [ ] Setup database and basic APIs

3. **Medium-term (Week 5-8):**
   - [ ] Implement CASE 1 (CRM Compliance)
   - [ ] Integrate STT service
   - [ ] Deploy to staging environment

4. **Long-term (Week 9-12):**
   - [ ] Performance optimization
   - [ ] User training and documentation
   - [ ] Production deployment

---

**Reviewed by:** System Architect  
**Date:** 11/10/2025  
**Status:** ✅ **APPROVED WITH CONDITIONS**

---

## PHỤ LỤC: CHECKLIST REVIEW

### Technical Checklist
- [x] Architecture design phù hợp
- [x] Database schema đầy đủ
- [x] API specification rõ ràng
- [x] Performance targets khả thi
- [x] Monitoring & logging adequate
- [x] Security considerations
- [ ] Authentication details (cần bổ sung)
- [ ] CI/CD pipeline (cần bổ sung)

### Business Checklist
- [x] Đáp ứng Use Case 1 (CRM Compliance)
- [x] Đáp ứng Use Case 2 (Call Scoring)
- [x] ROI justifiable
- [x] Scalability cho growth
- [x] Training plan outlined
- [ ] Change management plan (cần bổ sung)

### Compliance Checklist
- [x] Data privacy addressed
- [x] Audit trail capability
- [ ] GDPR/Legal compliance (cần review)
- [ ] Disaster recovery plan (cần bổ sung)