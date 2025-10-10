# UC04 – Kiểm tra tuân thủ cập nhật CRM (Compliance)

Mục tiêu: AI tự động quét rules/bộ lọc, phát hiện lỗi nhập liệu & tuân thủ CRM của Sales/CSKH; tự động nhắc nhở sửa lỗi và tổng hợp báo cáo thống kê.

Actors: CRM System (data source), Hệ thống QA (primary), Agent (người nhận nhắc), Team Manager (nhận báo cáo), Notification Service (email/chat/SMS).

Tiền điều kiện:
- Có khả năng liên kết Call ↔ CRM record (qua call_id hoặc mapping khác)
- Có quyền đọc CRM theo phạm vi được cấu hình (team/time range)

Dòng chính (Main Flow):
1) Chạy quét theo lịch hoặc on-demand, áp dụng bộ lọc (thời gian, team, campaign, call_type nếu có)
2) Đọc CRM records liên quan từng cuộc gọi
3) Đánh giá tuân thủ theo rules active:
   - Trường bắt buộc (required_fields) theo BH/CSKH
   - Chất lượng ghi chú (notes_quality, min length, keywords…)
   - Tạo ticket/case theo điều kiện (required_if)
   - SLA cập nhật (update_within_minutes)
4) Phân loại vi phạm thành M1/M2/M3 theo ngưỡng
5) Tạo Reminder cho từng Agent với due_at theo mức độ (M3: 1h, M2: 2h, M1: 4h); sinh nội dung theo template
6) Gửi Notification qua kênh cấu hình (M3: gửi ngay + escalate Manager; M2: trong 15’;
   M1: batch mỗi giờ); lưu outbox và trạng thái gửi
7) Theo dõi khắc phục: đến due_at tự động re-check CRM; nếu đã sửa → đánh dấu resolved; chưa sửa → gửi lại/escalate
8) Tổng hợp báo cáo theo ngày/tuần: by_type, by_severity, by_agent/team, trends; gửi Manager

Luồng thay thế/ngoại lệ:
- A1: CRM không khả dụng → retry theo backoff; log và alert nếu vượt ngưỡng
- A2: Notification service down → lưu outbox pending; retry sau 15 phút; alert nếu backlog lớn
- A3: Agent nghỉ việc/không còn scope → bỏ qua gửi và escalate cho Manager

Hậu điều kiện:
- Violations, reminders, delivery log và trạng thái được lưu đầy đủ (audit/traceability)
- Báo cáo compliance cập nhật theo lịch và sẵn sàng cho Manager/QA

Input/Output (logic):
- Input: CRM_RECORD (customer, ticket/case, opportunity, notes, updated_at…), call metadata
- Output: Violations[{type, severity, evidence}], Reminders[{agent_id, message, due_at, status}], Reports (aggregates/trends)

Quy tắc nghiệp vụ liên quan:
- Rule sets cấu hình theo loại cuộc gọi và quy trình nội bộ
- M1: nhắc nhẹ/trừ tỉ lệ nhỏ; M2: ảnh hưởng đáng kể/50% nhóm; M3: nghiêm trọng/escalate
- KPI: detection rate, false positive rate (<5%), resolution rate (>85%), avg resolution time, escalation rate
