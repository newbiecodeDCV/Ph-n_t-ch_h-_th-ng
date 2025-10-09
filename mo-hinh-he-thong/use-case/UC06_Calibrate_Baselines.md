# UC06 – Calibrate Baselines

Mục tiêu: Hiệu chỉnh baseline/ngưỡng dựa trên dữ liệu đạt chuẩn và phản hồi chuyên gia.

Actors: QA Reviewer/Analyst.

Tiền điều kiện:
- Có tập dữ liệu chuẩn (đạt ≥ 7.0)

Dòng chính:
1) Chọn tập mẫu hiệu chỉnh
2) So sánh điểm tự động với điểm chuyên gia
3) Đề xuất ngưỡng/baseline mới
4) Trình duyệt phê duyệt
5) Áp dụng và theo dõi drift

Ngoại lệ:
- A1: Không đủ mẫu → hoãn hiệu chỉnh

Hậu điều kiện:
- Baseline cập nhật, cải thiện MAE/F1