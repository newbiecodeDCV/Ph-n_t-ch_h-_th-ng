# Chiến lược Bootstrap khi KHÔNG CÓ BASELINE

**Tình huống:** Hệ thống mới, chưa có dữ liệu lịch sử để tính baseline team-specific.

**Vấn đề:** Không thể áp dụng phương pháp "so sánh với baseline ±kσ".

**Giải pháp:** Chiến lược 3 giai đoạn - Từ Cold Start → Warm Up → Production.

---

## 🚀 GIẢI PHÁP NHANH (Áp dụng ngay)

### Giai đoạn 1: COLD START (Tuần 1-2) - ƯU TIÊN CAO NHẤT

**Mục tiêu:** Có thể chấm điểm ngay lập tức mà KHÔNG CẦN baseline

#### Phương án 1A: Dùng ngưỡng tuyệt đối đơn giản

**Ý tưởng:** Áp dụng ngưỡng cố định dựa trên nghiên cứu & best practices

```python
SIMPLE_THRESHOLDS = {
    "speech_rate": {
        "min_acceptable": 100,  # wpm - quá chậm
        "optimal_min": 130,     # wpm
        "optimal_max": 180,     # wpm
        "max_acceptable": 220,  # wpm - quá nhanh
    }
}

def evaluate_simple(wpm_segment):
    """
    Đánh giá đơn giản theo ngưỡng tuyệt đối
    """
    if wpm_segment < 100:
        return "M3", "Nói quá chậm (<100 wpm), gây mất kiên nhẫn"
    elif wpm_segment < 130:
        return "M1", "Nói hơi chậm (100-130 wpm)"
    elif wpm_segment > 220:
        return "M3", "Nói quá nhanh (>220 wpm), KH không theo kịp"
    elif wpm_segment > 180:
        return "M1", "Nói hơi nhanh (180-220 wpm)"
    else:
        return "OK", "Tốc độ phù hợp (130-180 wpm)"

# Tổng hợp cho toàn cuộc gọi
def evaluate_call_simple(wpm_segments):
    median_wpm = np.median(wpm_segments)
    
    # Đếm % segments vi phạm
    violations = [evaluate_simple(w) for w in wpm_segments]
    m3_count = sum(1 for v, _ in violations if v == "M3")
    m1_count = sum(1 for v, _ in violations if v == "M1")
    
    m3_ratio = m3_count / len(wpm_segments)
    m1_ratio = m1_count / len(wpm_segments)
    
    # Mapping tổng thể
    if m3_ratio >= 0.20:  # 20% segments M3
        return "M3"
    elif m3_ratio >= 0.10 or m1_ratio >= 0.30:
        return "M2"
    elif m1_ratio >= 0.15:
        return "M1"
    else:
        return "OK"
```

**Ngưỡng gợi ý cho tiếng Việt:**

| Loại cuộc gọi | Min | Optimal | Max | Ghi chú |
|---------------|-----|---------|-----|---------|
| **CSKH - Giải quyết khiếu nại** | 100 | 120-160 | 200 | Cần chậm, thận trọng |
| **CSKH - Hỗ trợ kỹ thuật** | 110 | 130-170 | 210 | Vừa phải |
| **BH - Tư vấn sản phẩm** | 120 | 140-180 | 220 | Năng động |
| **BH - Chốt đơn/Upsell** | 130 | 150-190 | 230 | Thuyết phục nhanh |

**Ưu điểm:**
- ✅ Áp dụng NGAY, không cần dữ liệu lịch sử
- ✅ Đơn giản, dễ hiểu, dễ giải thích
- ✅ Đủ tốt cho 80% trường hợp

**Nhược điểm:**
- ⚠️ Không công bằng 100% (không xét đến đặc thù team)
- ⚠️ Có thể phạt oan một số Agent
- ⚠️ Cần fine-tune sau khi có dữ liệu

---

#### Phương án 1B: Hybrid với Customer Impact

**Ý tưởng:** Kết hợp ngưỡng tuyệt đối + Customer Impact (ưu tiên cao hơn)

```python
def evaluate_hybrid(wpm_segments, customer_impacts):
    """
    Ưu tiên Customer Impact, dùng ngưỡng tuyệt đối làm backup
    """
    # 1. Kiểm tra Customer Impact TRƯỚC
    repeat_requests = customer_impacts["repeat_requests"]
    
    if repeat_requests >= 3:
        return "M2", [
            f"KH yêu cầu nhắc lại {repeat_requests} lần",
            "Evidence: Xem transcript timestamps"
        ]
    
    # 2. Nếu không có Customer Impact → dùng ngưỡng
    median_wpm = np.median(wpm_segments)
    
    # Đếm outliers
    very_slow = sum(1 for w in wpm_segments if w < 100)
    very_fast = sum(1 for w in wpm_segments if w > 220)
    
    very_slow_ratio = very_slow / len(wpm_segments)
    very_fast_ratio = very_fast / len(wpm_segments)
    
    if very_slow_ratio >= 0.20 or very_fast_ratio >= 0.20:
        return "M3", [
            f"20%+ segments quá nhanh/chậm",
            f"Median: {median_wpm:.0f} wpm"
        ]
    
    if very_slow_ratio >= 0.10 or very_fast_ratio >= 0.10:
        return "M2", [
            f"10%+ segments quá nhanh/chậm",
            f"Median: {median_wpm:.0f} wpm"
        ]
    
    # Kiểm tra hơi lệch
    slow = sum(1 for w in wpm_segments if 100 <= w < 130)
    fast = sum(1 for w in wpm_segments if 180 < w <= 220)
    
    if (slow + fast) / len(wpm_segments) >= 0.25:
        return "M1", [
            f"25%+ segments hơi nhanh/chậm",
            f"Median: {median_wpm:.0f} wpm"
        ]
    
    return "OK", [f"Tốc độ phù hợp, Median: {median_wpm:.0f} wpm"]
```

**Ưu điểm:**
- ✅ Customer Impact ưu tiên cao → giảm false positive
- ✅ Vẫn áp dụng ngay được
- ✅ Công bằng hơn phương án 1A

**Nhược điểm:**
- ⚠️ Cần implement Customer Impact detection

**→ ĐỀ XUẤT: Dùng Phương án 1B cho Cold Start**

---

### Giai đoạn 2: WARM UP (Tuần 3-4) - Thu thập baseline

**Mục tiêu:** Thu thập dữ liệu thực tế để tính baseline nội bộ

#### Bước 2.1: Thu thập dữ liệu

```python
# Trong quá trình chạy Cold Start, LƯU tất cả metrics
def save_call_metrics(call_id, agent_id, team, call_type, metrics):
    """
    Lưu metrics của mỗi cuộc gọi vào database
    """
    db.insert({
        "call_id": call_id,
        "agent_id": agent_id,
        "team": team,
        "call_type": call_type,
        "median_wpm": metrics["median_wpm"],
        "mean_wpm": metrics["mean_wpm"],
        "p90_wpm": metrics["p90_wpm"],
        "segment_count": metrics["segment_count"],
        "violation_level": metrics["violation_level"],
        "customer_impact_count": metrics["customer_impact_count"],
        "created_at": datetime.now()
    })
```

**Mục tiêu thu thập:**
- Tối thiểu: **50 cuộc gọi/team** (đủ để tính baseline sơ bộ)
- Lý tưởng: **200-500 cuộc gọi/team** (baseline ổn định)

#### Bước 2.2: Tính baseline từ dữ liệu thực tế

```python
def calculate_baseline_from_data(team, call_type, min_samples=50):
    """
    Tính baseline từ dữ liệu đã thu thập
    
    Chiến lược: Lấy 50% cuộc gọi TỐT NHẤT làm baseline
    (vì chưa có QA score, không biết đâu là "đạt chuẩn")
    """
    # Query tất cả cuộc gọi của team
    calls = db.query("""
        SELECT median_wpm, customer_impact_count
        FROM call_metrics
        WHERE team = :team 
          AND call_type = :call_type
        ORDER BY created_at DESC
        LIMIT 500
    """, team=team, call_type=call_type)
    
    if len(calls) < min_samples:
        print(f"⚠️ Chưa đủ dữ liệu: {len(calls)}/{min_samples}")
        return None  # Tiếp tục dùng ngưỡng tuyệt đối
    
    # Lọc: Loại bỏ các cuộc gọi có customer_impact cao
    good_calls = [c for c in calls if c["customer_impact_count"] <= 1]
    
    if len(good_calls) < min_samples // 2:
        # Nếu quá ít good_calls, lấy 50% tốt nhất
        sorted_calls = sorted(calls, key=lambda x: x["customer_impact_count"])
        good_calls = sorted_calls[:len(calls)//2]
    
    # Tính baseline từ good calls
    wpm_values = [c["median_wpm"] for c in good_calls]
    
    baseline = {
        "base_wpm": np.median(wpm_values),  # Dùng median thay vì mean
        "std_wpm": np.std(wpm_values),
        "sample_count": len(good_calls),
        "p10": np.percentile(wpm_values, 10),
        "p90": np.percentile(wpm_values, 90)
    }
    
    return baseline

# Chạy định kỳ (mỗi ngày)
for team in ["Sales_BH", "CSKH_Team1", ...]:
    for call_type in ["BH", "CSKH"]:
        baseline = calculate_baseline_from_data(team, call_type)
        if baseline:
            print(f"✅ Baseline {team}/{call_type}: "
                  f"{baseline['base_wpm']:.0f} ± {baseline['std_wpm']:.0f} wpm "
                  f"(n={baseline['sample_count']})")
            # Lưu vào config
            save_baseline(team, call_type, baseline)
```

**Output sau 2 tuần:**

```
✅ Baseline Sales_BH/BH: 155 ± 22 wpm (n=87)
✅ Baseline CSKH_Team1/CSKH: 138 ± 18 wpm (n=102)
⚠️ Baseline Sales_Team2/BH: Chưa đủ dữ liệu: 23/50
```

#### Bước 2.3: Chuyển dần sang baseline-based

```python
def evaluate_with_fallback(wpm_segments, team, call_type, customer_impacts):
    """
    Ưu tiên baseline nếu có, fallback sang ngưỡng tuyệt đối
    """
    # Load baseline
    baseline = load_baseline(team, call_type)
    
    if baseline and baseline["sample_count"] >= 50:
        # Đủ dữ liệu → dùng baseline-based
        print(f"✅ Dùng baseline: {baseline['base_wpm']:.0f} ± {baseline['std_wpm']:.0f}")
        return evaluate_baseline_based(wpm_segments, baseline, customer_impacts)
    else:
        # Chưa đủ → fallback sang ngưỡng tuyệt đối
        print(f"⚠️ Fallback: Dùng ngưỡng tuyệt đối (chưa đủ baseline)")
        return evaluate_hybrid(wpm_segments, customer_impacts)
```

---

### Giai đoạn 3: PRODUCTION (Tuần 5+) - Hoàn toàn baseline-based

**Mục tiêu:** 100% cuộc gọi dùng baseline team-specific

```python
def evaluate_production(wpm_segments, team, call_type, customer_impacts):
    """
    Production: Bắt buộc phải có baseline
    """
    baseline = load_baseline(team, call_type)
    
    if not baseline:
        raise ValueError(f"❌ Thiếu baseline cho {team}/{call_type}")
    
    if baseline["sample_count"] < 100:
        print(f"⚠️ Baseline chưa ổn định: chỉ có {baseline['sample_count']} samples")
    
    # Áp dụng phương pháp đầy đủ như đã thiết kế
    return evaluate_baseline_based(wpm_segments, baseline, customer_impacts)
```

**Cập nhật baseline tự động:**

```python
# Cronjob chạy hàng tuần
def update_baselines():
    """
    Cập nhật baseline từ 90 ngày gần nhất
    """
    for team in get_all_teams():
        for call_type in ["BH", "CSKH"]:
            # Lấy các cuộc gọi đạt chuẩn (QA score >= 8.0)
            # Nếu chưa có QA score → dùng customer_impact <= 1
            baseline = calculate_baseline_from_data(
                team, call_type, 
                window_days=90,
                min_qa_score=8.0  # Nếu có rồi
            )
            
            if baseline:
                save_baseline(team, call_type, baseline)
                print(f"✅ Updated {team}/{call_type}: "
                      f"{baseline['base_wpm']:.0f} ± {baseline['std_wpm']:.0f}")
```

---

## 📊 So sánh 3 giai đoạn

| Giai đoạn | Khi nào? | Phương pháp | Độ chính xác | Công bằng |
|-----------|----------|-------------|--------------|-----------|
| **Cold Start** | Tuần 1-2 | Ngưỡng tuyệt đối + Customer Impact | 70-80% | ⚠️ Trung bình |
| **Warm Up** | Tuần 3-4 | Hybrid (baseline nếu có, fallback) | 80-90% | ✅ Tốt |
| **Production** | Tuần 5+ | Baseline team-specific 100% | 90-95% | ✅✅ Rất tốt |

---

## 🎯 Code hoàn chỉnh cho Cold Start

```python
import numpy as np
import re

# ========== CONFIG ==========
SIMPLE_THRESHOLDS = {
    "BH": {
        "very_slow": 100,      # <100 wpm → M3
        "slow": 130,           # 100-130 → M1
        "fast": 180,           # 180-220 → M1
        "very_fast": 220,      # >220 → M3
    },
    "CSKH": {
        "very_slow": 90,
        "slow": 120,
        "fast": 170,
        "very_fast": 210,
    }
}

# ========== FUNCTIONS ==========

def detect_customer_impact(transcript_segments):
    """Phát hiện KH phàn nàn (như đã thiết kế trước)"""
    patterns = {
        "request_repeat": [
            r"(nói lại|nhắc lại|lặp lại|nói từ từ|nói chậm)",
            r"(em ơi.*không nghe rõ|không hiểu)",
            r"(nói nhanh|nhanh quá)"
        ]
    }
    
    impacts = []
    for seg in transcript_segments:
        if seg["speaker"] != "CUSTOMER":
            continue
        
        text = seg["text"].lower()
        for category, pattern_list in patterns.items():
            for pattern in pattern_list:
                if re.search(pattern, text):
                    impacts.append({
                        "timestamp": seg["start"],
                        "text": seg["text"],
                        "category": category
                    })
                    break
    
    return {
        "repeat_requests": len(impacts),
        "impacts": impacts
    }


def evaluate_cold_start(wpm_segments, call_type, customer_impacts):
    """
    Đánh giá khi KHÔNG CÓ BASELINE
    
    Ưu tiên:
    1. Customer Impact (cao nhất)
    2. Ngưỡng tuyệt đối
    """
    thresholds = SIMPLE_THRESHOLDS[call_type]
    
    # ===== 1. CUSTOMER IMPACT (ưu tiên cao nhất) =====
    repeat_count = customer_impacts["repeat_requests"]
    
    if repeat_count >= 3:
        return {
            "violation_level": "M2",
            "evidence": [
                f"KH yêu cầu nhắc lại {repeat_count} lần",
                "Customer Impact ưu tiên cao nhất"
            ],
            "method": "customer_impact"
        }
    
    # ===== 2. NGƯỠNG TUYỆT ĐỐI =====
    median_wpm = np.median(wpm_segments)
    
    # Phân loại từng segment
    very_slow_count = sum(1 for w in wpm_segments if w < thresholds["very_slow"])
    slow_count = sum(1 for w in wpm_segments 
                     if thresholds["very_slow"] <= w < thresholds["slow"])
    fast_count = sum(1 for w in wpm_segments 
                    if thresholds["fast"] < w <= thresholds["very_fast"])
    very_fast_count = sum(1 for w in wpm_segments if w > thresholds["very_fast"])
    
    total_segments = len(wpm_segments)
    
    very_slow_ratio = very_slow_count / total_segments
    slow_ratio = slow_count / total_segments
    fast_ratio = fast_count / total_segments
    very_fast_ratio = very_fast_count / total_segments
    
    # Mapping
    if very_slow_ratio >= 0.20 or very_fast_ratio >= 0.20:
        return {
            "violation_level": "M3",
            "evidence": [
                f"20%+ segments quá nhanh/chậm (very_slow={very_slow_ratio:.1%}, very_fast={very_fast_ratio:.1%})",
                f"Median: {median_wpm:.0f} wpm"
            ],
            "method": "absolute_threshold"
        }
    
    if very_slow_ratio >= 0.10 or very_fast_ratio >= 0.10:
        return {
            "violation_level": "M2",
            "evidence": [
                f"10%+ segments quá nhanh/chậm (very_slow={very_slow_ratio:.1%}, very_fast={very_fast_ratio:.1%})",
                f"Median: {median_wpm:.0f} wpm"
            ],
            "method": "absolute_threshold"
        }
    
    # M1: hơi lệch
    outlier_ratio = (slow_ratio + fast_ratio)
    if outlier_ratio >= 0.25 or repeat_count >= 2:
        return {
            "violation_level": "M1",
            "evidence": [
                f"25%+ segments hơi nhanh/chậm (outlier={outlier_ratio:.1%})",
                f"Median: {median_wpm:.0f} wpm"
            ],
            "method": "absolute_threshold"
        }
    
    return {
        "violation_level": "OK",
        "evidence": [
            f"Tốc độ phù hợp",
            f"Median: {median_wpm:.0f} wpm"
        ],
        "method": "absolute_threshold"
    }


# ========== MAIN PIPELINE ==========

def evaluate_speech_rate_no_baseline(segments, call_type, transcript_segments):
    """
    Pipeline đầy đủ khi KHÔNG CÓ BASELINE
    """
    # Bước 1-8: Tính WPM cho từng segment (như trước)
    wpm_segments = calculate_wpm_for_segments(segments)  # Đã có
    wpm_values = [s["wpm"] for s in wpm_segments]
    
    # Bước 9: Phát hiện Customer Impact
    customer_impacts = detect_customer_impact(transcript_segments)
    
    # Bước 10: Đánh giá (KHÔNG CẦN BASELINE)
    result = evaluate_cold_start(wpm_values, call_type, customer_impacts)
    
    # Bước 11: Tính điểm trừ
    penalty = calculate_penalty(result["violation_level"], call_type)
    
    # Bước 12: Sinh evidence
    evidence_items = []
    for impact in customer_impacts["impacts"]:
        evidence_items.append({
            "type": "customer_impact",
            "timestamp": impact["timestamp"],
            "text": impact["text"]
        })
    
    # Tìm segments vi phạm
    thresholds = SIMPLE_THRESHOLDS[call_type]
    for seg in wpm_segments:
        if seg["wpm"] < thresholds["very_slow"] or seg["wpm"] > thresholds["very_fast"]:
            evidence_items.append({
                "type": "metric_violation",
                "segment_id": seg["segment_id"],
                "timestamp_start": seg["start"],
                "timestamp_end": seg["end"],
                "text": seg["text_preview"],
                "wpm": seg["wpm"]
            })
    
    return {
        "violation": result,
        "penalty": penalty,
        "evidence": evidence_items,
        "metrics": {
            "median_wpm": np.median(wpm_values),
            "p90_wpm": np.percentile(wpm_values, 90),
            "total_segments": len(wpm_values)
        },
        "note": "⚠️ Cold Start Mode: Dùng ngưỡng tuyệt đối (chưa có baseline)"
    }


# ========== USAGE ==========

# Khi chạy thực tế
result = evaluate_speech_rate_no_baseline(
    segments=agent_segments,
    call_type="BH",
    transcript_segments=full_transcript
)

print(f"Violation: {result['violation']['violation_level']}")
print(f"Method: {result['violation']['method']}")
print(f"Evidence: {result['violation']['evidence']}")
print(f"Penalty: {result['penalty']['penalty']}")
print(f"Note: {result['note']}")
```

---

## ⚡ Action Items NGAY LẬP TỨC

### Tuần 1 (Hiện tại):

1. **Implement Cold Start evaluation** với code trên
2. **Config ngưỡng** theo loại cuộc gọi (BH vs CSKH)
3. **LƯU TẤT CẢ metrics** vào database khi chạy
4. **Monitor** false positive rate (Agent phàn nàn phạt oan)

### Tuần 2:

1. **Fine-tune ngưỡng** dựa trên feedback
2. **Tích lũy dữ liệu** (mục tiêu: 50 cuộc gọi/team)

### Tuần 3-4:

1. **Tính baseline** từ dữ liệu thực tế
2. **A/B test** baseline-based vs threshold-based
3. **Chuyển dần** sang baseline cho từng team

### Tuần 5+:

1. **100% baseline-based**
2. **Auto-update baseline** hàng tuần
3. **Monitor drift** và điều chỉnh

---

## 🎓 Ví dụ Output Cold Start

```json
{
  "call_id": "12345",
  "violation": {
    "violation_level": "M1",
    "evidence": [
      "25%+ segments hơi nhanh/chậm (outlier=28%)",
      "Median: 185 wpm"
    ],
    "method": "absolute_threshold"
  },
  "penalty": {
    "amount": 0.067,
    "description": "Trừ điểm tiêu chí con"
  },
  "metrics": {
    "median_wpm": 185,
    "p90_wpm": 205,
    "total_segments": 18
  },
  "evidence": [
    {
      "type": "metric_violation",
      "segment_id": "S5",
      "timestamp_start": 45.2,
      "timestamp_end": 58.7,
      "text": "Anh quan tâm sản phẩm bảo hiểm...",
      "wpm": 227
    }
  ],
  "note": "⚠️ Cold Start Mode: Dùng ngưỡng tuyệt đối (chưa có baseline)",
  "recommendation": "Sau 2 tuần, hệ thống sẽ tự động chuyển sang baseline team-specific"
}
```

---

## ✅ Tóm tắt

**Vấn đề:** Không có baseline  
**Giải pháp:** 3 giai đoạn
1. **Cold Start (Tuần 1-2):** Ngưỡng tuyệt đối + Customer Impact
2. **Warm Up (Tuần 3-4):** Thu thập → Tính baseline → Hybrid
3. **Production (Tuần 5+):** 100% baseline-based

**Code ready:** Áp dụng ngay được, không chặn triển khai!

**Key insight:** Customer Impact ưu tiên cao nhất → giảm false positive ngay cả khi dùng ngưỡng tuyệt đối.

---

Bạn có thể **BẮT ĐẦU NGAY** với Cold Start approach này! 🚀