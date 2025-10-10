# THIẾT KẾ HỆ THỐNG ĐÁNH GIÁ TỐC ĐỘ NÓI

**Version:** 1.0  
**Ngày:** 10/10/2025  
**Tác giả:** System Design Team

---

## 📋 MỤC LỤC

1. [Tổng quan hệ thống](#1-tổng-quan-hệ-thống)
2. [Kiến trúc tổng thể](#2-kiến-trúc-tổng-thể)
3. [Components chi tiết](#3-components-chi-tiết)
4. [Data Flow](#4-data-flow)
5. [Database Schema](#5-database-schema)
6. [API Design](#6-api-design)
7. [Technology Stack](#7-technology-stack)
8. [Deployment Architecture](#8-deployment-architecture)
9. [Monitoring & Alerting](#9-monitoring--alerting)
10. [Scalability & Performance](#10-scalability--performance)

---

## 1. TỔNG QUAN HỆ THỐNG

### 1.1. Mục tiêu
Xây dựng hệ thống tự động đánh giá tốc độ nói của agent trong cuộc gọi, phát hiện vi phạm và tạo evidence cụ thể.

### 1.2. Yêu cầu chức năng
- ✅ Nhận audio + transcript từ hệ thống gọi
- ✅ Phân đoạn transcript theo người nói và pause
- ✅ Tính WPM cho từng segment
- ✅ Phát hiện Customer Impact (KH phàn nàn)
- ✅ Đánh giá vi phạm theo ngưỡng cố định
- ✅ Tạo evidence và báo cáo chi tiết
- ✅ Lưu trữ kết quả và metrics

### 1.3. Yêu cầu phi chức năng
- ⚡ **Latency:** <30 giây/cuộc gọi (5 phút audio)
- 📊 **Throughput:** 100 cuộc gọi/phút
- 🔒 **Availability:** 99.9% uptime
- 📈 **Scalability:** Horizontal scaling
- 🔐 **Security:** Mã hóa dữ liệu nhạy cảm

---

## 2. KIẾN TRÚC TỔNG THỂ

### 2.1. High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         CLIENT LAYER                             │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │  Call Center │  │  QA Portal   │  │  Dashboard   │          │
│  │   System     │  │              │  │              │          │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘          │
└─────────┼──────────────────┼──────────────────┼──────────────────┘
          │                  │                  │
          └──────────────────┴──────────────────┘
                             │
                    ┌────────▼────────┐
                    │   API Gateway   │
                    │   (Kong/Nginx)  │
                    └────────┬────────┘
                             │
┌────────────────────────────┴─────────────────────────────────────┐
│                      APPLICATION LAYER                            │
│                                                                   │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │              Speech Rate Evaluation Service              │    │
│  │                                                           │    │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │    │
│  │  │  Ingestion   │  │  Processing  │  │  Evaluation  │  │    │
│  │  │   Service    │→ │   Pipeline   │→ │   Service    │  │    │
│  │  └──────────────┘  └──────────────┘  └──────────────┘  │    │
│  │                                                           │    │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │    │
│  │  │     VAD      │  │   Customer   │  │   Evidence   │  │    │
│  │  │   Service    │  │    Impact    │  │  Generation  │  │    │
│  │  └──────────────┘  └──────────────┘  └──────────────┘  │    │
│  └─────────────────────────────────────────────────────────┘    │
└───────────────────────────────────────────────────────────────────┘
                             │
┌────────────────────────────┴─────────────────────────────────────┐
│                       DATA LAYER                                  │
│                                                                   │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │  PostgreSQL  │  │    Redis     │  │      S3      │          │
│  │  (Metadata)  │  │   (Cache)    │  │   (Audio)    │          │
│  └──────────────┘  └──────────────┘  └──────────────┘          │
│                                                                   │
│  ┌──────────────┐  ┌──────────────┐                             │
│  │ Elasticsearch│  │   RabbitMQ   │                             │
│  │  (Logging)   │  │  (Queue)     │                             │
│  └──────────────┘  └──────────────┘                             │
└───────────────────────────────────────────────────────────────────┘
```

### 2.2. Component Responsibilities

| Component | Trách nhiệm | Technology |
|-----------|-------------|------------|
| **API Gateway** | Load balancing, Rate limiting, Auth | Kong/Nginx |
| **Ingestion Service** | Nhận và validate input | FastAPI/Go |
| **Processing Pipeline** | Orchestrate toàn bộ flow | Celery/Temporal |
| **VAD Service** | Voice Activity Detection | Python + Silero VAD |
| **Evaluation Service** | Đánh giá vi phạm | Python |
| **Customer Impact** | Phát hiện KH phàn nàn | Python + NLP |
| **Evidence Generation** | Tạo báo cáo chi tiết | Python |
| **PostgreSQL** | Lưu metadata, kết quả | PostgreSQL 14+ |
| **Redis** | Cache, Rate limiting | Redis 7+ |
| **S3** | Lưu audio files | MinIO/AWS S3 |
| **Elasticsearch** | Logging, Search | Elasticsearch 8+ |
| **RabbitMQ** | Message Queue | RabbitMQ 3.11+ |

---

## 3. COMPONENTS CHI TIẾT

### 3.1. Ingestion Service

**Chức năng:**
- Nhận audio file + transcript + metadata
- Validate input data
- Upload audio lên S3
- Gửi message vào queue

**API Endpoint:**
```
POST /api/v1/speech-rate/evaluate
```

**Input:**
```json
{
  "call_id": "CALL_12345",
  "agent_id": "AG001",
  "team": "Sales_BH",
  "call_type": "BH",
  "audio_url": "s3://calls/CALL_12345.wav",
  "transcript": [
    {
      "speaker": "AGENT",
      "start": 0.0,
      "end": 5.2,
      "text": "Chào anh, em là tư vấn viên..."
    },
    {
      "speaker": "CUSTOMER",
      "start": 5.5,
      "end": 8.0,
      "text": "Vâng, em nghe"
    }
  ],
  "metadata": {
    "duration": 300.5,
    "created_at": "2025-10-10T10:30:00Z"
  }
}
```

**Validation Rules:**
- Audio file tồn tại và đúng format (WAV/MP3, mono, 16kHz)
- Transcript có ít nhất 1 segment của AGENT
- Timestamps hợp lệ (start < end, không overlap)
- call_type trong [BH, CSKH]

**Output:**
```json
{
  "job_id": "JOB_67890",
  "status": "queued",
  "estimated_time": 25
}
```

---

### 3.2. Processing Pipeline

**Orchestration:** Celery/Temporal workflow

**Pipeline Steps:**

```python
@app.task
def speech_rate_pipeline(job_id, call_data):
    """
    Main pipeline orchestrating all steps
    """
    try:
        # Step 1: Download audio
        audio_path = download_audio(call_data["audio_url"])
        
        # Step 2: Run VAD
        vad_result = run_vad(audio_path)
        
        # Step 3: Segment transcript
        segments = segment_transcript(
            call_data["transcript"], 
            vad_result
        )
        
        # Step 4: Calculate WPM
        wpm_segments = calculate_wpm(segments, vad_result)
        
        # Step 5: Detect Customer Impact
        customer_impacts = detect_customer_impact(
            call_data["transcript"]
        )
        
        # Step 6: Evaluate violation
        violation = evaluate_violation(
            wpm_segments,
            call_data["call_type"],
            customer_impacts
        )
        
        # Step 7: Generate evidence
        evidence = generate_evidence(
            violation,
            wpm_segments,
            customer_impacts
        )
        
        # Step 8: Save results
        save_results(job_id, {
            "violation": violation,
            "evidence": evidence,
            "metrics": compute_metrics(wpm_segments)
        })
        
        # Step 9: Send notification
        notify_completion(job_id)
        
        return {"status": "success"}
        
    except Exception as e:
        handle_error(job_id, e)
        return {"status": "failed", "error": str(e)}
```

**Error Handling:**
- Retry 3 lần với exponential backoff
- Dead Letter Queue cho failed jobs
- Alert khi error rate >5%

---

### 3.3. VAD Service

**Technology:** Silero VAD (ONNX Runtime)

**Function:**
```python
def run_vad(audio_path: str) -> Dict:
    """
    Run Voice Activity Detection
    
    Returns:
        {
            "speech_frames": [
                {"start": 0.0, "end": 2.5},
                {"start": 3.2, "end": 7.8}
            ],
            "pauses": [
                {"start": 2.5, "end": 3.2, "duration": 0.7}
            ]
        }
    """
    # Load model
    model = load_silero_vad()
    
    # Load audio
    audio, sr = librosa.load(audio_path, sr=16000, mono=True)
    
    # Run VAD
    speech_timestamps = model(audio, sr)
    
    # Find pauses >= 700ms
    pauses = find_long_pauses(speech_timestamps, min_duration=0.7)
    
    return {
        "speech_frames": speech_timestamps,
        "pauses": pauses
    }
```

**Performance:**
- Latency: ~0.5-1s cho 5 phút audio
- CPU-only, không cần GPU
- Batch processing: 10 files đồng thời

---

### 3.4. Segmentation Service

**Function:**
```python
def segment_transcript(
    transcript: List[Dict],
    vad_result: Dict
) -> List[Dict]:
    """
    Segment transcript based on speaker & pauses
    
    Steps:
    1. Split by speaker
    2. Split long segments (>15s) by pauses (>=700ms)
    3. Merge short segments (<2s) with previous
    
    Returns:
        [
            {
                "segment_id": "S1",
                "speaker": "AGENT",
                "start": 0.0,
                "end": 8.5,
                "text": "Chào anh...",
                "word_count": 15
            }
        ]
    """
    segments = []
    
    # Step 1: Split by speaker
    for turn in transcript:
        if turn["speaker"] != "AGENT":
            continue
        
        # Step 2: Check if need to split by pause
        if turn["end"] - turn["start"] > 15:
            sub_segments = split_by_pauses(
                turn, 
                vad_result["pauses"]
            )
            segments.extend(sub_segments)
        else:
            segments.append(turn)
    
    # Step 3: Merge short segments
    segments = merge_short_segments(segments, min_duration=2.0)
    
    return segments
```

---

### 3.5. WPM Calculation Service

**Function:**
```python
def calculate_wpm(
    segments: List[Dict],
    vad_result: Dict
) -> List[Dict]:
    """
    Calculate Words Per Minute for each segment
    
    Formula:
        WPM = (word_count / voiced_duration) * 60
        
    voiced_duration = total_duration - pauses (>200ms)
    """
    wpm_segments = []
    
    for seg in segments:
        # Count words
        word_count = len(seg["text"].split())
        
        # Calculate voiced duration
        voiced_duration = calculate_voiced_duration(
            seg["start"],
            seg["end"],
            vad_result["pauses"]
        )
        
        # Calculate WPM
        wpm = (word_count / voiced_duration) * 60 if voiced_duration > 0 else 0
        
        wpm_segments.append({
            **seg,
            "word_count": word_count,
            "voiced_duration": voiced_duration,
            "wpm": round(wpm, 1)
        })
    
    return wpm_segments
```

---

### 3.6. Customer Impact Detection

**Function:**
```python
import re

def detect_customer_impact(transcript: List[Dict]) -> Dict:
    """
    Detect customer complaints about speech rate
    
    Patterns:
    - Request repeat: "nói lại", "nhắc lại", "lặp lại"
    - Complaint: "nói nhanh quá", "nói chậm", "nói từ từ"
    - Not clear: "không nghe rõ", "không hiểu"
    """
    patterns = {
        "request_repeat": [
            r"(nói lại|nhắc lại|lặp lại|nói từ từ|nói chậm)",
            r"(em ơi.*không nghe rõ|không hiểu)",
            r"(nói nhanh|nhanh quá)"
        ]
    }
    
    impacts = []
    
    for turn in transcript:
        if turn["speaker"] != "CUSTOMER":
            continue
        
        text = turn["text"].lower()
        
        for category, pattern_list in patterns.items():
            for pattern in pattern_list:
                if re.search(pattern, text):
                    impacts.append({
                        "timestamp": turn["start"],
                        "text": turn["text"],
                        "category": category
                    })
                    break
    
    return {
        "repeat_requests": len(impacts),
        "impacts": impacts
    }
```

---

### 3.7. Evaluation Service

**Function:**
```python
THRESHOLDS = {
    "BH": {
        "very_slow": 100,
        "slow": 130,
        "fast": 180,
        "very_fast": 220
    },
    "CSKH": {
        "very_slow": 90,
        "slow": 120,
        "fast": 170,
        "very_fast": 210
    }
}

def evaluate_violation(
    wpm_segments: List[Dict],
    call_type: str,
    customer_impacts: Dict
) -> Dict:
    """
    Evaluate violation based on thresholds
    
    Priority:
    1. Customer Impact (highest)
    2. Segment violation ratio
    """
    thresholds = THRESHOLDS[call_type]
    wpm_values = [s["wpm"] for s in wpm_segments]
    
    # Priority 1: Customer Impact
    repeat_count = customer_impacts["repeat_requests"]
    if repeat_count >= 3:
        return {
            "violation_level": "M2",
            "evidence_summary": [
                f"KH yêu cầu nhắc lại {repeat_count} lần",
                "Customer Impact ưu tiên cao nhất"
            ],
            "method": "customer_impact"
        }
    
    # Priority 2: Segment violations
    total = len(wpm_values)
    very_slow = sum(1 for w in wpm_values if w < thresholds["very_slow"])
    very_fast = sum(1 for w in wpm_values if w > thresholds["very_fast"])
    slow = sum(1 for w in wpm_values if thresholds["very_slow"] <= w < thresholds["slow"])
    fast = sum(1 for w in wpm_values if thresholds["fast"] < w <= thresholds["very_fast"])
    
    very_slow_ratio = very_slow / total
    very_fast_ratio = very_fast / total
    outlier_ratio = (slow + fast) / total
    
    median_wpm = np.median(wpm_values)
    
    # M3: Very severe
    if very_slow_ratio >= 0.20 or very_fast_ratio >= 0.20:
        return {
            "violation_level": "M3",
            "evidence_summary": [
                f"20%+ segments quá nhanh/chậm",
                f"Median: {median_wpm:.0f} wpm"
            ],
            "method": "absolute_threshold"
        }
    
    # M2: Severe
    if very_slow_ratio >= 0.10 or very_fast_ratio >= 0.10:
        return {
            "violation_level": "M2",
            "evidence_summary": [
                f"10%+ segments quá nhanh/chậm",
                f"Median: {median_wpm:.0f} wpm"
            ],
            "method": "absolute_threshold"
        }
    
    # M1: Minor
    if outlier_ratio >= 0.25 or repeat_count >= 2:
        return {
            "violation_level": "M1",
            "evidence_summary": [
                f"25%+ segments hơi lệch",
                f"Median: {median_wpm:.0f} wpm"
            ],
            "method": "absolute_threshold"
        }
    
    # OK
    return {
        "violation_level": "OK",
        "evidence_summary": [
            f"Tốc độ phù hợp",
            f"Median: {median_wpm:.0f} wpm"
        ],
        "method": "absolute_threshold"
    }
```

---

### 3.8. Evidence Generation Service

**Function:**
```python
def generate_evidence(
    violation: Dict,
    wpm_segments: List[Dict],
    customer_impacts: Dict,
    call_type: str
) -> List[Dict]:
    """
    Generate evidence for violation
    """
    evidence_items = []
    thresholds = THRESHOLDS[call_type]
    
    # 1. Customer Impact evidence
    for impact in customer_impacts["impacts"]:
        evidence_items.append({
            "type": "customer_impact",
            "timestamp": impact["timestamp"],
            "text": impact["text"],
            "speaker": "CUSTOMER",
            "severity": "high"
        })
    
    # 2. Metric violation evidence
    for seg in wpm_segments:
        if seg["wpm"] < thresholds["very_slow"] or seg["wpm"] > thresholds["very_fast"]:
            evidence_items.append({
                "type": "metric_violation",
                "segment_id": seg["segment_id"],
                "timestamp_start": seg["start"],
                "timestamp_end": seg["end"],
                "text": seg["text"][:100] + "...",
                "wpm": seg["wpm"],
                "threshold_violated": get_threshold_name(seg["wpm"], thresholds),
                "severity": "high"
            })
        elif thresholds["slow"] <= seg["wpm"] < thresholds["fast"]:
            continue  # OK range
        else:
            evidence_items.append({
                "type": "metric_violation",
                "segment_id": seg["segment_id"],
                "timestamp_start": seg["start"],
                "timestamp_end": seg["end"],
                "text": seg["text"][:100] + "...",
                "wpm": seg["wpm"],
                "threshold_violated": get_threshold_name(seg["wpm"], thresholds),
                "severity": "medium"
            })
    
    return evidence_items
```

---

## 4. DATA FLOW

### 4.1. Request Flow

```
┌──────────┐     ┌──────────┐     ┌──────────┐     ┌──────────┐
│  Client  │────→│   API    │────→│  Queue   │────→│  Worker  │
│          │     │ Gateway  │     │ RabbitMQ │     │  Celery  │
└──────────┘     └──────────┘     └──────────┘     └────┬─────┘
                                                          │
                                                          ▼
     ┌────────────────────────────────────────────────────────┐
     │              Processing Pipeline                       │
     │                                                         │
     │  1. VAD → 2. Segment → 3. WPM → 4. Customer Impact   │
     │                                                         │
     │  5. Evaluate → 6. Evidence → 7. Save                  │
     └────────────────────────────┬───────────────────────────┘
                                  │
                    ┌─────────────▼─────────────┐
                    │      Save Results         │
                    │   PostgreSQL + Cache      │
                    └───────────────────────────┘
```

### 4.2. Query Flow

```
┌──────────┐     ┌──────────┐     ┌──────────┐
│  Client  │────→│   API    │────→│  Cache   │
│          │     │ Gateway  │     │  Redis   │
└──────────┘     └──────────┘     └────┬─────┘
                                        │
                                   Cache Hit?
                                        │
                                  ┌─────┴─────┐
                                  │           │
                               Yes│          │No
                                  │           │
                           ┌──────▼───┐  ┌───▼──────┐
                           │  Return  │  │   Query  │
                           │  Cached  │  │  Postgres│
                           └──────────┘  └────┬─────┘
                                              │
                                         ┌────▼────┐
                                         │ Cache & │
                                         │ Return  │
                                         └─────────┘
```

---

## 5. DATABASE SCHEMA

### 5.1. PostgreSQL Tables

#### Table: `calls`
```sql
CREATE TABLE calls (
    call_id VARCHAR(50) PRIMARY KEY,
    agent_id VARCHAR(50) NOT NULL,
    team VARCHAR(50) NOT NULL,
    call_type VARCHAR(10) NOT NULL CHECK (call_type IN ('BH', 'CSKH')),
    audio_url TEXT NOT NULL,
    duration FLOAT NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    
    INDEX idx_agent_id (agent_id),
    INDEX idx_team (team),
    INDEX idx_created_at (created_at)
);
```

#### Table: `speech_rate_evaluations`
```sql
CREATE TABLE speech_rate_evaluations (
    id SERIAL PRIMARY KEY,
    call_id VARCHAR(50) NOT NULL REFERENCES calls(call_id),
    job_id VARCHAR(50) UNIQUE NOT NULL,
    
    -- Metrics
    median_wpm FLOAT NOT NULL,
    mean_wpm FLOAT NOT NULL,
    p90_wpm FLOAT NOT NULL,
    total_segments INT NOT NULL,
    
    -- Segment breakdown
    very_slow_segments INT DEFAULT 0,
    slow_segments INT DEFAULT 0,
    ok_segments INT DEFAULT 0,
    fast_segments INT DEFAULT 0,
    very_fast_segments INT DEFAULT 0,
    
    -- Customer Impact
    customer_impact_count INT DEFAULT 0,
    
    -- Violation
    violation_level VARCHAR(10) NOT NULL CHECK (violation_level IN ('OK', 'M1', 'M2', 'M3')),
    violation_method VARCHAR(50) NOT NULL,
    
    -- Penalty
    penalty_amount FLOAT NOT NULL,
    penalty_description TEXT,
    
    -- Processing info
    processing_time_ms INT,
    status VARCHAR(20) DEFAULT 'completed',
    error_message TEXT,
    
    created_at TIMESTAMP DEFAULT NOW(),
    
    INDEX idx_call_id (call_id),
    INDEX idx_violation_level (violation_level),
    INDEX idx_created_at (created_at)
);
```

#### Table: `segments`
```sql
CREATE TABLE segments (
    id SERIAL PRIMARY KEY,
    evaluation_id INT NOT NULL REFERENCES speech_rate_evaluations(id),
    segment_id VARCHAR(20) NOT NULL,
    
    start_time FLOAT NOT NULL,
    end_time FLOAT NOT NULL,
    text TEXT NOT NULL,
    
    word_count INT NOT NULL,
    voiced_duration FLOAT NOT NULL,
    wpm FLOAT NOT NULL,
    
    violation_type VARCHAR(20),  -- very_slow, slow, fast, very_fast, NULL
    
    created_at TIMESTAMP DEFAULT NOW(),
    
    INDEX idx_evaluation_id (evaluation_id),
    INDEX idx_wpm (wpm)
);
```

#### Table: `evidence`
```sql
CREATE TABLE evidence (
    id SERIAL PRIMARY KEY,
    evaluation_id INT NOT NULL REFERENCES speech_rate_evaluations(id),
    
    evidence_type VARCHAR(30) NOT NULL,  -- customer_impact, metric_violation
    timestamp FLOAT NOT NULL,
    text TEXT,
    speaker VARCHAR(20),
    
    -- For metric_violation
    segment_id VARCHAR(20),
    wpm FLOAT,
    threshold_violated VARCHAR(20),
    
    severity VARCHAR(10) NOT NULL CHECK (severity IN ('low', 'medium', 'high')),
    
    created_at TIMESTAMP DEFAULT NOW(),
    
    INDEX idx_evaluation_id (evaluation_id),
    INDEX idx_evidence_type (evidence_type)
);
```

### 5.2. Redis Cache Structure

```
# Job status
job:{job_id} -> {
    "status": "processing|completed|failed",
    "progress": 0.75,
    "created_at": "2025-10-10T10:30:00Z"
}
TTL: 3600s

# Evaluation result (cache)
eval:{call_id} -> {full JSON result}
TTL: 86400s (1 day)

# Rate limiting
ratelimit:{ip_address} -> counter
TTL: 60s
```

---

## 6. API DESIGN

### 6.1. REST API Endpoints

#### POST `/api/v1/speech-rate/evaluate`
**Description:** Submit a new evaluation job

**Request:**
```json
{
  "call_id": "CALL_12345",
  "agent_id": "AG001",
  "team": "Sales_BH",
  "call_type": "BH",
  "audio_url": "s3://calls/CALL_12345.wav",
  "transcript": [...]
}
```

**Response (202 Accepted):**
```json
{
  "job_id": "JOB_67890",
  "status": "queued",
  "estimated_time": 25,
  "status_url": "/api/v1/jobs/JOB_67890"
}
```

---

#### GET `/api/v1/jobs/{job_id}`
**Description:** Get job status

**Response (200 OK):**
```json
{
  "job_id": "JOB_67890",
  "status": "completed",
  "progress": 1.0,
  "result_url": "/api/v1/speech-rate/results/CALL_12345",
  "created_at": "2025-10-10T10:30:00Z",
  "completed_at": "2025-10-10T10:30:25Z"
}
```

---

#### GET `/api/v1/speech-rate/results/{call_id}`
**Description:** Get evaluation result

**Response (200 OK):**
```json
{
  "call_id": "CALL_12345",
  "agent_id": "AG001",
  "violation": {
    "violation_level": "M1",
    "evidence_summary": [...]
  },
  "penalty": {
    "amount": 0.067,
    "description": "Trừ điểm tiêu chí con"
  },
  "metrics": {
    "median_wpm": 185,
    "p90_wpm": 205
  },
  "evidence": [...]
}
```

---

#### GET `/api/v1/speech-rate/stats`
**Description:** Get aggregate statistics

**Query Parameters:**
- `team` (optional)
- `agent_id` (optional)
- `start_date` (required)
- `end_date` (required)

**Response (200 OK):**
```json
{
  "total_calls": 1500,
  "violation_breakdown": {
    "OK": 1100,
    "M1": 250,
    "M2": 100,
    "M3": 50
  },
  "avg_median_wpm": 162.5,
  "false_positive_rate": 0.08
}
```

---

## 7. TECHNOLOGY STACK

### 7.1. Backend

| Layer | Technology | Version | Reason |
|-------|-----------|---------|--------|
| **API Framework** | FastAPI | 0.104+ | High performance, async, auto docs |
| **Task Queue** | Celery | 5.3+ | Mature, reliable, distributed |
| **Message Broker** | RabbitMQ | 3.11+ | Persistent, clustering |
| **Cache** | Redis | 7+ | Fast, versatile |
| **Database** | PostgreSQL | 14+ | ACID, JSON support, TimescaleDB |
| **Object Storage** | MinIO/S3 | - | Scalable, S3-compatible |
| **Search/Logging** | Elasticsearch | 8+ | Full-text search, analytics |

### 7.2. Audio Processing

| Tool | Purpose | Version |
|------|---------|---------|
| **Silero VAD** | Voice Activity Detection | Latest |
| **librosa** | Audio loading | 0.10+ |
| **numpy** | Numerical computation | 1.24+ |
| **scipy** | Signal processing | 1.11+ |

### 7.3. NLP/ML

| Tool | Purpose | Version |
|------|---------|---------|
| **regex** | Pattern matching | Built-in |
| **underthesea** | Vietnamese NLP | 6.3+ |
| **pydantic** | Data validation | 2.0+ |

### 7.4. Infrastructure

| Tool | Purpose | Version |
|------|---------|---------|
| **Docker** | Containerization | 24+ |
| **Kubernetes** | Orchestration | 1.28+ |
| **Prometheus** | Monitoring | 2.45+ |
| **Grafana** | Visualization | 10+ |
| **ELK Stack** | Logging | 8+ |

---

## 8. DEPLOYMENT ARCHITECTURE

### 8.1. Kubernetes Deployment

```yaml
# api-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: speech-rate-api
spec:
  replicas: 3
  selector:
    matchLabels:
      app: speech-rate-api
  template:
    metadata:
      labels:
        app: speech-rate-api
    spec:
      containers:
      - name: api
        image: speech-rate-api:1.0
        ports:
        - containerPort: 8000
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: db-secret
              key: url
        resources:
          requests:
            memory: "512Mi"
            cpu: "500m"
          limits:
            memory: "1Gi"
            cpu: "1000m"
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /ready
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 5
---
# worker-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: speech-rate-worker
spec:
  replicas: 5
  selector:
    matchLabels:
      app: speech-rate-worker
  template:
    metadata:
      labels:
        app: speech-rate-worker
    spec:
      containers:
      - name: worker
        image: speech-rate-worker:1.0
        env:
        - name: CELERY_BROKER_URL
          value: "amqp://rabbitmq:5672"
        resources:
          requests:
            memory: "2Gi"
            cpu: "1000m"
          limits:
            memory: "4Gi"
            cpu: "2000m"
```

### 8.2. Service Configuration

```yaml
# service.yaml
apiVersion: v1
kind: Service
metadata:
  name: speech-rate-api
spec:
  selector:
    app: speech-rate-api
  ports:
  - protocol: TCP
    port: 80
    targetPort: 8000
  type: LoadBalancer
```

### 8.3. Horizontal Pod Autoscaler

```yaml
# hpa.yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: speech-rate-api-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: speech-rate-api
  minReplicas: 3
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
  - type: Resource
    resource:
      name: memory
      target:
        type: Utilization
        averageUtilization: 80
```

---

## 9. MONITORING & ALERTING

### 9.1. Metrics to Monitor

#### Application Metrics
```python
# Prometheus metrics
from prometheus_client import Counter, Histogram, Gauge

# Request metrics
request_count = Counter(
    'speech_rate_requests_total',
    'Total requests',
    ['endpoint', 'status']
)

request_duration = Histogram(
    'speech_rate_request_duration_seconds',
    'Request duration',
    ['endpoint']
)

# Processing metrics
processing_duration = Histogram(
    'speech_rate_processing_duration_seconds',
    'Processing duration',
    ['step']
)

queue_size = Gauge(
    'speech_rate_queue_size',
    'Queue size'
)

# Business metrics
violation_count = Counter(
    'speech_rate_violations_total',
    'Total violations',
    ['level', 'team']
)

false_positive_rate = Gauge(
    'speech_rate_false_positive_rate',
    'False positive rate'
)
```

#### Infrastructure Metrics
- CPU utilization
- Memory utilization
- Disk I/O
- Network I/O
- Pod restart count

### 9.2. Alerting Rules

```yaml
# prometheus-alerts.yaml
groups:
- name: speech-rate-alerts
  rules:
  # High error rate
  - alert: HighErrorRate
    expr: rate(speech_rate_requests_total{status="5xx"}[5m]) > 0.05
    for: 5m
    labels:
      severity: critical
    annotations:
      summary: "High error rate (>5%)"
      
  # High latency
  - alert: HighLatency
    expr: histogram_quantile(0.95, rate(speech_rate_request_duration_seconds_bucket[5m])) > 30
    for: 5m
    labels:
      severity: warning
    annotations:
      summary: "95th percentile latency >30s"
      
  # Queue backlog
  - alert: QueueBacklog
    expr: speech_rate_queue_size > 1000
    for: 10m
    labels:
      severity: warning
    annotations:
      summary: "Queue backlog >1000 jobs"
      
  # High false positive
  - alert: HighFalsePositiveRate
    expr: speech_rate_false_positive_rate > 0.15
    for: 15m
    labels:
      severity: warning
    annotations:
      summary: "False positive rate >15%"
```

### 9.3. Grafana Dashboard

**Panels:**
1. Request Rate (req/s)
2. Latency (p50, p95, p99)
3. Error Rate (%)
4. Queue Size
5. Processing Duration by Step
6. Violation Breakdown (Pie chart)
7. False Positive Rate (Time series)
8. Resource Utilization (CPU/Memory)

---

## 10. SCALABILITY & PERFORMANCE

### 10.1. Performance Targets

| Metric | Target | Current |
|--------|--------|---------|
| **API Latency (p95)** | <200ms | TBD |
| **Processing Time** | <30s/call | ~25s |
| **Throughput** | 100 calls/min | TBD |
| **Queue Latency** | <5s | TBD |
| **Availability** | 99.9% | TBD |

### 10.2. Scaling Strategies

#### Horizontal Scaling
- **API:** Auto-scale 3-10 pods based on CPU
- **Workers:** Auto-scale 5-20 pods based on queue size
- **Database:** Read replicas for queries

#### Vertical Scaling
- Workers: 2-4 CPU cores, 2-4GB RAM
- API: 1-2 CPU cores, 512MB-1GB RAM

#### Caching Strategy
- Cache evaluation results for 24h
- Cache job status for 1h
- Cache stats queries for 5 minutes

### 10.3. Optimization Techniques

#### 1. VAD Optimization
```python
# Batch processing multiple files
def batch_vad(audio_paths: List[str]) -> List[Dict]:
    """Process multiple audio files in parallel"""
    with ThreadPoolExecutor(max_workers=10) as executor:
        results = executor.map(run_vad, audio_paths)
    return list(results)
```

#### 2. Database Optimization
```sql
-- Partitioning by date
CREATE TABLE speech_rate_evaluations (
    ...
) PARTITION BY RANGE (created_at);

CREATE TABLE speech_rate_evaluations_2025_10
    PARTITION OF speech_rate_evaluations
    FOR VALUES FROM ('2025-10-01') TO ('2025-11-01');

-- Indexes
CREATE INDEX CONCURRENTLY idx_eval_call_created
    ON speech_rate_evaluations(call_id, created_at DESC);

CREATE INDEX CONCURRENTLY idx_segments_eval_wpm
    ON segments(evaluation_id, wpm);
```

#### 3. Query Optimization
```python
# Use connection pooling
from sqlalchemy.pool import QueuePool

engine = create_engine(
    DATABASE_URL,
    poolclass=QueuePool,
    pool_size=20,
    max_overflow=40
)

# Batch inserts
def save_segments_batch(segments: List[Dict]):
    """Batch insert segments"""
    db.execute(
        insert(Segment),
        segments
    )
```

---

## 11. SECURITY

### 11.1. Authentication & Authorization

```python
# JWT-based auth
from fastapi import Security, HTTPException
from fastapi.security import HTTPBearer

security = HTTPBearer()

async def verify_token(credentials: HTTPAuthorizationCredentials = Security(security)):
    token = credentials.credentials
    payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
    return payload

@app.post("/api/v1/speech-rate/evaluate")
async def evaluate(request: EvaluateRequest, user=Depends(verify_token)):
    # Check permissions
    if not user.has_permission("speech_rate:write"):
        raise HTTPException(403, "Forbidden")
    ...
```

### 11.2. Data Encryption

- **In Transit:** TLS 1.3
- **At Rest:** 
  - Database: Transparent Data Encryption (TDE)
  - S3: Server-side encryption (SSE-S3)

### 11.3. Rate Limiting

```python
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

@app.post("/api/v1/speech-rate/evaluate")
@limiter.limit("100/minute")
async def evaluate(request: Request):
    ...
```

---

## 12. TESTING STRATEGY

### 12.1. Unit Tests

```python
# test_wpm_calculation.py
def test_calculate_wpm():
    segments = [{
        "text": "Chào anh em là tư vấn viên",
        "start": 0.0,
        "end": 3.0
    }]
    vad_result = {"pauses": []}
    
    result = calculate_wpm(segments, vad_result)
    
    assert result[0]["wpm"] == pytest.approx(120, rel=0.1)
```

### 12.2. Integration Tests

```python
# test_pipeline.py
@pytest.mark.integration
async def test_full_pipeline():
    # Submit job
    response = client.post("/api/v1/speech-rate/evaluate", json=test_data)
    assert response.status_code == 202
    
    job_id = response.json()["job_id"]
    
    # Wait for completion
    await wait_for_job(job_id, timeout=60)
    
    # Check result
    result = client.get(f"/api/v1/speech-rate/results/{call_id}")
    assert result.status_code == 200
    assert "violation" in result.json()
```

### 12.3. Load Tests

```python
# locustfile.py
from locust import HttpUser, task, between

class SpeechRateUser(HttpUser):
    wait_time = between(1, 3)
    
    @task
    def evaluate_call(self):
        self.client.post("/api/v1/speech-rate/evaluate", json=sample_data)
```

---

## 13. DISASTER RECOVERY

### 13.1. Backup Strategy

- **Database:** Daily full backup, hourly incremental
- **Retention:** 30 days
- **S3:** Versioning enabled, lifecycle policy

### 13.2. Recovery Procedures

**RTO (Recovery Time Objective):** 1 hour  
**RPO (Recovery Point Objective):** 1 hour

**Steps:**
1. Restore database from latest backup
2. Replay message queue (if available)
3. Restart services
4. Verify data integrity

---

## PHỤ LỤC

### A. Environment Variables

```bash
# .env.example
DATABASE_URL=postgresql://user:pass@localhost:5432/speechrate
REDIS_URL=redis://localhost:6379/0
RABBITMQ_URL=amqp://guest:guest@localhost:5672/
S3_ENDPOINT=http://localhost:9000
S3_ACCESS_KEY=minioadmin
S3_SECRET_KEY=minioadmin
SECRET_KEY=your-secret-key
LOG_LEVEL=INFO
```

### B. Docker Compose (Development)

```yaml
version: '3.8'

services:
  postgres:
    image: postgres:14
    environment:
      POSTGRES_DB: speechrate
      POSTGRES_USER: user
      POSTGRES_PASSWORD: pass
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
      
  redis:
    image: redis:7
    ports:
      - "6379:6379"
      
  rabbitmq:
    image: rabbitmq:3.11-management
    ports:
      - "5672:5672"
      - "15672:15672"
      
  minio:
    image: minio/minio
    command: server /data --console-address ":9001"
    ports:
      - "9000:9000"
      - "9001:9001"
    volumes:
      - minio_data:/data
      
volumes:
  postgres_data:
  minio_data:
```

---

**Document Version:** 1.0  
**Last Updated:** 10/10/2025  
**Next Review:** 10/11/2025