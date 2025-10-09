# Mô hình hệ thống – Hướng dẫn đọc tài liệu

Tài liệu này tập hợp các artefact của giai đoạn Phân tích hệ thống xuất phát từ đặc tả yêu cầu đã thống nhất.

- use-case/
  - UC_OVERVIEW.md: Tổng quan actors ↔ use case
  - UC01..UC08: Use case chi tiết
- activity/: Activity diagrams cho các luồng chính
- dfd/: DFD Context & Level-1
- erd/: ERD khái niệm & logic
- state/: Vòng đời xử lý chấm điểm
- data-dictionary/: Danh mục trường dữ liệu mức logic

Nguyên tắc cốt lõi được phản ánh trong các mô hình:
- Call type được xác định tự động từ CRM và nội dung 30s đầu
- Đánh giá tốc độ nói là đa yếu tố; **customer impact** được ưu tiên cao nhất
- NTT/CRM tuân thủ theo mức M1/M2/M3 (M3 = 0 điểm nhóm)

Đề xuất bước tiếp theo:
1) Review các use case và diagrams cùng stakeholders
2) Bổ sung/điều chỉnh tiêu chí nếu còn thiếu
3) Chuyển sang Thiết kế tổng thể (High-level Architecture) dựa trên các artefact này
