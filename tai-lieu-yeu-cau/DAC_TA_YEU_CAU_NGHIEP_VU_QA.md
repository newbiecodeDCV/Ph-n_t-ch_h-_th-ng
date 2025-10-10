# ĐẶC TẢ YÊU CẦU NGHIỆP VỤ HỆ THỐNG CHẤM ĐIỂM QA CUỘC GỌI

## 1. BỐI CẢNH VÀ MỤC TIÊU

### 1.1. Bối cảnh hiện tại
- Công ty đang vận hành call center với 2 loại cuộc gọi chính: Bán hàng (BH) và Chăm sóc khách hàng (CSKH)
- Việc đánh giá chất lượng cuộc gọi hiện đang thực hiện thủ công bởi đội ngũ QA
- Cần số hóa và tự động hóa quy trình để tăng hiệu quả và tính khách quan

### 1.2. Mục tiêu dự án
- Tự động hóa việc chấm điểm chất lượng cuộc gọi
- Đảm bảo tính công bằng và nhất quán trong đánh giá
- Cung cấp phản hồi kịp thời cho nhân viên để cải thiện
- Giảm 70% khối lượng công việc thủ công của đội QA

### 1.3. Phạm vi áp dụng
- Tất cả cuộc gọi từ hệ thống tổng đài
- Áp dụng cho cả nhân viên mới và nhân viên hiện tại
- Tích hợp với hệ thống CRM hiện có

## 2. CÁC BÊN LIÊN QUAN

### 2.1. Người dùng chính
- **Nhân viên telesales/CSKH**: Nhận điểm và feedback
- **Quản lý trực tiếp**: Xem báo cáo đội nhóm
- **QA team**: Review và calibrate hệ thống
- **Ban giám đốc**: Xem báo cáo tổng hợp

### 2.2. Hệ thống liên quan
- **CRM**: Cung cấp file ghi âm
- **HR System**: Nhận điểm KPI để tính lương thưởng

## 3. YÊU CẦU CHỨC NĂNG

### 3.1. Xác định loại cuộc gọi
**Mô tả**: Hệ thống tự động xác định cuộc gọi thuộc loại BH hay CSKH

**Đầu vào cần có**:
- Thông tin từ CRM (ticket, case, opportunity, campaign)
- Nội dung cuộc gọi (đặc biệt 30 giây đầu)

**Quy tắc xác định**:
- Ưu tiên thông tin CRM nếu có
- Phân tích nội dung nếu CRM không rõ ràng
- Có cơ chế fallback dựa vào trạng thái khách hàng

**Kết quả mong đợi**:
- Độ chính xác ≥ 95% khi có đủ thông tin CRM
- Độ chính xác ≥ 85% khi chỉ dựa vào nội dung

### 3.2. Đánh giá kỹ năng giao tiếp (KNGT)

#### 3.2.1. Chào hỏi và xưng danh
**Yêu cầu nghiệp vụ**:
- Chào hỏi trong 10 giây đầu cuộc gọi
- Xưng danh đầy đủ (tên, đơn vị)
- Xác nhận tên khách hàng
- Giọng nói thể hiện sự nhiệt tình

**Tiêu chí đánh giá**:
- Có/không thực hiện đầy đủ các bước
- Thời gian thực hiện
- Chất lượng thực hiện (rõ ràng, nhiệt tình)

#### 3.2.2. Kỹ năng nói
**Yêu cầu nghiệp vụ**:
- Tốc độ nói phù hợp để khách hàng hiểu rõ
- Âm lượng vừa phải, không quá to/nhỏ
- Phát âm rõ ràng

**Quan trọng - Nguyên tắc đánh giá tốc độ**
- Cần có một threahold đánh giá cụ thể chứ không nên dựa vào khách hàng
**Lưu ý đặc biệt**:
- PHẢI phạt nếu nói nhanh ở phần quan trọng (OTP, điều khoản)

#### 3.2.3. Kỹ năng lắng nghe và đồng cảm
**Yêu cầu nghiệp vụ**:
- Không ngắt lời khách hàng
- Thể hiện sự đồng cảm khi khách than phiền
- Xác nhận lại thông tin khách hàng chia sẻ
- Phản hồi kịp thời

**Tiêu chí đánh giá**:
- Số lần ngắt lời không cần thiết
- Có sử dụng từ ngữ đồng cảm không
- Có paraphrase lại vấn đề của khách không

#### 3.2.4. Thái độ và ngôn ngữ
**Yêu cầu nghiệp vụ**:
- Sử dụng ngôn ngữ lịch sự, tôn trọng
- Giữ thái độ tích cực trong suốt cuộc gọi
- Không có từ ngữ tiêu cực hoặc mỉa mai

### 3.3. Đánh giá kỹ năng bán hàng (KNBH)

#### 3.3.1. Xác nhận thông tin
**Yêu cầu nghiệp vụ**:
- Xác nhận thông tin khách hàng từ CRM
- Xác nhận lại nhu cầu/vấn đề của khách

#### 3.3.2. Kỹ năng dẫn dắt cuộc gọi
**Yêu cầu nghiệp vụ**:
- Chủ động trong cuộc gọi
- Sử dụng câu hỏi mở để khai thác
- Chuyển chủ đề mượt mà

#### 3.3.3. Khai thác nhu cầu
**Yêu cầu nghiệp vụ**:
- Tìm hiểu hiện trạng khách hàng
- Xác định vấn đề/pain points
- Hiểu rõ mong muốn và ngân sách

#### 3.3.4. Nắm bắt vấn đề
**Yêu cầu nghiệp vụ**:
- Hiểu đúng vấn đề cốt lõi
- Tóm tắt lại chính xác
- Không phải hỏi lặp lại nhiều lần

#### 3.3.5. Tư vấn sản phẩm
**Yêu cầu nghiệp vụ**:
- Giới thiệu đúng sản phẩm phù hợp
- Nêu rõ lợi ích cho khách hàng
- Thông tin chính xác, không mơ hồ

#### 3.3.6. Xử lý từ chối và thuyết phục
**Yêu cầu nghiệp vụ**:
- Nhận diện rào cản của khách
- Đưa ra giải pháp phù hợp
- Tạo cảm giác cấp thiết nếu cần

#### 3.3.7. Kết thúc cuộc gọi
**Yêu cầu nghiệp vụ**:
- Có call-to-action rõ ràng
- Xác nhận bước tiếp theo
- Cảm ơn và chào tạm biệt

### 3.4. Kiểm tra tuân thủ CRM

**Yêu cầu nghiệp vụ**:
- Cập nhật đầy đủ thông tin bắt buộc
- Ghi chú chi tiết nội dung trao đổi
- Tạo ticket/case khi cần thiết
- Cập nhật trong vòng 60 phút sau cuộc gọi

**Tiêu chí đánh giá**:
- Độ đầy đủ của thông tin
- Chất lượng ghi chú
- Tính kịp thời

## 4. YÊU CẦU PHI CHỨC NĂNG

### 4.1. Hiệu suất
- Xử lý được 1000 cuộc gọi/giờ
- Thời gian chấm điểm < 5 giây/cuộc gọi
- Độ trễ báo cáo < 1 phút

### 4.2. Độ chính xác
- Sai lệch với chuyên gia < 10%
- Tỷ lệ phát hiện lỗi nghiêm trọng > 95%
- False positive rate < 5%

### 4.3. Khả năng mở rộng
- Dễ dàng thêm tiêu chí mới
- Có thể điều chỉnh trọng số
- Hỗ trợ nhiều ngôn ngữ trong tương lai

### 4.4. Tích hợp
- API chuẩn RESTful
- Webhook cho real-time notification
- Batch processing cho dữ liệu lịch sử

## 5. QUY TẮC TÍNH ĐIỂM

### 5.1. Phân bổ điểm theo loại cuộc gọi

| Nhóm tiêu chí | Cuộc gọi BH | Cuộc gọi CSKH |
|---------------|-------------|---------------|
| Kỹ năng giao tiếp (KNGT) | 20% | 40% |
| Kỹ năng bán hàng (KNBH) | 70% | 50% |
| Nhập thông tin (NTT) | 10% | 10% |

### 5.2. Mức độ vi phạm

**Mức 1 (Nhẹ)**:
- Ảnh hưởng nhỏ đến trải nghiệm khách hàng
- Có thể cải thiện dễ dàng
- Trừ điểm theo tỷ lệ tiêu chí

**Mức 2 (Trung bình)**:
- Ảnh hưởng rõ rệt đến khách hàng
- Cần đào tạo lại
- Trừ 50% điểm nhóm

**Mức 3 (Nghiêm trọng)**:
- Ảnh hưởng nghiêm trọng hoặc vi phạm quy định
- Cần xử lý kỷ luật
- Điểm nhóm = 0

### 5.3. Ngưỡng đánh giá

| Xếp loại | Điểm số |
|----------|---------|
| Xuất sắc | 9.0 - 10.0 |
| Tốt | 8.0 - 8.9 |
| Khá | 7.0 - 7.9 |
| Trung bình | 5.0 - 6.9 |
| Yếu | < 5.0 |

**Ngưỡng đạt**: ≥ 5.0 điểm

## 6. LUỒNG XỬ LÝ TỔNG QUAN

### 6.1. Thu thập dữ liệu
1. Nhận file ghi âm từ tổng đài
2. Lấy thông tin CRM của cuộc gọi
3. Kiểm tra tính hợp lệ của dữ liệu

### 6.2. Xác định context
1. Phân loại cuộc gọi (BH/CSKH)
2. Xác định khách hàng mới/cũ   
3. Xác định sản phẩm/dịch vụ liên quan

### 6.3. Phân tích nội dung
1. Chuyển đổi âm thanh thành văn bản
2. Phân tách lượt nói (agent/khách)
3. Xác định các mốc thời gian quan trọng

### 6.4. Đánh giá theo tiêu chí
1. Kiểm tra từng tiêu chí theo checklist
2. Xác định mức độ vi phạm (nếu có)
3. Tính điểm cho từng nhóm

### 6.5. Tổng hợp kết quả
1. Tính điểm tổng theo trọng số
2. Xếp loại cuộc gọi
3. Tạo recommendations

### 6.6. Xuất báo cáo
1. Báo cáo chi tiết cho từng cuộc gọi
2. Dashboard tổng hợp
3. Alerts cho các vi phạm nghiêm trọng

## 7. YÊU CẦU VỀ DỮ LIỆU

### 7.1. Dữ liệu đầu vào bắt buộc
- File âm thanh cuộc gọi (WAV/MP3)
- Call ID để liên kết với CRM
- Thời gian thực hiện cuộc gọi  ? Có cần không 
- Agent ID

### 7.2. Dữ liệu từ CRM
- Thông tin khách hàng
- Lịch sử tương tác
- Loại ticket/case (nếu có)
- Campaign/Source

### 7.3. Dữ liệu cần lưu trữ
- Điểm số và xếp loại
- Chi tiết vi phạm (nếu có)
- Transcript cuộc gọi
- Thời điểm chấm điểm

## 8. TIÊU CHÍ NGHIỆM THU

### 8.1. Chức năng
- Chấm điểm được 100% cuộc gọi mẫu
- Phân loại đúng BH/CSKH ≥ 95%
- Tạo báo cáo đầy đủ thông tin

### 8.2. Chất lượng
- Độ lệch với QA thủ công < 10%
- User acceptance ≥ 80%
- Không có lỗi critical trong 1 tháng

### 8.3. Tài liệu
- Tài liệu hướng dẫn sử dụng
- Tài liệu training cho QA team
- API documentation

## 9. RỦI RO VÀ GIẢI PHÁP

### 9.1. Rủi ro về độ chính xác
**Rủi ro**: Hệ thống đánh giá sai do không hiểu context
**Giải pháp**: 
- Human-in-the-loop cho 10% mẫu
- Continuous learning từ feedback
- Cơ chế appeal cho nhân viên

### 9.2. Rủi ro về chấp nhận
**Rủi ro**: Nhân viên không tin tưởng hệ thống
**Giải pháp**:
- Pilot với nhóm nhỏ trước
- Training kỹ lưỡng
- Transparent về cách tính điểm

### 9.3. Rủi ro kỹ thuật
**Rủi ro**: Chất lượng âm thanh kém ảnh hưởng kết quả
**Giải pháp**:
- Pre-processing để enhance audio
- Flag các cuộc gọi chất lượng thấp
- Fallback to manual nếu cần

## 10. KẾ HOẠCH TRIỂN KHAI

### Phase 1: MVP (Tháng 1-2)
- Xây dựng core engine
- Tích hợp cơ bản với CRM
- Test với 500 cuộc gọi mẫu

### Phase 2: Pilot (Tháng 3)
- Chạy song song với QA thủ công
- Thu thập feedback
- Tinh chỉnh thuật toán

### Phase 3: Rollout (Tháng 4-6)
- Triển khai từng phòng ban
- Training cho users
- Monitor và optimize

### Phase 4: Optimization (Ongoing)
- Cập nhật tiêu chí theo yêu cầu business
- Tích hợp thêm data sources
- Advanced analytics

---

**Ghi chú quan trọng**:
1. Đây là đặc tả YÊU CẦU, không phải thiết kế kỹ thuật
2. Các con số cụ thể cần được validate với business
3. Cần workshop với các stakeholders để finalize
4. Ưu tiên trải nghiệm khách hàng trên mọi metrics kỹ thuật