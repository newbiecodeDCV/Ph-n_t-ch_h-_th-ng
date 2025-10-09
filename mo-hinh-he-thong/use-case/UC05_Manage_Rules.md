# UC05 – Manage Rules

Mục tiêu: Quản lý tập luật chấm điểm (tiêu chí, ngưỡng, trọng số) và lịch sử thay đổi.

Actors: Admin, QA Reviewer.

Tiền điều kiện:
- Người dùng có quyền quản trị

Dòng chính:
1) Xem cấu hình hiện tại (tiêu chí, ngưỡng, trọng số)
2) Tạo/sửa/xóa rule; ghi nhận lý do thay đổi
3) Áp dụng thay đổi theo môi trường (dev/staging/prod)
4) Lưu lịch sử thay đổi (audit trail) và thông báo

Ngoại lệ:
- A1: Thay đổi làm tăng rủi ro → yêu cầu phê duyệt 2 lớp

Hậu điều kiện:
- Rule mới có hiệu lực, có thể rollback nếu cần