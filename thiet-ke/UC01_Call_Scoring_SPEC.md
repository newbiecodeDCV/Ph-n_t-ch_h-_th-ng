# UC01 – Đánh giá chấm điểm cuộc gọi (Re-Spec)

Trạng thái: Draft v0.1 – Chỉ tập trung CASE chấm điểm cuộc gọi. Các nội dung CRM compliance được coi là bối cảnh/tham chiếu, không thuộc phạm vi tính điểm của UC01.

## 1) Mục tiêu
- Tự động chấm điểm và đánh giá cuộc gọi giữa Agent và Khách hàng.
- Cung cấp tóm tắt nội dung cuộc gọi (executive summary) để xem nhanh.
- Chấm điểm theo checklist KNGT (kỹ năng giao tiếp) và KNBH (kỹ năng bán hàng/giải quyết yêu cầu) tùy theo loại cuộc gọi BH/CSKH.
- Đề xuất cải thiện theo ngữ cảnh và gợi ý kịch bản giao tiếp mẫu.
- Lưu trữ bằng chứng (evidence) cho từng tiêu chí.

## 2) Phạm vi và nguyên tắc
- Phạm vi: chỉ chấm KNGT và KNBH. Không chấm NTT/tuân thủ CRM trong UC01 (được xử lý ở UC09).
- Call type: KHÔNG cung cấp sẵn. Hệ thống phải tự phát hiện từ audio/transcript (audio-only). CRM không bắt buộc cho bước này.
- Ưu tiên “Customer Impact” (mức độ khách hàng hiểu/đồng thuận) hơn các vi phạm kỹ thuật thuần túy.
- Context-aware: Không phạt trong các ngữ cảnh hợp lý (đọc OTP, KH yêu cầu nói nhanh/chậm, tra cứu thông tin,…).

## 3) Actors
- Agent (Sales/CSKH): Nhận kết quả, xem evidence, khuyến nghị.
- QA Reviewer: Theo dõi chất lượng, hiệu chỉnh thresholds/weights.
- Manager: Xem báo cáo đội, xu hướng điểm.

## 4) Đầu vào (Inputs)
- Audio recording + transcript có diarization (AGENT/CUSTOMER) với timestamps.
- Metadata: call_id, agent_id, call_time. Không yêu cầu call_type.
- Signals/Features (tối thiểu): wpm (words per minute) theo segment, pause_ratio, interrupt_count, sentiment trend, customer_repeat_count, explicit_complaint flags.

### 4.1) Phát hiện loại cuộc gọi từ audio (audio-only)
- Đầu vào: transcript (ưu tiên 30–60 giây đầu) + cues hội thoại.
- Tín hiệu: từ khóa/chủ đề (bán hàng, giá, ưu đãi vs. lỗi, khiếu nại, hỗ trợ), hành động hội thoại (giới thiệu sản phẩm vs. xác minh/giải quyết vấn đề), mẫu tương tác (agent dẫn dắt chào bán vs. khách mở khiếu nại), sentiment pattern.
- Đầu ra: call_type_pred ∈ {BH, CSKH} và confidence ∈ [0, 1].
- Quy tắc sử dụng: nếu confidence ≥ τ (ví dụ 0.75) → áp trọng số theo type; nếu < τ → dùng cơ chế “mixture-of-weights” hoặc mặc định neutral.

## 5) Đầu ra (Outputs)
- Tổng điểm 0–10, nhãn xếp loại (Yếu/Trung bình/Khá/Tốt/Xuất sắc), passed (>=5.0).
- Breakdown theo nhóm KNGT/KNBH và theo tiêu chí con.
- Executive summary (3–5 câu súc tích) + Key highlights.
- Recommendations theo ngữ cảnh, gắn với tiêu chí vi phạm.
- Suggested scripts (mẫu câu) phù hợp lỗi.
- Evidence: trích đoạn transcript + metrics kèm timestamp.

## 6) Khung chấm điểm

### 6.1. Trọng số nhóm theo loại cuộc gọi
- Trọng số được quyết định bởi call_type_pred (từ bước phát hiện dựa trên audio).
- Nếu confidence ≥ τ: áp trọng số của type tương ứng.
- Nếu confidence < τ: dùng “mixture-of-weights” theo xác suất: W_eff = p_BH·W_BH + (1−p_BH)·W_CSKH (hoặc mặc định 50/50 nếu chưa ước lượng được p_BH).
- Giá trị đề xuất khi chắc chắn (confidence cao):
  - BH: KNGT 40% | KNBH 60%
  - CSKH: KNGT 70% | KNBH 30%

### 6.2. Nhóm KNGT (Kỹ năng giao tiếp)
Tiêu chí con (ví dụ, có thể tinh chỉnh sau review):
1) Chào hỏi & xưng danh (GRT) – có/không + chất lượng
2) Tốc độ nói & rõ ràng (SR) – dựa trên baseline wpm + customer impact
3) Âm lượng & nhịp (VOL) – phù hợp, không quá to/nhỏ, nhịp đều
4) Lắng nghe & không ngắt lời (LSN) – interrupt_count, turn-taking
5) Đồng cảm & thái độ (EMP) – từ ngữ đồng cảm, phản hồi phù hợp
6) Ngôn ngữ phù hợp (LAN) – lịch sự, không tiêu cực, tránh jargon
7) Kết thúc lịch sự (CLS) – cảm ơn, tóm tắt, chốt bước tiếp theo

Mức lỗi và gợi ý mapping:
- OK: Không lỗi đáng kể
- M1: Lỗi nhẹ (không ảnh hưởng lớn đến hiểu/đồng thuận của KH)
- M2: Lỗi trung bình (ảnh hưởng rõ đến trải nghiệm/hiểu của KH)
- M3: Lỗi nặng (KH hiểu sai, bức xúc, bỏ cuộc)

Điểm nhóm KNGT = Weight_KNGT × (1 − Penalty_KNGT)
- Penalty dựa trên mức lỗi cao nhất trong các tiêu chí con, có thể cộng dồn nhỏ cho nhiều M1.

### 6.3. Nhóm KNBH (BH) / KNSV (CSKH)
Tùy call_type:
- Với BH (KNBH):
  1) Xác nhận thông tin (CIN)
  2) Dẫn dắt cuộc gọi (LEAD)
  3) Khai thác nhu cầu (NEED)
  4) Nắm bắt vấn đề (PRB)
  5) Tư vấn sản phẩm phù hợp (ADV)
  6) Xử lý từ chối (OBJ)
  7) Chốt & CTA rõ ràng (CLS2)
- Với CSKH (KNSV – kỹ năng dịch vụ):
  1) Xác nhận vấn đề (ISS)
  2) Chuẩn đoán nguyên nhân (DGN)
  3) Đưa giải pháp & hướng dẫn (SOL)
  4) Xác nhận lại & follow-up (FUP)

Cách tính tương tự KNGT, nhấn mạnh outcome (đồng ý bước tiếp theo/giải quyết vấn đề).

### 6.4. Context-aware rules (không phạt trong ngữ cảnh hợp lý)
- Pause dài khi tra cứu/đọc OTP/điều khoản
- Nói nhanh/chậm theo yêu cầu KH
- Nhắc lại thông tin quan trọng với pace chậm hơn

## 7) Executive Summary – Đặc tả
- Độ dài: 3–5 câu, < 80 từ
- Nội dung tối thiểu:
  - Mục đích cuộc gọi & call type
  - Nhu cầu/vấn đề chính của KH (1 câu)
  - Hành động của Agent (2–3 ý chính)
  - Kết quả & bước tiếp theo (nếu có)
- Cấu trúc gợi ý:
  "Cuộc gọi [BH/CSKH] về [chủ đề]. KH [nhu cầu/vấn đề]. Agent đã [tóm tắt hành động]. Kết quả: [kết quả]. Next step: [bước tiếp theo]."

## 8) Recommendations – Đặc tả
- Mapping lỗi → khuyến nghị cụ thể, actionable.
- Ví dụ:
  - SR=M2: "Giảm tốc độ xuống 130–140 wpm khi trình bày điều khoản; xen kẽ câu ngắn và kiểm tra sự hiểu của KH."
  - LSN=M1: "Tránh cắt lời; đợi 1–2s sau khi KH dừng trước khi phản hồi."
  - NEED=M2: "Dùng 2–3 câu hỏi mở để làm rõ nhu cầu cốt lõi trước khi tư vấn."

## 9) Suggested Scripts – Đặc tả
- Theo call_type và stage.
- Ví dụ (BH – Objection Handling):
  - "Em hiểu anh/chị đang băn khoăn về chi phí. Cho em hỏi hiện tại anh/chị kỳ vọng ngân sách khoảng…? Em đề xuất gói… vì…"
- Ví dụ (CSKH – Solution Delivery):
  - "Để khắc phục nhanh, em xin phép hướng dẫn anh/chị theo 3 bước… Nếu vẫn chưa ổn, em sẽ tạo ticket ưu tiên và cập nhật trong hôm nay."

## 10) Output JSON – Mẫu (tham chiếu, chưa ràng buộc implementation)
```json
{
  "call_id": "CALL-2025-001",
  "call_type": "BH",
  "summary": "Cuộc gọi BH về gói A. KH quan tâm đến... Agent đã ... Kết quả ... Next step ...",
  "score": {
    "total": 7.8,
    "label": "Khá",
    "passed": true,
    "groups": {
      "KNGT": {"points": 3.1, "weight": 0.4, "violations": [
        {"code": "SR", "level": "M1", "evidence": {"wpm": 150, "baseline": 130, "ts": ["00:04:10-00:04:35"]}}
      ]},
      "KNBH": {"points": 4.7, "weight": 0.6, "violations": [
        {"code": "NEED", "level": "M2", "evidence": {"quote": "…", "ts": ["00:02:10-00:02:30"]}}
      ]}
    }
  },
  "recommendations": [
    "Giảm pace khi trình bày điều khoản quan trọng",
    "Dùng 2 câu hỏi mở để làm rõ nhu cầu"
  ],
  "suggested_scripts": ["scripts/bh/objection_cost_v1"],
  "evidence_refs": [
    {"ts": "00:04:10-00:04:35", "text": "…"},
    {"ts": "00:02:10-00:02:30", "text": "…"}
  ]
}
```

## 11) Tiêu chí nghiệm thu
- Với tập 100 cuộc gọi đã có nhãn từ QA:
  - MAE điểm tổng so với QA thủ công ≤ 1.0
  - F1 cho phát hiện lỗi M2/M3 trong các tiêu chí chính ≥ 0.8
  - Thời gian sinh báo cáo cho 1 cuộc gọi ≤ 5 giây (không tính thời gian STT)
- Báo cáo hiển thị đầy đủ: summary, breakdown, evidence, recommendations, scripts.

## 12) Rủi ro & phương án
- Sai lệch ngữ cảnh → Có human review sample 10% để hiệu chỉnh.
- Chất lượng STT kém → Flag "audio quality low" và hạn chế penalize từ transcript.
- Tiêu chí mơ hồ → Chuẩn hóa definitions + ví dụ minh họa.

## 13) Phụ lục A – Bảng tiêu chí chi tiết (draft)

| Code | Tiêu chí                     | BH Weight | CSKH Weight | M1 (Ví dụ)                               | M2 (Ví dụ)                                       | M3 (Ví dụ)                               |
|------|------------------------------|-----------|-------------|-------------------------------------------|--------------------------------------------------|-------------------------------------------|
| GRT  | Chào hỏi & xưng danh        | 0.05      | 0.08        | Thiếu 1 thành phần                         | Không chào/xưng danh                            | Thô lỗ/mất lịch sự                         |
| SR   | Tốc độ nói & rõ ràng        | 0.08      | 0.10        | >±1σ trong 20% thời lượng                  | >±2σ trong 30–40%                               | >±2.5σ >40% + KH hiểu sai/bỏ cuộc         |
| VOL  | Âm lượng & nhịp             | 0.04      | 0.06        | Hơi to/nhỏ                                 | Quá to/nhỏ, ảnh hưởng trải nghiệm               | Gây khó nghe nghiêm trọng                  |
| LSN  | Lắng nghe, không ngắt lời   | 0.06      | 0.08        | 1–2 lần cắt lời nhẹ                        | Nhiều lần cắt lời, không xác nhận lại           | Tranh luận gay gắt, làm gián đoạn KH      |
| EMP  | Đồng cảm & thái độ          | 0.05      | 0.08        | Thiếu cụm từ đồng cảm                      | Dập tắt cảm xúc KH                              | Thái độ tiêu cực/mỉa mai                   |
| LAN  | Ngôn ngữ phù hợp            | 0.05      | 0.05        | Một vài từ chưa lịch sự                    | Từ ngữ không phù hợp bối cảnh                   | Từ ngữ xúc phạm                             |
| CLS  | Kết thúc lịch sự            | 0.07      | 0.07        | Không tóm tắt                               | Không chốt next step                            | Kết thúc đột ngột, không chào tạm biệt    |
| NEED | Khai thác nhu cầu (BH)      | 0.10      | -           | Câu hỏi đóng nhiều                         | Không làm rõ nhu cầu chính                      | Tư vấn sai nhu cầu                          |
| LEAD | Dẫn dắt cuộc gọi (BH)       | 0.08      | -           | Luồng nói vòng                              | Lạc hướng, không kiểm soát nhịp                 | Mất kiểm soát hoàn toàn                     |
| ADV  | Tư vấn sản phẩm (BH)        | 0.10      | -           | Lợi ích chưa rõ                             | Tư vấn mơ hồ/sai thông tin                      | Tư vấn sai nghiêm trọng                     |
| OBJ  | Xử lý từ chối (BH)          | 0.07      | -           | Phản hồi chung chung                         | Không xử lý lý do từ chối                       | Tranh luận/đẩy trách nhiệm                  |
| CLS2 | Chốt & CTA (BH)             | 0.08      | -           | CTA chưa rõ                                 | Không chốt bước tiếp theo                       | Chốt sai/áp lực tiêu cực                    |
| ISS  | Xác nhận vấn đề (CSKH)      | -         | 0.10        | Xác nhận mơ hồ                              | Hiểu sai vấn đề                                 | Bỏ lỡ vấn đề chính                          |
| DGN  | Chuẩn đoán nguyên nhân      | -         | 0.08        | Giả định thiếu chứng cứ                     | Chẩn đoán sai                                   | Gây hiểu sai nghiêm trọng                   |
| SOL  | Đưa giải pháp & hướng dẫn   | -         | 0.08        | Hướng dẫn thiếu bước                        | Hướng dẫn sai/khó làm theo                      | Gợi ý sai gây rủi ro                         |
| FUP  | Xác nhận & follow-up        | -         | 0.04        | Không xác nhận lại                          | Không hẹn follow-up                              | Không ghi nhận trách nhiệm theo dõi         |

Ghi chú: Tổng trọng số trong bảng theo từng call_type = 1.0. Bảng này là draft để review business trước khi đóng băng.
