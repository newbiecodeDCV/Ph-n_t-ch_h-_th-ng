# UC01 – Đánh giá chấm điểm cuộc gọi

Mục tiêu: AI chấm điểm và đánh giá một cuộc gọi giữa Agent và Khách hàng theo CHUẨN “Tiêu chí chấm” (Job AI cho chấm điểm QA cuộc gọi Cloud). Bao gồm: tóm tắt 3–5 câu; chấm theo checklist KNGT/KNBH/NTT đúng trọng số; đưa khuyến nghị theo ngữ cảnh và gợi ý kịch bản mẫu.

Actors: PBX (nguồn audio), STT Service, Hệ thống QA (primary), QA Reviewer, Agent, Manager.

Tiền điều kiện:
- Call audio + metadata cơ bản (call_id, agent_id, call_time) khả dụng
- Call_type KHÔNG cung cấp sẵn; hệ thống phát hiện từ audio/transcript (audio-only)
- CRM dùng để chấm nhóm NTT (Nhập thông tin CRM/ticket) theo đúng chuẩn; không thêm bớt nội dung ngoài chuẩn

Dòng chính (Main Flow):
1) Nhận audio + metadata từ CRM
2) Thực hiện STT + diarization để có transcript theo vai AGENT/CUSTOMER
3) Phát hiện loại cuộc gọi từ audio/transcript → trả về call_type_pred (BH/CSKH) + confidence ∈ [0,1]
4) Trích xuất tín hiệu cho chấm điểm: wpm, pause_ratio, interrupt_count, sentiment trend, customer_repeat_count, keyword cues…
5) Chấm theo checklist (đúng danh mục và trọng số chuẩn):
   - KNGT (Kỹ năng giao tiếp)
     • Chào/xưng danh
     • Kỹ năng nói (tốc độ & âm lượng)
     • Kỹ năng nghe, trấn an
     • Thái độ giao tiếp & sử dụng ngôn ngữ
   - KNBH (Kỹ năng bán hàng) – áp cho cả BH và CSKH nhưng tỷ trọng con khác nhau theo chuẩn
     • Xác nhận thông tin
     • Kỹ năng tiếp cận/dẫn dắt
     • Khai thác thực trạng & nhu cầu
     • Nắm bắt vấn đề
     • Tư vấn & Hỗ trợ sản phẩm
     • Đề xuất giải pháp, Xử lý rào cản, Thuyết phục
     • Kết thúc (CTA/Follow-up)
   - NTT (Nhập hệ thống CRM, ticket)
     • Ghi chú CRM nội dung trao đổi; điền thông tin theo quy định; tạo ticket (khi cần)
   - Áp quy tắc context-aware (không phạt khi ngữ cảnh hợp lý: đọc OTP/điều khoản, KH yêu cầu pace, đang tra cứu…)
   - Nếu confidence thấp (< τ, ví dụ 0.75) → dùng mixture-of-weights cho nhóm điểm để giảm sai số
6) Tổng hợp điểm nhóm → điểm tổng 0–10, gắn nhãn xếp loại (Yếu/Trung bình/Khá/Tốt/Xuất sắc), xác định passed (≥5)
7) Sinh Executive Summary (3–5 câu) + highlights
8) Sinh Recommendations theo ngữ cảnh và Suggested Scripts dựa trên violations
9) Lưu kết quả, evidence (trích đoạn + timestamps) và phát hành báo cáo cho UI

Luồng thay thế/ngoại lệ:
- A1: Audio chất lượng thấp → gắn cờ, giảm trọng số dựa trên transcript; vẫn sinh báo cáo với cảnh báo
- A2: STT thất bại một phần → cố gắng tái chạy/đổi model; nếu vẫn lỗi, sinh báo cáo rút gọn (no-penalty cho mục phụ thuộc transcript)
- A3: Phân loại call_type confidence rất thấp → áp trọng số neutral 50/50 và yêu cầu xác nhận thủ công từ QA

Hậu điều kiện:
- Kết quả chấm điểm, tóm tắt, recommendations và scripts được lưu và hiển thị
- Evidence theo tiêu chí (trích đoạn + metric) sẵn sàng cho QA/Agent/Manager

Quy tắc nghiệp vụ liên quan (theo chuẩn, không thêm bớt):
- Phân bổ điểm theo loại cuộc gọi (tổng 10 điểm):
  • BH: KNGT 20% (2.0) | KNBH 70% (7.0) | NTT 10% (1.0)
  • CSKH: KNGT 40% (4.0) | KNBH 50% (5.0) | NTT 10% (1.0)
- Trọng số con trong KNGT (tính trên điểm nhóm KNGT):
  • Chào/xưng danh: 10% → BH 0.2 | CSKH 0.4
  • Kỹ năng nói (tốc độ & âm lượng): 10% → BH 0.2 | CSKH 0.4
  • Kỹ năng nghe, Trấn an: 40% → BH 0.8 | CSKH 1.6
  • Thái độ giao tiếp & Ngôn ngữ: 40% → BH 0.8 | CSKH 1.6
- Trọng số con trong KNBH (tính trên điểm nhóm KNBH):
  • Xác nhận thông tin: 5% → BH 0.35 | CSKH 0.25
  • Tiếp cận/Dẫn dắt: 10% → BH 0.7 | CSKH 0.5
  • Khai thác thực trạng & nhu cầu: 20%/30% → BH 1.4 | CSKH 1.5
  • Nắm bắt vấn đề: 10% → BH 0.7 | CSKH 0.5
  • Tư vấn & Hỗ trợ sản phẩm: 30%/5% → BH 2.1 | CSKH 0.25
  • Đề xuất giải pháp, Xử lý rào cản, Thuyết phục: 20%/30% → BH 1.4 | CSKH 1.5
  • Kết thúc (CTA/Follow-up): 5%/10% → BH 0.35 | CSKH 0.5
- Nhập hệ thống CRM (NTT): 10% tổng điểm (BH 1.0 | CSKH 1.0) – ghi chú/điền thông tin/tạo ticket đúng quy định
- Quy tắc trừ điểm theo mức lỗi (áp cho từng nhóm theo chuẩn):
  • KNGT, KNBH: M1 → trừ theo tỷ trọng tiêu chí; M2 → trừ 50% điểm nhóm; M3 → điểm nhóm = 0
  • NTT: M1 → trừ 20%; M2 → trừ 50%; M3 → điểm nhóm = 0
- Xếp loại theo tổng điểm: Yếu [0–<5.0], Trung bình [5.0–<7.0], Khá [7.0–<8.0], Tốt [8.0–<9.0], Xuất sắc [9.0–10]
- Mixture-of-weights khi confidence call_type thấp: W_eff = p_BH·W_BH + (1−p_BH)·W_CSKH
- Bắt buộc evidence cho mọi vi phạm M2/M3 (timestamp + trích đoạn)
