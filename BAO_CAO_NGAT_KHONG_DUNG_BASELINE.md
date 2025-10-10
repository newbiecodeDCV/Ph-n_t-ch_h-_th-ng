# BÁO CÁO: QUY TRÌNH ĐÁNH GIÁ TỐC ĐỘ NÓI KHÔNG DÙNG BASELINE

**Người báo cáo:** [Tên bạn]  
**Ngày:** 10/10/2025  
**Chủ đề:** Quy trình đơn giản hóa - Bỏ baseline, dùng ngưỡng cố định

---

## 1. VẤN ĐỀ

**Tình huống:**
- Hệ thống mới, chưa có dữ liệu lịch sử để tạo baseline team-specific
- Phương pháp baseline-based (so sánh với ±1σ, ±2σ) không thể triển khai ngay
- **Cần giải pháp đơn giản để go-live nhanh**

**Quyết định:**
→ **BỎ BASELINE**, dùng **ngưỡng cố định** kết hợp **Customer Impact**

---

## 2. QUY TRÌNH ĐỀ XUẤT (8 BƯỚC)

### Bước 1: Chuẩn bị dữ liệu đầu vào
**Input:**
- Audio file cuộc gọi (mono, 16kHz)
- Transcript có phân tách người nói (Agent/Customer)
- Metadata: agent_id, team, call_type (BH/CSKH)

---

### Bước 2: Phân đoạn transcript (Segmentation)
**Mục tiêu:** Chia transcript thành các đoạn nói (segments) của Agent

**Phương pháp:**
- Mỗi lần đổi người nói → segment mới
- Segment dài >15 giây → chia nhỏ theo pause dài (≥700ms)
- Segment ngắn <2 giây → gộp với segment trước (nếu cùng speaker)
- **Kết quả:** Các segments độ dài 5-15 giây

**Công cụ:** VAD (Voice Activity Detection) để tìm pause

---

### Bước 3: Xác định khoảng pause dài
**Mục tiêu:** Tìm các điểm ngắt tự nhiên trong lời nói

**Phương pháp:**
- Chạy VAD trên audio để phát hiện vùng nói/im lặng
- Xác định pause có duration ≥700ms
- Đánh dấu vị trí các pause dài

**Output:** Danh sách timestamps của các pause dài

---

### Bước 4: Chia nhỏ segments theo pause
**Mục tiêu:** Chia segments dài thành sub-segments theo ý nghĩa

**Quy tắc:**
- Nếu segment >15s VÀ có pause ≥700ms → chia thành 2 sub-segments
- Mỗi sub-segment tương ứng 1 ý nói của agent
- Không chia nếu segment <15s (giữ nguyên)

**Output:** Danh sách segments/sub-segments với timestamps

---

### Bước 5: Tính tốc độ nói (WPM) cho từng segment
**Công thức:**
```
WPM = (Số từ trong segment) / (Thời lượng phát âm - pause dài) × 60
```

**Chi tiết:**
- Đếm số từ trong text của segment
- Tính thời lượng phát âm thực tế (loại bỏ pause >200ms)
- WPM = Words Per Minute (từ/phút)

**Output:** 
```json
[
  {
    "segment_id": "S1",
    "start": 0.0,
    "end": 8.5,
    "text": "Chào anh, em là...",
    "word_count": 15,
    "voiced_duration": 7.2,
    "wpm": 125
  },
  ...
]
```

---

### Bước 6: Phát hiện Customer Impact
**Mục tiêu:** Tìm các dấu hiệu khách hàng bị ảnh hưởng bởi tốc độ nói

**Patterns phát hiện:**
- KH yêu cầu nhắc lại: "nói lại", "nhắc lại", "lặp lại"
- KH phàn nàn: "nói nhanh quá", "nói chậm", "nói từ từ"
- KH không nghe rõ: "không nghe rõ", "không hiểu"

**Output:**
```json
{
  "repeat_requests": 2,
  "impacts": [
    {
      "timestamp": 45.2,
      "text": "Em nói lại được không?",
      "category": "request_repeat"
    }
  ]
}
```

---

### Bước 7: Đánh giá vi phạm theo ngưỡng cố định

#### 7.1. Định nghĩa ngưỡng

| Loại cuộc gọi | Quá chậm | Hơi chậm | TỐT | Hơi nhanh | Quá nhanh |
|---------------|----------|----------|-----|-----------|-----------|
| **BH (Bán hàng)** | <100 wpm | 100-130 | 130-180 | 180-220 | >220 wpm |
| **CSKH** | <90 wpm | 90-120 | 120-170 | 170-210 | >210 wpm |

#### 7.2. Đánh giá từng segment
- Quá chậm/nhanh (very_slow/very_fast) → Vi phạm nghiêm trọng
- Hơi chậm/nhanh (slow/fast) → Vi phạm nhẹ

#### 7.3. Tổng hợp toàn cuộc gọi
**Ưu tiên 1: Customer Impact (cao nhất)**
- Nếu KH yêu cầu nhắc lại ≥3 lần → **M2** (bất kể WPM)
- Nếu KH yêu cầu nhắc lại 2 lần → **M1**

**Ưu tiên 2: Tỷ lệ segments vi phạm**
- ≥20% segments quá nhanh/chậm → **M3**
- ≥10% segments quá nhanh/chậm → **M2**
- ≥25% segments hơi lệch → **M1**
- Còn lại → **OK**

**Mapping mức độ:**
- **M3:** Vi phạm nghiêm trọng - Trừ điểm tiêu chí cha (toàn bộ)
- **M2:** Vi phạm khá nghiêm trọng - Trừ 50% điểm tiêu chí cha
- **M1:** Vi phạm nhẹ - Trừ điểm tiêu chí con
- **OK:** Không vi phạm - Không trừ điểm

---

### Bước 8: Tạo evidence (bằng chứng)
**Mục tiêu:** Cung cấp bằng chứng cụ thể cho mức độ vi phạm

**Evidence bao gồm:**

1. **Customer Impact** (nếu có):
   ```json
   {
     "type": "customer_impact",
     "timestamp": 45.2,
     "text": "Em nói lại được không?",
     "speaker": "CUSTOMER"
   }
   ```

2. **Metric Violation** (segments vi phạm):
   ```json
   {
     "type": "metric_violation",
     "segment_id": "S5",
     "timestamp_start": 45.2,
     "timestamp_end": 58.7,
     "text": "Anh quan tâm sản phẩm...",
     "wpm": 227,
     "threshold": "very_fast (>220)"
   }
   ```

---

## 3. OUTPUT CUỐI CÙNG

```json
{
  "call_id": "12345",
  "agent_id": "AG001",
  "team": "Sales_BH",
  "call_type": "BH",
  
  "violation": {
    "violation_level": "M1",
    "evidence_summary": [
      "25% segments hơi nhanh/chậm (outlier=28%)",
      "Median: 185 wpm"
    ],
    "method": "absolute_threshold"
  },
  
  "penalty": {
    "amount": 0.067,
    "description": "Trừ điểm tiêu chí con",
    "calculation": "1/15 = 0.067"
  },
  
  "metrics": {
    "median_wpm": 185,
    "mean_wpm": 178,
    "p90_wpm": 205,
    "total_segments": 18,
    "very_slow_segments": 0,
    "slow_segments": 1,
    "ok_segments": 12,
    "fast_segments": 5,
    "very_fast_segments": 0
  },
  
  "customer_impacts": {
    "repeat_requests": 2,
    "impacts": [
      {
        "timestamp": 45.2,
        "text": "Em nói lại được không?"
      },
      {
        "timestamp": 102.5,
        "text": "Em nói từ từ thôi"
      }
    ]
  },
  
  "evidence": [
    {
      "type": "customer_impact",
      "timestamp": 45.2,
      "text": "Em nói lại được không?"
    },
    {
      "type": "metric_violation",
      "segment_id": "S5",
      "timestamp_start": 45.2,
      "timestamp_end": 58.7,
      "text": "Anh quan tâm sản phẩm bảo hiểm nào...",
      "wpm": 205,
      "threshold": "fast (180-220)"
    }
  ],
  
  "note": "⚠️ Dùng ngưỡng tuyệt đối (không có baseline)",
  "recommendation": "Agent nên điều chỉnh tốc độ nói trong các đoạn tư vấn sản phẩm"
}
```

---

## 4. SO SÁNH VỚI PHƯƠNG PHÁP BASELINE

| Khía cạnh | Phương pháp Baseline | Phương pháp Ngưỡng cố định |
|-----------|---------------------|---------------------------|
| **Yêu cầu dữ liệu** | 200-500 cuộc gọi/team | Không cần |
| **Thời gian chuẩn bị** | 1-2 tháng | Ngay lập tức |
| **Độ chính xác** | 90-95% | 70-80% |
| **Công bằng** | Rất cao (xét đặc thù team) | Trung bình |
| **Rủi ro phạt oan** | Rất thấp | Trung bình |
| **Dễ giải thích** | Khó (cần hiểu σ) | Dễ (số cụ thể) |
| **Phù hợp khi** | Đã có dữ liệu lịch sử | Hệ thống mới |

---

## 5. ƯU ĐIỂM VÀ HẠN CHẾ

### ✅ Ưu điểm
1. **Triển khai ngay:** Không cần chờ thu thập dữ liệu
2. **Đơn giản:** Dễ hiểu, dễ giải thích
3. **Customer Impact ưu tiên cao:** Giảm false positive đáng kể
4. **Đủ tốt cho 70-80% trường hợp**

### ⚠️ Hạn chế
1. **Không xét đặc thù team:** Team A nói nhanh bình thường, team B chậm bình thường
2. **Có thể phạt oan:** Agent có phong cách nói khác biệt nhưng vẫn hiệu quả
3. **Độ chính xác thấp hơn:** 70-80% so với 90-95% của baseline

### 🔧 Giảm thiểu hạn chế
- **Customer Impact ưu tiên cao:** Chỉ phạt nghiêm trọng khi KH thực sự bị ảnh hưởng
- **Fine-tune ngưỡng:** Điều chỉnh dựa trên feedback tuần đầu
- **Monitor false positive rate:** Theo dõi số agent phàn nàn bị phạt oan

---

## 6. NGƯỠNG ĐỀ XUẤT CHI TIẾT

### 6.1. Bán hàng (BH)

| Phân loại | Ngưỡng | Ý nghĩa | Ví dụ |
|-----------|--------|---------|-------|
| **Quá chậm** | <100 wpm | Gây mất kiên nhẫn, KH chán | "Vâng... anh... đang... quan tâm... sản phẩm... nào... ạ?" |
| **Hơi chậm** | 100-130 wpm | Thiếu năng lượng, không thuyết phục | "Vâng anh đang quan tâm sản phẩm nào ạ" (chậm) |
| **TỐT** | 130-180 wpm | Rõ ràng, thuyết phục, năng động | "Vâng anh đang quan tâm sản phẩm nào ạ" (vừa phải) |
| **Hơi nhanh** | 180-220 wpm | Hơi vội, nhưng vẫn nghe được | "Vâng anh đang quan tâm sản phẩm nào ạ" (nhanh) |
| **Quá nhanh** | >220 wpm | KH không theo kịp, stress | "VânganhđangquantâmsảnphẩmnàoạAnhcóthểcho..." |

### 6.2. Chăm sóc khách hàng (CSKH)

| Phân loại | Ngưỡng | Ý nghĩa | Lý do khác với BH |
|-----------|--------|---------|-------------------|
| **Quá chậm** | <90 wpm | Gây khó chịu | CSKH cần empathy, chấp nhận chậm hơn |
| **Hơi chậm** | 90-120 wpm | Thiếu chuyên nghiệp | |
| **TỐT** | 120-170 wpm | Thấu hiểu, chuyên nghiệp | Không cần "bán hàng" nhanh |
| **Hơi nhanh** | 170-210 wpm | Thiếu empathy | KH đang có vấn đề, cần thời gian |
| **Quá nhanh** | >210 wpm | KH không theo kịp | |

### 6.3. Ngoại lệ (Context-aware)
**Không phạt trong các trường hợp:**
- Đọc OTP, mã xác nhận (cho phép chậm)
- Đọc điều khoản, hợp đồng (bắt buộc chậm)
- KH chủ động yêu cầu nói nhanh/chậm
- Tra cứu thông tin (pause dài là bình thường)

---

## 7. TIMELINE TRIỂN KHAI

### Tuần 1
- [ ] Review và approve quy trình
- [ ] Xác định ngưỡng cho từng loại cuộc gọi (điều chỉnh nếu cần)
- [ ] Implement 8 bước trên
- [ ] Test với 10-20 cuộc gọi mẫu

### Tuần 2
- [ ] Go-live cho 20-30% cuộc gọi (A/B test)
- [ ] Thu thập feedback từ team QA
- [ ] Đo false positive rate
- [ ] Fine-tune ngưỡng nếu cần

### Tuần 3+
- [ ] Rollout 100% cuộc gọi
- [ ] Monitor metrics:
  - Accuracy (so với QA thủ công)
  - False positive rate
  - Agent satisfaction
- [ ] Báo cáo hàng tuần

---

## 8. METRICS THEO DÕI

### Metrics chính
1. **Accuracy:** % cuộc gọi đánh giá đúng so với QA thủ công
   - Target: ≥70%

2. **False Positive Rate:** % agent bị phạt oan
   - Target: ≤10%

3. **Coverage:** % cuộc gọi được đánh giá tự động
   - Target tuần 2: ≥20%
   - Target tuần 4: 100%

### Metrics phụ
- **Agent complaints:** Số lượng agent phàn nàn bị phạt oan
- **QA workload reduction:** % giảm thời gian QA thủ công
- **Customer satisfaction impact:** Có tương quan giữa vi phạm tốc độ nói và CSAT không?

---

## 9. RỦI RO VÀ GIẢM THIỂU

### Rủi ro 1: False Positive (Phạt oan agent)
**Xác suất:** Trung bình (20-30% ban đầu)

**Giảm thiểu:**
- Customer Impact ưu tiên cao → chỉ phạt nghiêm trọng khi KH bị ảnh hưởng
- Fine-tune ngưỡng dựa trên feedback
- Context-aware: Không phạt trong trường hợp ngoại lệ
- Manual review cho các trường hợp biên

### Rủi ro 2: Không công bằng giữa các team
**Xác suất:** Cao (team có văn hóa nói nhanh bị ảnh hưởng)

**Giảm thiểu:**
- Áp dụng ngưỡng khác nhau cho BH vs CSKH
- Monitor phân phối vi phạm theo team
- Điều chỉnh ngưỡng cho từng team nếu cần (thủ công)

### Rủi ro 3: Agent "game" hệ thống
**Xác suất:** Thấp

**Giảm thiểu:**
- Customer Impact không thể fake (KH thực sự phàn nàn)
- Monitor patterns bất thường

---

## 10. KẾT LUẬN

### Quyết định
→ **BỎ BASELINE**, dùng **ngưỡng cố định** kết hợp **Customer Impact**

### Lý do
1. ✅ **Triển khai ngay** - Không cần chờ 1-2 tháng
2. ✅ **Đủ tốt** - 70-80% accuracy, phát hiện được vi phạm nghiêm trọng
3. ✅ **Đơn giản** - Dễ hiểu, dễ maintain
4. ✅ **Customer Impact ưu tiên cao** - Giảm false positive

### Trade-off chấp nhận
- ⚠️ Độ chính xác thấp hơn (70-80% vs 90-95%)
- ⚠️ Không hoàn toàn công bằng giữa các team
- ⚠️ False positive rate cao hơn (10% vs 5%)

### Lưu ý quan trọng
**Phương pháp này phù hợp khi:**
- ✅ Cần triển khai nhanh
- ✅ Chưa có dữ liệu lịch sử
- ✅ Chấp nhận trade-off về độ chính xác

**KHÔNG phù hợp khi:**
- ❌ Yêu cầu độ chính xác rất cao (>90%)
- ❌ Có sẵn dữ liệu lịch sử đủ lớn
- ❌ Muốn công bằng tuyệt đối giữa các team

---

## PHỤ LỤC: CHECKLIST TRIỂN KHAI

### Cần chuẩn bị
- [ ] Audio files + Transcript với diarization
- [ ] VAD tool (Silero VAD, WebRTC VAD)
- [ ] Database để lưu metrics
- [ ] Pattern để phát hiện Customer Impact

### Cần implement
- [ ] Segmentation logic (Bước 2-4)
- [ ] WPM calculation (Bước 5)
- [ ] Customer Impact detection (Bước 6)
- [ ] Evaluation logic (Bước 7)
- [ ] Evidence generation (Bước 8)

### Cần config
- [ ] Ngưỡng cho từng loại cuộc gọi (BH/CSKH)
- [ ] Customer Impact patterns
- [ ] Penalty mapping (M0/M1/M2/M3)

---

**Chuẩn bị bởi:** [Tên bạn]  
**Liên hệ:** [Email/Slack]  
**Ngày cập nhật:** 10/10/2025