# UC02 – View Reports

Mục tiêu: Cho phép Agent/QA/Manager xem điểm, chi tiết lỗi, bằng chứng (trích đoạn transcript/timecode), và gợi ý cải thiện.

Actors: Agent, QA Reviewer, Team Manager.

Tiền điều kiện:
- Có kết quả chấm điểm đã được lưu
- Người dùng có quyền truy cập phù hợp

Dòng chính:
1) Người dùng mở trang/báo cáo
2) Chọn phạm vi (theo thời gian, agent, team)
3) Xem tổng điểm, điểm theo nhóm, xếp loại, Đạt/Không đạt
4) Mở chi tiết tiêu chí: mức lỗi, điểm trừ, evidence
5) Xem đề xuất cải thiện và kịch bản mẫu

Ngoại lệ:
- A1: Không có dữ liệu → hiển thị hướng dẫn lọc
- A2: Quyền hạn không đủ → ẩn dữ liệu nhạy cảm

Hậu điều kiện:
- Người dùng nắm được tình trạng chất lượng và hành động tiếp theo
