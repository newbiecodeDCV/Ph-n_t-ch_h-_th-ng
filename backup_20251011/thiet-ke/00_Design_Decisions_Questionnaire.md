# Design Decisions Questionnaire

## Mục đích
Tài liệu này tập hợp các câu hỏi quan trọng cần được trả lời trước khi thiết kế chi tiết hệ thống. Các câu trả lời sẽ ảnh hưởng trực tiếp đến kiến trúc, technology stack, và cách triển khai.

## Trạng thái: ⏳ ĐANG CHỜ STAKEHOLDERS TRẢ LỜI

---

## SECTION A: Technical Infrastructure

### Q1: Infrastructure hiện có
**Câu hỏi**: Hệ thống sẽ chạy trên infrastructure nào?

**Options**:
- [ ] **On-premise** (Data center riêng của công ty)
- [ ] **Cloud** (AWS/Azure/GCP)
- [ ] **Hybrid** (Mix giữa on-premise và cloud)
- [ ] **Chưa có, cần đề xuất**

**Nếu Cloud, chọn provider**:
- [ ] AWS
- [ ] Azure
- [ ] Google Cloud Platform
- [ ] Alibaba Cloud
- [ ] Local provider (VNG Cloud, Viettel Cloud, FPT Cloud)

**Follow-up questions**:
- Có giới hạn về budget không? (ước tính USD/month)
- Có yêu cầu data phải ở Việt Nam không?

**Impact on design**:
- ✅ On-premise → Cần thiết kế self-hosted, quản lý infrastructure
- ✅ Cloud → Có thể dùng managed services (RDS, S3, Lambda...)
- ✅ Hybrid → Phức tạp hơn về networking và security

**Trả lời**:
```
[Stakeholder điền vào đây]
```

---

### Q2: Database hiện tại
**Câu hỏi**: Công ty đang dùng database gì? Có preference không?

**Options**:
- [ ] **PostgreSQL** (recommended cho structured data + JSON)
- [ ] **MySQL/MariaDB**
- [ ] **MongoDB** (document-oriented)
- [ ] **SQL Server**
- [ ] **Oracle**
- [ ] **Chưa có, cần đề xuất**

**Follow-up questions**:
- Có team DBA chuyên quản lý không?
- Có license hiện có không? (SQL Server, Oracle rất đắt)
- Có yêu cầu về backup/recovery không?

**Impact on design**:
- ✅ PostgreSQL → Tốt cho complex queries, JSON support, open-source
- ✅ MongoDB → Tốt cho flexible schema, horizontal scaling
- ✅ SQL Server/Oracle → Enterprise features nhưng licensing cost cao

**Đề xuất của tôi**: PostgreSQL (open-source, mature, có cả relational và JSON)

**Trả lời**:
```
[Stakeholder điền vào đây]
```

---

### Q3: Message Queue / Event Streaming
**Câu hỏi**: Có hệ thống message queue sẵn không?

**Options**:
- [ ] **RabbitMQ** (classic message broker)
- [ ] **Apache Kafka** (high-throughput event streaming)
- [ ] **Redis Pub/Sub** (simple, fast)
- [ ] **AWS SQS/SNS** (cloud managed)
- [ ] **Chưa có, cần đề xuất**

**Use cases trong hệ thống**:
- Async processing: Audio → STT → Scoring pipeline
- Notification delivery queue
- CRM scan scheduling

**Impact on design**:
- ✅ RabbitMQ → Dễ setup, đủ cho medium scale
- ✅ Kafka → Overkill nếu < 10K messages/sec, nhưng tốt cho future scale
- ✅ Redis → Đơn giản nhất, tốt cho quick MVP

**Đề xuất của tôi**: RabbitMQ (balance giữa simplicity và features)

**Trả lời**:
```
[Stakeholder điền vào đây]
```

---

### Q4: Budget cho Cloud Services
**Câu hỏi**: Có budget cho external services không?

**Services cần trả tiền**:
1. **Speech-to-Text**: ~$0.02-0.05/minute
   - 10,000 calls/month × 5 min avg = 50,000 min = $1,000-2,500/month
2. **Object Storage (S3/similar)**: ~$0.02/GB/month
   - 10,000 calls × 5MB audio = 50GB = $1/month (cheap)
3. **Email service**: ~$1/10,000 emails (SendGrid, AWS SES)
4. **SMS**: ~$0.05/SMS (nếu dùng)

**Total estimate**: $1,500-3,000/month cho 10K calls

**Options**:
- [ ] **Có budget** → Dùng cloud services (recommended)
- [ ] **Budget hạn chế** → Self-host một số services (phức tạp hơn)
- [ ] **Không có budget** → Cần tìm giải pháp open-source/free tier

**Trả lời**:
```
[Stakeholder điền vào đây]
Budget estimate: _______ USD/month
```

---

## SECTION B: Integrations

### Q5: CRM System
**Câu hỏi**: CRM hiện tại là gì?

**Options**:
- [ ] **Salesforce**
- [ ] **Microsoft Dynamics**
- [ ] **SAP CRM**
- [ ] **HubSpot**
- [ ] **Zoho CRM**
- [ ] **Custom in-house CRM**
- [ ] **Chưa có CRM** (!)

**Thông tin cần biết**:
- Tên CRM: ______________
- Có API documentation không? (link): ______________
- Có API key/credentials để test không?
- Rate limits: _______ requests/minute
- Authentication method: [ ] API Key [ ] OAuth 2.0 [ ] Other

**Impact on design**:
- ✅ Salesforce/major vendors → Có SDK sẵn, documentation tốt
- ✅ Custom CRM → Cần reverse-engineer API, có thể không stable
- ✅ Chưa có CRM → Cần thiết kế data model cho customer/tickets trong hệ thống

**Trả lời**:
```
[Stakeholder điền vào đây]
CRM name: 
API docs: 
Rate limits:
Auth method:
```

---

### Q6: CRM API Details
**Câu hỏi**: CRM API có những endpoints nào cần thiết?

**Endpoints cần có**:
- [ ] GET /customers/{id} - Lấy thông tin khách hàng
- [ ] GET /tickets?call_id={id} - Lấy tickets theo call
- [ ] GET /opportunities?customer_id={id} - Lấy opportunities
- [ ] POST /notes - Tạo ghi chú (optional)

**Dữ liệu cần lấy**:
- ✅ Customer: name, status, segment, created_at
- ✅ Tickets: ticket_id, category, status, created_at, updated_at
- ✅ Opportunities: opportunity_id, stage, value, product_interest
- ✅ Notes: content, author, created_at

**Performance expectations**:
- Response time: < _____ ms (typical)
- Downtime: _____ % (SLA của CRM)

**Trả lời**:
```
[Stakeholder điền vào đây]
Available endpoints:

Expected response time:
CRM uptime SLA:
```

---

### Q7: PBX System
**Câu hỏi**: Hệ thống tổng đài là gì?

**Options**:
- [ ] **Cisco Unified Communications**
- [ ] **Avaya**
- [ ] **3CX**
- [ ] **Asterisk/FreePBX**
- [ ] **Cloud PBX** (RingCentral, 8x8, Vonage)
- [ ] **Custom/Local vendor**

**Thông tin cần biết**:
- Tên PBX: ______________
- Format audio: [ ] WAV [ ] MP3 [ ] OGG [ ] Other: ____
- Sample rate: _____ Hz (8000, 16000, 44100?)
- Channels: [ ] Mono [ ] Stereo [ ] Separate (agent + customer)

**Cách deliver audio files**:
- [ ] **FTP/SFTP** → PBX upload files định kỳ
- [ ] **REST API** → PBX call webhook với audio URL
- [ ] **Real-time stream** → WebSocket/RTP
- [ ] **Manual upload** → Agent upload sau cuộc gọi (không khuyến nghị)

**Impact on design**:
- ✅ FTP → Cần scheduled poller, batch processing
- ✅ Webhook → Real-time, event-driven architecture
- ✅ Stream → Phức tạp nhất, cần streaming pipeline

**Trả lời**:
```
[Stakeholder điền vào đây]
PBX name:
Audio format:
Sample rate:
Delivery method:
```

---

### Q8: PBX Integration Method
**Câu hỏi**: PBX có hỗ trợ API/webhook không?

**Questions**:
- PBX có thể call webhook khi có cuộc gọi mới không?
- PBX có REST API để query call history không?
- Có access credentials để test không?

**Options**:
- [ ] **Yes** - PBX có API/webhook modern
- [ ] **Limited** - Chỉ có FTP hoặc database export
- [ ] **No** - Cần agent manually upload
- [ ] **Chưa rõ** - Cần confirm với IT team

**Trả lời**:
```
[Stakeholder điền vào đây]
```

---

## SECTION C: Data & Compliance

### Q9: Compliance Requirements
**Câu hỏi**: Có yêu cầu compliance đặc biệt không?

**Regulations to consider**:
- [ ] **GDPR** (EU customers)
- [ ] **PDPA** (Vietnam Personal Data Protection)
- [ ] **PCI-DSS** (nếu có payment info)
- [ ] **SOC 2** (nếu phục vụ enterprise clients)
- [ ] **ISO 27001**
- [ ] **Chưa có yêu cầu cụ thể**

**Impact on design**:
- ✅ GDPR → Right to erasure, data portability, consent management
- ✅ PDPA → Data residency trong VN, consent requirements
- ✅ PCI-DSS → Không lưu credit card info, encryption standards

**Trả lời**:
```
[Stakeholder điền vào đây]
Applicable regulations:

Specific requirements:
```

---

### Q10: Audio Retention Policy
**Câu hỏi**: Lưu audio bao lâu?

**Options**:
- [ ] **30 days** (minimum cho QA purposes)
- [ ] **90 days** (recommended cho training & disputes)
- [ ] **1 year** (nếu có legal requirements)
- [ ] **Forever** (not recommended - storage cost)

**Legal/Compliance input**:
- Legal team có yêu cầu gì không?
- Có quy định về informed consent (thông báo cho KH là đang ghi âm)?

**Storage cost estimation**:
- 10,000 calls/month × 5MB avg = 50GB/month
- 90 days retention = 150GB total = ~$3-5/month (S3)
- 1 year = 600GB = ~$12-20/month

**Trả lời**:
```
[Stakeholder điền vào đây]
Retention period: _____ days
Legal requirements:
```

---

### Q11: Data Residency
**Câu hỏi**: Data phải được lưu tại Việt Nam không?

**Context**:
- Một số quy định yêu cầu personal data của công dân VN phải lưu trong VN
- Cloud providers có data centers tại VN: AWS (coming), Azure (available), VNG Cloud, Viettel Cloud

**Options**:
- [ ] **Yes, mandatory** → Chọn provider có VN region
- [ ] **Preferred but not mandatory** → Có thể dùng Singapore region
- [ ] **No requirement** → Flexible

**Impact on design**:
- ✅ VN-only → Giới hạn provider choices, có thể cost cao hơn
- ✅ No restriction → Nhiều options, cost thấp hơn (Singapore, US regions)

**Trả lời**:
```
[Stakeholder điền vào đây]
```

---

## SECTION D: Users & Access

### Q12: User Scale
**Câu hỏi**: Có bao nhiêu users?

**User roles và số lượng**:
- Sales/CSKH Agents: _______ users
- QA Reviewers: _______ users
- Team Managers: _______ users
- System Admins: _______ users

**Total**: _______ concurrent users (peak time)

**Growth projection**:
- Year 1: _______ users
- Year 2: _______ users
- Year 3: _______ users

**Impact on design**:
- ✅ < 100 users → Simple deployment, single server có thể đủ
- ✅ 100-1000 users → Cần load balancer, caching
- ✅ > 1000 users → Multi-region, CDN cho frontend

**Trả lời**:
```
[Stakeholder điền vào đây]
Agents: 
QA Reviewers:
Managers:
Admins:
Total concurrent (peak):
```

---

### Q13: Authentication System
**Câu hỏi**: Công ty có SSO/LDAP không?

**Options**:
- [ ] **Active Directory** (Windows)
- [ ] **LDAP**
- [ ] **SAML SSO** (Okta, Azure AD, Google Workspace)
- [ ] **OAuth providers** (Google, Microsoft)
- [ ] **None** - Cần build authentication from scratch

**Preference**:
- [ ] **Integrate với existing** (recommended)
- [ ] **Build new system** (có thể dùng Auth0, Firebase Auth)

**Impact on design**:
- ✅ SSO → Dễ cho users (single sign-on), cần integrate với identity provider
- ✅ Build new → Phải manage passwords, forgot password flow, 2FA...

**Trả lời**:
```
[Stakeholder điền vào đây]
Current auth system:
Preferred approach:
```

---

### Q14: Mobile App Requirement
**Câu hỏi**: Có cần mobile app không?

**Options**:
- [ ] **Yes, mandatory** (Phase 1)
- [ ] **Nice to have** (Phase 2 or later)
- [ ] **No need** (web-only is fine)

**If Yes**:
- Platforms: [ ] iOS [ ] Android [ ] Both
- Use cases: 
  - [ ] Agents xem điểm on-the-go
  - [ ] Managers xem dashboard trên mobile
  - [ ] Push notifications
  - [ ] Other: ______________

**Impact on design**:
- ✅ Mobile required → Cần REST API design chuẩn, responsive design
- ✅ Web-only → Có thể đơn giản hóa architecture

**Trả lời**:
```
[Stakeholder điền vào đây]
Mobile needed:
Platforms:
Use cases:
```

---

## SECTION E: Additional Considerations

### Q15: Notification Preferences
**Câu hỏi**: Prefer kênh notification nào?

**For CRM compliance reminders**:
- [ ] **Email** (universal, cost-effective)
- [ ] **Slack** (nếu team dùng Slack)
- [ ] **Microsoft Teams** (nếu dùng Office 365)
- [ ] **SMS** (urgent only, có cost)
- [ ] **In-app notification** (web/mobile)

**Priority**: [Xếp thứ tự 1-5]

**Current tools**:
- Email server: ______________
- Chat platform: ______________

**Trả lời**:
```
[Stakeholder điền vào đây]
Preferred channels:
1. 
2.
3.
```

---

### Q16: Development Team
**Câu hỏi**: Team sẽ develop hệ thống này như thế nào?

**Options**:
- [ ] **In-house team** (công ty có developers)
- [ ] **Outsource/vendor**
- [ ] **Mix** (in-house + vendor)

**Tech stack preferences**:
- Backend language: [ ] Python [ ] Node.js [ ] Java [ ] .NET [ ] Other: ____
- Frontend: [ ] React [ ] Vue [ ] Angular [ ] Other: ____
- Team có experience với stack nào?

**Impact on design**:
- ✅ Python → Django/FastAPI, good for data processing/ML
- ✅ Node.js → Express/NestJS, good for real-time, JavaScript full-stack
- ✅ Java → Spring Boot, enterprise-grade
- ✅ .NET → ASP.NET Core, good for Windows ecosystem

**Trả lời**:
```
[Stakeholder điền vào đây]
Development approach:
Backend preference:
Frontend preference:
Team size:
Team experience:
```

---

### Q17: Timeline & Phases
**Câu hỏi**: Timeline mong muốn?

**Phases**:
- **Phase 1 (MVP)**: Core scoring + CRM compliance
  - Timeline: _______ months
  - Must-have features: ______________
  
- **Phase 2**: Advanced features (KNBH checklist, recommendations)
  - Timeline: _______ months
  
- **Phase 3**: Optimization & scale
  - Timeline: _______ months

**Constraints**:
- Hard deadline: ______________
- Budget per phase: ______________

**Trả lời**:
```
[Stakeholder điền vào đây]
Phase 1 timeline:
Phase 1 must-haves:

Hard deadlines:
```

---

## SUMMARY & NEXT STEPS

### Decision Matrix Template

Sau khi trả lời các câu hỏi trên, chúng ta sẽ fill bảng này:

| Decision Area | Choice | Rationale | Impact on Cost | Impact on Timeline |
|--------------|--------|-----------|----------------|-------------------|
| Infrastructure | [TBD] | | | |
| Database | [TBD] | | | |
| Message Queue | [TBD] | | | |
| STT Service | [TBD] | | | |
| Object Storage | [TBD] | | | |
| CRM Integration | [TBD] | | | |
| PBX Integration | [TBD] | | | |
| Notification | [TBD] | | | |
| Auth Method | [TBD] | | | |
| Compliance | [TBD] | | | |

### Action Items

**Sau khi có answers**:
1. ✅ Review và validate answers với stakeholders
2. ✅ Tạo Technology Decision Records (TDRs)
3. ✅ Vẽ Container Diagram (C4 Level 1) dựa trên decisions
4. ✅ Estimate chi tiết về cost và effort
5. ✅ Risk assessment based on choices
6. ✅ Create POC plan để validate critical integrations

### Approval Sign-off

**Stakeholders cần approve**:
- [ ] Business Owner: ______________ (Name & Date)
- [ ] Technical Lead: ______________ (Name & Date)
- [ ] IT/Infrastructure: ______________ (Name & Date)
- [ ] Legal/Compliance: ______________ (Name & Date)
- [ ] Finance (budget): ______________ (Name & Date)

---

## Notes for Stakeholders

**Tại sao cần trả lời chi tiết?**
- Mỗi quyết định ảnh hưởng đến architecture, cost, timeline
- Thay đổi sau này sẽ rất tốn kém (refactoring, re-deploy)
- Một số choices là one-way doors (khó rollback)

**Nếu chưa có câu trả lời chắc chắn**:
- Đánh dấu "TBD" và ghi rõ ai sẽ provide info
- Set deadline để có answer (recommend: trong 1 tuần)
- Có thể schedule workshop để discuss collectively

**Contact for questions**:
- Architect: ______________
- Project Manager: ______________
