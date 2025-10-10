# DFD – Context Level (Level 0)

```mermaid
graph LR
  Customer((Khách hàng)) -- Gọi điện --> PBX[PBX/Telephony]
  PBX -- Audio + Metadata --> QA[Hệ thống QA]
  CRM[Hệ thống CRM] -- Dữ liệu KH/Ticket --> QA
  QA -- Báo cáo/Điểm --> Agent[Agent]
  QA -- Dashboard --> Manager[Manager]
  QA -- Review/Calibration --> QAReviewer[QA Reviewer]
  QA -- Nhắc nhở CRM --> Notification[Email/Chat/SMS]
```

# DFD – Call Scoring (Level 1)

```mermaid
graph LR
  A[Audio + Metadata] --> B[ASR + Diarization]
  B --> C[Call Type Detection (audio-only)]
  B --> D[Extraction Tín hiệu]
  C --> E[Tính điểm theo nhóm (KNGT/KNBH/NTT)]
  D --> E
  E --> F[Tóm tắt + Khuyến nghị + Kịch bản]
  F --> G[Báo cáo + Lưu trữ]
```

# DFD – CRM Compliance (Level 1)

```mermaid
graph LR
  CRM[CRM] --> A[Lấy records theo Call/Time]
  A --> B[Áp Rules/Filters]
  B --> C[Phát hiện vi phạm]
  C --> D[Phân loại M1/M2/M3]
  D --> E[Tạo nhắc nhở + Escalate]
  E --> F[Theo dõi khắc phục]
  F --> G[Báo cáo tổng hợp]
```
