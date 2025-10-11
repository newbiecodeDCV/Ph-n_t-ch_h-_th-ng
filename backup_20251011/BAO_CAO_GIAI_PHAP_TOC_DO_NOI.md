# BÁO CÁO: GIẢI PHÁP ĐÁNH GIÁ TỐC ĐỘ NÓI KHI CHƯA CÓ BASELINE

**Người báo cáo:** [Tên bạn]  
**Ngày:** 10/10/2025  
**Chủ đề:** Đề xuất chiến lược triển khai đánh giá tốc độ nói cho hệ thống QA

---

## 1. BỐI CẢNH VÀ VẤN ĐỀ

### Tình huống hiện tại
- Hệ thống QA tự động đang được xây dựng để đánh giá chất lượng cuộc gọi
- Cần đánh giá tiêu chí **"Tốc độ nói"** của agent (nói quá nhanh/chậm)
- **Vấn đề:** Hệ thống mới, **chưa có dữ liệu lịch sử** để tạo baseline team-specific

### Thách thức kỹ thuật
Phương pháp tiêu chuẩn đòi hỏi:
- Tính baseline (trung bình + độ lệch chuẩn) từ 200-500 cuộc gọi đạt chuẩn/team
- So sánh tốc độ nói của agent với baseline: ±1σ, ±2σ, ±2.5σ
- **➡️ Không thể áp dụng ngay vì không có baseline!**

---

## 2. GIẢI PHÁP ĐỀ XUẤT: CHIẾN LƯỢC 3 GIAI ĐOẠN

### 📍 Giai đoạn 1: COLD START (Tuần 1-2) - ƯU TIÊN CAO

**Mục tiêu:** Triển khai ngay, không cần baseline

**Phương pháp:**
1. **Dùng ngưỡng cố định (absolute threshold)**
   - Dựa trên nghiên cứu và best practices quốc tế
   - Áp dụng ngưỡng khác nhau cho từng loại cuộc gọi
   
   | Loại cuộc gọi | Quá chậm | Hơi chậm | TỐT | Hơi nhanh | Quá nhanh |
   |---------------|----------|----------|-----|-----------|-----------|
   | **BH (Bán hàng)** | <100 wpm | 100-130 | 130-180 | 180-220 | >220 wpm |
   | **CSKH** | <90 wpm | 90-120 | 120-170 | 170-210 | >210 wpm |

2. **Kết hợp Customer Impact (ưu tiên cao nhất)**
   - Phát hiện khách hàng yêu cầu nhắc lại, phàn nàn
   - Nếu KH yêu cầu nhắc lại ≥3 lần → vi phạm nghiêm trọng
   - **Lợi ích:** Giảm đáng kể false positive (phạt oan agent)

**Quy tắc đánh giá:**
- **M3 (Nghiêm trọng):** ≥20% segments quá nhanh/chậm HOẶC KH phàn nàn nhiều
- **M2 (Khá nghiêm trọng):** ≥10% segments quá nhanh/chậm HOẶC KH yêu cầu nhắc lại ≥3 lần
- **M1 (Nhẹ):** ≥25% segments hơi lệch HOẶC KH yêu cầu nhắc lại 2 lần
- **OK:** Trong ngưỡng chấp nhận được

**Ưu điểm:**
- ✅ Triển khai ngay lập tức, không chặn dự án
- ✅ Đủ tốt cho 70-80% trường hợp
- ✅ Customer Impact ưu tiên cao → giảm sai số
- ✅ Đơn giản, dễ giải thích cho team

**Nhược điểm:**
- ⚠️ Không hoàn toàn công bằng (chưa xét đặc thù từng team)
- ⚠️ Có thể phạt oan một số agent có phong cách nói khác biệt

**→ Giải pháp:** Thu thập dữ liệu song song để cải thiện ở giai đoạn tiếp theo

---

### 📍 Giai đoạn 2: WARM UP (Tuần 3-4)

**Mục tiêu:** Thu thập dữ liệu thực tế và tính baseline sơ bộ

**Hành động:**
1. **Thu thập dữ liệu tự động**
   - Trong khi chạy Cold Start, lưu tất cả metrics vào database
   - Lưu: median_wpm, p90_wpm, customer_impact_count, team, call_type
   - Mục tiêu: ≥50 cuộc gọi/team (tối thiểu), lý tưởng 200-500 cuộc gọi

2. **Tính baseline từ dữ liệu thực tế**
   - Lọc các cuộc gọi "tốt" (ít customer impact, QA score cao)
   - Tính median + std từ 50% cuộc gọi tốt nhất
   - Cập nhật baseline tự động mỗi ngày

3. **Chuyển dần sang baseline-based**
   - Các team đã đủ dữ liệu → dùng baseline
   - Team chưa đủ → tiếp tục dùng ngưỡng cố định
   - **Hybrid approach:** Tự động fallback linh hoạt

**Ưu điểm:**
- ✅ Tăng độ chính xác lên 80-90%
- ✅ Bắt đầu công bằng hơn cho từng team
- ✅ Không gián đoạn dịch vụ

---

### 📍 Giai đoạn 3: PRODUCTION (Tuần 5+)

**Mục tiêu:** Hoàn toàn baseline-based như thiết kế ban đầu

**Phương pháp:**
- 100% cuộc gọi dùng baseline team-specific
- So sánh với ±1σ, ±2σ, ±2.5σ như đã thiết kế
- Auto-update baseline hàng tuần từ 90 ngày gần nhất
- Độ chính xác 90-95%, công bằng cao

---

## 3. SO SÁNH CÁC GIAI ĐOẠN

| Tiêu chí | Cold Start | Warm Up | Production |
|----------|------------|---------|------------|
| **Thời gian** | Tuần 1-2 | Tuần 3-4 | Tuần 5+ |
| **Phương pháp** | Ngưỡng cố định + Customer Impact | Hybrid | Baseline 100% |
| **Độ chính xác** | 70-80% | 80-90% | 90-95% |
| **Công bằng** | Trung bình | Tốt | Rất tốt |
| **Yêu cầu dữ liệu** | Không | 50+ calls/team | 200-500 calls/team |
| **Rủi ro false positive** | Trung bình | Thấp | Rất thấp |
| **Sẵn sàng triển khai** | ✅ Ngay lập tức | ⏳ Sau 2 tuần | ⏳ Sau 1 tháng |

---

## 4. LỢI ÍCH KINH DOANH

### Triển khai ngay (Cold Start)
- ✅ **Không trì hoãn dự án** - Có thể go-live ngay tuần này
- ✅ **Giá trị ngay lập tức** - Phát hiện 70-80% vi phạm nghiêm trọng
- ✅ **Giảm workload QA thủ công** - Tự động screening cuộc gọi có vấn đề

### Cải thiện dần (Warm Up → Production)
- ✅ **Tăng độ chính xác** từ 70% → 90-95% trong 1 tháng
- ✅ **Công bằng hơn** - Xét đặc thù từng team/chi nhánh
- ✅ **Tự động hóa hoàn toàn** - Cập nhật baseline tự động, không cần can thiệp thủ công

### ROI rõ ràng
- **Tuần 1:** Phát hiện được các trường hợp vi phạm nghiêm trọng
- **Tuần 4:** Đánh giá chính xác cho toàn bộ team
- **Tháng 2+:** Hệ thống tự vận hành, cải tiến liên tục

---

## 5. RỦI RO VÀ GIẢM THIỂU

### Rủi ro chính: False Positive (Phạt oan agent)

**Giai đoạn Cold Start:**
- **Rủi ro:** Ngưỡng cố định có thể phạt oan agent có phong cách nói đặc biệt
- **Giảm thiểu:**
  - Customer Impact ưu tiên cao → chỉ phạt khi KH thực sự bị ảnh hưởng
  - Monitor feedback từ team QA và agent
  - Fine-tune ngưỡng dựa trên feedback tuần 1-2

**Giai đoạn Warm Up:**
- **Rủi ro:** Baseline thiếu ổn định (chưa đủ dữ liệu)
- **Giảm thiểu:**
  - Chỉ dùng baseline khi có ≥50 samples
  - Fallback sang ngưỡng cố định nếu chưa đủ
  - Hiển thị warning khi baseline chưa ổn định

**Giai đoạn Production:**
- **Rủi ro:** Baseline drift (thay đổi theo thời gian)
- **Giảm thiểu:**
  - Auto-update baseline hàng tuần
  - Monitor phân phối WPM, cảnh báo nếu có drift bất thường
  - A/B test trước khi apply baseline mới

---

## 6. TIMELINE ĐỀ XUẤT

### Tuần 1 (Tuần này)
- [ ] Review và approve chiến lược
- [ ] Config ngưỡng cho từng loại cuộc gọi (BH vs CSKH)
- [ ] Triển khai Cold Start evaluation
- [ ] Thiết lập database schema lưu metrics

### Tuần 2
- [ ] Go-live Cold Start cho 20-30% cuộc gọi (A/B test)
- [ ] Thu thập feedback từ team QA
- [ ] Fine-tune ngưỡng nếu cần
- [ ] Tích lũy dữ liệu (mục tiêu: 50 calls/team)

### Tuần 3-4
- [ ] Tính baseline từ dữ liệu thực tế
- [ ] Triển khai Warm Up (hybrid approach)
- [ ] A/B test: baseline-based vs threshold-based
- [ ] Rollout 100% cuộc gọi

### Tuần 5+
- [ ] Chuyển hoàn toàn sang Production (baseline-based)
- [ ] Thiết lập cronjob auto-update baseline
- [ ] Monitor và optimize liên tục

---

## 7. METRIC THEO DÕI THÀNH CÔNG

### KPI chính
- **Accuracy:** % cuộc gọi được đánh giá chính xác (so với QA thủ công)
  - Target tuần 1-2: ≥70%
  - Target tuần 5+: ≥90%

- **False Positive Rate:** % agent bị phạt oan
  - Target: ≤10%

- **Coverage:** % cuộc gọi được đánh giá tự động
  - Target tuần 2: ≥20%
  - Target tuần 4: 100%

### KPI phụ
- **Số cuộc gọi có baseline:** Theo dõi tiến độ thu thập dữ liệu
- **Agent Satisfaction:** Khảo sát agent về tính công bằng
- **QA Workload Reduction:** % giảm thời gian QA thủ công

---

## 8. ĐỀ XUẤT QUYẾT ĐỊNH

### Lựa chọn 1: TRIỂN KHAI NGAY (Khuyến nghị ✅)
- **Hành động:** Approve chiến lược 3 giai đoạn, bắt đầu Cold Start tuần này
- **Lợi ích:** 
  - Go-live nhanh, không trì hoãn dự án
  - Giá trị ngay lập tức (70-80% accuracy)
  - Cải thiện dần đến 90-95% trong 1 tháng
- **Rủi ro:** Thấp, có phương án giảm thiểu rõ ràng

### Lựa chọn 2: CHỜ CÓ BASELINE ĐẦY ĐỦ
- **Hành động:** Trì hoãn 1-2 tháng để thu thập dữ liệu thủ công
- **Lợi ích:** Accuracy cao ngay từ đầu (90-95%)
- **Rủi ro:** 
  - ❌ Trì hoãn dự án 1-2 tháng
  - ❌ Mất cơ hội tự động hóa sớm
  - ❌ Vẫn phải thu thập dữ liệu thủ công (workload cao)

### Lựa chọn 3: HỆ THỐNG HYBRID DÀI HẠN
- **Hành động:** Duy trì ngưỡng cố định + baseline song song
- **Lợi ích:** Linh hoạt, phù hợp với team mới
- **Rủi ro:** Phức tạp trong vận hành, khó maintain

---

## 9. KẾT LUẬN

### Khuyến nghị
**→ Triển khai ngay với chiến lược 3 giai đoạn (Lựa chọn 1)**

### Lý do
1. **Không chặn dự án** - Có thể go-live ngay
2. **Đủ tốt ngay từ đầu** - 70-80% accuracy với Cold Start
3. **Cải thiện tự động** - Tự động đạt 90-95% trong 1 tháng
4. **Rủi ro thấp** - Customer Impact ưu tiên cao, giảm false positive
5. **Linh hoạt** - Có thể điều chỉnh ngưỡng dựa trên feedback

### Yêu cầu hỗ trợ
- **Từ team Business:** Approve chiến lược và timeline
- **Từ team QA:** Feedback về ngưỡng và kết quả đánh giá tuần đầu
- **Từ team Data:** Thiết lập database schema lưu metrics
- **Từ team Dev:** Triển khai code theo tài liệu kỹ thuật đã chuẩn bị

---

## PHỤ LỤC: TÀI LIỆU THAM KHẢO

Chi tiết kỹ thuật đầy đủ có trong các file:
- `thiet-ke/11_BOOTSTRAP_STRATEGY_NO_BASELINE.md` - Chiến lược chi tiết + code
- `thiet-ke/05_Scoring_Criteria_Decomposition.md` - Tiêu chí đánh giá
- `thiet-ke/07_Segmentation_Strategy_Detailed.md` - Phương pháp phân đoạn
- `thiet-ke/09_VAD_Latency_And_Text_Splitting.md` - Kỹ thuật xử lý audio

---

**Chuẩn bị bởi:** [Tên bạn]  
**Liên hệ:** [Email/Slack]  
**Ngày cập nhật:** 10/10/2025