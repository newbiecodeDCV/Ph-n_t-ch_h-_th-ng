# UC09 – Auto Remind CRM Compliance

## Mục tiêu
Tự động quét rules, phát hiện lỗi cập nhật CRM của Sales/CSKH và gửi nhắc nhở để sửa lỗi, đồng thời tổng hợp báo cáo thống kê lỗi.

## Actors
- **Hệ thống QA** (primary): Thực hiện quét và phát hiện lỗi
- **CRM System** (external): Nguồn dữ liệu cần kiểm tra
- **Agent** (Sales/CSKH): Nhận nhắc nhở và thực hiện sửa lỗi
- **Team Manager**: Nhận báo cáo tổng hợp
- **Notification Service**: Gửi nhắc nhở qua email/chat/SMS

## Tiền điều kiện
- Có quyền truy cập đọc CRM records
- Rules CRM compliance đã được định nghĩa trong QA_RULES.yaml
- Notification service khả dụng
- Agent profiles có thông tin liên lạc

## Dòng chính (Main Flow)

### 1. Quét định kỳ (Scheduled Scan)
1. Hệ thống chạy theo lịch (mỗi 30 phút hoặc real-time sau mỗi cuộc gọi)
2. Lấy danh sách CRM records cần kiểm tra (calls trong khung thời gian)
3. Load rules từ QA_RULES.yaml (phần CRM_COMPLIANCE)

### 2. Phát hiện vi phạm (Detection)
4. Với mỗi CRM record:
   - Kiểm tra trường bắt buộc (required_fields)
   - Đánh giá chất lượng ghi chú (notes_quality)
   - Kiểm tra ticket/case creation (nếu bắt buộc)
   - Kiểm tra thời gian cập nhật (SLA compliance)
5. Phân loại mức độ vi phạm (M1/M2/M3) theo rules
6. Ghi violations vào database với evidence

### 3. Tạo nhắc nhở (Reminder Generation)
7. Với mỗi violation:
   - Tạo reminder record với due_date (M1: 4h, M2: 2h, M3: 1h)
   - Phân nhóm theo agent_id
   - Sinh nội dung nhắc nhở theo template (violation_code → message)

### 4. Gửi thông báo (Notification Dispatch)
8. Gửi notification qua kênh ưu tiên (email/chat/SMS):
   - M3: Gửi ngay + escalate tới Manager
   - M2: Gửi trong 15 phút
   - M1: Gửi trong 1 giờ (batch)
9. Đánh dấu reminder.status = 'sent'
10. Lưu vào notification_outbox để track delivery

### 5. Theo dõi (Tracking & Follow-up)
11. Scan lại CRM sau due_date để check đã fix chưa
12. Nếu đã fix: reminder.status = 'resolved', ghi resolved_at
13. Nếu chưa fix: gửi reminder thứ 2, escalate nếu quá 2 lần
14. Cập nhật metrics: resolution_rate, avg_resolution_time

### 6. Tổng hợp báo cáo (Reporting)
15. Aggregate hàng ngày/tuần:
    - Tổng số vi phạm theo type/severity/agent/team
    - Tỷ lệ giải quyết kịp thời
    - Top violations
    - Trend so với tuần trước
16. Gửi dashboard/email tới Manager

## Luồng thay thế/ngoại lệ

### A1: CRM không khả dụng
- Retry với exponential backoff (3 lần)
- Nếu fail: Ghi log, skip batch này, alert ops team
- Không block các cuộc gọi khác

### A2: Notification service down
- Lưu vào outbox với status='pending'
- Retry service gửi batch sau 15 phút
- Alert ops nếu outbox vượt 500 messages

### A3: Agent không còn làm việc
- Skip gửi notification
- Escalate trực tiếp tới Manager với context

### A4: False positive (Agent appeal)
- Agent submit feedback qua UC07
- QA Reviewer xem xét và whitelist nếu hợp lý
- Update rules/thresholds để tránh lặp lại

## Hậu điều kiện

### Success
- Violations được phát hiện và lưu trữ đầy đủ với evidence
- Reminders được gửi đúng SLA và kênh ưu tiên
- Tracking status cập nhật real-time
- Báo cáo tổng hợp sẵn sàng cho Manager

### Failure
- Ghi log chi tiết lỗi và context
- Alert ops team nếu là system failure
- Không làm mất dữ liệu (at-least-once delivery cho notifications)

## Quy tắc nghiệp vụ liên quan

### CRM_COMPLIANCE Rules (từ QA_RULES.yaml)
```yaml
CRM_COMPLIANCE:
  required_fields:
    BH:
      - customer_name
      - phone
      - opportunity_stage
      - product_interest
      - next_action
    CSKH:
      - customer_name
      - ticket_id
      - issue_category
      - resolution_status
  
  notes_quality:
    min_length: 50  # characters
    must_contain: ["khách hàng", "nhu cầu"]  # for BH
    
  ticket_creation:
    CSKH:
      required_if: ["issue_category in ['complaint', 'bug']"]
    BH:
      required_if: ["opportunity_stage == 'qualified'"]
      
  sla:
    update_within_minutes:
      M1: 120  # warning nếu > 2h
      M2: 60   # error nếu > 1h
      M3: 30   # critical nếu > 30 phút (cho CSKH urgent)
```

### Reminder SLA
- M3: due trong 1 giờ, gửi ngay + escalate
- M2: due trong 2 giờ, gửi trong 15 phút
- M1: due trong 4 giờ, gửi batch 1 giờ 1 lần

### Escalation Policy
- M3 + chưa fix sau 1h → Manager + Director
- M2 + chưa fix sau 2h → Manager
- M1 + chưa fix sau 4h → Warning, đưa vào review tuần

## Metrics & KPIs
- **Detection Rate**: % calls được scan trong SLA
- **False Positive Rate**: Target < 5%
- **Resolution Rate**: % violations được fix trong due_date (target > 85%)
- **Avg Resolution Time**: Thời gian trung bình từ detect → fix
- **Escalation Rate**: % cases cần escalate (target < 10%)
- **Notification Delivery Rate**: % notifications được deliver thành công (target > 99%)

## Tích hợp với UC khác
- **UC01 (Score Call)**: Sau khi chấm điểm, trigger UC09 để check CRM
- **UC02 (View Reports)**: Agent/Manager xem violations và resolution status
- **UC07 (Feedback/Appeal)**: Agent có thể appeal nếu là false positive
- **UC08 (Manage Users)**: Admin quản lý notification preferences

## Dữ liệu liên quan
- **Input**: CRM_RECORD, CALL, RULE (CRM_COMPLIANCE section)
- **Output**: VIOLATION, REMINDER, NOTIFICATION_OUTBOX, REPORT_AGG_DAILY
- **Intermediate**: SCAN_LOG, RETRY_QUEUE

## Cấu hình triển khai
```yaml
scanner:
  schedule: "*/30 * * * *"  # Every 30 minutes
  batch_size: 100
  lookback_hours: 24
  
notification:
  channels:
    - email  # primary
    - slack  # secondary
    - sms    # M3 only
  retry:
    max_attempts: 3
    backoff: exponential
    
reporting:
  schedule: "0 8 * * *"  # Daily at 8 AM
  recipients:
    - team_managers
    - qa_lead
```

## Ví dụ Violation Record
```json
{
  "violation_id": "V-2025-001234",
  "call_id": "CALL-20250109-0001",
  "agent_id": "A-001",
  "detected_at": "2025-01-09T10:30:00Z",
  "violation_type": "missing_ticket",
  "severity": "M2",
  "evidence": {
    "call_type": "CSKH",
    "issue_category": "complaint",
    "ticket_id": null,
    "rule": "ticket_creation.CSKH.required_if"
  },
  "reminder_due": "2025-01-09T12:30:00Z",
  "status": "open",
  "resolution": null
}
```

## Ví dụ Reminder Message
```
🔔 **Nhắc nhở CRM Compliance - Mức độ: Trung bình (M2)**

Call ID: CALL-20250109-0001  
Khách hàng: Nguyễn Văn A  
Thời gian: 09/01/2025 10:15

**Vấn đề**: Chưa tạo ticket cho khiếu nại của khách hàng

**Yêu cầu**: 
- Tạo ticket trong CRM với category "complaint"
- Ghi rõ nội dung khiếu nại và bước đã xử lý
- Deadline: 12:30 hôm nay (còn 2 giờ)

**Hướng dẫn**: [Link CRM] | [Link Quy trình xử lý complaint]

Nếu đã xử lý, vui lòng bỏ qua email này.
Nếu cần hỗ trợ, liên hệ QA team.
```
