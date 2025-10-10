# Pha 1: Thiết lập baseline và rule engine cho chấm QA cuộc gọi

Mục tiêu Pha 1
- Chuẩn hoá đầu vào (transcript, CRM) và thiết lập baseline cho tốc độ nói.
- Xây dựng rule engine tối thiểu để: (a) kiểm tra tuân thủ CRM, (b) chấm tiêu chí KNGT/"Kỹ năng nói" (nhanh/chậm, giọng địa phương) theo M1/M2/M3, tính điểm 0–10.
- Xuất báo cáo chi tiết cho từng cuộc gọi: điểm nhóm, tổng điểm, Đạt/Không đạt và bằng chứng (đoạn transcript, số liệu WPM, repeat count, CRM violations).

Dữ liệu đầu vào cần có
- transcripts.jsonl: mỗi dòng một cuộc gọi gồm các segment có speaker (AGENT/CUSTOMER), start, end, text; và signals tùy chọn (wer_gap, customer_repeat_count...).
- crm.jsonl (tùy chọn Pha 1): mỗi dòng chứa call_id và danh sách vi phạm/fields để tính nhóm NTT.
- Loại cuộc gọi cho mỗi record: BH hoặc CSKH (nếu chưa có, tạm lấy từ metadata).

Baseline tốc độ nói (khuyến nghị)
- Lấy tối thiểu 200 cuộc gọi “đạt”/điểm tốt hiện tại làm tập chuẩn.
- Tính tốc độ nói (WPM hoặc số âm tiết/phút) trên các segment của AGENT; bỏ im lặng.
- Tham số baseline: baseline_rate, baseline_std.
- Ánh xạ mức lỗi theo tỷ lệ thời lượng vượt ngưỡng (ví dụ M1: ±1σ ≥ 20%; M2: ±2σ ≥ 30%; M3: ±2.5σ ≥ 40%).

Rule engine (tối thiểu trong Pha 1)
- KNGT → Kỹ năng nói (tốc độ & âm lượng): dùng baseline + ngưỡng sigma để xác định M1/M2/M3.
- "Giọng địa phương": không phạt vì “có giọng”, chỉ phạt khi gây khó hiểu. Tín hiệu: wer_gap (ASR), customer_repeat_count, flags của reviewer.
- NTT (CRM):
  - M1: trừ 20% điểm nhóm khi thiếu nhỏ/ghi chú sơ sài.
  - M2: trừ 50% khi thiếu nhiều trường quan trọng hoặc chậm SLA rõ rệt.
  - M3: điểm nhóm = 0 nếu không nhập/không tạo ticket bắt buộc.
- KNBH: Pha 1 chưa tự động hoá; tạm giữ trọn điểm để không làm sai lệch.

Báo cáo và chỉ số đánh giá
- Cho mỗi call: json gồm điểm KNGT/KNBH/NTT, tổng điểm, Đạt/Không đạt, mức lỗi, trích đoạn.
- Chất lượng hệ thống: MAE điểm so với chuyên gia (nếu có label), F1 cho M2/M3 (ưu tiên lỗi nặng).

Sản phẩm bàn giao Pha 1
- docs/QA_RULES.yaml: cấu hình baseline và ngưỡng.
- docs/transcript.schema.json, docs/crm.schema.json: schema vào/ra.
- docs/compute_baseline.py: tính baseline_rate và baseline_std từ transcripts.
- docs/qa_score.py: chấm điểm 0–10 (KNGT nhanh/chậm + accent; NTT nếu có crm.jsonl).
- docs/examples_transcript.jsonl, docs/examples_crm.jsonl: ví dụ dữ liệu đầu vào.

Cách chạy (sau khi cài requirements)
- Tính baseline:
  python3 docs/compute_baseline.py --transcripts path/to/transcripts.jsonl --out docs/baselines.json
- Chấm điểm:
  python3 docs/qa_score.py --transcripts path/to/transcripts.jsonl --rules docs/QA_RULES.yaml --call-type BH --crm path/to/crm.jsonl --out scores.jsonl

Tiêu chí nghiệm thu Pha 1
- Pipeline chạy hết trên tập mẫu, xuất điểm hợp lệ (0–10) và trạng thái Đạt/Không đạt.
- Có baseline tính được; rule engine áp dụng đúng công thức trừ điểm.
- Tài liệu kèm theo mô tả rõ cách thêm/điều chỉnh ngưỡng.

Kế hoạch Pha 2 (nháp)
- Mở rộng chấm KNBH (xác nhận, dẫn dắt, khai thác nhu cầu, xử lý rào cản, kết thúc) bằng rule + mẫu ngôn ngữ.
- So khớp với label chuyên gia; tinh chỉnh ngưỡng và trọng số.
