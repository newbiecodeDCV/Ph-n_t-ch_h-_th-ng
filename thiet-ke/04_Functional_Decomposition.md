# Functional Decomposition – Theo hai nhóm chức năng trong hình

Trạng thái: Draft v0.1 – Mục tiêu là phân rã CHỨC NĂNG đúng như hình bạn cung cấp. Các tiêu chí chấm điểm đã biết sẽ được dùng trong nhánh “Đánh giá chấm điểm cuộc gọi”. Không có phần code trong tài liệu này.

---

## 0) Phạm vi chung
- Đối tượng: Cuộc gọi giữa Agent và Khách hàng (BH/CSKH) và các bản ghi CRM liên quan.
- Hai nhóm chức năng chính (song song, độc lập về mục tiêu):
  1) Kiểm tra tuân thủ cập nhật CRM của Sales/CSKH (CRM Compliance Checking)
  2) Đánh giá chấm điểm cuộc gọi của Sales trao đổi với KH (Call Scoring & Evaluation)
- Cross-cutting: Bảo mật, audit, retention, RBAC, quan sát hệ thống.

---

## 1) Tổng quan phân rã chức năng (Top-level)

```mermaid
flowchart TD
  A[AI QA Assistant] --> B[1. CRM Compliance Checking]
  A --> C[2. Call Scoring & Evaluation]

  %% 1) CRM Compliance
  B --> B1[Quy tắc & Bộ lọc (Rules/Filters)]
  B --> B2[Quét & Đánh giá tuân thủ (Scan & Evaluate)]
  B --> B3[Phân loại vi phạm (M1/M2/M3)]
  B --> B4[Nhắc nhở & Escalation]
  B --> B5[Theo dõi khắc phục (Tracking)]
  B --> B6[Tổng hợp báo cáo thống kê]
  B --> B7[Audit logs & Traceability]

  %% 2) Call Scoring
  C --> C1[STT + Diarization]
  C --> C1b[Phát hiện loại cuộc gọi từ audio\n(call_type_pred, confidence)]
  C --> C2[Trích xuất dữ liệu]
  C --> C3[Tóm tắt nội dung (Executive Summary)]
  C --> C4[Chấm điểm theo checklist (KNGT/KNBH/KNSV)]
  C --> C5[Đề xuất cải thiện theo ngữ cảnh]
  C --> C6[Gợi ý kịch bản giao tiếp mẫu]
  C --> C7[Tạo báo cáo & hiển thị]
  C --> C8[Hiệu chỉnh ngưỡng & baseline]
```

---

## 2) Nhóm chức năng 1 – Kiểm tra tuân thủ cập nhật CRM

### 2.1. Mục tiêu
- AI tự động phát hiện lỗi và cảnh báo nhắc nhở; tổng hợp báo cáo thống kê lỗi.

### 2.2. Phân rã chức năng
- F1.1 Rules/Filters Management
  - Khai báo tập rules: required_fields theo BH/CSKH; chất lượng notes; ticket/case bắt buộc theo tình huống; SLA cập nhật trong X phút; điều kiện đặc thù theo quy trình nội bộ.
  - Bộ lọc phạm vi quét: theo thời gian, team, campaign, call_type…
- F1.2 Data Ingestion (CRM)
  - Lấy records CRM theo call_id/customer_id trong khung thời gian.
  - Kết hợp metadata cuộc gọi nếu cần (agent_id, call_time…).
- F1.3 Compliance Evaluation
  - Áp rules để phát hiện violations: missing fields, poor notes, missing ticket/opportunity, SLA violation, v.v.
- F1.4 Violation Classification
  - Phân loại mức độ: M1 (nhẹ), M2 (trung bình), M3 (nặng) theo ngưỡng.
- F1.5 Reminder & Escalation
  - Sinh nhắc nhở cho Agent (kênh email/chat/SMS). M3 gửi ngay + escalate Manager.
  - SLA cho nhắc nhở (due time) và retry khi chưa gửi được.
- F1.6 Resolution Tracking
  - Theo dõi trạng thái: pending → sent → resolved/escalated/expired.
  - Tự kiểm tra lại CRM sau due time để xác nhận đã sửa.
- F1.7 Reporting & Analytics
  - Báo cáo tổng hợp/slice theo đội, agent, type, severity, thời gian.
  - KPI: detection rate, resolution rate, avg resolution time, escalation rate.
- F1.8 Audit & Traceability
  - Ghi log chi tiết rule áp dụng, evidence, ai nhận nhắc nhở, khi nào sửa xong.

### 2.3. Input/Output (mức logic)
- Input: CRM records (customer, ticket/case, opportunity, notes, timestamps), call metadata.
- Output:
  - Violations: {call_id, agent_id, type, severity, evidence, detected_at}
  - Reminders: {recipient, message, channel, due_at, status}
  - Reports: {by_type, by_severity, by_agent, trend}

### 2.4. Tiêu chí nghiệm thu (cho CRM compliance)
- >95% violations nghiêm trọng (M3) được phát hiện trong vòng X phút.
- >85% reminders được giải quyết trước hạn (resolution rate).
- False positive rate < 5% (được QA xác nhận trên mẫu).

---

## 3) Nhóm chức năng 2 – Đánh giá chấm điểm cuộc gọi

### 3.1. Mục tiêu
- AI chấm điểm & đánh giá cuộc gọi; cung cấp tóm tắt; đề xuất cải thiện; gợi ý kịch bản giao tiếp mẫu.

### 3.2. Phân rã chức năng
- F2.0 Call Type Detection (Audio-only)
  - Phân loại BH vs CSKH dựa hoàn toàn trên audio/transcript (không phụ thuộc CRM).
  - Tín hiệu: từ khóa/chủ đề, ý định (intent), hành động hội thoại, pattern tương tác đầu cuộc gọi (30–60s đầu), sentiment.
  - Đầu ra: call_type_pred và confidence (0–1). Nếu confidence thấp, sử dụng mixture-of-weights cho việc tính điểm.
- F2.1 Speech-to-Text & Diarization
  - Chuyển audio → transcript có phân vai (AGENT/CUSTOMER) + timestamps.
- F2.2 Feature Extraction
  - Trích xuất wpm theo segment (đã loại im lặng hợp lý), pause_ratio, interrupt_count, sentiment trend, repeats, keyword cues…
- F2.3 Executive Summary
  - Tạo tóm tắt 3–5 câu: mục đích, nhu cầu/vấn đề KH, hành động của Agent, kết quả & bước tiếp theo.
- F2.4 Checklist-based Scoring
  - Ánh xạ tiêu chí đã biết vào 2 nhóm: KNGT và KNBH/KNSV (tùy BH/CSKH).
  - Ví dụ KNGT: Chào hỏi/xưng danh (GRT), Tốc độ & rõ ràng (SR), Âm lượng & nhịp (VOL), Lắng nghe (LSN), Đồng cảm (EMP), Ngôn ngữ (LAN), Kết thúc lịch sự (CLS).
  - Ví dụ KNBH (BH): Xác nhận thông tin (CIN), Dẫn dắt (LEAD), Khai thác nhu cầu (NEED), Nắm bắt vấn đề (PRB), Tư vấn (ADV), Xử lý từ chối (OBJ), Chốt & CTA (CLS2).
  - Ví dụ KNSV (CSKH): ISS, DGN, SOL, FUP.
  - Trọng số nhóm (đề xuất, có thể tinh chỉnh):
    - BH: KNGT 40% | KNBH 60%
    - CSKH: KNGT 70% | KNSV 30%
  - Context-aware: không phạt ở các ngữ cảnh hợp lý (đọc OTP, KH yêu cầu pace, tra cứu…).
- F2.5 Recommendations (Contextual Coaching)
  - Mapping từ violation/code → khuyến nghị cụ thể, actionable.
- F2.6 Suggested Scripts
  - Gợi ý kịch bản mẫu theo call_type và stage (ví dụ: objection handling, solution delivery…).
- F2.7 Report Generation & Delivery
  - Báo cáo cho từng cuộc gọi: score 0–10, label, passed, breakdown, evidence (trích đoạn + metric), summary, recommendations, scripts.
- F2.8 Calibration & Governance
  - Hiệu chỉnh baseline/thresholds theo feedback của QA Reviewer; theo dõi MAE/F1.

### 3.3. Input/Output (mức logic)
- Input: audio + transcript + features; metadata: call_id, agent_id, call_time, call_type.
- Output:
  - Score object: {total, label, passed, groups[KNGT/KNBH], violations[], evidence_refs[]}
  - Summary text; Recommendations[]; ScriptIDs[]

### 3.4. Tiêu chí nghiệm thu (cho Call Scoring)
- MAE điểm tổng với QA thủ công ≤ 1.0 trên tập mẫu chuẩn.
- F1 phát hiện M2/M3 trong tiêu chí chính ≥ 0.8.
- Thời gian sinh báo cáo cho 1 cuộc gọi ≤ 5s (không tính STT).

---

## 4) Liên kết hai nhóm chức năng (không phụ thuộc nhưng bổ trợ)
- Dữ liệu call_id, agent_id, call_time là chìa khóa nối kết giữa chấm điểm và compliance.
- Dashboard hợp nhất có thể hiển thị:
  - Điểm cuộc gọi + lỗi CRM (nếu có) theo thời gian.
  - Coaching view: từ vi phạm/điểm thấp → khuyến nghị → kịch bản mẫu.

---

## 5) Non-functional & Cross-cutting
- Security & Privacy: RBAC, encryption in transit/at rest, PII masking.
- Audit: ghi nhận mọi thay đổi rules/thresholds, ai xem dữ liệu gì.
- Observability: metrics (throughput, latency), business KPIs (resolution rate, score distribution).
- Data retention: audio 90 ngày (gợi ý), transcripts 1 năm, scores 3 năm (tùy chính sách).

---

## 6) Phụ lục – Functional to Feature Mapping (mẫu)

| Nhóm | Mã chức năng | Mô tả ngắn | Đầu vào | Đầu ra | KPI chính |
|------|---------------|-----------|---------|--------|-----------|
| CRM | F1.1 | Quản lý rules/filters | Rule config | Bản rules active | N/A |
| CRM | F1.2 | Ingest CRM records | call_id/time range | Dataset records | N/A |
| CRM | F1.3 | Evaluate compliance | Records + Rules | Violations[] | Detection rate |
| CRM | F1.4 | Classify severity | Violations | Labeled M1/M2/M3 | FP rate |
| CRM | F1.5 | Reminders & Escalation | Violations | Reminders | Resolution rate |
| CRM | F1.6 | Tracking | Reminders + CRM | Status timeline | Avg resolution time |
| CRM | F1.7 | Reporting | Violations history | Aggregates | Trend stability |
| CRM | F1.8 | Audit | Actions | Audit log | Coverage |
| Call | F2.1 | STT & Diarization | Audio | Transcript | STT success rate |
| Call | F2.2 | Feature extraction | Transcript | Features | Feature completeness |
| Call | F2.3 | Summary | Transcript | 3–5 câu | Readability score |
| Call | F2.4 | Checklist scoring | Features + Rules | Score breakdown | MAE, F1 |
| Call | F2.5 | Recommendations | Violations | List recs | Adoption rate |
| Call | F2.6 | Script suggestions | Violations | Script IDs | Usage rate |
| Call | F2.7 | Report delivery | Score + recs | Report view | Report latency |
| Call | F2.8 | Calibration | Feedback | Updated thresholds | Drift control |

---

## 7) Quy ước & tiếp theo
- Tài liệu này nêu phân rã chức năng theo đúng hai khối trong hình. 
- Nếu bạn đồng ý, bước kế tiếp sẽ là: 
  1) Khóa danh sách chức năng con (F1.x, F2.x) và KPI. 
  2) Chuẩn hóa dữ liệu vào/ra dạng schema mô tả (không code). 
  3) Vẽ thêm Component Diagram cho từng nhóm (nếu cần). 
