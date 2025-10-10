# Master Specification – AI QA Call (CASE chuẩn)

Trạng thái: Draft v0.1 – Tổng hợp chuẩn trước khi phân rã case cụ thể. Là nguồn tham chiếu duy nhất (single source of truth) cho thuật ngữ, phạm vi, trọng số, quy tắc chấm điểm và luồng chính.

## 1. Phạm vi & CASE chuẩn
- CASE 1 – CRM Compliance: AI quét rules/bộ lọc → phát hiện vi phạm M1/M2/M3 → nhắc nhở Agent → theo dõi khắc phục → báo cáo tổng hợp.
- CASE 2 – Call Scoring & Coaching: STT + diarization → phát hiện call_type từ audio → trích xuất tín hiệu → chấm điểm theo checklist KNGT/KNBH/NTT (đúng chuẩn) → tóm tắt → khuyến nghị → gợi ý kịch bản → báo cáo chi tiết.

Ghi chú: Call type KHÔNG cung cấp sẵn; hệ thống tự phát hiện từ audio/transcript (audio-only). CRM bắt buộc ở CASE 1 và nhóm NTT trong chấm điểm.

## 2. Actors
- Agent (Sales/CSKH), QA Reviewer, Team Manager, Admin; External: PBX/Telephony, CRM, Notification.

## 3. Chuẩn chấm điểm (theo tài liệu “Tiêu chí chấm”)
- Tổng điểm 10, xếp loại: Yếu [0–<5.0] | Trung bình [5.0–<7.0] | Khá [7.0–<8.0] | Tốt [8.0–<9.0] | Xuất sắc [9.0–10].
- Phân bổ điểm theo loại cuộc gọi:
  - BH: KNGT 20% (2.0) | KNBH 70% (7.0) | NTT 10% (1.0)
  - CSKH: KNGT 40% (4.0) | KNBH 50% (5.0) | NTT 10% (1.0)
- KNGT (trên điểm nhóm KNGT):
  - Chào/xưng danh 10% → BH 0.2 | CSKH 0.4
  - Kỹ năng nói (tốc độ & âm lượng) 10% → BH 0.2 | CSKH 0.4
  - Kỹ năng nghe, trấn an 40% → BH 0.8 | CSKH 1.6
  - Thái độ giao tiếp & ngôn ngữ 40% → BH 0.8 | CSKH 1.6
- KNBH (trên điểm nhóm KNBH):
  - Xác nhận thông tin 5% → BH 0.35 | CSKH 0.25
  - Tiếp cận/Dẫn dắt 10% → BH 0.7 | CSKH 0.5
  - Khai thác thực trạng & nhu cầu 20%/30% → BH 1.4 | CSKH 1.5
  - Nắm bắt vấn đề 10% → BH 0.7 | CSKH 0.5
  - Tư vấn & Hỗ trợ sản phẩm 30%/5% → BH 2.1 | CSKH 0.25
  - Đề xuất giải pháp/ Xử lý rào cản/ Thuyết phục 20%/30% → BH 1.4 | CSKH 1.5
  - Kết thúc (CTA/Follow-up) 5%/10% → BH 0.35 | CSKH 0.5
- NTT (CRM/ticket): 10% tổng điểm (BH/CSKH đều 1.0).
- Quy tắc trừ điểm:
  - KNGT & KNBH: M1 → trừ theo tỷ trọng tiêu chí; M2 → trừ 50% điểm nhóm; M3 → nhóm = 0.
  - NTT: M1 → trừ 20%; M2 → trừ 50%; M3 → nhóm = 0.

## 4. Call Type Detection (audio-only)
- Input: transcript (ưu tiên 30–60s đầu) + cues hội thoại.
- Signals: từ khóa/chủ đề; hành động hội thoại; mô hình tương tác đầu cuộc gọi; sentiment pattern.
- Output: call_type_pred ∈ {BH, CSKH}, confidence ∈ [0,1].
- Khi confidence < τ (ví dụ 0.75): dùng mixture-of-weights khi tính điểm.

## 5. CASE 1 – CRM Compliance: I/O & KPIs (logic)
- Input: CRM records (notes, ticket/case, opportunity, updated_at), call metadata.
- Output: Violations[{type, severity, evidence}], Reminders[{agent_id, message, due_at, status}], Reports (aggregates/trends).
- KPIs: detection rate, false positive rate (<5%), resolution rate (>85%), avg resolution time, escalation rate.

## 6. CASE 2 – Call Scoring & Coaching: I/O & KPIs (logic)
- Input: Audio + transcript + features; metadata: call_id, agent_id, call_time.
- Output: Score (total, label, passed, breakdown per group), violations (M1/M2/M3) + evidence (trích đoạn + timestamps), summary 3–5 câu, recommendations[], script_ids[].
- KPIs: MAE tổng ≤ 1.0; F1 phát hiện M2/M3 ≥ 0.8; latency sinh báo cáo ≤ 5s (không tính STT).

## 7. Luồng tổng quan (Mermaid)
```mermaid
flowchart LR
  subgraph CASE 2: Call Scoring
    A[Audio + Metadata] --> B[STT + Diarization]
    B --> C[Call Type Detection (audio-only)]
    B --> D[Extract Features]
    C --> E[Score KNGT/KNBH/NTT]
    D --> E
    E --> F[Summary]
    E --> G[Recommendations]
    E --> H[Suggested Scripts]
    F --> I[Report + Store]
    G --> I
    H --> I
  end

  subgraph CASE 1: CRM Compliance
    CRM[CRM Records] --> R1[Apply Rules/Filters]
    R1 --> R2[Detect Violations]
    R2 --> R3[Classify M1/M2/M3]
    R3 --> R4[Remind + Escalate]
    R4 --> R5[Track Resolution]
    R5 --> R6[Aggregate Reports]
  end
```

## 8. Thuật ngữ chung (Glossary)
- KNGT: Kỹ năng giao tiếp; KNBH: Kỹ năng bán hàng; NTT: Nhập thông tin CRM/ticket; CTA: Call-to-Action.
- Confidence (call type): độ tin cậy của dự đoán loại cuộc gọi từ audio.
- Evidence: trích đoạn transcript + timestamps + metric chứng minh vi phạm.

## 9. Bảo mật & Phi chức năng (tóm tắt)
- RBAC; mã hoá in-transit (TLS 1.2/1.3) & at-rest; PII masking.
- Observability: metrics (throughput, latency), business KPIs (như trên).
- Retention gợi ý: Audio 90 ngày; Transcript 1 năm; Scores/Reports 3 năm.

## 10. Quy ước tài liệu & liên kết
- UC01 – Đánh giá chấm điểm cuộc gọi
- UC04 – Kiểm tra tuân thủ cập nhật CRM
- DFD/Sequence/Activity đã cập nhật call_type audio-only.
- Mọi thay đổi về trọng số/tiêu chí phải cập nhật vào tài liệu này trước.
