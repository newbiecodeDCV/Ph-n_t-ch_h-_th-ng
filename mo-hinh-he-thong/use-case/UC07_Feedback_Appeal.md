# UC07 – Feedback/Appeal

Mục tiêu: Cho phép Agent gửi khiếu nại/giải trình, QA xử lý và cập nhật kết quả.

Actors: Agent, QA Reviewer.

Tiền điều kiện:
- Có báo cáo chấm điểm ban đầu

Dòng chính:
1) Agent gửi feedback (chọn mục, nêu lý do, đính kèm bằng chứng)
2) QA xem xét, có thể chấp thuận, bác bỏ hoặc yêu cầu thêm thông tin
3) Nếu chấp thuận → điều chỉnh điểm/ghi chú; nếu bác bỏ → nêu lý do
4) Ghi lịch sử xử lý và thông báo kết quả

Ngoại lệ:
- A1: Feedback trùng/không hợp lệ → từ chối

Hậu điều kiện:
- Ticket feedback đóng; kết quả có thể thay đổi nếu hợp lý