# Scoring Criteria Decomposition – Phân rã tiêu chí chấm điểm (theo chuẩn)

Trạng thái: Draft v0.1 – Tài liệu này phân rã chi tiết các tiêu chí và tiêu chí con, cùng trọng số nội bộ và ví dụ M1/M2/M3. Mục tiêu: làm rõ cách tính điểm trong luồng chấm điểm (UC01).

Tổng quan trọng số theo loại cuộc gọi (nhắc lại)
- BH: KNGT 20% (2.0) | KNBH 70% (7.0) | NTT 10% (1.0)
- CSKH: KNGT 40% (4.0) | KNBH 50% (5.0) | NTT 10% (1.0)

Quy tắc trừ điểm theo mức lỗi
- KNGT, KNBH: M1 → trừ đúng điểm quy đổi của tiêu chí con; M2 → trừ 50% điểm NHÓM; M3 → điểm NHÓM = 0.
- NTT: M1 → trừ 20% điểm nhóm; M2 → trừ 50%; M3 → nhóm = 0.

A. KNGT – Kỹ năng giao tiếp (group)
A.1 Chào/xưng danh (10% điểm KNGT)
- Trọng số con (cùng trọng số; 3 mục → mỗi mục 1/3 của 10% KNGT)
  1) Xưng danh đầy đủ theo mẫu câu chuẩn (tên + đơn vị)
  2) Xác nhận tên khách hàng rõ ràng
  3) Thái độ khi chào: vui vẻ, hồ hởi, đúng mực
- Ví dụ lỗi
  - M1: Xưng danh đủ nhưng nói hơi nhỏ/nhanh; thiếu xác nhận tên KH
  - M2: Không chào/xưng danh khi KH đã chào; thái độ hời hợt
  - M3: Thái độ thiếu tôn trọng khi chào/xưng danh

A.2 Kỹ năng nói (tốc độ & âm lượng) (10% điểm KNGT)
- Trọng số con (cùng trọng số; 3 mục → mỗi mục 1/3 của 10% KNGT)
  1) Tốc độ nói so với baseline (speech rate)
  2) Âm lượng phù hợp (không quá to/nhỏ, ổn định)
  3) Độ rõ ràng phát âm/articulation (hạn chế ngọng/giọng địa phương gây khó hiểu)

A.2.x Đặc tả đo lường chi tiết

A.2.1 Tốc độ nói (Speech/Articulation Rate)
- Đầu vào: transcript đã diarization (AGENT/CUSTOMER), timestamps từng segment; VAD để tính thời lượng voiced.
- Thuật ngữ:
  • Speaking rate = tổng từ / tổng thời gian nói (bao gồm pause ngắn)
  • Articulation rate = tổng từ / tổng thời gian VOICED (loại bỏ im lặng) ← DÙNG cho chấm điểm vì công bằng hơn
- Cách tính trên mỗi segment của AGENT:
  1) Tính voiced_duration_s bằng VAD (loại bỏ im lặng > 200ms)
  2) Đếm tokens N (tiếng Việt: tách theo khoảng trắng hoặc syllable tokeniser)
  3) wpm_segment = 60 * N / max(1s, voiced_duration_s)
- Tổng hợp theo cuộc gọi: median_wpm (trung vị), p90_wpm, và tỉ lệ_thời_gian_vượt_ngưỡng(σ) theo công thức:
  • Với ngưỡng ±k·σ quanh baseline team/cohort: đếm phần trăm segments có wpm_segment ngoài khoảng [base−kσ, base+kσ]
- Baseline: base (wpm) và std (σ) được tính theo đội/chi nhánh/loại cuộc gọi trên tập “đạt chuẩn”. Cập nhật định kỳ.
- Mapping mức lỗi (ưu tiên customer impact nếu có):
  • OK: r_out(±1σ) < 20%
  • M1: r_out(±1σ) ≥ 20%
  • M2: r_out(±2σ) ≥ 30% HOẶC KH yêu cầu nhắc lại ≥ 3 lần/than phiền “nói nhanh/chậm”
  • M3: r_out(±2.5σ) ≥ 40% HOẶC gây hiểu sai nội dung quan trọng (OTP/điều khoản)
- Context-aware: Không phạt khi KH chủ động yêu cầu nói nhanh/chậm; khi đọc OTP/điều khoản; khi cần dừng để tra cứu.

A.2.2 Âm lượng (Volume/Loudness)
- Đầu vào: tín hiệu audio của lượt nói AGENT (sau diarization).
- Cách đo:
  1) Tính RMS theo cửa sổ 25ms, bước 10ms; chuyển dBFS.
  2) Lọc bằng VAD để chỉ giữ voiced frames.
  3) Tính các đặc trưng: mean_dbfs (trung bình), p05/p95 (dynamic range), clipping_ratio (tỉ lệ mẫu |x| ≈ 1.0), quá yên lặng ratio.
- Baseline: base_dbfs và std_dbfs theo thiết bị/đội.
- Ngưỡng gợi ý:
  • OK: |mean_dbfs − base_dbfs| ≤ 3dB VÀ frames_ngoài_±6dB < 10% VÀ 6dB ≤ (p95−p05) ≤ 24dB VÀ clipping < 0.5%
  • M1: |mean_dbfs − base_dbfs| trong (3,6] dB HOẶC frames_ngoài_±6dB ∈ [10%,25%]
  • M2: |mean_dbfs − base_dbfs| trong (6,9] dB HOẶC frames_ngoài_±6dB ∈ (25%,40%] HOẶC clipping ∈ [0.5%,1%]
  • M3: |mean_dbfs − base_dbfs| > 9dB HOẶC frames_ngoài_±6dB > 40% HOẶC clipping > 1% HOẶC KH than phiền “không nghe rõ/quá to” nhiều lần
- Context-aware: Không phạt khi KH xác nhận nghe rõ dù âm lượng hơi lệch; phạt nếu lệch gây repeat/hiểu sai.

A.2.3 Độ rõ phát âm / Giọng địa phương / Ngọng (Articulation Clarity)
- Mục tiêu: chỉ phạt khi “gây khó hiểu/hiểu sai”, không phạt việc có chất giọng địa phương tự nhiên.
- Tín hiệu đo lường kết hợp (3 nhánh):
  1) Low‑confidence từ ASR: tỉ lệ từ có confidence < τ_conf (ví dụ 0.85) trên lượt AGENT; hoặc WER_gap so với baseline team
  2) Customer impact: số lần KH yêu cầu nhắc lại (“nói lại/không nghe rõ”), explicit complaint markers
  3) Mẫu nhầm âm/phoneme confusions liên tục: các cặp phổ biến (l/n, s/x, ch/tr, d/gi/r, v/d/gi, tr/ch, r/g) xuất hiện lặp ≥ 3 lần trong 1 cuộc gọi ở các vị trí từ khác nhau
- Cách tổng hợp mức lỗi (ưu tiên impact):
  • Nếu 2) cho thấy KH nhắc lại ≥ 3 lần hoặc có complaint rõ → ít nhất M2
  • Nếu WER_gap ≥ 0.20 HOẶC low‑confidence ratio ≥ 0.30 → M2; ≥ 0.35 → M3
  • Nếu có confusions lặp lại và trùng với đoạn KH phải hỏi lại → nâng mức lên 1 bậc
  • Nếu 1) cao nhưng 2) thấp (KH vẫn hiểu, không hỏi lại) → tối đa M1
- Evidence bắt buộc: trích đoạn transcript (timestamps) nơi KH hỏi lại/complaint; danh sách từ low‑confidence; ví dụ confusions lặp lại.
- Context-aware: Không phạt khi đường truyền/xuất âm kém (network jitter) gây ASR thấp nhưng KH vẫn hiểu; không phạt khác biệt vùng miền nếu KH không bị ảnh hưởng.

- Ví dụ lỗi (tham chiếu baseline/σ và customer impact)
  - M1: Một số đoạn phát âm chưa rõ nhưng KH vẫn theo kịp; low‑confidence ratio ~0.15–0.25
  - M2: KH phải hỏi lại ≥ 3 lần hoặc WER_gap ≥ 0.20; confusions lặp lại nhiều
  - M3: Hiểu sai nội dung quan trọng do phát âm (sai số tài khoản/điều khoản), hoặc low‑confidence ratio ≥ 0.35 kèm complaint

A.3 Kỹ năng nghe & trấn an (40% điểm KNGT)
- Trọng số con (cùng trọng số; 4 mục → mỗi mục 1/4 của 40% KNGT)
  1) Không cắt lời; turn‑taking hợp lý
  2) Thể hiện đồng cảm/trấn an khi KH chưa hài lòng
  3) Paraphrase/xác nhận lại ý chính của KH
  4) Phản hồi kịp thời, đúng trọng tâm vấn đề KH nêu
- Ví dụ lỗi
  - M1: Thỉnh thoảng chen ngang nhẹ; trấn an còn chung chung
  - M2: Cắt lời nhiều, không xác nhận lại, khiến KH khó chịu
  - M3: Bỏ qua cảm xúc KH; tranh luận gay gắt; làm KH bức xúc

A.4 Thái độ giao tiếp & sử dụng ngôn ngữ (40% điểm KNGT)
- Trọng số con (cùng trọng số; 4 mục → mỗi mục 1/4 của 40% KNGT)
  1) Ngôn từ lịch sự/tôn trọng (không mỉa mai/tiêu cực)
  2) Thái độ tích cực/chuyên nghiệp; nhất quán trong cuộc gọi
  3) Cách diễn đạt rõ ràng, tránh jargon gây khó hiểu
  4) Giữ lời hứa/nhắc lại cam kết (nếu có)
- Ví dụ lỗi
  - M1: Một vài từ ngữ chưa lịch sự; diễn đạt dài dòng
  - M2: Lời lẽ không phù hợp bối cảnh, làm giảm trải nghiệm KH
  - M3: Ngôn từ xúc phạm/thiếu văn hoá

B. KNBH – Kỹ năng bán hàng (group)
Ghi chú: Áp dụng cho cả BH và CSKH nhưng tỷ trọng con theo chuẩn BH/CSKH khác nhau (điểm quy đổi đã nêu trong Master Spec). Bên dưới là tiêu chí con và phân rã; khi áp cho BH hoặc CSKH, dùng trọng số quy đổi đúng bảng.

B.1 Xác nhận thông tin (5% KNBH)
- Trọng số con (cùng trọng số; 3 mục)
  1) Kiểm tra thông tin KH hiện hữu (CRM/khai thác)
  2) Xác nhận đúng nhu cầu/vấn đề KH
  3) Xác nhận các thông tin cá nhân trọng yếu (nếu quy định)
- Ví dụ lỗi: không xác nhận; xác nhận mơ hồ; hiểu sai nhu cầu

B.2 Tiếp cận/Dẫn dắt (10% KNBH)
- Trọng số con (cùng trọng số; 3 mục)
  1) Đặt mục tiêu/agenda rõ ràng đầu cuộc gọi
  2) Dẫn dắt bằng câu hỏi mở, gợi mở hợp lý
  3) Giữ luồng trao đổi đúng trọng tâm, tránh lan man
- Ví dụ lỗi: bị động, ấp úng, phụ thuộc thông tin KH

B.3 Khai thác thực trạng & nhu cầu (BH 20%, CSKH 30% trong KNBH)
- Trọng số con (cùng trọng số; 4 mục)
  1) Khai thác hiện trạng (who/what/how now)
  2) Nhu cầu/mục tiêu mong muốn (desired outcomes)
  3) Vấn đề/pain points cụ thể
  4) Ràng buộc (ngân sách/thời gian/quy trình)
- Ví dụ lỗi: khai thác nông; nhu cầu chung chung; không cụ thể hoá

B.4 Nắm bắt vấn đề (10% KNBH)
- Trọng số con (cùng trọng số; 3 mục)
  1) Nhận diện đúng vấn đề cốt lõi
  2) Tóm tắt và xác nhận lại chính xác
  3) Tránh hỏi lặp/không cần thiết
- Ví dụ lỗi: hiểu sai; tóm tắt sai; hỏi lại nguyên xi gây phiền hà

B.5 Tư vấn & hỗ trợ sản phẩm (BH 30%, CSKH 5% trong KNBH)
- Trọng số con (cùng trọng số; 3 mục)
  1) Đề xuất sản phẩm/giải pháp đúng nhu cầu; thông tin chính xác
  2) Nêu rõ lợi ích/selling points, ví dụ minh hoạ
  3) Hướng dẫn/hỗ trợ cụ thể, khả thi
- Ví dụ lỗi: tư vấn mơ hồ; thông tin sai; thiếu chủ động hỗ trợ

B.6 Đề xuất giải pháp, xử lý rào cản, thuyết phục (BH 20%, CSKH 30% trong KNBH)
- Trọng số con (cùng trọng số; 3 mục)
  1) Nhận diện rào cản/chướng ngại (price, timing, policy…)
  2) Xử lý rào cản bằng bằng chứng/lợi ích phù hợp
  3) Kỹ năng thuyết phục/đàm phán dẫn tới đồng thuận
- Ví dụ lỗi: bỏ qua rào cản; lập luận yếu; không dẫn đến đồng thuận

B.7 Kết thúc (CTA/Follow-up) (BH 5%, CSKH 10% trong KNBH)
- Trọng số con (cùng trọng số; 3 mục)
  1) CTA rõ ràng (đăng ký/bước tiếp theo)
  2) Hẹn/kế hoạch follow‑up cụ thể (thời điểm, kênh)
  3) Lời cảm ơn/chào kết thúc đúng chuẩn
- Ví dụ lỗi: kết thúc cụt; CTA không rõ; không hứa hẹn theo dõi

C. NTT – Nhập hệ thống CRM/ticket (group – 10% tổng điểm)
- Trọng số con (cùng trọng số; 3 mục, mỗi mục 1/3 của 10%)
  1) Ghi chú CRM đầy đủ nội dung trao đổi
  2) Điền đúng/đủ thông tin bắt buộc theo quy định
  3) Tạo ticket/case khi thuộc điều kiện bắt buộc
- Quy tắc trừ điểm theo mức lỗi NTT: M1 −20%; M2 −50%; M3 nhóm = 0
- Ví dụ lỗi: ghi chú sơ sài; thiếu trường quan trọng; không tạo ticket bắt buộc

D. Ánh xạ tiêu chí → dữ liệu (evidence & signals)
- Mỗi tiêu chí con phải gắn được: evidence_ref (trích đoạn transcript + timestamps) và/hoặc signals (metrics), ví dụ:
  - Tốc độ nói: wpm vs baseline σ; tỉ lệ thời lượng vượt ngưỡng
  - Âm lượng: min/mean/max dBFS, ratio nói‑nhỏ/nói‑to
  - Cắt lời: interrupt_count, turn‑taking gaps
  - Đồng cảm/Trấn an: từ khoá/empathy markers + sentiment shift
  - Khai thác nhu cầu: số câu hỏi mở, cụm từ xác nhận nhu cầu
  - CTA/Follow‑up: keyword cues ("em sẽ liên hệ lại…", "hẹn…")
  - NTT: độ dài ghi chú, presence của trường bắt buộc, ticket_id

E. Nguyên tắc xử lý “context‑aware”
- Không phạt khi: đọc OTP/điều khoản; KH yêu cầu nói nhanh/chậm; đang tra cứu; KH chủ động ngắt quãng.
- Phạt nặng (ưu tiên) khi: KH hiểu sai; khiếu nại phát sinh do tư vấn sai; bỏ quên xử lý vấn đề/không có CTA.

F. Công thức gợi ý tính điểm (logic mô tả)
- Điểm nhóm = Điểm nhóm tối đa − (tổng trừ theo M1) − (penalty M2/M3 theo quy tắc nhóm)
- Điểm tổng = sum(điểm nhóm KNGT, KNBH, NTT)
- Khi confidence call_type thấp: dùng mixture‑of‑weights cho KNGT/KNBH để tính điểm nhóm tương ứng.

G. Acceptance (đối chiếu theo chuẩn)
- Mỗi báo cáo phải hiển thị: tổng điểm 0–10, label, passed; breakdown nhóm → tiêu chí → tiêu chí con (điểm & mức lỗi); evidence (trích đoạn + timestamps); summary; recommendations; script IDs.
- Nhãn mức lỗi M2/M3 phải có evidence rõ ràng.

Liên kết
- Master Spec: thiet-ke/00_Master_Spec.md
- UC01: mo-hinh-he-thong/use-case/UC01_Score_Call.md
