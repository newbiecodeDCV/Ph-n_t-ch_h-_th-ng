# Hướng dẫn Đầy đủ: Đánh giá Tốc độ Nói (Speech Rate Evaluation)

**Phiên bản:** v1.0 - Tổng hợp từ tài liệu chuẩn  
**Mục đích:** Tóm tắt hoàn chỉnh quy trình đánh giá tốc độ nói nhanh/chậm của Agent trong hệ thống AI QA Call

---

## 📋 Tổng quan

### Vị trí trong hệ thống chấm điểm

```
Tiêu chí: A.2 - Kỹ năng nói (10% điểm KNGT)
├─ A.2.1 Tốc độ nói (1/3 của 10% KNGT)
├─ A.2.2 Âm lượng (1/3 của 10% KNGT)
└─ A.2.3 Độ rõ phát âm (1/3 của 10% KNGT)

Điểm quy đổi:
- BH: 10% × 2.0 (KNGT) × 1/3 = 0.067 điểm
- CSKH: 10% × 4.0 (KNGT) × 1/3 = 0.133 điểm
```

### Mức độ ảnh hưởng

| Mức lỗi | Trừ điểm | Ví dụ |
|---------|----------|-------|
| **M1** | Đúng điểm tiêu chí con | Agent nói hơi nhanh/chậm nhưng KH vẫn theo kịp |
| **M2** | Trừ 50% điểm NHÓM KNGT | KH yêu cầu nhắc lại ≥3 lần do nói quá nhanh/chậm |
| **M3** | Điểm NHÓM KNGT = 0 | Gây hiểu sai nội dung quan trọng (OTP, điều khoản) |

---

## 🎯 Pipeline Đầy đủ (10 Bước)

### Bước 1: Chuẩn bị Input

**Input cần có:**
```
✓ Audio file (mono, 16kHz)
✓ Call metadata (call_id, agent_id, call_time, team)
```

**Tools:**
- STT: Whisper / Google Cloud STT / Azure Speech
- Diarization: pyannote.audio / AWS Transcribe
- VAD: webrtcvad / silero-vad

**Output Bước 1:**
```json
{
  "audio_path": "call_12345.wav",
  "call_id": "12345",
  "agent_id": "AGENT_001",
  "team": "Sales_BH",
  "duration_total": 300.0
}
```

**Thời gian:** Chuẩn bị tức thì

---

### Bước 2: Speech-to-Text (STT)

**Mục đích:** Chuyển audio → text với timestamps

**Input:** Audio file  
**Process:**
```python
import whisper

model = whisper.load_model("large-v2")
result = model.transcribe(
    "call_12345.wav",
    language="vi",
    word_timestamps=True  # ← QUAN TRỌNG!
)
```

**Output:**
```json
{
  "text": "Em xin chào anh ạ...",
  "segments": [...],
  "words": [
    {"word": "Em", "start": 0.0, "end": 0.2},
    {"word": "xin", "start": 0.2, "end": 0.4},
    ...
  ]
}
```

**Thời gian:** 2-5 giây cho 5 phút audio

---

### Bước 3: Diarization (Phân người nói)

**Mục đích:** Tách AGENT vs CUSTOMER

**Input:** Audio + Transcript  
**Process:**
```python
from pyannote.audio import Pipeline

pipeline = Pipeline.from_pretrained("pyannote/speaker-diarization")
diarization = pipeline("call_12345.wav", num_speakers=2)

# Gắn nhãn AGENT/CUSTOMER
labeled_segments = label_speakers(diarization, transcript)
```

**Output:**
```json
[
  {
    "speaker": "AGENT",
    "start": 0.0,
    "end": 8.5,
    "text": "Em xin chào anh ạ, em là Hoa",
    "words": [...]
  },
  {
    "speaker": "CUSTOMER",
    "start": 9.0,
    "end": 11.2,
    "text": "Chào em"
  },
  ...
]
```

**Thời gian:** 1-3 giây

---

### Bước 4: VAD (Voice Activity Detection)

**Mục đích:** Phát hiện đâu là nói (voiced), đâu là im lặng (silence)

**Input:** Audio file  
**Process:**
```python
import webrtcvad
import numpy as np

vad = webrtcvad.Vad(2)  # aggressiveness level 2
vad_array = compute_vad(audio_data, sample_rate=16000, frame_ms=10)

# Output: array nhị phân
# vad_array = [1, 1, 1, 0, 0, 1, 1, ...] @ 10ms resolution
#              ↑           ↑
#           voiced     silence
```

**Output:**
```python
# Numpy array, mỗi phần tử = 10ms
vad_array = np.array([1, 1, 1, ..., 0, 0, ..., 1, 1, 1])
# Shape: (30000,) cho audio 5 phút (300s / 0.01s = 30000 frames)
```

**Thời gian:** 0.5-1 giây ← **RẤT NHANH, KHÔNG GÂY TRỄ!**

---

### Bước 5: Chia Segments theo Speaker

**Mục đích:** Tách riêng từng lượt nói của AGENT

**Input:** Diarization output  
**Process:** Lọc lấy `speaker == "AGENT"`

**Output:**
```json
[
  {
    "segment_id": "S1",
    "speaker": "AGENT",
    "start": 0.0,
    "end": 8.5,
    "duration": 8.5,
    "text": "Em xin chào anh ạ...",
    "words": [...]
  },
  {
    "segment_id": "S3",
    "speaker": "AGENT",
    "start": 12.0,
    "end": 45.8,  ← Segment dài! (33.8s)
    "duration": 33.8,
    "text": "Em là Hoa từ công ty ABC...",
    "words": [...]
  },
  ...
]
```

**Thời gian:** <0.1 giây

---

### Bước 6: Chia Segments Dài theo Pause

**Mục đích:** Chia segment >15s thành các sub-segments nhỏ hơn

**Quy tắc:**
```
IF segment.duration > 15s:
    - Tìm pause dài ≥700ms trong segment
    - Chia tại các pause
    - Tạo sub-segments
ELSE:
    - Giữ nguyên
```

#### 6.1. Tìm Pause

**Input:** VAD array + segment boundaries  
**Process:**
```python
def find_pauses(start_sec, end_sec, vad_array, threshold_ms=700):
    """
    Tìm các đoạn im lặng ≥700ms
    
    Returns:
        [(pause_start, pause_end), ...]
    """
    frame_duration = 0.01  # 10ms
    threshold_sec = threshold_ms / 1000.0
    
    # Lấy phần VAD tương ứng segment
    start_frame = int(start_sec / frame_duration)
    end_frame = int(end_sec / frame_duration)
    vad_segment = vad_array[start_frame:end_frame]
    
    pauses = []
    in_pause = False
    pause_start_frame = 0
    
    for i, is_voiced in enumerate(vad_segment):
        if is_voiced == 0:  # Silence
            if not in_pause:
                in_pause = True
                pause_start_frame = i
        else:  # Voiced
            if in_pause:
                pause_duration = (i - pause_start_frame) * frame_duration
                if pause_duration >= threshold_sec:
                    pause_start = start_sec + pause_start_frame * frame_duration
                    pause_end = start_sec + i * frame_duration
                    pauses.append((pause_start, pause_end))
                in_pause = False
    
    return pauses

# Ví dụ
pauses = find_pauses(12.0, 45.8, vad_array, threshold_ms=700)
# Output: [(18.5, 19.2), (28.7, 30.1)]
```

#### 6.2. Chia Segment

**Input:** Segment + pause positions  
**Process:**

**Cách 1: Chia text theo tỷ lệ thời gian** (Đơn giản, 85-90% accuracy)
```python
def split_text_by_duration_ratio(segment, pauses):
    """
    Chia text theo tỷ lệ thời lượng
    """
    words = segment["text"].split()
    total_duration = segment["duration"]
    
    sub_segments = []
    current_start = segment["start"]
    words_used = 0
    
    for pause_start, pause_end in pauses:
        sub_duration = pause_start - current_start
        ratio = sub_duration / total_duration
        word_count = round(len(words) * ratio)
        
        sub_text = " ".join(words[words_used:words_used + word_count])
        
        sub_seg = {
            "segment_id": f"{segment['segment_id']}_split",
            "speaker": "AGENT",
            "start": current_start,
            "end": pause_start,
            "duration": sub_duration,
            "text": sub_text,
            "word_count": word_count
        }
        sub_segments.append(sub_seg)
        
        current_start = pause_end
        words_used += word_count
    
    # Sub-segment cuối cùng
    final_seg = {
        "segment_id": f"{segment['segment_id']}_split",
        "speaker": "AGENT",
        "start": current_start,
        "end": segment["end"],
        "duration": segment["end"] - current_start,
        "text": " ".join(words[words_used:]),
        "word_count": len(words) - words_used
    }
    sub_segments.append(final_seg)
    
    return sub_segments
```

**Cách 2: Chia text theo word timestamps** (Chính xác 100%)
```python
def split_text_by_word_timestamps(words_with_timestamps, pause_positions):
    """
    Chia text dựa trên timestamps từng từ
    """
    sub_segments = []
    current_words = []
    current_start = words_with_timestamps[0]["start"]
    pause_idx = 0
    
    for word_obj in words_with_timestamps:
        word_end = word_obj["end"]
        
        # Kiểm tra vượt pause?
        if pause_idx < len(pause_positions) and word_end >= pause_positions[pause_idx]:
            # Kết thúc sub-segment hiện tại
            sub_seg = {
                "start": current_start,
                "end": pause_positions[pause_idx],
                "text": " ".join(current_words),
                "word_count": len(current_words)
            }
            sub_segments.append(sub_seg)
            
            # Bắt đầu sub-segment mới
            current_words = [word_obj["word"]]
            current_start = word_obj["start"]
            pause_idx += 1
        else:
            current_words.append(word_obj["word"])
    
    # Sub-segment cuối
    if current_words:
        sub_seg = {
            "start": current_start,
            "end": words_with_timestamps[-1]["end"],
            "text": " ".join(current_words),
            "word_count": len(current_words)
        }
        sub_segments.append(sub_seg)
    
    return sub_segments
```

**Output:**
```json
[
  {
    "segment_id": "S3_split_1",
    "speaker": "AGENT",
    "start": 12.0,
    "end": 18.5,
    "duration": 6.5,
    "text": "Em là Hoa từ công ty ABC",
    "word_count": 7
  },
  {
    "segment_id": "S3_split_2",
    "speaker": "AGENT",
    "start": 19.2,
    "end": 28.7,
    "duration": 9.5,
    "text": "Hiện tại công ty em đang có chương trình...",
    "word_count": 15
  },
  {
    "segment_id": "S3_split_3",
    "speaker": "AGENT",
    "start": 30.1,
    "end": 45.8,
    "duration": 15.7,
    "text": "Anh có quan tâm đến sản phẩm bảo hiểm...",
    "word_count": 18
  }
]
```

**Thời gian:** 0.1 giây

---

### Bước 7: Tính Voiced Duration cho từng Segment

**Mục đích:** Loại bỏ im lặng, chỉ giữ thời lượng phát âm thực tế

**Input:** Segments + VAD array  
**Process:**
```python
def calculate_voiced_duration(segment, vad_array):
    """
    Tính thời lượng phát âm thực tế (loại im lặng)
    """
    frame_duration = 0.01  # 10ms
    
    start_frame = int(segment["start"] / frame_duration)
    end_frame = int(segment["end"] / frame_duration)
    vad_segment = vad_array[start_frame:end_frame]
    
    voiced_frames = np.sum(vad_segment == 1)
    voiced_duration = voiced_frames * frame_duration
    
    return voiced_duration

# Áp dụng cho tất cả segments
for seg in segments:
    seg["voiced_duration"] = calculate_voiced_duration(seg, vad_array)
```

**Output:**
```json
{
  "segment_id": "S3_split_1",
  "duration": 6.5,
  "voiced_duration": 6.1,  ← Loại bỏ 0.4s im lặng
  "text": "Em là Hoa từ công ty ABC",
  "word_count": 7
}
```

**Thời gian:** 0.1 giây

---

### Bước 8: Tính Articulation Rate (WPM) cho từng Segment

**Công thức:**
```
wpm_segment = 60 × word_count / voiced_duration_seconds
```

**Lý do dùng Articulation Rate (không phải Speaking Rate):**
- ✅ Công bằng với Agent dừng hợp lý
- ✅ Tách biệt "tốc độ phát âm" vs "quản lý nhịp cuộc gọi"
- ✅ Ổn định hơn giữa các cuộc gọi

**Process:**
```python
def calculate_wpm_for_segments(segments):
    """
    Tính WPM cho mỗi segment của AGENT
    """
    wpm_results = []
    
    for seg in segments:
        if seg["speaker"] != "AGENT":
            continue
        
        if seg["voiced_duration"] < 1.0:  # Quá ngắn, bỏ qua
            continue
        
        wpm = 60.0 * seg["word_count"] / seg["voiced_duration"]
        
        wpm_results.append({
            "segment_id": seg["segment_id"],
            "start": seg["start"],
            "end": seg["end"],
            "duration": seg["duration"],
            "voiced_duration": seg["voiced_duration"],
            "word_count": seg["word_count"],
            "wpm": wpm,
            "text_preview": seg["text"][:50]
        })
    
    return wpm_results

# Ví dụ
wpm_results = calculate_wpm_for_segments(segments)
```

**Output:**
```json
[
  {
    "segment_id": "S1",
    "start": 0.0,
    "end": 8.5,
    "duration": 8.5,
    "voiced_duration": 8.1,
    "word_count": 12,
    "wpm": 88.9,  ← 60 × 12 / 8.1
    "text_preview": "Em xin chào anh ạ, em là Hoa đây ạ"
  },
  {
    "segment_id": "S3_split_1",
    "start": 12.0,
    "end": 18.5,
    "duration": 6.5,
    "voiced_duration": 6.1,
    "word_count": 7,
    "wpm": 68.9,  ← Chậm
    "text_preview": "Em là Hoa từ công ty ABC"
  },
  {
    "segment_id": "S3_split_2",
    "start": 19.2,
    "end": 28.7,
    "duration": 9.5,
    "voiced_duration": 9.2,
    "word_count": 15,
    "wpm": 97.8,  ← Bình thường
    "text_preview": "Hiện tại công ty em đang có chương trình..."
  },
  {
    "segment_id": "S5",
    "start": 50.0,
    "end": 65.3,
    "duration": 15.3,
    "voiced_duration": 14.8,
    "word_count": 48,
    "wpm": 194.6,  ← RẤT NHANH! Vượt ngưỡng
    "text_preview": "Anh quan tâm sản phẩm bảo hiểm nhân thọ không..."
  }
]
```

**Thời gian:** 0.2 giây

---

### Bước 9: Tổng hợp Metrics và So sánh Baseline

**Mục đích:** Tính các chỉ số thống kê và so với baseline team

#### 9.1. Tính Metrics Tổng hợp

```python
def aggregate_metrics(wpm_results):
    """
    Tính các chỉ số thống kê
    """
    wpm_values = [r["wpm"] for r in wpm_results]
    
    metrics = {
        "median_wpm": np.median(wpm_values),
        "mean_wpm": np.mean(wpm_values),
        "std_wpm": np.std(wpm_values),
        "p10_wpm": np.percentile(wpm_values, 10),
        "p90_wpm": np.percentile(wpm_values, 90),
        "min_wpm": np.min(wpm_values),
        "max_wpm": np.max(wpm_values),
        "total_segments": len(wpm_values)
    }
    
    return metrics

metrics = aggregate_metrics(wpm_results)
# Output: {
#   "median_wpm": 145.3,
#   "mean_wpm": 148.7,
#   "p90_wpm": 192.5,
#   ...
# }
```

#### 9.2. Load Baseline Team

**Baseline:** Tính từ các cuộc gọi "đạt chuẩn" (QA score ≥8.0) của cùng team

```python
def load_baseline(team_name, call_type):
    """
    Load baseline từ database
    
    Baseline được cập nhật định kỳ (tuần/tháng)
    """
    baseline = db.query("""
        SELECT 
            AVG(median_wpm) as base_wpm,
            STDDEV(median_wpm) as std_wpm,
            COUNT(*) as sample_count
        FROM call_metrics
        WHERE team = :team
          AND call_type = :call_type
          AND qa_score >= 8.0
          AND created_at >= NOW() - INTERVAL '90 days'
    """, team=team_name, call_type=call_type)
    
    return {
        "base_wpm": baseline["base_wpm"],
        "std_wpm": baseline["std_wpm"],
        "sample_count": baseline["sample_count"]
    }

# Ví dụ
baseline = load_baseline("Sales_BH", "BH")
# Output: {
#   "base_wpm": 150.0,
#   "std_wpm": 20.0,
#   "sample_count": 245
# }
```

#### 9.3. Tính Outlier Ratio

**Công thức:**
```
r_out(±kσ) = (số segments ngoài [base - k×σ, base + k×σ]) / tổng segments

k=1 → ±1σ (68% trường hợp bình thường)
k=2 → ±2σ (95%)
k=2.5 → ±2.5σ (99%)
```

**Process:**
```python
def calculate_outlier_ratio(wpm_results, baseline, k=1):
    """
    Tính tỷ lệ segments vượt ngưỡng ±k×σ
    """
    base = baseline["base_wpm"]
    std = baseline["std_wpm"]
    
    lower_bound = base - k * std
    upper_bound = base + k * std
    
    wpm_values = [r["wpm"] for r in wpm_results]
    
    outliers = []
    for i, wpm in enumerate(wpm_values):
        if wpm < lower_bound or wpm > upper_bound:
            outliers.append({
                "segment_id": wpm_results[i]["segment_id"],
                "wpm": wpm,
                "deviation": wpm - base,
                "direction": "too_fast" if wpm > upper_bound else "too_slow"
            })
    
    outlier_ratio = len(outliers) / len(wpm_values)
    
    return {
        "k": k,
        "lower_bound": lower_bound,
        "upper_bound": upper_bound,
        "outlier_ratio": outlier_ratio,
        "outlier_count": len(outliers),
        "total_segments": len(wpm_values),
        "outliers": outliers
    }

# Tính cho nhiều k
outlier_1sigma = calculate_outlier_ratio(wpm_results, baseline, k=1)
outlier_2sigma = calculate_outlier_ratio(wpm_results, baseline, k=2)
outlier_2_5sigma = calculate_outlier_ratio(wpm_results, baseline, k=2.5)
```

**Output:**
```json
{
  "k": 1,
  "lower_bound": 130.0,  // base - 1×std = 150 - 20
  "upper_bound": 170.0,  // base + 1×std = 150 + 20
  "outlier_ratio": 0.28,  // 28% segments ngoài khoảng
  "outlier_count": 7,
  "total_segments": 25,
  "outliers": [
    {
      "segment_id": "S2",
      "wpm": 68.9,
      "deviation": -81.1,
      "direction": "too_slow"
    },
    {
      "segment_id": "S5",
      "wpm": 194.6,
      "deviation": 44.6,
      "direction": "too_fast"  ← VI PHẠM!
    },
    ...
  ]
}
```

**Thời gian:** 0.2 giây

---

### Bước 10: Phát hiện Customer Impact

**Mục đích:** Phát hiện KH yêu cầu nhắc lại hoặc than phiền về tốc độ

**Process:**
```python
def detect_customer_impact(transcript_segments):
    """
    Tìm các tín hiệu KH phàn nàn về tốc độ
    """
    # Patterns để detect
    patterns = {
        "request_repeat": [
            r"(nói lại|nhắc lại|lặp lại|nói từ từ|nói chậm)",
            r"(em ơi|anh không nghe rõ|không hiểu)",
            r"(sao nói nhanh vậy|nhanh quá)"
        ],
        "confusion": [
            r"(cái gì|sao|hả|gì cơ|không rõ)",
            r"(em nói rõ hơn|rõ ràng hơn)"
        ]
    }
    
    customer_impacts = []
    customer_segments = [s for s in transcript_segments if s["speaker"] == "CUSTOMER"]
    
    for seg in customer_segments:
        text = seg["text"].lower()
        
        # Kiểm tra patterns
        for category, pattern_list in patterns.items():
            for pattern in pattern_list:
                if re.search(pattern, text):
                    customer_impacts.append({
                        "segment_id": seg["segment_id"],
                        "timestamp": seg["start"],
                        "text": seg["text"],
                        "category": category,
                        "pattern_matched": pattern
                    })
                    break
    
    return {
        "total_impacts": len(customer_impacts),
        "repeat_requests": len([c for c in customer_impacts if c["category"] == "request_repeat"]),
        "confusion_markers": len([c for c in customer_impacts if c["category"] == "confusion"]),
        "impacts": customer_impacts
    }

customer_impact = detect_customer_impact(transcript_segments)
```

**Output:**
```json
{
  "total_impacts": 3,
  "repeat_requests": 2,
  "confusion_markers": 1,
  "impacts": [
    {
      "segment_id": "C3",
      "timestamp": 55.2,
      "text": "Em ơi, em nói chậm lại được không?",
      "category": "request_repeat",
      "pattern_matched": "nói chậm"
    },
    {
      "segment_id": "C5",
      "timestamp": 67.8,
      "text": "Em lặp lại cái đó được không anh không nghe rõ",
      "category": "request_repeat",
      "pattern_matched": "lặp lại"
    },
    {
      "segment_id": "C7",
      "timestamp": 82.5,
      "text": "Cái gì cơ em?",
      "category": "confusion",
      "pattern_matched": "cái gì"
    }
  ]
}
```

**Thời gian:** 0.2 giây

---

### Bước 11: Context-Aware Gating

**Mục đích:** Không phạt khi có ngữ cảnh hợp lý

**Các trường hợp miễn trừ:**

```python
def detect_context_flags(segment, next_customer_segment=None):
    """
    Phát hiện các context cần miễn trừ
    """
    flags = {}
    text = segment["text"].lower()
    
    # 1. Đọc OTP/Mã xác nhận
    if re.search(r'\b\d{4,6}\b', text) and \
       any(kw in text for kw in ["otp", "mã xác nhận", "mã đơn"]):
        flags["reading_otp"] = True
    
    # 2. Đọc điều khoản/Chính sách
    if any(kw in text for kw in ["điều khoản", "quy định", "cam kết", "chính sách"]):
        if segment["word_count"] > 30:  # Đọc dài
            flags["reading_terms"] = True
    
    # 3. KH yêu cầu nói nhanh/chậm hơn
    if next_customer_segment:
        next_text = next_customer_segment["text"].lower()
        if any(phrase in next_text for phrase in 
               ["nói nhanh", "nhanh hơn", "chậm lại", "từ từ"]):
            flags["customer_requests_pace"] = True
    
    # 4. Tra cứu/Kiểm tra hệ thống
    if any(kw in text for kw in ["em kiểm tra", "cho em tra", "em xem giúp"]):
        flags["lookup_mode"] = True
    
    return flags

# Áp dụng cho tất cả segments
for i, seg in enumerate(segments):
    next_cust_seg = get_next_customer_segment(segments, i)
    seg["context_flags"] = detect_context_flags(seg, next_cust_seg)
```

**Quy tắc áp dụng:**
```python
def apply_context_aware_gating(violation_level, context_flags, customer_impact_count):
    """
    Giảm hoặc miễn phạt dựa trên context
    
    Nguyên tắc:
    1. Có context hợp lý → hạ 1 mức hoặc miễn phạt
    2. Ưu tiên customer impact: nếu KH phàn nàn → KHÔNG miễn phạt
    """
    # Nếu có customer impact cao → ưu tiên, không miễn
    if customer_impact_count >= 3:
        return violation_level  # Không giảm
    
    # Có context hợp lý và impact thấp → giảm mức
    if any(context_flags.values()):
        if violation_level == "M1":
            return "OK"
        elif violation_level == "M2":
            return "M1"
        elif violation_level == "M3":
            return "M2"
    
    return violation_level
```

**Thời gian:** 0.1 giây

---

### Bước 12: Mapping Mức Lỗi M1/M2/M3

**Quy tắc mapping (ưu tiên Customer Impact):**

```python
def map_violation_level(outlier_1sigma, outlier_2sigma, outlier_2_5sigma, 
                        customer_impact, context_flags):
    """
    Mapping mức lỗi theo thứ tự ưu tiên:
    1. Customer Impact (cao nhất)
    2. Outlier ratio + sigma levels
    3. Context-aware gating
    """
    violation_level = "OK"
    evidence = []
    
    # ==== NGƯỠNG METRICS ====
    r_1sigma = outlier_1sigma["outlier_ratio"]
    r_2sigma = outlier_2sigma["outlier_ratio"]
    r_2_5sigma = outlier_2_5sigma["outlier_ratio"]
    
    # Xác định mức lỗi ban đầu
    if r_2_5sigma >= 0.40:
        violation_level = "M3"
        evidence.append(f"r_out(±2.5σ) = {r_2_5sigma:.1%} ≥ 40%")
    elif r_2sigma >= 0.30:
        violation_level = "M2"
        evidence.append(f"r_out(±2σ) = {r_2sigma:.1%} ≥ 30%")
    elif r_1sigma >= 0.20:
        violation_level = "M1"
        evidence.append(f"r_out(±1σ) = {r_1sigma:.1%} ≥ 20%")
    
    # ==== CUSTOMER IMPACT (ưu tiên cao nhất) ====
    repeat_count = customer_impact["repeat_requests"]
    
    if repeat_count >= 3:
        # Nâng lên ít nhất M2
        if violation_level in ["OK", "M1"]:
            violation_level = "M2"
        evidence.append(f"KH yêu cầu nhắc lại {repeat_count} lần")
    
    # Kiểm tra hiểu sai nội dung quan trọng
    if has_critical_misunderstanding(customer_impact):
        violation_level = "M3"
        evidence.append("Gây hiểu sai nội dung quan trọng (OTP/điều khoản)")
    
    # ==== CONTEXT-AWARE GATING ====
    if any(context_flags.values()) and repeat_count < 3:
        violation_level = apply_context_aware_gating(
            violation_level, context_flags, repeat_count
        )
        evidence.append(f"Context: {', '.join([k for k, v in context_flags.items() if v])}")
    
    return {
        "violation_level": violation_level,
        "evidence": evidence,
        "metrics": {
            "r_out_1sigma": r_1sigma,
            "r_out_2sigma": r_2sigma,
            "r_out_2_5sigma": r_2_5sigma
        },
        "customer_impact_count": repeat_count,
        "context_flags": context_flags
    }
```

**Bảng mapping chi tiết:**

| Điều kiện | Mức lỗi | Evidence |
|-----------|---------|----------|
| r_out(±1σ) < 20% | **OK** | Không có vi phạm |
| r_out(±1σ) ≥ 20% | **M1** | Lệch nhẹ, KH vẫn theo kịp |
| r_out(±2σ) ≥ 30% | **M2** | Lệch nhiều |
| KH yêu cầu nhắc lại ≥3 lần | **M2** | Customer impact cao |
| r_out(±2.5σ) ≥ 40% | **M3** | Lệch rất nhiều |
| Gây hiểu sai OTP/điều khoản | **M3** | Critical misunderstanding |

**Output:**
```json
{
  "violation_level": "M2",
  "evidence": [
    "r_out(±2σ) = 32% ≥ 30%",
    "KH yêu cầu nhắc lại 3 lần",
    "Outliers: S5 [50.0-65.3s] wpm=194.6 (quá nhanh)"
  ],
  "metrics": {
    "r_out_1sigma": 0.28,
    "r_out_2sigma": 0.32,
    "r_out_2_5sigma": 0.12
  },
  "customer_impact_count": 3,
  "context_flags": {}
}
```

**Thời gian:** 0.1 giây

---

### Bước 13: Tính Điểm Trừ

**Quy tắc trừ điểm:**

```python
def calculate_penalty(violation_level, call_type):
    """
    Tính điểm trừ theo mức lỗi
    
    Quy tắc:
    - M1: Trừ đúng điểm tiêu chí con
    - M2: Trừ 50% điểm NHÓM KNGT
    - M3: Điểm NHÓM KNGT = 0
    """
    # Điểm KNGT tối đa
    max_kngt = 2.0 if call_type == "BH" else 4.0
    
    # Điểm tiêu chí con (A.2.1 Tốc độ nói = 1/3 của A.2)
    criterion_weight = 0.10  # 10% KNGT
    sub_criterion_weight = criterion_weight / 3  # 1/3 của 10%
    criterion_score = max_kngt * sub_criterion_weight
    
    if violation_level == "OK":
        penalty = 0.0
        final_score = max_kngt
    elif violation_level == "M1":
        penalty = criterion_score
        final_score = max_kngt - penalty
    elif violation_level == "M2":
        penalty = 0.5 * max_kngt  # Trừ 50% nhóm
        final_score = max_kngt - penalty
    elif violation_level == "M3":
        penalty = max_kngt  # Nhóm = 0
        final_score = 0.0
    
    return {
        "max_kngt": max_kngt,
        "criterion_score": criterion_score,
        "penalty": penalty,
        "final_kngt_score": final_score,
        "penalty_percentage": (penalty / max_kngt) * 100
    }

# Ví dụ
penalty = calculate_penalty("M2", "BH")
```

**Output:**
```json
{
  "max_kngt": 2.0,
  "criterion_score": 0.067,  // 2.0 × 10% × 1/3
  "penalty": 1.0,  // 50% × 2.0
  "final_kngt_score": 1.0,  // 2.0 - 1.0
  "penalty_percentage": 50.0
}
```

**Thời gian:** <0.1 giây

---

### Bước 14: Sinh Evidence và Báo cáo

**Mục đích:** Tạo evidence chi tiết cho vi phạm

```python
def generate_evidence(wpm_results, outlier_data, customer_impact, 
                      violation_level, baseline):
    """
    Sinh evidence với timestamps và trích đoạn transcript
    """
    evidence_items = []
    
    # 1. Outlier segments
    for outlier in outlier_data["outliers"]:
        seg_data = next(s for s in wpm_results if s["segment_id"] == outlier["segment_id"])
        
        evidence_items.append({
            "type": "metric_violation",
            "segment_id": outlier["segment_id"],
            "timestamp_start": seg_data["start"],
            "timestamp_end": seg_data["end"],
            "text_excerpt": seg_data["text_preview"],
            "metric": {
                "wpm": outlier["wpm"],
                "baseline": baseline["base_wpm"],
                "deviation": outlier["deviation"],
                "direction": outlier["direction"]
            }
        })
    
    # 2. Customer impact
    for impact in customer_impact["impacts"]:
        evidence_items.append({
            "type": "customer_impact",
            "timestamp": impact["timestamp"],
            "text_excerpt": impact["text"],
            "category": impact["category"]
        })
    
    # 3. Tạo summary
    summary = {
        "violation_level": violation_level,
        "total_segments": len(wpm_results),
        "outlier_count": outlier_data["outlier_count"],
        "customer_impact_count": customer_impact["total_impacts"],
        "baseline": f"{baseline['base_wpm']:.0f} ± {baseline['std_wpm']:.0f} wpm",
        "agent_median": f"{np.median([r['wpm'] for r in wpm_results]):.0f} wpm"
    }
    
    return {
        "summary": summary,
        "evidence_items": evidence_items
    }
```

**Output:**
```json
{
  "summary": {
    "violation_level": "M2",
    "total_segments": 25,
    "outlier_count": 7,
    "customer_impact_count": 3,
    "baseline": "150 ± 20 wpm",
    "agent_median": "148 wpm"
  },
  "evidence_items": [
    {
      "type": "metric_violation",
      "segment_id": "S5",
      "timestamp_start": 50.0,
      "timestamp_end": 65.3,
      "text_excerpt": "Anh quan tâm sản phẩm bảo hiểm nhân thọ không...",
      "metric": {
        "wpm": 194.6,
        "baseline": 150.0,
        "deviation": 44.6,
        "direction": "too_fast"
      }
    },
    {
      "type": "customer_impact",
      "timestamp": 67.8,
      "text_excerpt": "Em lặp lại cái đó được không anh không nghe rõ",
      "category": "request_repeat"
    }
  ]
}
```

**Thời gian:** 0.2 giây

---

## 📊 Tổng hợp Pipeline

### Timeline Đầy đủ

```
┌────────────────────────────────────────────────────────────┐
│ Bước 1: Chuẩn bị Input (tức thì)                           │
├────────────────────────────────────────────────────────────┤
│ Bước 2: STT (2-5s)                                         │
├────────────────────────────────────────────────────────────┤
│ Bước 3: Diarization (1-3s)                                 │
├────────────────────────────────────────────────────────────┤
│ Bước 4: VAD (0.5-1s) ← NHANH!                             │
├────────────────────────────────────────────────────────────┤
│ Bước 5: Chia Segments theo Speaker (0.1s)                 │
├────────────────────────────────────────────────────────────┤
│ Bước 6: Chia Segments Dài theo Pause (0.1s)               │
├────────────────────────────────────────────────────────────┤
│ Bước 7: Tính Voiced Duration (0.1s)                       │
├────────────────────────────────────────────────────────────┤
│ Bước 8: Tính WPM cho từng Segment (0.2s)                  │
├────────────────────────────────────────────────────────────┤
│ Bước 9: Tổng hợp Metrics & So sánh Baseline (0.2s)        │
├────────────────────────────────────────────────────────────┤
│ Bước 10: Phát hiện Customer Impact (0.2s)                 │
├────────────────────────────────────────────────────────────┤
│ Bước 11: Context-Aware Gating (0.1s)                      │
├────────────────────────────────────────────────────────────┤
│ Bước 12: Mapping Mức Lỗi (0.1s)                           │
├────────────────────────────────────────────────────────────┤
│ Bước 13: Tính Điểm Trừ (0.1s)                             │
├────────────────────────────────────────────────────────────┤
│ Bước 14: Sinh Evidence & Báo cáo (0.2s)                   │
└────────────────────────────────────────────────────────────┘

TỔNG: ~5-10 giây (cho cuộc gọi 5 phút)
      (60-80% là STT, không phải đo tốc độ!)
```

### Config Khuyến nghị

```python
SPEECH_RATE_CONFIG = {
    # Segmentation
    "max_segment_duration": 15.0,      # seconds
    "min_segment_duration": 2.0,       # seconds
    "long_pause_threshold": 0.7,       # seconds (700ms)
    "overlap_tolerance": 0.2,          # seconds (200ms)
    
    # VAD
    "vad_frame_duration": 0.01,        # 10ms
    "vad_aggressiveness": 2,           # webrtcvad level (0-3)
    
    # Baseline
    "baseline_window_days": 90,        # 90 ngày
    "baseline_min_qa_score": 8.0,      # Chỉ lấy cuộc gọi đạt ≥8.0
    "baseline_min_samples": 50,        # Tối thiểu 50 cuộc gọi
    
    # Thresholds
    "min_voiced_duration": 1.0,        # Segment tối thiểu 1s
    "outlier_k_values": [1, 2, 2.5],   # Tính cho ±1σ, ±2σ, ±2.5σ
    
    # Mapping thresholds
    "m1_threshold": 0.20,              # r_out(±1σ) ≥ 20%
    "m2_threshold": 0.30,              # r_out(±2σ) ≥ 30%
    "m3_threshold": 0.40,              # r_out(±2.5σ) ≥ 40%
    "m2_customer_impact_threshold": 3, # KH yêu cầu nhắc lại ≥3 lần
    
    # Text splitting
    "text_split_method": "word_timestamps",  # Ưu tiên
    "text_split_fallback": "duration_ratio"  # Fallback
}
```

---

## 🎓 Ví dụ Đầy đủ End-to-End

### Input
```
Audio: call_12345.wav (300 giây = 5 phút)
Agent: AGENT_001
Team: Sales_BH
Call Type: BH
```

### Output Cuối cùng

```json
{
  "call_id": "12345",
  "agent_id": "AGENT_001",
  "team": "Sales_BH",
  "call_type": "BH",
  
  "criteria": {
    "name": "A.2.1 - Tốc độ nói",
    "group": "KNGT",
    "weight": 0.033,  // 10% × 1/3
    "max_score": 0.067  // 2.0 × 10% × 1/3
  },
  
  "metrics": {
    "total_segments": 25,
    "agent_segments": 15,
    "median_wpm": 148.3,
    "p90_wpm": 192.1,
    "baseline": {
      "base_wpm": 150.0,
      "std_wpm": 20.0,
      "sample_count": 245
    },
    "outlier_ratio_1sigma": 0.28,
    "outlier_ratio_2sigma": 0.32,
    "outlier_ratio_2_5sigma": 0.12
  },
  
  "customer_impact": {
    "repeat_requests": 3,
    "confusion_markers": 1,
    "total_impacts": 4
  },
  
  "violation": {
    "level": "M2",
    "reason": [
      "r_out(±2σ) = 32% ≥ 30%",
      "KH yêu cầu nhắc lại 3 lần"
    ]
  },
  
  "penalty": {
    "amount": 1.0,
    "percentage": 50.0,
    "description": "Trừ 50% điểm nhóm KNGT"
  },
  
  "score": {
    "max_kngt": 2.0,
    "final_kngt": 1.0,
    "criterion_penalty": 0.067
  },
  
  "evidence": [
    {
      "type": "metric_violation",
      "segment_id": "S5",
      "timestamp": "[50.0 - 65.3s]",
      "text": "Anh quan tâm sản phẩm bảo hiểm nhân thọ không...",
      "wpm": 194.6,
      "deviation": "+44.6 wpm (quá nhanh)"
    },
    {
      "type": "customer_impact",
      "timestamp": "67.8s",
      "text": "Em lặp lại cái đó được không anh không nghe rõ",
      "category": "request_repeat"
    }
  ],
  
  "recommendations": [
    "Agent nên giảm tốc độ nói xuống, đặc biệt tại segment S5",
    "Lưu ý pause sau các câu quan trọng để KH có thời gian xử lý",
    "Quan sát phản ứng KH, nếu KH yêu cầu nhắc lại thì điều chỉnh ngay"
  ]
}
```

---

## ✅ Checklist Triển khai

### Phase 1: MVP (Tuần 1-2)
- [ ] Tích hợp STT (Whisper hoặc Google Cloud STT)
- [ ] Tích hợp Diarization (pyannote.audio)
- [ ] Implement VAD (webrtcvad)
- [ ] Implement segmentation cơ bản (speaker-based)
- [ ] Tính WPM theo công thức đơn giản
- [ ] Chia text theo tỷ lệ thời gian (phương pháp 1)
- [ ] Tính outlier ratio với baseline cố định tạm

### Phase 2: Production (Tuần 3-4)
- [ ] Thu thập baseline từ dữ liệu thực tế (200-500 cuộc gọi/team)
- [ ] Implement chia segment dài theo pause
- [ ] Tính voiced_duration chính xác với VAD
- [ ] Phát hiện customer impact với regex patterns
- [ ] Implement context-aware gating
- [ ] Mapping mức lỗi M1/M2/M3 đầy đủ
- [ ] Sinh evidence với timestamps

### Phase 3: Optimization (Tuần 5+)
- [ ] Upgrade lên word-level timestamps (phương pháp 2)
- [ ] Cập nhật baseline tự động (hàng tuần/tháng)
- [ ] Monitor drift detection
- [ ] A/B test các threshold
- [ ] Fine-tune patterns cho customer impact
- [ ] Optimize performance (parallel processing, caching)

---

## 🔧 Troubleshooting

### Vấn đề thường gặp

**1. VAD phát hiện sai (nhiều false positive/negative)**
```
Giải pháp:
- Điều chỉnh aggressiveness level (0-3)
- Kết hợp với ASR confidence
- Filter các segment có word_count=0
```

**2. Baseline không đại diện**
```
Giải pháp:
- Tăng window_days lên 120-180 ngày
- Giảm min_qa_score xuống 7.5
- Tách baseline theo sản phẩm/campaign cụ thể
```

**3. Quá nhiều false positive (phạt oan)**
```
Giải pháp:
- Tăng threshold (M1: 20% → 25%)
- Kiểm tra customer impact kỹ hơn
- Mở rộng context-aware patterns
```

**4. Không phát hiện được vi phạm rõ ràng**
```
Giải pháp:
- Giảm threshold (M2: 30% → 25%)
- Tăng trọng số customer impact
- Review baseline có đúng không
```

---

## 📚 Tham khảo

- [05_Scoring_Criteria_Decomposition.md](./05_Scoring_Criteria_Decomposition.md)
- [07_Segmentation_Strategy_Detailed.md](./07_Segmentation_Strategy_Detailed.md)
- [08_Pause_Based_Splitting_Visual_Guide.md](./08_Pause_Based_Splitting_Visual_Guide.md)
- [09_VAD_Latency_And_Text_Splitting.md](./09_VAD_Latency_And_Text_Splitting.md)
- [Master Spec](./00_Master_Spec.md)

---

**Kết luận:** Quy trình đánh giá tốc độ nói gồm 14 bước, từ chuẩn bị input đến sinh báo cáo cuối cùng. Tổng thời gian ~5-10 giây cho cuộc gọi 5 phút, trong đó STT chiếm 60-80%. VAD và các bước đo tốc độ **RẤT NHANH, KHÔNG gây trễ**.