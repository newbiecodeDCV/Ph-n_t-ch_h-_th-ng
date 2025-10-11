# ĐẶC TẢ HỆ THỐNG AI QA CALL SCORING - VERSION CLEAN

**Version:** 3.0  
**Ngày:** 11/10/2025  
**Mục đích:** Đặc tả đầy đủ, loại bỏ code thừa, tập trung vào thiết kế

---

## 📋 MỤC LỤC

1. [Tổng quan hệ thống](#1-tổng-quan-hệ-thống)
2. [Yêu cầu nghiệp vụ](#2-yêu-cầu-nghiệp-vụ)
3. [Phân tích Use Cases](#3-phân-tích-use-cases)
4. [Kiến trúc hệ thống](#4-kiến-trúc-hệ-thống)
5. [Thiết kế chi tiết](#5-thiết-kế-chi-tiết)
6. [Luồng xử lý](#6-luồng-xử-lý)
7. [Cơ sở dữ liệu](#7-cơ-sở-dữ-liệu)
8. [API Interface](#8-api-interface)
9. [Non-functional Requirements](#9-non-functional-requirements)
10. [Deployment Strategy](#10-deployment-strategy)

---

## 1. TỔNG QUAN HỆ THỐNG

### 1.1. Mục tiêu
Xây dựng hệ thống AI tự động đánh giá chất lượng cuộc gọi của Sales/CSKH với 2 chức năng chính:
- **Kiểm tra tuân thủ CRM** (CASE 1)
- **Chấm điểm chất lượng cuộc gọi** (CASE 2)

### 1.2. Phạm vi
- **Đối tượng:** Agent Sales và CSKH
- **Dữ liệu đầu vào:** Audio cuộc gọi, CRM records
- **Output:** Điểm số, vi phạm, recommendations

### 1.3. Stakeholders
- **End Users:** Sales/CSKH Agents
- **Managers:** Team Leaders, QA Managers
- **System:** IT Admin, Data Analyst

---

## 2. YÊU CẦU NGHIỆP VỤ

### 2.1. CASE 1: Kiểm tra tuân thủ CRM

#### 2.1.1. Mục tiêu
- Tự động phát hiện vi phạm cập nhật CRM
- Nhắc nhở agent sửa lỗi
- Tổng hợp báo cáo tuân thủ

#### 2.1.2. Chức năng chính
| ID | Chức năng | Mô tả |
|----|-----------|-------|
| CR1.1 | Quét rules tự động | Kiểm tra CRM sau mỗi cuộc gọi |
| CR1.2 | Phát hiện vi phạm | Phân loại M1/M2/M3 |
| CR1.3 | Nhắc nhở tự động | Email/SMS/In-app notification |
| CR1.4 | Báo cáo thống kê | Daily/Weekly/Monthly reports |
| CR1.5 | Export dữ liệu | Excel/CSV với filters |

#### 2.1.3. Rules kiểm tra
- **Thời gian cập nhật:** Trong vòng 24h sau cuộc gọi
- **Trường bắt buộc:** Contact outcome, Next action, Notes
- **Chất lượng notes:** Tối thiểu 50 ký tự
- **Phân loại vi phạm:**
  - M1: Vi phạm nhẹ (delay 24-48h)
  - M2: Vi phạm trung bình (delay 48-72h)
  - M3: Vi phạm nặng (>72h hoặc missing fields)

### 2.2. CASE 2: Chấm điểm cuộc gọi

#### 2.2.1. Mục tiêu
- Tự động chấm điểm cuộc gọi (0-10)
- Đánh giá theo checklist chuẩn
- Đưa ra recommendations cải thiện

#### 2.2.2. Tiêu chí đánh giá

**A. KNGT - Kỹ năng giao tiếp (40% BH, 70% CSKH)**
| Mã | Tiêu chí | Trọng số BH | Trọng số CSKH |
|----|----------|-------------|---------------|
| GRT | Chào hỏi & xưng danh | 5% | 8% |
| SR | Tốc độ nói | 8% | 10% |
| VOL | Âm lượng | 4% | 6% |
| LSN | Lắng nghe | 6% | 8% |
| EMP | Đồng cảm | 5% | 8% |
| LAN | Ngôn ngữ | 5% | 5% |
| CLS | Kết thúc | 7% | 7% |

**B. KNBH - Kỹ năng bán hàng (60% BH, 30% CSKH)**
| Mã | Tiêu chí | Trọng số |
|----|----------|----------|
| CIN | Xác nhận thông tin | 5% |
| LEAD | Dẫn dắt cuộc gọi | 8% |
| NEED | Khai thác nhu cầu | 10% |
| ADV | Tư vấn sản phẩm | 10% |
| OBJ | Xử lý từ chối | 7% |
| CLS2 | Chốt sale | 8% |

#### 2.2.3. Output mong đợi
- **Điểm số:** 0-10 với breakdown theo nhóm
- **Summary:** Tóm tắt 3-5 câu
- **Recommendations:** Gợi ý cải thiện cụ thể
- **Scripts:** Kịch bản mẫu tham khảo
- **Evidence:** Timestamps và quotes

---

## 3. PHÂN TÍCH USE CASES

### 3.1. UC01: Kiểm tra tuân thủ CRM

```
Actor: System (Tự động)
Trigger: Sau mỗi cuộc gọi kết thúc
Flow:
1. System nhận notification cuộc gọi kết thúc
2. Đợi 24h → Check CRM updates
3. Nếu chưa update → Send reminder level 1
4. Đợi thêm 24h → Check lại
5. Nếu vẫn chưa → Escalate to supervisor
6. Log violation vào database
7. Update compliance report
```

### 3.2. UC02: Chấm điểm cuộc gọi

```
Actor: QA System
Trigger: Audio file available
Flow:
1. Receive audio + metadata
2. Speech-to-Text với diarization
3. Detect call type (BH/CSKH) từ transcript
4. Extract features (WPM, pauses, sentiment...)
5. Evaluate KNGT criteria
6. Evaluate KNBH/KNSV criteria
7. Calculate total score với weights
8. Generate summary & recommendations
9. Map suggested scripts
10. Create evidence với timestamps
11. Save results to database
12. Notify completion
```

---

## 4. KIẾN TRÚC HỆ THỐNG

### 4.1. Architecture Overview

```
┌─────────────────────────────────────────────────┐
│                 CLIENT LAYER                     │
│   Web Portal | Mobile App | Admin Dashboard      │
└─────────────────┬───────────────────────────────┘
                  │
┌─────────────────▼───────────────────────────────┐
│              API GATEWAY                         │
│         (Authentication, Routing)                │
└─────────────────┬───────────────────────────────┘
                  │
┌─────────────────▼───────────────────────────────┐
│           APPLICATION SERVICES                   │
├─────────────────────────┬───────────────────────┤
│    CASE 1: CRM          │   CASE 2: SCORING     │
│  ┌──────────────┐       │  ┌──────────────┐    │
│  │Rules Engine  │       │  │STT Service   │    │
│  │Reminder Svc  │       │  │Call Detector │    │
│  │Report Gen    │       │  │Score Engine  │    │
│  └──────────────┘       │  │Summary Gen   │    │
│                         │  └──────────────┘    │
└─────────────────────────┴───────────────────────┘
                  │
┌─────────────────▼───────────────────────────────┐
│              DATA LAYER                          │
│  PostgreSQL | Redis Cache | S3 Storage           │
│  Elasticsearch | Message Queue                   │
└──────────────────────────────────────────────────┘
```

### 4.2. Technology Stack

| Layer | Technology | Lý do chọn |
|-------|------------|------------|
| API Gateway | Kong/Nginx | Load balancing, rate limiting |
| Application | Python/FastAPI | Performance, async support |
| Queue | RabbitMQ/Celery | Reliable async processing |
| Database | PostgreSQL | ACID, JSON support |
| Cache | Redis | Fast key-value store |
| Storage | S3/MinIO | Scalable object storage |
| Search | Elasticsearch | Full-text search, analytics |
| Monitoring | Prometheus + Grafana | Industry standard |

---

## 5. THIẾT KẾ CHI TIẾT

### 5.1. Module CRM Compliance (CASE 1)

#### Components:
1. **Rules Engine**
   - Config rules theo team/department
   - Real-time validation
   - Batch processing historical data

2. **Reminder Service**
   - Multi-channel: Email, SMS, In-app
   - Escalation matrix
   - Tracking acknowledgments

3. **Report Generator**
   - Scheduled reports
   - On-demand exports
   - Trend analysis

### 5.2. Module Call Scoring (CASE 2)

#### Components:
1. **Speech Processing**
   - STT với speaker diarization
   - Language: Vietnamese + English
   - Accuracy target: >90%

2. **Call Type Detection**
   - Phân loại BH/CSKH từ audio
   - Confidence threshold: 0.75
   - Fallback: mixture-of-weights

3. **Scoring Engine**
   - 14 criteria evaluation
   - Dynamic weight application
   - Context-aware rules

4. **Report Generation**
   - Executive summary
   - Actionable recommendations
   - Evidence with timestamps

### 5.3. Speech Rate Evaluation Module

#### Đặc tả chi tiết:
1. **Segmentation**
   - Chia theo speaker changes
   - Split long segments (>15s) by pauses (≥700ms)
   - Merge short segments (<2s)
   - Target: 5-15s per segment

2. **WPM Calculation**
   - Count words in Vietnamese
   - Remove silence periods (>200ms)
   - Formula: WPM = (word_count / voiced_duration) × 60

3. **Thresholds (không có baseline)**
   - BH: [100-130-180-220] wpm
   - CSKH: [90-120-170-210] wpm
   - Vi phạm: M1 (25% outliers), M2 (10% extreme), M3 (20% extreme)

4. **Customer Impact Priority**
   - Detect "nói lại", "nhắc lại", "không nghe rõ"
   - Override metrics if customer complains ≥3 times

---

## 6. LUỒNG XỬ LÝ

### 6.1. Main Processing Pipeline

```
[Audio Input]
     ↓
[STT + Diarization] ← 8-10s/minute audio
     ↓
[Call Type Detection] ← Analyze first 60s
     ↓
[Feature Extraction] ← WPM, pauses, interrupts
     ↓
[Parallel Evaluation]
    ├── [KNGT Evaluation]
    └── [KNBH Evaluation]
     ↓
[Score Calculation] ← Apply dynamic weights
     ↓
[Report Generation]
    ├── Summary (3-5 sentences)
    ├── Recommendations
    ├── Suggested Scripts
    └── Evidence
     ↓
[Save & Notify]
```

### 6.2. Processing Time Budget

| Step | Target Time | Note |
|------|-------------|------|
| STT | ~90s for 5min audio | Parallel processing |
| Feature extraction | <2s | Cached computations |
| Evaluation | <1s | Rule-based, fast |
| Report generation | <2s | Template-based |
| **Total** | **<5s** (excluding STT) | Meet KPI |

---

## 7. CƠ SỞ DỮ LIỆU

### 7.1. Main Tables

**calls**
- call_id (PK)
- agent_id
- call_time
- duration
- audio_url
- call_type_detected
- status

**call_scores**
- score_id (PK)
- call_id (FK)
- total_score (0-10)
- kngt_score
- knbh_score
- violation_level
- summary_text
- created_at

**crm_compliance**
- compliance_id (PK)
- call_id (FK)
- update_delay_hours
- missing_fields[]
- violation_level
- reminder_sent_at
- resolved_at

**evaluation_details**
- detail_id (PK)
- score_id (FK)
- criterion_code
- weight
- earned_points
- max_points
- evidence_json

### 7.2. Indexes & Performance
- Index on agent_id, call_time for quick filtering
- Partition by month for historical data
- Cache hot data in Redis

---

## 8. API INTERFACE

### 8.1. Core Endpoints

| Method | Endpoint | Purpose |
|--------|----------|---------|
| POST | /api/v1/calls/score | Submit call for scoring |
| GET | /api/v1/calls/{id}/score | Get scoring results |
| GET | /api/v1/compliance/check | Check CRM compliance |
| POST | /api/v1/compliance/remind | Send reminder |
| GET | /api/v1/reports/agent/{id} | Agent performance |
| GET | /api/v1/reports/team/{id} | Team dashboard |

### 8.2. Response Format

```json
{
  "status": "success|error",
  "data": {
    // Actual response data
  },
  "meta": {
    "timestamp": "2025-10-11T04:30:00Z",
    "version": "1.0"
  }
}
```

---

## 9. NON-FUNCTIONAL REQUIREMENTS

### 9.1. Performance
- Response time: <5s per call (excluding STT)
- Throughput: 100 concurrent calls
- STT accuracy: >90% for Vietnamese

### 9.2. Reliability
- Availability: 99.9% uptime
- Data durability: 99.999999999%
- Backup: Daily full, hourly incremental

### 9.3. Security
- Authentication: JWT tokens
- Authorization: Role-based (RBAC)
- Encryption: TLS 1.3 in transit, AES-256 at rest
- Audit: All actions logged

### 9.4. Scalability
- Horizontal scaling for workers
- Auto-scaling based on queue depth
- Database read replicas

### 9.5. Monitoring
- Real-time metrics dashboard
- Alert thresholds configured
- Business KPIs tracked

---

## 10. DEPLOYMENT STRATEGY

### 10.1. Environment Setup

| Environment | Purpose | Configuration |
|------------|---------|---------------|
| Development | Local testing | Docker Compose |
| Staging | UAT testing | Kubernetes (small) |
| Production | Live system | Kubernetes (HA) |

### 10.2. Deployment Phases

**Phase 1: MVP (Week 1-2)**
- Core scoring for KNGT
- Basic API
- Manual CRM check

**Phase 2: Enhancement (Week 3-4)**
- Full KNBH scoring
- Automated CRM compliance
- Dashboard v1

**Phase 3: Production (Week 5-6)**
- Performance optimization
- Full monitoring
- User training

### 10.3. Rollout Strategy
1. Pilot với 10% calls
2. Gradual increase 25% → 50% → 100%
3. A/B testing cho accuracy validation
4. Rollback plan ready

---

## 📊 SUCCESS METRICS

| Metric | Target | Measurement |
|--------|--------|-------------|
| Scoring Accuracy | MAE ≤ 1.0 | Compare với QA manual |
| CRM Compliance | >85% | Daily compliance rate |
| False Positive | <5% | Agent feedback |
| Processing Speed | <5s | P95 latency |
| User Adoption | >80% | Active users/total |

---

## ⚠️ RISKS & MITIGATIONS

| Risk | Impact | Mitigation |
|------|--------|------------|
| STT accuracy thấp | High | Multiple STT engines, human review |
| Agent resistance | Medium | Training, gradual rollout |
| System overload | Medium | Queue management, scaling |
| Data privacy | High | Encryption, access control |

---

## 📝 APPENDIX

### A. Glossary
- **KNGT:** Kỹ năng giao tiếp
- **KNBH:** Kỹ năng bán hàng
- **KNSV:** Kỹ năng dịch vụ (CSKH variant)
- **WPM:** Words Per Minute
- **VAD:** Voice Activity Detection
- **CRM:** Customer Relationship Management

### B. References
- Master Requirements Document
- Technical Architecture Guidelines
- QA Scoring Manual

---

**Document Status:** FINAL SPECIFICATION  
**Next Steps:** Technical Design Review → Implementation Planning

---