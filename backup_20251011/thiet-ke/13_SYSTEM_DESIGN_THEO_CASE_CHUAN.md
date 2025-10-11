# THIẾT KẾ HỆ THỐNG - THEO CHUẨN CASE DỰ ÁN

**Version:** 2.0  
**Ngày:** 10/10/2025  
**Tác giả:** System Design Team  
**Tuân thủ:** Master Spec v0.1 + UC01 Re-Spec

---

## 📋 MỤC LỤC

1. [Tổng quan 2 CASE](#1-tổng-quan-2-case)
2. [CASE 2: Call Scoring & Coaching (Ưu tiên)](#2-case-2-call-scoring--coaching)
3. [Kiến trúc tổng thể CASE 2](#3-kiến-trúc-tổng-thể-case-2)
4. [Components chi tiết](#4-components-chi-tiết)
5. [Data Flow & Sequence](#5-data-flow--sequence)
6. [Database Schema](#6-database-schema)
7. [API Design](#7-api-design)
8. [Call Type Detection (Audio-only)](#8-call-type-detection-audio-only)
9. [Speech Rate Evaluation (SR - KNGT)](#9-speech-rate-evaluation-sr---kngt)
10. [CASE 1: CRM Compliance (Tham chiếu)](#10-case-1-crm-compliance)

---

## 1. TỔNG QUAN 2 CASE

### 1.1. CASE Definitions

#### **CASE 1 – CRM Compliance**
- **Mục tiêu:** Kiểm tra Agent có cập nhật CRM/ticket đúng quy định
- **Input:** CRM records (notes, ticket, opportunity, updated_at), call metadata
- **Output:** Violations (M1/M2/M3), Reminders, Reports
- **Phạm vi:** Chỉ đánh giá **NTT (Nhập thông tin)** - 10% tổng điểm
- **KPIs:** Detection rate, False positive <5%, Resolution rate >85%

#### **CASE 2 – Call Scoring & Coaching** ⭐ (Ưu tiên cao)
- **Mục tiêu:** Chấm điểm chất lượng cuộc gọi theo **KNGT + KNBH**
- **Input:** Audio + Transcript (diarization) + Metadata
- **Output:** Score (0-10), Summary, Recommendations, Suggested Scripts, Evidence
- **Phạm vi:** KNGT (40-70%) + KNBH (30-60%) - Tùy call_type
- **KPIs:** MAE ≤1.0, F1 M2/M3 ≥0.8, Latency ≤5s (không tính STT)

### 1.2. Phân bổ điểm theo loại cuộc gọi

| Nhóm | BH | CSKH | Ghi chú |
|------|-----|------|---------|
| **KNGT** (Kỹ năng giao tiếp) | 40% (4.0 điểm) | 70% (7.0 điểm) | CSKH cần empathy cao hơn |
| **KNBH/KNSV** (Kỹ năng bán hàng/dịch vụ) | 60% (6.0 điểm) | 30% (3.0 điểm) | BH focus outcomes |
| **NTT** (Nhập CRM) | 10% (1.0 điểm) | 10% (1.0 điểm) | Xử lý ở CASE 1 (UC09) |

**Tổng:** 110% → UC01 chỉ chấm KNGT+KNBH = 100%, NTT riêng biệt

### 1.3. Quy tắc trừ điểm

| Mức độ | KNGT & KNBH | NTT (CASE 1) |
|--------|-------------|--------------|
| **OK** | Không trừ điểm | Không trừ |
| **M1** | Trừ điểm tiêu chí con (theo trọng số) | Trừ 20% |
| **M2** | Trừ 50% điểm nhóm | Trừ 50% |
| **M3** | Điểm nhóm = 0 | Điểm nhóm = 0 |

---

## 2. CASE 2: CALL SCORING & COACHING

### 2.1. Actors

| Actor | Vai trò | Tương tác |
|-------|---------|-----------|
| **Agent (Sales/CSKH)** | Người thực hiện cuộc gọi | Nhận kết quả, xem evidence, recommendations |
| **QA Reviewer** | Kiểm định chất lượng | Review kết quả, điều chỉnh thresholds |
| **Team Manager** | Quản lý đội | Xem báo cáo tổng hợp, xu hướng |
| **System Admin** | Vận hành hệ thống | Config rules, monitor performance |
| **PBX/Telephony** | Hệ thống gọi | Gửi audio + metadata |

### 2.2. Use Case Flow (High-level)

```mermaid
flowchart TB
    A[PBX gửi Audio + Metadata] --> B[STT + Diarization]
    B --> C[Call Type Detection<br/>audio-only]
    B --> D[Feature Extraction<br/>wpm, pause, interrupts]
    
    C --> E{Confidence >= τ?}
    E -->|Yes| F[Apply Weight theo Type]
    E -->|No| G[Mixture-of-Weights]
    
    D --> H[Evaluate KNGT]
    D --> I[Evaluate KNBH]
    
    F --> H
    F --> I
    G --> H
    G --> I
    
    H --> J[Calculate Total Score]
    I --> J
    
    J --> K[Generate Summary]
    J --> L[Generate Recommendations]
    J --> M[Map Suggested Scripts]
    
    K --> N[Save to DB + Cache]
    L --> N
    M --> N
    
    N --> O[Return Report to UI]
```

### 2.3. Input Specification

#### Bắt buộc:
```json
{
  "call_id": "CALL-2025-001",
  "agent_id": "AG001",
  "call_time": "2025-10-10T10:30:00Z",
  "audio_url": "s3://calls/CALL-2025-001.wav",
  "transcript": [
    {
      "speaker": "AGENT",
      "start": 0.0,
      "end": 5.2,
      "text": "Chào anh, em là tư vấn viên của..."
    },
    {
      "speaker": "CUSTOMER",
      "start": 5.5,
      "end": 8.0,
      "text": "Vâng, em nghe"
    }
  ]
}
```

#### Không yêu cầu:
- ❌ `call_type` (hệ thống tự phát hiện từ audio)
- ❌ `crm_data` (chỉ cần cho NTT/CASE 1)

#### Features tối thiểu (được extract tự động):
- `wpm` (words per minute) theo segment
- `pause_ratio` (% thời gian im lặng)
- `interrupt_count` (số lần ngắt lời)
- `sentiment_trend` (xu hướng cảm xúc)
- `customer_repeat_count` (KH yêu cầu nhắc lại)
- `explicit_complaint` flags (phàn nàn rõ ràng)

### 2.4. Output Specification

```json
{
  "call_id": "CALL-2025-001",
  "agent_id": "AG001",
  "call_time": "2025-10-10T10:30:00Z",
  
  "call_type_detection": {
    "predicted": "BH",
    "confidence": 0.85,
    "method": "audio_only",
    "signals": {
      "keywords": ["gói bảo hiểm", "ưu đãi", "phí"],
      "interaction_pattern": "agent_led_sales",
      "first_60s_sentiment": "neutral_to_positive"
    }
  },
  
  "score": {
    "total": 7.8,
    "label": "Khá",
    "passed": true,
    "weights_used": {
      "KNGT": 0.4,
      "KNBH": 0.6
    },
    "groups": {
      "KNGT": {
        "points": 3.1,
        "max_points": 4.0,
        "percentage": 77.5,
        "criteria": [
          {
            "code": "GRT",
            "name": "Chào hỏi & xưng danh",
            "weight": 0.05,
            "max_points": 0.2,
            "earned_points": 0.2,
            "violation_level": "OK"
          },
          {
            "code": "SR",
            "name": "Tốc độ nói & rõ ràng",
            "weight": 0.08,
            "max_points": 0.32,
            "earned_points": 0.24,
            "violation_level": "M1",
            "evidence": {
              "median_wpm": 185,
              "baseline_wpm": 155,
              "segments_violated": 3,
              "total_segments": 18,
              "customer_impact": 0,
              "timestamps": ["00:04:10-00:04:35", "00:07:20-00:07:50"]
            }
          }
        ]
      },
      "KNBH": {
        "points": 4.7,
        "max_points": 6.0,
        "percentage": 78.3,
        "criteria": [
          {
            "code": "NEED",
            "name": "Khai thác nhu cầu",
            "weight": 0.10,
            "max_points": 0.6,
            "earned_points": 0.3,
            "violation_level": "M2",
            "evidence": {
              "open_questions": 1,
              "expected_min": 2,
              "quote": "Anh có quan tâm đến bảo hiểm không ạ?",
              "timestamps": ["00:02:10-00:02:30"],
              "reason": "Câu hỏi đóng, chưa làm rõ nhu cầu cốt lõi"
            }
          }
        ]
      }
    }
  },
  
  "summary": {
    "text": "Cuộc gọi BH về gói bảo hiểm sức khỏe. KH quan tâm đến quyền lợi và chi phí. Agent đã giới thiệu 2 gói phù hợp, giải thích điều khoản và ưu đãi. Kết quả: KH đồng ý nhận báo giá chi tiết qua email. Next step: Gửi proposal trong 24h.",
    "highlights": [
      "Agent chào hỏi chuyên nghiệp, xưng danh rõ ràng",
      "Tốc độ nói hơi nhanh khi trình bày điều khoản (185 wpm)",
      "Chưa khai thác đủ nhu cầu cốt lõi của KH",
      "Giải thích sản phẩm rõ ràng, so sánh 2 gói hiệu quả",
      "Chốt CTA rõ ràng, xác nhận next step"
    ]
  },
  
  "recommendations": [
    {
      "priority": "high",
      "category": "KNGT",
      "criterion": "SR",
      "message": "Giảm tốc độ xuống 130-140 wpm khi trình bày điều khoản quan trọng. Xen kẽ câu ngắn và kiểm tra sự hiểu của KH bằng câu hỏi: 'Anh có thắc mắc điểm nào không ạ?'",
      "actionable": true
    },
    {
      "priority": "high",
      "category": "KNBH",
      "criterion": "NEED",
      "message": "Dùng 2-3 câu hỏi mở để làm rõ nhu cầu cốt lõi trước khi tư vấn. Ví dụ: 'Anh/chị quan tâm đến bảo hiểm vì lý do gì ạ?', 'Hiện tại anh/chị có bảo hiểm nào chưa ạ?'",
      "actionable": true
    }
  ],
  
  "suggested_scripts": [
    {
      "id": "scripts/bh/need_exploration_v1",
      "stage": "need_identification",
      "text": "Em xin phép hỏi thêm để tư vấn chính xác: Hiện tại anh/chị đang quan tâm đến bảo hiểm vì lý do gì ạ? Anh/chị kỳ vọng quyền lợi nào là quan trọng nhất?",
      "when_to_use": "Khi cần khai thác nhu cầu sâu hơn"
    },
    {
      "id": "scripts/bh/pace_control_v1",
      "stage": "product_explanation",
      "text": "Em xin giải thích từng phần để anh/chị dễ theo dõi. [Giải thích điều khoản 1]. Anh/chị có thắc mắc điểm này không ạ? [Đợi phản hồi]. Tiếp theo là...",
      "when_to_use": "Khi trình bày thông tin phức tạp"
    }
  ],
  
  "evidence": [
    {
      "type": "metric_violation",
      "criterion": "SR",
      "segment_id": "S5",
      "timestamp_start": 250.0,
      "timestamp_end": 275.0,
      "text": "Anh quan tâm gói bảo hiểm này có quyền lợi nằm viện tối đa 365 ngày phí phẫu thuật chi trả 100% không giới hạn...",
      "wpm": 205,
      "threshold": "fast (180-220)",
      "severity": "medium",
      "customer_impact": false
    },
    {
      "type": "criterion_violation",
      "criterion": "NEED",
      "timestamp_start": 130.0,
      "timestamp_end": 150.0,
      "text": "Anh có quan tâm đến bảo hiểm không ạ?",
      "reason": "Câu hỏi đóng (yes/no), không khai thác nhu cầu sâu",
      "severity": "high",
      "expected_behavior": "Dùng câu hỏi mở: 'Anh quan tâm đến loại bảo hiểm nào ạ?' hoặc 'Anh đang tìm bảo hiểm để giải quyết vấn đề gì ạ?'"
    }
  ],
  
  "metadata": {
    "processing_time_ms": 4500,
    "stt_duration_ms": 8000,
    "evaluation_method": "absolute_threshold",
    "baseline_available": false,
    "context_aware_rules_applied": ["pause_for_lookup", "reading_terms"],
    "created_at": "2025-10-10T10:35:25Z"
  }
}
```

---

## 3. KIẾN TRÚC TỔNG THỂ CASE 2

### 3.1. High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                       CLIENT LAYER                               │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │ PBX/Telephony│  │  Agent UI    │  │ QA Dashboard │          │
│  │   System     │  │              │  │              │          │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘          │
└─────────┼──────────────────┼──────────────────┼──────────────────┘
          │                  │                  │
          └──────────────────┴──────────────────┘
                             │
                    ┌────────▼────────┐
                    │   API Gateway   │
                    │  (Kong/Nginx)   │
                    └────────┬────────┘
                             │
┌────────────────────────────┴─────────────────────────────────────┐
│                    APPLICATION LAYER                              │
│                                                                   │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │            Call Scoring & Coaching Service                 │  │
│  │                                                             │  │
│  │  ┌──────────────────────────────────────────────────────┐ │  │
│  │  │           CASE 2: Call Scoring Pipeline              │ │  │
│  │  │                                                        │ │  │
│  │  │  ┌──────────┐  ┌──────────┐  ┌──────────┐          │ │  │
│  │  │  │Ingestion │→ │   STT    │→ │Call Type │          │ │  │
│  │  │  │ Service  │  │+Diarize  │  │Detector  │          │ │  │
│  │  │  └──────────┘  └──────────┘  └────┬─────┘          │ │  │
│  │  │                                    │                 │ │  │
│  │  │  ┌──────────┐  ┌──────────┐  ┌───▼──────┐          │ │  │
│  │  │  │ Feature  │  │  KNGT    │  │  KNBH    │          │ │  │
│  │  │  │Extractor │→ │Evaluator │  │Evaluator │          │ │  │
│  │  │  └──────────┘  └────┬─────┘  └────┬─────┘          │ │  │
│  │  │                     │              │                 │ │  │
│  │  │  ┌──────────┐  ┌───▼──────────────▼───┐            │ │  │
│  │  │  │ Summary  │  │   Score Calculator   │            │ │  │
│  │  │  │Generator │  │  (Weight Applier)    │            │ │  │
│  │  │  └────┬─────┘  └─────────┬────────────┘            │ │  │
│  │  │       │                   │                          │ │  │
│  │  │  ┌────▼─────┐  ┌─────────▼──────┐                  │ │  │
│  │  │  │Recomm-   │  │Script Mapper   │                  │ │  │
│  │  │  │endation  │  │                │                  │ │  │
│  │  │  └────┬─────┘  └────────┬───────┘                  │ │  │
│  │  │       └──────────┬───────┘                          │ │  │
│  │  │                  │                                   │ │  │
│  │  │         ┌────────▼────────┐                         │ │  │
│  │  │         │Evidence Generator│                         │ │  │
│  │  │         └────────┬────────┘                         │ │  │
│  │  └──────────────────┼──────────────────────────────────┘ │  │
│  │                     │                                     │  │
│  │  ┌──────────────────▼──────────────────────────────────┐ │  │
│  │  │           CASE 1: CRM Compliance (UC09)            │ │  │
│  │  │  (Tách biệt, chỉ đánh giá NTT - 10% điểm)          │ │  │
│  │  └─────────────────────────────────────────────────────┘ │  │
│  └───────────────────────────────────────────────────────────┘  │
└───────────────────────────────────────────────────────────────────┘
                             │
┌────────────────────────────┴─────────────────────────────────────┐
│                        DATA LAYER                                 │
│                                                                   │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │  PostgreSQL  │  │    Redis     │  │      S3      │          │
│  │   (Scores)   │  │   (Cache)    │  │   (Audio)    │          │
│  └──────────────┘  └──────────────┘  └──────────────┘          │
│                                                                   │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │Elasticsearch │  │   RabbitMQ   │  │  Prometheus  │          │
│  │  (Logging)   │  │   (Queue)    │  │  (Metrics)   │          │
│  └──────────────┘  └──────────────┘  └──────────────┘          │
└───────────────────────────────────────────────────────────────────┘
```

### 3.2. Component Responsibilities (CASE 2)

| Component | Trách nhiệm | Input | Output | Technology |
|-----------|-------------|-------|--------|------------|
| **Ingestion Service** | Nhận audio + metadata, validate | Call data + audio URL | Job ID queued | FastAPI |
| **STT + Diarization** | Speech-to-text + phân người nói | Audio file | Transcript + segments | Whisper/Google STT |
| **Call Type Detector** | Phát hiện BH/CSKH từ audio | Transcript (60s đầu) | call_type + confidence | Python + ML |
| **Feature Extractor** | Trích xuất signals | Transcript + audio | wpm, pause_ratio, interrupts... | Python + VAD |
| **KNGT Evaluator** | Đánh giá kỹ năng giao tiếp | Features + transcript | Violations + scores | Python + Rules |
| **KNBH Evaluator** | Đánh giá kỹ năng bán hàng/dịch vụ | Features + transcript | Violations + scores | Python + Rules |
| **Score Calculator** | Tính điểm tổng theo weights | Violations + call_type | Total score + breakdown | Python |
| **Summary Generator** | Tạo tóm tắt 3-5 câu | Transcript + scores | Executive summary | Python + LLM |
| **Recommendation** | Gợi ý cải thiện | Violations | Actionable recommendations | Python + Templates |
| **Script Mapper** | Map kịch bản mẫu | Violations + call_type | Script IDs | Python + DB |
| **Evidence Generator** | Tạo bằng chứng | Violations + segments | Evidence với timestamps | Python |

---

## 4. COMPONENTS CHI TIẾT

### 4.1. Call Type Detector (Audio-only)

**Mục tiêu:** Phát hiện loại cuộc gọi (BH/CSKH) từ audio/transcript, KHÔNG dựa vào CRM

**Input:**
```python
{
    "transcript": [...],  # Ưu tiên 30-60s đầu
    "call_metadata": {
        "duration": 300.5,
        "agent_id": "AG001"
    }
}
```

**Signals:**

1. **Từ khóa/Chủ đề:**
   - BH: "gói bảo hiểm", "ưu đãi", "phí", "quyền lợi", "giá", "khuyến mãi"
   - CSKH: "lỗi", "không hoạt động", "khiếu nại", "hỗ trợ", "báo lỗi", "fix"

2. **Hành động hội thoại:**
   - BH: Giới thiệu sản phẩm, hỏi nhu cầu, so sánh gói
   - CSKH: Xác minh vấn đề, hướng dẫn khắc phục, tạo ticket

3. **Mẫu tương tác đầu cuộc gọi:**
   - BH: Agent chủ động chào hỏi, dẫn dắt
   - CSKH: Khách hàng mở đầu với vấn đề

4. **Sentiment pattern:**
   - BH: neutral → positive (thuyết phục)
   - CSKH: negative/frustrated → neutral/resolved

**Logic:**

```python
def detect_call_type(transcript: List[Dict]) -> Dict:
    """
    Detect call type from audio/transcript
    
    Returns:
        {
            "predicted": "BH" | "CSKH",
            "confidence": float [0-1],
            "signals": {...}
        }
    """
    # Lấy 60s đầu
    first_60s = [seg for seg in transcript if seg["end"] <= 60]
    
    # 1. Keywords scoring
    bh_keywords = ["gói", "bảo hiểm", "ưu đãi", "phí", "quyền lợi", "giá"]
    cskh_keywords = ["lỗi", "không hoạt động", "khiếu nại", "hỗ trợ", "fix"]
    
    bh_score = count_keywords(first_60s, bh_keywords)
    cskh_score = count_keywords(first_60s, cskh_keywords)
    
    # 2. Interaction pattern
    first_speaker = transcript[0]["speaker"]
    if first_speaker == "AGENT":
        pattern_score_bh = 0.3
    else:
        pattern_score_bh = -0.2
    
    # 3. Sentiment trend
    sentiment_trend = analyze_sentiment_trend(first_60s)
    if sentiment_trend == "neutral_to_positive":
        sentiment_score_bh = 0.2
    elif sentiment_trend == "negative_to_neutral":
        sentiment_score_bh = -0.3
    else:
        sentiment_score_bh = 0
    
    # 4. Calculate confidence
    total_score_bh = bh_score + pattern_score_bh + sentiment_score_bh
    total_score_cskh = cskh_score - pattern_score_bh - sentiment_score_bh
    
    # Normalize to probability
    exp_bh = np.exp(total_score_bh)
    exp_cskh = np.exp(total_score_cskh)
    prob_bh = exp_bh / (exp_bh + exp_cskh)
    
    predicted = "BH" if prob_bh > 0.5 else "CSKH"
    confidence = max(prob_bh, 1 - prob_bh)
    
    return {
        "predicted": predicted,
        "confidence": confidence,
        "signals": {
            "bh_keyword_count": bh_score,
            "cskh_keyword_count": cskh_score,
            "first_speaker": first_speaker,
            "sentiment_trend": sentiment_trend,
            "prob_bh": prob_bh
        }
    }
```

**Áp dụng weights:**

```python
TAU = 0.75  # Ngưỡng confidence

def apply_weights(call_type_detection: Dict) -> Dict:
    """
    Apply weights based on call type confidence
    """
    predicted = call_type_detection["predicted"]
    confidence = call_type_detection["confidence"]
    
    if confidence >= TAU:
        # High confidence → Dùng weight thuần
        if predicted == "BH":
            return {"KNGT": 0.4, "KNBH": 0.6}
        else:
            return {"KNGT": 0.7, "KNBH": 0.3}
    else:
        # Low confidence → Mixture-of-weights
        prob_bh = call_type_detection["signals"]["prob_bh"]
        prob_cskh = 1 - prob_bh
        
        weight_kngt = prob_bh * 0.4 + prob_cskh * 0.7
        weight_knbh = prob_bh * 0.6 + prob_cskh * 0.3
        
        return {
            "KNGT": weight_kngt,
            "KNBH": weight_knbh,
            "note": f"Mixture-of-weights applied (confidence={confidence:.2f})"
        }
```

---

### 4.2. KNGT Evaluator (Kỹ năng giao tiếp)

**7 Tiêu chí KNGT:**

| Code | Tiêu chí | BH Weight | CSKH Weight | Tín hiệu chính |
|------|----------|-----------|-------------|----------------|
| **GRT** | Chào hỏi & xưng danh | 0.05 | 0.08 | Pattern matching đầu cuộc gọi |
| **SR** | Tốc độ nói & rõ ràng | 0.08 | 0.10 | WPM + customer_repeat_count |
| **VOL** | Âm lượng & nhịp | 0.04 | 0.06 | Audio amplitude + pause_ratio |
| **LSN** | Lắng nghe, không ngắt lời | 0.06 | 0.08 | interrupt_count + turn-taking |
| **EMP** | Đồng cảm & thái độ | 0.05 | 0.08 | Sentiment + từ ngữ đồng cảm |
| **LAN** | Ngôn ngữ phù hợp | 0.05 | 0.05 | Negative words + formality |
| **CLS** | Kết thúc lịch sự | 0.07 | 0.07 | Pattern cuối cuộc gọi |

**Implementation:**

```python
class KNGTEvaluator:
    """
    Evaluate KNGT criteria
    """
    
    def evaluate(self, features: Dict, transcript: List[Dict]) -> Dict:
        """
        Main evaluation function
        """
        violations = []
        
        # 1. GRT - Chào hỏi & xưng danh
        grt_violation = self.evaluate_grt(transcript)
        if grt_violation:
            violations.append(grt_violation)
        
        # 2. SR - Tốc độ nói (QUAN TRỌNG - như đã thiết kế)
        sr_violation = self.evaluate_sr(features["speech_rate"])
        if sr_violation:
            violations.append(sr_violation)
        
        # 3. VOL - Âm lượng
        vol_violation = self.evaluate_vol(features["volume"])
        if vol_violation:
            violations.append(vol_violation)
        
        # 4. LSN - Lắng nghe
        lsn_violation = self.evaluate_lsn(features["interrupts"])
        if lsn_violation:
            violations.append(lsn_violation)
        
        # 5. EMP - Đồng cảm
        emp_violation = self.evaluate_emp(transcript, features["sentiment"])
        if emp_violation:
            violations.append(emp_violation)
        
        # 6. LAN - Ngôn ngữ
        lan_violation = self.evaluate_lan(transcript)
        if lan_violation:
            violations.append(lan_violation)
        
        # 7. CLS - Kết thúc
        cls_violation = self.evaluate_cls(transcript)
        if cls_violation:
            violations.append(cls_violation)
        
        return {
            "violations": violations,
            "criteria_count": 7,
            "violated_count": len(violations)
        }
    
    def evaluate_sr(self, speech_rate_data: Dict) -> Optional[Dict]:
        """
        Evaluate Speech Rate - Tốc độ nói
        
        Sử dụng logic đã thiết kế trong các file trước:
        - Segmentation theo speaker + pause
        - WPM calculation
        - Customer Impact ưu tiên cao
        - Absolute threshold (không dùng baseline)
        """
        from speech_rate_evaluation import evaluate_speech_rate_no_baseline
        
        result = evaluate_speech_rate_no_baseline(
            segments=speech_rate_data["segments"],
            call_type=speech_rate_data["call_type"],
            transcript_segments=speech_rate_data["transcript"]
        )
        
        if result["violation"]["violation_level"] == "OK":
            return None
        
        return {
            "code": "SR",
            "name": "Tốc độ nói & rõ ràng",
            "level": result["violation"]["violation_level"],
            "evidence": result["evidence"],
            "metrics": result["metrics"]
        }
```

---

### 4.3. KNBH Evaluator (BH) vs KNSV Evaluator (CSKH)

**KNBH (Bán hàng) - 7 tiêu chí:**

| Code | Tiêu chí | Weight | Tín hiệu |
|------|----------|--------|----------|
| **CIN** | Xác nhận thông tin | 0.05 | Pattern xác nhận |
| **LEAD** | Dẫn dắt cuộc gọi | 0.08 | Turn control |
| **NEED** | Khai thác nhu cầu | 0.10 | Open questions |
| **PRB** | Nắm bắt vấn đề | 0.07 | Problem identification |
| **ADV** | Tư vấn sản phẩm | 0.10 | Product mention quality |
| **OBJ** | Xử lý từ chối | 0.07 | Objection handling |
| **CLS2** | Chốt & CTA | 0.08 | Clear next steps |

**KNSV (CSKH) - 4 tiêu chí:**

| Code | Tiêu chí | Weight | Tín hiệu |
|------|----------|--------|----------|
| **ISS** | Xác nhận vấn đề | 0.10 | Problem verification |
| **DGN** | Chuẩn đoán nguyên nhân | 0.08 | Root cause analysis |
| **SOL** | Đưa giải pháp & hướng dẫn | 0.08 | Solution clarity |
| **FUP** | Xác nhận & follow-up | 0.04 | Follow-up commitment |

---

## 5. DATA FLOW & SEQUENCE

### 5.1. Sequence Diagram (Tuân thủ UC01)

```mermaid
sequenceDiagram
    autonumber
    participant PBX as PBX/Telephony
    participant API as QA Scoring API
    participant STT as Speech-to-Text
    participant CTD as Call Type Detector
    participant FX as Feature Extractor
    participant KNGT as KNGT Evaluator
    participant KNBH as KNBH Evaluator
    participant SC as Score Calculator
    participant SUM as Summary Generator
    participant REC as Recommender
    participant SCR as Script Mapper
    participant EVD as Evidence Generator
    participant DB as Database
    participant UI as Agent/QA UI
    
    PBX->>API: POST /score (audio_url, metadata)
    API->>STT: Send audio for transcription
    STT-->>API: Transcript + diarization (AGENT/CUSTOMER)
    
    API->>CTD: Detect call type (audio-only, 60s đầu)
    CTD-->>API: call_type_pred + confidence + signals
    
    API->>FX: Extract features (wpm, pause, interrupts...)
    FX-->>API: Features per segment
    
    par Evaluate KNGT
        API->>KNGT: Evaluate 7 criteria (SR, GRT, VOL...)
        KNGT-->>API: KNGT violations + scores
    and Evaluate KNBH/KNSV
        API->>KNBH: Evaluate criteria (NEED, ADV, CTA...)
        KNBH-->>API: KNBH violations + scores
    end
    
    API->>SC: Calculate total score (apply weights)
    SC-->>API: Total score + breakdown
    
    API->>SUM: Generate executive summary (3-5 sentences)
    SUM-->>API: Summary text + highlights
    
    API->>REC: Build recommendations (per violations)
    REC-->>API: Recommendations[]
    
    API->>SCR: Map suggested scripts
    SCR-->>API: ScriptIDs[]
    
    API->>EVD: Generate evidence (timestamps + quotes)
    EVD-->>API: Evidence[]
    
    API->>DB: Persist (score, summary, evidence, recs)
    DB-->>API: Ack with score_id
    
    API-->>UI: Return full report
```

### 5.2. Processing Pipeline (Celery)

```python
@app.task
def score_call_pipeline(job_id: str, call_data: Dict):
    """
    Main pipeline for CASE 2: Call Scoring
    
    Steps match UC01 sequence diagram
    """
    try:
        # Step 1: Download audio
        audio_path = download_audio(call_data["audio_url"])
        
        # Step 2: STT + Diarization
        transcript = stt_service.transcribe(audio_path, diarize=True)
        
        # Step 3: Call Type Detection (audio-only)
        call_type_detection = detect_call_type(transcript)
        
        # Step 4: Feature Extraction
        features = extract_features(audio_path, transcript)
        
        # Step 5: Apply Weights (based on confidence)
        weights = apply_weights(call_type_detection)
        
        # Step 6: Evaluate KNGT
        kngt_result = KNGTEvaluator().evaluate(features, transcript)
        
        # Step 7: Evaluate KNBH/KNSV
        if call_type_detection["predicted"] == "BH":
            knbh_result = KNBHEvaluator().evaluate(features, transcript)
        else:
            knbh_result = KNSVEvaluator().evaluate(features, transcript)
        
        # Step 8: Calculate Total Score
        score = ScoreCalculator().calculate(
            kngt_result,
            knbh_result,
            weights
        )
        
        # Step 9: Generate Summary
        summary = SummaryGenerator().generate(transcript, score)
        
        # Step 10: Build Recommendations
        recommendations = Recommender().build(
            kngt_result["violations"] + knbh_result["violations"]
        )
        
        # Step 11: Map Scripts
        scripts = ScriptMapper().map(
            call_type_detection["predicted"],
            kngt_result["violations"] + knbh_result["violations"]
        )
        
        # Step 12: Generate Evidence
        evidence = EvidenceGenerator().generate(
            kngt_result["violations"] + knbh_result["violations"],
            transcript
        )
        
        # Step 13: Save Results
        save_results(job_id, {
            "call_type_detection": call_type_detection,
            "score": score,
            "summary": summary,
            "recommendations": recommendations,
            "scripts": scripts,
            "evidence": evidence
        })
        
        return {"status": "success", "score_id": score["id"]}
        
    except Exception as e:
        handle_error(job_id, e)
        return {"status": "failed", "error": str(e)}
```

---

## 6. DATABASE SCHEMA

### 6.1. Core Tables

#### Table: `calls`
```sql
CREATE TABLE calls (
    call_id VARCHAR(50) PRIMARY KEY,
    agent_id VARCHAR(50) NOT NULL,
    call_time TIMESTAMP NOT NULL,
    audio_url TEXT NOT NULL,
    duration FLOAT NOT NULL,
    
    -- Call Type Detection
    call_type_predicted VARCHAR(10) CHECK (call_type_predicted IN ('BH', 'CSKH')),
    call_type_confidence FLOAT CHECK (call_type_confidence BETWEEN 0 AND 1),
    call_type_signals JSONB,
    
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    
    INDEX idx_agent_id (agent_id),
    INDEX idx_call_time (call_time),
    INDEX idx_call_type (call_type_predicted)
);
```

#### Table: `call_scores`
```sql
CREATE TABLE call_scores (
    id SERIAL PRIMARY KEY,
    call_id VARCHAR(50) NOT NULL REFERENCES calls(call_id),
    job_id VARCHAR(50) UNIQUE NOT NULL,
    
    -- Scores
    total_score FLOAT NOT NULL CHECK (total_score BETWEEN 0 AND 10),
    label VARCHAR(20) NOT NULL CHECK (label IN ('Yếu', 'Trung bình', 'Khá', 'Tốt', 'Xuất sắc')),
    passed BOOLEAN NOT NULL,
    
    -- Weights used
    weight_kngt FLOAT NOT NULL,
    weight_knbh FLOAT NOT NULL,
    weights_method VARCHAR(50),  -- 'pure' | 'mixture'
    
    -- Group scores
    kngt_points FLOAT NOT NULL,
    kngt_max_points FLOAT NOT NULL,
    kngt_percentage FLOAT,
    
    knbh_points FLOAT NOT NULL,
    knbh_max_points FLOAT NOT NULL,
    knbh_percentage FLOAT,
    
    -- Summary
    summary_text TEXT NOT NULL,
    highlights JSONB,
    
    -- Processing metadata
    processing_time_ms INT,
    stt_duration_ms INT,
    evaluation_method VARCHAR(50),
    
    created_at TIMESTAMP DEFAULT NOW(),
    
    INDEX idx_call_id (call_id),
    INDEX idx_total_score (total_score),
    INDEX idx_label (label),
    INDEX idx_created_at (created_at)
);
```

#### Table: `criterion_evaluations`
```sql
CREATE TABLE criterion_evaluations (
    id SERIAL PRIMARY KEY,
    score_id INT NOT NULL REFERENCES call_scores(id),
    
    group_name VARCHAR(10) NOT NULL CHECK (group_name IN ('KNGT', 'KNBH', 'KNSV')),
    criterion_code VARCHAR(10) NOT NULL,  -- GRT, SR, NEED, ADV...
    criterion_name VARCHAR(100) NOT NULL,
    
    weight FLOAT NOT NULL,
    max_points FLOAT NOT NULL,
    earned_points FLOAT NOT NULL,
    
    violation_level VARCHAR(5) CHECK (violation_level IN ('OK', 'M1', 'M2', 'M3')),
    evidence JSONB,
    
    created_at TIMESTAMP DEFAULT NOW(),
    
    INDEX idx_score_id (score_id),
    INDEX idx_criterion_code (criterion_code),
    INDEX idx_violation_level (violation_level)
);
```

#### Table: `recommendations`
```sql
CREATE TABLE recommendations (
    id SERIAL PRIMARY KEY,
    score_id INT NOT NULL REFERENCES call_scores(id),
    
    priority VARCHAR(10) NOT NULL CHECK (priority IN ('low', 'medium', 'high')),
    category VARCHAR(10) NOT NULL,  -- KNGT | KNBH
    criterion VARCHAR(10) NOT NULL,
    
    message TEXT NOT NULL,
    actionable BOOLEAN DEFAULT true,
    
    created_at TIMESTAMP DEFAULT NOW(),
    
    INDEX idx_score_id (score_id),
    INDEX idx_priority (priority)
);
```

#### Table: `suggested_scripts`
```sql
CREATE TABLE suggested_scripts (
    id SERIAL PRIMARY KEY,
    score_id INT NOT NULL REFERENCES call_scores(id),
    
    script_id VARCHAR(50) NOT NULL,
    stage VARCHAR(50),
    text TEXT NOT NULL,
    when_to_use TEXT,
    
    INDEX idx_score_id (score_id),
    INDEX idx_script_id (script_id)
);
```

#### Table: `evidence`
```sql
CREATE TABLE evidence (
    id SERIAL PRIMARY KEY,
    score_id INT NOT NULL REFERENCES call_scores(id),
    criterion_code VARCHAR(10),
    
    evidence_type VARCHAR(30) NOT NULL,  -- metric_violation | criterion_violation | customer_impact
    
    timestamp_start FLOAT,
    timestamp_end FLOAT,
    text TEXT,
    
    -- For metric_violation (e.g., SR)
    wpm FLOAT,
    threshold VARCHAR(50),
    
    -- For criterion_violation
    reason TEXT,
    expected_behavior TEXT,
    
    severity VARCHAR(10) CHECK (severity IN ('low', 'medium', 'high')),
    customer_impact BOOLEAN DEFAULT false,
    
    created_at TIMESTAMP DEFAULT NOW(),
    
    INDEX idx_score_id (score_id),
    INDEX idx_criterion_code (criterion_code),
    INDEX idx_evidence_type (evidence_type)
);
```

### 6.2. Views for Reporting

```sql
-- View: Agent performance summary
CREATE VIEW agent_performance_summary AS
SELECT 
    c.agent_id,
    COUNT(*) as total_calls,
    AVG(cs.total_score) as avg_score,
    SUM(CASE WHEN cs.passed THEN 1 ELSE 0 END) as passed_count,
    SUM(CASE WHEN cs.label = 'Xuất sắc' THEN 1 ELSE 0 END) as excellent_count,
    AVG(cs.kngt_percentage) as avg_kngt_percentage,
    AVG(cs.knbh_percentage) as avg_knbh_percentage
FROM calls c
JOIN call_scores cs ON c.call_id = cs.call_id
WHERE c.created_at >= NOW() - INTERVAL '30 days'
GROUP BY c.agent_id;

-- View: Common violations by criterion
CREATE VIEW common_violations AS
SELECT 
    ce.criterion_code,
    ce.criterion_name,
    ce.group_name,
    ce.violation_level,
    COUNT(*) as violation_count,
    AVG(ce.earned_points / ce.max_points) as avg_score_ratio
FROM criterion_evaluations ce
WHERE ce.violation_level IN ('M1', 'M2', 'M3')
  AND created_at >= NOW() - INTERVAL '30 days'
GROUP BY ce.criterion_code, ce.criterion_name, ce.group_name, ce.violation_level
ORDER BY violation_count DESC;
```

---

## 7. API DESIGN

### 7.1. Main Endpoints

#### POST `/api/v1/calls/score`
**Description:** Submit a call for scoring (CASE 2)

**Request:**
```json
{
  "call_id": "CALL-2025-001",
  "agent_id": "AG001",
  "call_time": "2025-10-10T10:30:00Z",
  "audio_url": "s3://calls/CALL-2025-001.wav",
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

#### GET `/api/v1/calls/{call_id}/score`
**Description:** Get call scoring result

**Response (200 OK):**
```json
{
  "call_id": "CALL-2025-001",
  "call_type_detection": {...},
  "score": {...},
  "summary": {...},
  "recommendations": [...],
  "suggested_scripts": [...],
  "evidence": [...],
  "metadata": {...}
}
```

---

#### GET `/api/v1/agents/{agent_id}/performance`
**Description:** Get agent performance summary

**Query Parameters:**
- `start_date` (required)
- `end_date` (required)
- `call_type` (optional: BH | CSKH)

**Response (200 OK):**
```json
{
  "agent_id": "AG001",
  "period": {
    "start": "2025-09-01",
    "end": "2025-10-01"
  },
  "summary": {
    "total_calls": 150,
    "avg_score": 7.8,
    "passed_rate": 0.92,
    "label_distribution": {
      "Xuất sắc": 20,
      "Tốt": 70,
      "Khá": 40,
      "Trung bình": 15,
      "Yếu": 5
    }
  },
  "kngt_avg": 7.5,
  "knbh_avg": 8.0,
  "common_violations": [
    {
      "criterion": "SR",
      "count": 25,
      "avg_level": "M1"
    },
    {
      "criterion": "NEED",
      "count": 18,
      "avg_level": "M2"
    }
  ],
  "trend": "improving"
}
```

---

## 8. CALL TYPE DETECTION (AUDIO-ONLY)

### 8.1. Detailed Implementation

**File:** `services/call_type_detector.py`

```python
import re
from typing import Dict, List
import numpy as np

class CallTypeDetector:
    """
    Detect call type (BH/CSKH) from audio/transcript only
    
    No CRM data required - pure audio-based detection
    """
    
    # Keywords dictionary
    BH_KEYWORDS = [
        "gói", "bảo hiểm", "ưu đãi", "khuyến mãi", "giá", "phí",
        "quyền lợi", "sản phẩm", "dịch vụ", "mua", "đăng ký",
        "chiết khấu", "thanh toán", "hợp đồng", "cam kết"
    ]
    
    CSKH_KEYWORDS = [
        "lỗi", "không hoạt động", "khiếu nại", "hỗ trợ", "báo lỗi",
        "fix", "sửa", "khắc phục", "vấn đề", "trục trặc",
        "không dùng được", "bị lỗi", "không thể", "help", "giúp"
    ]
    
    def detect(self, transcript: List[Dict], audio_features: Dict = None) -> Dict:
        """
        Main detection method
        
        Args:
            transcript: Full transcript with diarization
            audio_features: Optional audio features (sentiment, etc.)
        
        Returns:
            {
                "predicted": "BH" | "CSKH",
                "confidence": float,
                "signals": {...}
            }
        """
        # Focus on first 60 seconds
        first_60s = self._get_first_n_seconds(transcript, 60)
        
        # 1. Keyword analysis
        keyword_signal = self._analyze_keywords(first_60s)
        
        # 2. Interaction pattern
        pattern_signal = self._analyze_interaction_pattern(transcript[:5])
        
        # 3. Sentiment trend
        sentiment_signal = self._analyze_sentiment(first_60s, audio_features)
        
        # 4. Agent action analysis
        action_signal = self._analyze_agent_actions(first_60s)
        
        # Combine signals
        prob_bh = self._combine_signals(
            keyword_signal,
            pattern_signal,
            sentiment_signal,
            action_signal
        )
        
        predicted = "BH" if prob_bh > 0.5 else "CSKH"
        confidence = max(prob_bh, 1 - prob_bh)
        
        return {
            "predicted": predicted,
            "confidence": confidence,
            "signals": {
                "keyword": keyword_signal,
                "pattern": pattern_signal,
                "sentiment": sentiment_signal,
                "action": action_signal,
                "prob_bh": prob_bh
            },
            "method": "audio_only"
        }
    
    def _get_first_n_seconds(self, transcript: List[Dict], n: int) -> List[Dict]:
        """Get segments in first N seconds"""
        return [seg for seg in transcript if seg["end"] <= n]
    
    def _analyze_keywords(self, segments: List[Dict]) -> Dict:
        """Analyze keywords to determine call type"""
        text_combined = " ".join([seg["text"].lower() for seg in segments])
        
        bh_count = sum(1 for kw in self.BH_KEYWORDS if kw in text_combined)
        cskh_count = sum(1 for kw in self.CSKH_KEYWORDS if kw in text_combined)
        
        total = bh_count + cskh_count
        if total == 0:
            score = 0.5  # Neutral
        else:
            score = bh_count / total
        
        return {
            "bh_keyword_count": bh_count,
            "cskh_keyword_count": cskh_count,
            "score_bh": score,
            "weight": 0.4
        }
    
    def _analyze_interaction_pattern(self, first_segments: List[Dict]) -> Dict:
        """
        Analyze who speaks first and interaction flow
        
        BH: Agent typically leads (proactive)
        CSKH: Customer typically opens with problem
        """
        if not first_segments:
            return {"score_bh": 0.5, "weight": 0.2}
        
        first_speaker = first_segments[0]["speaker"]
        
        # Count agent vs customer turns in first 3 exchanges
        agent_turns = sum(1 for s in first_segments[:3] if s["speaker"] == "AGENT")
        customer_turns = sum(1 for s in first_segments[:3] if s["speaker"] == "CUSTOMER")
        
        # BH: Agent leads, more agent turns
        # CSKH: Customer often leads with complaint
        if first_speaker == "AGENT" and agent_turns >= customer_turns:
            score = 0.7  # Likely BH
        elif first_speaker == "CUSTOMER" and customer_turns > agent_turns:
            score = 0.3  # Likely CSKH
        else:
            score = 0.5
        
        return {
            "first_speaker": first_speaker,
            "agent_turns": agent_turns,
            "customer_turns": customer_turns,
            "score_bh": score,
            "weight": 0.2
        }
    
    def _analyze_sentiment(self, segments: List[Dict], audio_features: Dict = None) -> Dict:
        """
        Analyze sentiment trend
        
        BH: neutral → positive (persuasion)
        CSKH: negative/frustrated → neutral/resolved
        """
        if audio_features and "sentiment_trend" in audio_features:
            trend = audio_features["sentiment_trend"]
        else:
            # Simple heuristic based on text
            first_half = segments[:len(segments)//2]
            second_half = segments[len(segments)//2:]
            
            first_sentiment = self._simple_sentiment(first_half)
            second_sentiment = self._simple_sentiment(second_half)
            
            if first_sentiment < 0 and second_sentiment > first_sentiment:
                trend = "negative_to_neutral"  # Typical CSKH
            elif first_sentiment >= 0 and second_sentiment > first_sentiment:
                trend = "neutral_to_positive"  # Typical BH
            else:
                trend = "mixed"
        
        if trend == "neutral_to_positive":
            score = 0.7  # BH
        elif trend == "negative_to_neutral":
            score = 0.3  # CSKH
        else:
            score = 0.5
        
        return {
            "trend": trend,
            "score_bh": score,
            "weight": 0.2
        }
    
    def _analyze_agent_actions(self, segments: List[Dict]) -> Dict:
        """
        Analyze what agent is doing
        
        BH: Introducing products, asking about needs, offering deals
        CSKH: Diagnosing issues, providing solutions, creating tickets
        """
        agent_text = " ".join([
            seg["text"].lower() 
            for seg in segments 
            if seg["speaker"] == "AGENT"
        ])
        
        # BH actions
        bh_patterns = [
            r"(giới thiệu|tư vấn|sản phẩm|gói|quyền lợi)",
            r"(anh.*quan tâm|anh.*cần|anh.*muốn)",
            r"(ưu đãi|khuyến mãi|chiết khấu)"
        ]
        
        # CSKH actions
        cskh_patterns = [
            r"(vấn đề.*gì|lỗi.*gì|khiếu nại.*gì)",
            r"(em.*kiểm tra|em.*hỗ trợ|em.*fix)",
            r"(ticket|phiếu|ghi nhận)"
        ]
        
        bh_matches = sum(1 for p in bh_patterns if re.search(p, agent_text))
        cskh_matches = sum(1 for p in cskh_patterns if re.search(p, agent_text))
        
        total = bh_matches + cskh_matches
        if total == 0:
            score = 0.5
        else:
            score = bh_matches / total
        
        return {
            "bh_action_count": bh_matches,
            "cskh_action_count": cskh_matches,
            "score_bh": score,
            "weight": 0.2
        }
    
    def _combine_signals(
        self,
        keyword_signal: Dict,
        pattern_signal: Dict,
        sentiment_signal: Dict,
        action_signal: Dict
    ) -> float:
        """
        Combine all signals using weighted average
        """
        signals = [keyword_signal, pattern_signal, sentiment_signal, action_signal]
        
        weighted_sum = sum(s["score_bh"] * s["weight"] for s in signals)
        total_weight = sum(s["weight"] for s in signals)
        
        prob_bh = weighted_sum / total_weight
        
        return prob_bh
    
    def _simple_sentiment(self, segments: List[Dict]) -> float:
        """
        Simple sentiment analysis based on keywords
        Returns: -1 (negative) to 1 (positive)
        """
        text = " ".join([seg["text"].lower() for seg in segments])
        
        positive_words = ["tốt", "cảm ơn", "đồng ý", "ổn", "được", "vui"]
        negative_words = ["lỗi", "không", "khiếu nại", "tệ", "kém", "thất vọng"]
        
        pos_count = sum(1 for w in positive_words if w in text)
        neg_count = sum(1 for w in negative_words if w in text)
        
        total = pos_count + neg_count
        if total == 0:
            return 0.0
        
        return (pos_count - neg_count) / total
```

---

## 9. SPEECH RATE EVALUATION (SR - KNGT)

### 9.1. Integration với KNGT

**Speech Rate (SR)** là 1 trong 7 tiêu chí của KNGT, chiếm:
- **BH:** 0.08 × 4.0 = 0.32 điểm
- **CSKH:** 0.10 × 7.0 = 0.70 điểm

### 9.2. Implementation

**File:** `services/kngt/speech_rate_evaluator.py`

```python
from typing import Dict, List, Optional

class SpeechRateEvaluator:
    """
    Evaluate Speech Rate criterion (SR) in KNGT
    
    Sử dụng logic đã thiết kế trong:
    - 11_BOOTSTRAP_STRATEGY_NO_BASELINE.md
    - BAO_CAO_NGAT_KHONG_DUNG_BASELINE.md
    """
    
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
    
    def evaluate(
        self,
        segments: List[Dict],
        call_type: str,
        transcript: List[Dict]
    ) -> Optional[Dict]:
        """
        Evaluate speech rate
        
        Returns None if OK, otherwise returns violation dict
        """
        # Bước 1-8: Tính WPM cho từng segment (như thiết kế)
        wpm_segments = self._calculate_wpm_segments(segments)
        wpm_values = [s["wpm"] for s in wpm_segments]
        
        # Bước 9: Phát hiện Customer Impact
        customer_impacts = self._detect_customer_impact(transcript)
        
        # Bước 10: Đánh giá (KHÔNG CẦN BASELINE)
        violation = self._evaluate_cold_start(
            wpm_values,
            call_type,
            customer_impacts
        )
        
        if violation["violation_level"] == "OK":
            return None  # No violation
        
        # Bước 11: Tạo evidence
        evidence = self._generate_evidence(
            wpm_segments,
            customer_impacts,
            call_type
        )
        
        return {
            "code": "SR",
            "name": "Tốc độ nói & rõ ràng",
            "level": violation["violation_level"],
            "evidence": {
                "median_wpm": np.median(wpm_values),
                "p90_wpm": np.percentile(wpm_values, 90),
                "total_segments": len(wpm_values),
                "customer_impact_count": customer_impacts["repeat_requests"],
                "violated_segments": evidence["metric_violations"],
                "customer_complaints": evidence["customer_impacts"]
            },
            "recommendation": self._get_recommendation(
                violation["violation_level"],
                np.median(wpm_values),
                call_type
            )
        }
    
    def _calculate_wpm_segments(self, segments: List[Dict]) -> List[Dict]:
        """Calculate WPM for each segment"""
        # Implementation từ 11_BOOTSTRAP_STRATEGY_NO_BASELINE.md
        # ...
        pass
    
    def _detect_customer_impact(self, transcript: List[Dict]) -> Dict:
        """Detect customer complaints about speech rate"""
        # Implementation từ 11_BOOTSTRAP_STRATEGY_NO_BASELINE.md
        # ...
        pass
    
    def _evaluate_cold_start(
        self,
        wpm_values: List[float],
        call_type: str,
        customer_impacts: Dict
    ) -> Dict:
        """
        Evaluate using absolute thresholds (no baseline)
        
        Priority:
        1. Customer Impact (highest)
        2. Segment violation ratio
        """
        thresholds = self.THRESHOLDS[call_type]
        
        # Ưu tiên 1: Customer Impact
        repeat_count = customer_impacts["repeat_requests"]
        if repeat_count >= 3:
            return {
                "violation_level": "M2",
                "reason": f"KH yêu cầu nhắc lại {repeat_count} lần"
            }
        
        # Ưu tiên 2: Tỷ lệ segments vi phạm
        total = len(wpm_values)
        very_slow = sum(1 for w in wpm_values if w < thresholds["very_slow"])
        very_fast = sum(1 for w in wpm_values if w > thresholds["very_fast"])
        slow = sum(1 for w in wpm_values if thresholds["very_slow"] <= w < thresholds["slow"])
        fast = sum(1 for w in wpm_values if thresholds["fast"] < w <= thresholds["very_fast"])
        
        very_slow_ratio = very_slow / total
        very_fast_ratio = very_fast / total
        outlier_ratio = (slow + fast) / total
        
        # M3: Very severe
        if very_slow_ratio >= 0.20 or very_fast_ratio >= 0.20:
            return {
                "violation_level": "M3",
                "reason": f"20%+ segments quá nhanh/chậm"
            }
        
        # M2: Severe
        if very_slow_ratio >= 0.10 or very_fast_ratio >= 0.10:
            return {
                "violation_level": "M2",
                "reason": f"10%+ segments quá nhanh/chậm"
            }
        
        # M1: Minor
        if outlier_ratio >= 0.25 or repeat_count >= 2:
            return {
                "violation_level": "M1",
                "reason": f"25%+ segments hơi lệch"
            }
        
        return {"violation_level": "OK"}
    
    def _get_recommendation(
        self,
        level: str,
        median_wpm: float,
        call_type: str
    ) -> str:
        """Generate actionable recommendation"""
        thresholds = self.THRESHOLDS[call_type]
        
        if median_wpm > thresholds["fast"]:
            return (
                f"Giảm tốc độ xuống {thresholds['slow']}-{thresholds['fast']} wpm "
                f"khi trình bày thông tin quan trọng. Xen kẽ câu ngắn và kiểm tra "
                f"sự hiểu của KH bằng câu hỏi: 'Anh có thắc mắc điểm nào không ạ?'"
            )
        elif median_wpm < thresholds["slow"]:
            return (
                f"Tăng tốc độ lên {thresholds['slow']}-{thresholds['fast']} wpm "
                f"để duy trì năng lượng cuộc gọi. Tránh im lặng quá lâu giữa các câu."
            )
        else:
            return (
                f"Duy trì tốc độ ổn định trong khoảng "
                f"{thresholds['slow']}-{thresholds['fast']} wpm. "
                f"Điều chỉnh linh hoạt theo phản ứng của KH."
            )
```

---

## 10. CASE 1: CRM COMPLIANCE (Tham chiếu)

### 10.1. Scope & Integration

**CASE 1** (UC09) xử lý **NTT (Nhập thông tin)** - 10% điểm tổng:
- Kiểm tra Agent có cập nhật CRM/ticket đúng hạn
- Phát hiện vi phạm M1/M2/M3
- Gửi nhắc nhở và theo dõi khắc phục
- **KHÔNG** thuộc CASE 2, nhưng điểm NTT được cộng vào tổng

### 10.2. Integration Point

```python
def calculate_final_score_with_ntt(
    case2_score: Dict,  # KNGT + KNBH từ CASE 2
    ntt_score: Dict     # NTT từ CASE 1 (UC09)
) -> Dict:
    """
    Combine CASE 2 (KNGT+KNBH) with CASE 1 (NTT)
    
    Total = CASE2 (9.0) + NTT (1.0) = 10.0
    """
    # CASE 2: KNGT + KNBH = 90% điểm (9.0/10)
    kngt_points = case2_score["kngt_points"]
    knbh_points = case2_score["knbh_points"]
    case2_total = kngt_points + knbh_points  # Max 9.0
    
    # CASE 1: NTT = 10% điểm (1.0/10)
    ntt_points = ntt_score["points"]  # Max 1.0
    
    # Total
    total_score = case2_total + ntt_points
    
    return {
        "total_score": total_score,
        "breakdown": {
            "KNGT": kngt_points,
            "KNBH": knbh_points,
            "NTT": ntt_points
        },
        "label": get_label(total_score),
        "passed": total_score >= 5.0
    }
```

---

## 11. PERFORMANCE & SCALABILITY

### 11.1. Performance Targets (Tuân thủ UC01)

| Metric | Target | Measurement |
|--------|--------|-------------|
| **MAE điểm tổng** | ≤ 1.0 | vs QA thủ công trên 100 calls |
| **F1 phát hiện M2/M3** | ≥ 0.8 | Precision & Recall |
| **Latency sinh báo cáo** | ≤ 5s | Không tính STT |
| **STT duration** | ~30% audio length | 5 phút → ~90s |
| **Call Type accuracy** | ≥ 85% | Validation set |

### 11.2. Monitoring (Prometheus)

```python
# Business metrics
from prometheus_client import Counter, Histogram, Gauge

# Call Type Detection
calltype_detection_accuracy = Gauge(
    'calltype_detection_accuracy',
    'Call type detection accuracy'
)

calltype_confidence = Histogram(
    'calltype_confidence',
    'Call type confidence distribution'
)

# Scoring metrics
score_mae = Gauge(
    'score_mae',
    'Mean Absolute Error vs QA manual',
    ['call_type']
)

violation_f1 = Gauge(
    'violation_f1_score',
    'F1 score for M2/M3 detection',
    ['criterion']
)

# Performance metrics
scoring_latency = Histogram(
    'scoring_latency_seconds',
    'Time to generate score (excluding STT)',
    ['call_type']
)
```

---

## 12. DEPLOYMENT & OPERATIONS

### 12.1. Docker Compose (Development)

```yaml
version: '3.8'

services:
  # API Service
  api:
    build: ./services/api
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://user:pass@postgres:5432/qa_scoring
      - REDIS_URL=redis://redis:6379/0
      - RABBITMQ_URL=amqp://guest:guest@rabbitmq:5672/
    depends_on:
      - postgres
      - redis
      - rabbitmq
  
  # Celery Worker (CASE 2)
  worker-case2:
    build: ./services/worker
    command: celery -A tasks worker --loglevel=info --queues=case2
    environment:
      - DATABASE_URL=postgresql://user:pass@postgres:5432/qa_scoring
      - REDIS_URL=redis://redis:6379/0
      - RABBITMQ_URL=amqp://guest:guest@rabbitmq:5672/
    depends_on:
      - postgres
      - redis
      - rabbitmq
  
  # STT Service
  stt:
    build: ./services/stt
    ports:
      - "8001:8000"
    volumes:
      - ./models:/models
  
  # PostgreSQL
  postgres:
    image: postgres:14
    environment:
      POSTGRES_DB: qa_scoring
      POSTGRES_USER: user
      POSTGRES_PASSWORD: pass
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
  
  # Redis
  redis:
    image: redis:7
    ports:
      - "6379:6379"
  
  # RabbitMQ
  rabbitmq:
    image: rabbitmq:3.11-management
    ports:
      - "5672:5672"
      - "15672:15672"

volumes:
  postgres_data:
```

---

## PHỤ LỤC

### A. Tham chiếu tài liệu

Thiết kế này tuân thủ:
- ✅ `00_Master_Spec.md` - Master specification
- ✅ `UC01_Call_Scoring_SPEC.md` - Use case chi tiết
- ✅ `02_Sequence_UC01_Call_Scoring.md` - Sequence diagram
- ✅ `05_Scoring_Criteria_Decomposition.md` - Tiêu chí chấm điểm
- ✅ `11_BOOTSTRAP_STRATEGY_NO_BASELINE.md` - Speech Rate strategy
- ✅ `BAO_CAO_NGAT_KHONG_DUNG_BASELINE.md` - Speech Rate implementation

### B. Glossary

- **KNGT:** Kỹ năng giao tiếp (Communication Skills)
- **KNBH:** Kỹ năng bán hàng (Sales Skills)
- **KNSV:** Kỹ năng dịch vụ (Service Skills) - CSKH variant
- **NTT:** Nhập thông tin (CRM Data Entry)
- **CTA:** Call-to-Action
- **BH:** Bán hàng (Sales)
- **CSKH:** Chăm sóc khách hàng (Customer Service)
- **τ (tau):** Ngưỡng confidence cho call type (0.75)

---

**Document Version:** 2.0  
**Last Updated:** 10/10/2025  
**Status:** Draft - Ready for Review