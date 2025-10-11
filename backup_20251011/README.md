# Phân Tích và Thiết Kế Hệ Thống

## Mô tả dự án
Dự án phân tích và thiết kế hệ thống theo nội dung được định nghĩa sẵn. Mục tiêu là tạo ra một hệ thống hoàn chỉnh từ giai đoạn phân tích yêu cầu đến thiết kế chi tiết.

## Cấu trúc dự án
```
phan-tich-thiet-ke-he-thong/
├── README.md                    # Tài liệu mô tả dự án
├── docs/                        # Tài liệu tổng hợp
├── tai-lieu-yeu-cau/           # Tài liệu yêu cầu và định nghĩa
├── thiet-ke/                   # Thiết kế hệ thống
├── mo-hinh-he-thong/          # Mô hình và sơ đồ
└── ket-qua-phan-tich/         # Kết quả phân tích
```

## Quy trình thực hiện (Chuẩn hoá theo CASE chuẩn)

CASE chuẩn (theo hình):
1) CRM Compliance: Quét rules/bộ lọc → Phát hiện vi phạm → Nhắc nhở → Báo cáo
2) Call Scoring & Coaching: STT + diarization → Phát hiện call_type (audio-only) → Trích xuất tín hiệu → Chấm điểm KNGT/KNBH/NTT theo chuẩn → Tóm tắt → Khuyến nghị → Kịch bản

### 1. Thu thập và phân tích yêu cầu
- Đặc tả 2 CASE chuẩn và KPI
- Định nghĩa các yêu cầu phi chức năng
- Phân tích stakeholder

### 2. Thiết kế kiến trúc hệ thống
- Thiết kế tổng thể xoay quanh 2 CASE
- Định nghĩa các component chính (Scoring, Call Type Detection, Compliance Scanner, Notification)
- Thiết kế mô hình dữ liệu

### 3. Thiết kế chi tiết
- Thiết kế API/Schema vào-ra cho 2 CASE
- Thiết kế luồng dữ liệu & báo cáo
- Quy tắc chấm điểm theo chuẩn

### 4. Mô hình hóa hệ thống
- Use Case (UC01 – Call Scoring, UC04 – CRM Compliance)
- DFD/Sequence/Activity cập nhật (call_type audio-only)
- ERD & Data Dictionary (có NTT/Reminders)

## Công cụ sử dụng
- Markdown cho tài liệu
- Diagrams as Code cho sơ đồ
- Git cho quản lý phiên bản

## Tác giả
Được tạo vào ngày: $(date +"%Y-%m-%d")

## Ghi chú
Dự án này được khởi tạo để thực hiện phân tích và thiết kế hệ thống một cách có hệ thống và khoa học.