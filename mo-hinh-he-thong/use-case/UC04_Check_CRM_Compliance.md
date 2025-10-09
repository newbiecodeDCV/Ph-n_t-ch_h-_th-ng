# UC04 – Check CRM Compliance

Mục tiêu: Kiểm tra tuân thủ nhập liệu CRM/ticket theo quy định và SLA.

Actors: CRM System, Hệ thống QA.

Tiền điều kiện:
- Có liên kết Call ↔ CRM record

Dòng chính:
1) Đối soát các trường bắt buộc và chất lượng ghi chú
2) Kiểm tra tạo ticket (khi cần) và SLA cập nhật
3) Phát hiện vi phạm và phân loại M1/M2/M3 theo quy tắc
4) Gắn kết quả vào báo cáo cuộc gọi

Ngoại lệ:
- A1: Không tìm thấy CRM record → flag “thiếu dữ liệu”

Hậu điều kiện:
- Có danh sách vi phạm NTT để trừ điểm và thống kê tuân thủ