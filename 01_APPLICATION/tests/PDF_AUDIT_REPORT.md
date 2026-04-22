# TCP-WO-007: PDF Accuracy Audit Report
## DRAFT — REQUIRES COMMANDER REVIEW
**Date**: 2026-04-17
**Auditor**: Agent B (Claude Code — PDF Audit Team)
**Source PDF**: `I:\Petition_to_Establish_Child_Support.pdf` (29 pages, ~200 form widgets)
**Application**: `I:\child_support_app\app.py` (1,201 lines)

---

## Overall Assessment

The PDF filling engine is in **excellent shape**. All 9 previously reported bugs have been confirmed FIXED. Three new actionable issues were found, plus two minor observations.

---

## ACTIONABLE ISSUES

### BUG 1: `wife_pregnant` disclosure collected but never mapped to PDF
- **Severity**: MEDIUM — data is collected from user but silently dropped
- **Location**: `intake.html` line ~1331 collects `wife_pregnant`; `intake.js` line ~1139 sends it; `app.py` radio_selections (lines 645-655) does NOT include it
- **PDF Widget**: Page 7 has `undefined_3` RadioButton (x2) at rects [387.5, 658.9] and [387.5, 689.0] — the wife-pregnant Yes/No buttons
- **Fix**: Add to `app.py` `build_field_maps()` around line 655:
```python
radio_selections["undefined_3"] = "yes" if disclosures.get("wife_pregnant") else "no"
```

### BUG 2: Orphan field references — dead code
- **Severity**: LOW — no user impact, but confusing for maintainers
- **Location**: `app.py` lines 244-245
- **Problem**: `text_fields["Telephone Numbers"]` and `text_fields["Daytime Telephone Numbers"]` reference field names that do NOT exist in the PDF. The PDF only has "Telephone Number" (singular).
- **Impact**: None — "Telephone Number" is already filled at line 243 and propagates correctly.
- **Fix**: Remove lines 244-245 (dead code cleanup).

### BUG 3: Petitioner employer address not mapped to page 4
- **Severity**: LOW — data not collected in intake, so nothing to map
- **Location**: Page 4 has "REQUESTING ADDRESS PROTECTION 6" (petitioner employer address row). App fills rows 1-5 but skips row 6.
- **Root cause**: Intake Step 8 only collects petitioner employer name and employment type, not employer street address.
- **Fix**: Either add petitioner employer address fields to intake Step 8, or leave as-is (acceptable for MVP).

---

## MINOR OBSERVATIONS

1. **Empty string write** (line 315): When petitioner employer exists but no city/state/zip is collected, `text_fields["Employer City State Zip Code"] = ""` writes an empty string. Harmless but triggers an empty widget update.

2. **Respondent county auto-detection** (lines 170-179): Only detects Maricopa (Phoenix metro), Pima (Tucson), and Coconino (Flagstaff). Cities in Navajo County (Show Low, Pinetop, Snowflake) map to empty string, leaving "County of Residence_2" blank on page 9. Consider adding Navajo County cities.

---

## PREVIOUSLY REPORTED BUGS — ALL CONFIRMED FIXED

| # | Issue | Status | Code Location |
|---|-------|--------|---------------|
| 1 | Page 4: Gender checkboxes "Male or"/"Female"/"Male or_2"/"Female_2" | FIXED | lines 532-544 |
| 2 | Page 4: Respondent DOB → field "1" | FIXED | line 261 |
| 3 | Page 4: SSN fields "Date of Birth MonthDayYear 2" (pet) and "2" (resp) | FIXED | lines 267-269 |
| 4 | Page 5: Child SSN → "Child Social Security Number 1" | FIXED | line 327 |
| 5 | Page 6: Text5=email, Text6=DOB (corrected swap) | FIXED | lines 344-347 |
| 6 | Page 10: Check Box19=Respondent role, Check Box22=Venue | FIXED | lines 567-575 |
| 7 | Page 16: Lines 20, 21, 29 at SINGLE_X=434 | FIXED | line 799 |
| 8 | Page 16: Dollar sign prefix removed from overlay | FIXED | dollar() fn line 764 |
| 9 | Page 26: Tax exemption alternating years | FIXED | lines 489-494 |

---

## RECOMMENDED FIXES (Priority Order)

1. **Add wife_pregnant radio mapping** — 1 line of code, fixes data loss
2. **Add Navajo County cities to resp_county detection** — improves form accuracy for local users
3. **Remove dead code** (lines 244-245) — cleanup
4. **Consider adding petitioner employer address to intake** — Phase 2 enhancement

---

## TEST DATA

A comprehensive test data file should be created at `Z:\SE_T1\THEMIS\01_APPLICATION\tests\full_test_data.json` exercising all field paths:
- Both parties with full PII (Show Low, AZ addresses)
- Petitioner=Mother, Respondent=Father
- Paternity method = married (Check Box31)
- Child with SSN and DOB
- Father $5,200/mo, Mother $3,800/mo income
- Medical split 35/65, travel split 35/65
- Arrears requested from 01/01/2024 ($5,826)
- Tax exemption = alternating years
- All disclosures = YES
- All jurisdiction boxes checked
- 120/245 day parenting time (Table B)
- Both employers with addresses

---

*TCP-WO-007 Complete — Agent B PDF Audit Team*
