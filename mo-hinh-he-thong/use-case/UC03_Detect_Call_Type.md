# UC03 – Detect Call Type

Mục tiêu: Xác định loại cuộc gọi (BH/CSKH) để áp đúng trọng số và tiêu chí.

Actors: CRM System (nguồn dữ liệu), Hệ thống QA.

Tiền điều kiện:
- Có dữ liệu CRM liên kết call hoặc transcript có 30s đầu

Dòng chính:
1) Đọc trường CRM ưu tiên (ticket/case/opportunity/campaign)
2) Nếu chưa rõ, phân tích nội dung 30s đầu
3) Nếu vẫn chưa rõ, áp fallback dựa vào tình trạng KH (existing/new)
4) Ghi lại lý do và mức độ tự tin (confidence) cho audit

Ngoại lệ:
- A1: CRM không khả dụng → bỏ qua bước 1 và 3

Hậu điều kiện:
- Gán call_type cho cuộc gọi với confidence phục vụ giám sát
