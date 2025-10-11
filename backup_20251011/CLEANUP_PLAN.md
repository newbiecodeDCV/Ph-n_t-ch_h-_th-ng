# KẾ HOẠCH CLEAN UP DỰ ÁN

**Ngày:** 11/10/2025  
**Mục đích:** Sắp xếp lại cấu trúc, xóa files thừa, giữ tài liệu cần thiết

---

## 📁 CẤU TRÚC MỚI ĐỀ XUẤT

```
phan-tich-thiet-ke-he-thong/
│
├── README.md                           # Giữ lại - update navigation
├── MASTER_SPECIFICATION_CLEAN.md       # MỚI - Đặc tả tổng thể (không code)
├── REVIEW_REPORT.md                    # Từ REVIEW_THIET_KE_FINAL.md
│
├── thiet-ke/
│   ├── 00_Master_Spec.md              # GIỮ - Requirements gốc
│   ├── UC01_Call_Scoring_SPEC.md      # GIỮ - Use case chi tiết
│   ├── 02_Sequence_UC01.md            # GIỮ - Sequence diagram
│   ├── 03_Activity_UC01.md            # GIỮ - Activity diagram  
│   └── Speech_Rate_Module.md          # MỚI - Merge tất cả speech rate
│
└── docs/
    └── Archive/                        # Di chuyển files cũ vào đây
```

---

## 🗑️ DANH SÁCH FILES CẦN XÓA/ARCHIVE

### A. Files thừa cần XÓA NGAY

| File | Lý do | Action |
|------|-------|--------|
| `BAO_CAO_GIAI_PHAP_TOC_DO_NOI.md` | Duplicate content | DELETE |
| `BAO_CAO_NGAT_KHONG_DUNG_BASELINE.md` | Duplicate content | DELETE |
| `thiet-ke/00_Design_Decisions_Questionnaire.md` | Không cần thiết | DELETE |
| `thiet-ke/01_System_Context_Diagram.md` | Outdated | DELETE |
| `thiet-ke/12_SYSTEM_DESIGN_SPEECH_RATE.md` | Code quá nhiều | DELETE |
| `thiet-ke/13_SYSTEM_DESIGN_THEO_CASE_CHUAN.md` | Code quá nhiều, thay bằng MASTER_SPEC | DELETE |

### B. Files Speech Rate cần MERGE

**Merge 6 files này → 1 file `Speech_Rate_Module.md`:**
- `07_Segmentation_Strategy_Detailed.md`
- `08_Pause_Based_Splitting_Visual_Guide.md`
- `09_VAD_Latency_And_Text_Splitting.md`
- `10_COMPLETE_SPEECH_RATE_EVALUATION_GUIDE.md`
- `11_BOOTSTRAP_STRATEGY_NO_BASELINE.md`
- `05_Scoring_Criteria_Decomposition.md` (phần SR)

**Nội dung sau merge:**
1. Tổng quan module
2. Segmentation strategy
3. WPM calculation method
4. Thresholds & rules
5. Cold start approach
6. Customer impact detection

### C. Files cần GIỮ LẠI

| File | Lý do |
|------|-------|
| `README.md` | Entry point |
| `thiet-ke/00_Master_Spec.md` | Requirements gốc |
| `thiet-ke/UC01_Call_Scoring_SPEC.md` | Use case detail |
| `thiet-ke/02_Sequence_UC01_Call_Scoring.md` | Sequence flow |
| `thiet-ke/03_Activity_UC01_Call_Scoring.md` | Activity flow |
| `thiet-ke/04_Functional_Decomposition.md` | Function breakdown |
| `MASTER_SPECIFICATION_CLEAN.md` | Đặc tả mới (không code) |
| `REVIEW_THIET_KE_FINAL.md` | Review report |

---

## 🔨 THỰC HIỆN CLEAN UP

### Bước 1: Backup
```bash
# Backup toàn bộ
tar -czf backup_20251011.tar.gz .
```

### Bước 2: Xóa files thừa
```bash
# Xóa files báo cáo duplicate
rm BAO_CAO_GIAI_PHAP_TOC_DO_NOI.md
rm BAO_CAO_NGAT_KHONG_DUNG_BASELINE.md

# Xóa files thiết kế cũ
rm thiet-ke/00_Design_Decisions_Questionnaire.md
rm thiet-ke/01_System_Context_Diagram.md
rm thiet-ke/12_SYSTEM_DESIGN_SPEECH_RATE.md
rm thiet-ke/13_SYSTEM_DESIGN_THEO_CASE_CHUAN.md
```

### Bước 3: Merge Speech Rate files
- Tạo file mới: `thiet-ke/Speech_Rate_Module.md`
- Copy nội dung từ 6 files
- Loại bỏ code implementation
- Giữ lại specification & design

### Bước 4: Archive files cũ
```bash
# Tạo folder archive
mkdir -p docs/archive

# Move files cần archive
mv thiet-ke/07_*.md docs/archive/
mv thiet-ke/08_*.md docs/archive/
mv thiet-ke/09_*.md docs/archive/
mv thiet-ke/10_*.md docs/archive/
mv thiet-ke/11_*.md docs/archive/
```

### Bước 5: Update README
- Update navigation links
- Add structure documentation
- Quick start guide

---

## ✅ KẾT QUẢ SAU CLEAN UP

### Trước: 20+ files
```
├── Nhiều báo cáo trùng
├── 6-7 files Speech Rate  
├── Code implementation lẫn lộn
└── Khó navigate
```

### Sau: 8-10 files core
```
├── 1 Master Specification (no code)
├── 1 Speech Rate Module (merged)
├── Clear use cases & flows
└── Easy to navigate
```

---

## 📊 BẢNG SO SÁNH

| Aspect | Trước | Sau |
|--------|-------|-----|
| **Tổng số files** | 20+ | 8-10 |
| **Speech Rate docs** | 6-7 files | 1 file |
| **Code trong spec** | Nhiều | Không có |
| **Duplicate content** | Có | Đã xóa |
| **Navigation** | Khó | Dễ |
| **Maintainability** | Thấp | Cao |

---

## ⚠️ LƯU Ý QUAN TRỌNG

1. **KHÔNG XÓA** trước khi backup
2. **GIỮ LẠI** version history (git)
3. **TEST** tất cả cross-references sau khi move
4. **REVIEW** lại structure với team

---

## 📝 CHECKLIST THỰC HIỆN

- [ ] Backup toàn bộ project
- [ ] Xóa 6 files thừa đã liệt kê
- [ ] Merge 6 files Speech Rate → 1 file
- [ ] Archive files cũ vào docs/archive
- [ ] Update README với structure mới
- [ ] Review cross-references
- [ ] Commit với message rõ ràng

---

**Status:** READY TO EXECUTE  
**Estimated Time:** 30 phút  
**Risk:** Low (có backup)