# UC01 – Score Call

Mục tiêu: Tự động chấm điểm một cuộc gọi, tính điểm theo KNGT/KNBH/NTT, xác định Đạt/Không đạt và sinh báo cáo chi tiết.

Actors: PBX (nguồn audio), CRM System (metadata), Hệ thống QA (primary), QA Reviewer (tham chiếu), Agent (thụ hưởng kết quả).

Tiền điều kiện:
- Call audio và metadata khả dụng
- Có quyền truy cập CRM liên quan

Dòng chính (Main Flow):
1) Nhận audio + metadata từ PBX
2) Nhận dữ liệu CRM liên quan call
3) Xác định call type (BH/CSKH) dựa trên CRM/nội dung
4) Xử lý âm thanh (VAD, diarization) và chuyển lời nói → văn bản
5) Trích xuất tín hiệu cho từng tiêu chí theo rule
6) Đánh giá mức lỗi M1/M2/M3 per nhóm
7) Tính điểm nhóm và tổng; xác định xếp loại và Đạt/Không đạt
8) Lưu kết quả, sinh báo cáo chi tiết (evidence + recommendations)

Luồng thay thế/ngoại lệ:
- A1: Thiếu CRM → tiếp tục chấm điểm nhưng gắn cờ “thiếu dữ liệu”; call type fallback bằng nội dung
- A2: Audio lỗi kém → gắn cờ “chất lượng thấp”; giới hạn trách nhiệm
- A3: Không thể phân định call type → mặc định theo trạng thái KH (existing/new)

Hậu điều kiện:
- Kết quả chấm điểm được lưu, có thể tra cứu
- Báo cáo chi tiết sẵn sàng cho QA/Agent/Manager

Quy tắc nghiệp vụ liên quan:
- Ưu tiên Customer Impact trong đánh giá tốc độ nói
- NTT: M1 trừ 20%, M2 trừ 50%, M3 = 0
