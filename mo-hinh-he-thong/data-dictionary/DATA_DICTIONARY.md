# Data Dictionary (Tóm tắt thực thể & trường)

Lưu ý: Đây là mô tả nghiệp vụ ở mức logic. Tên và kiểu dữ liệu cụ thể sẽ xác định trong thiết kế chi tiết.

## CALL
- call_id: Định danh cuộc gọi
- call_time: Thời điểm gọi
- duration: Thời lượng (giây)
- agent_id: Mã nhân viên
- customer_id: Mã khách hàng
- call_type: BH|CSKH (phát hiện tự động, kèm confidence trong log)
- quality_flags: Cờ chất lượng (thiếu CRM, audio kém, v.v.)

## CRM_RECORD
- record_id: Id bản ghi CRM liên quan
- call_id: Liên kết CALL
- customer_status: existing|new
- ticket_id: Id ticket (nếu có)
- opportunity_stage: giai đoạn cơ hội (nếu có)
- source/campaign: nguồn/campaign
- updated_at: thời gian cập nhật gần nhất

## TRANSCRIPT_SEGMENT
- id
- call_id
- speaker: AGENT|CUSTOMER
- start_ms, end_ms
- text

## DIARIZATION_SEGMENT
- id
- call_id
- speaker: AGENT|CUSTOMER
- start_ms, end_ms
- confidence

## FEATURE_SET
- id, call_id
- wpm_median: tốc độ nói (đã xử lý silence hợp lý)
- pause_ratio: tỉ lệ im lặng
- volume_stats: min/mean/max/std dBFS
- sentiment_stats: điểm sentiment tổng hợp
- interrupt_count: số lần cắt lời
- wer_gap: chênh sai số nhận dạng
- repeat_count: KH yêu cầu nhắc lại

## SCORE
- score_id, call_id
- total: tổng điểm 0–10
- label: Yếu/Trung bình/Khá/Tốt/Xuất sắc
- passed: Đạt (>=5) | Không đạt

## SCORE_GROUP
- id, score_id
- group_code: KNGT|KNBH|NTT
- group_points: điểm sau trừ

## VIOLATION
- id, group_id
- criterion_code: mã tiêu chí con
- level: M1|M2|M3
- deduction: điểm trừ (nếu M1)
- evidence_ref: tham chiếu đoạn trích/metrics

## CRITERION
- code, name
- group_code
- weight_bh, weight_cskh
- description

## RULE
- rule_id, criterion_code
- params_json: tham số ngưỡng/trọng số
- active, updated_by, updated_at

## BASELINE
- id
- metric_code (ví dụ: speech_rate_wpm)
- value, std
- cohort (đội/chi nhánh)
- effective_at

## USER & ROLE_ASSIGNMENT
- user_id, name, role
- assignment: scope theo team/đơn vị

## FEEDBACK
- id, score_id, user_id
- reason, status (open/resolved/rejected)
- created_at, resolved_at
