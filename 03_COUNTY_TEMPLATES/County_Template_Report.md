# TCP-WO-008: Arizona Statewide County Template Report
## DRAFT — REQUIRES COMMANDER REVIEW
**Date**: 2026-04-17
**Compiled by**: Agent B (Claude Code — County Templates Team)

---

## Key Finding

A single state-standard (Type A) template engine can serve **11 of 15 counties**. Only Maricopa, Pima, Mohave, and Yuma require county-specific template work. All 15 counties accept e-filing via eFileAZ.

---

## County Classification Table

| County | Pop. | Type | Court Website | Notable Local Rules | Priority |
|--------|------|------|---------------|---------------------|----------|
| **Maricopa** | 4.4M | **B** | superiorcourt.maricopa.gov/llrc/family-court-forms/ | Custom LLRC packets, unique DRES form numbering, copyrighted forms | HIGHEST |
| **Pima** | 1.0M | **B** | sc.pima.gov/judges-courts/family-court/family-court-forms | Only Pima-issued forms accepted. File at 110 W. Congress, Tucson | HIGH |
| **Pinal** | 425K | **A/B** | pinalcourtsaz.gov/166/Family-Court | COSC forms at coscpinalcountyaz.gov. Contact: 520-866-5321 | HIGH |
| **Yavapai** | 232K | **A** | courts.yavapaiaz.gov — Self-Service Center | Hard-copy packets available for purchase (Packet #21) | MEDIUM |
| **Mohave** | 212K | **B** | mohavecourts.com/forms-and-form-kits | County-branded forms (revised 2025). Clerk: (928) 753-0713 x4213 | MEDIUM |
| **Yuma** | 203K | **B** | yumacountyaz.gov — Self-Service Center | Does NOT accept EZ-CourtForms. Bilingual (EN/ES) required | MEDIUM |
| **Coconino** | 145K | **A** | coconino.az.gov/864/Forms-and-Answers | Law Library: (928) 679-7540, Flagstaff | MEDIUM |
| **Navajo** | 110K | **A** | (in Themis already) | — | DONE |
| **Cochise** | 126K | **A** | cochise.az.gov/241/Superior-Court-Self-Help-Center | Attorneys must e-file since 3/2022 | LOW |
| **Gila** | 53K | **A** | gilacountyaz.gov — Family Law Forms | Packets include instructions + official docs | LOW |
| **Santa Cruz** | 46K | **A** | santacruzcountyaz.gov/130/Superior-Court | Must change county name from Maricopa to Santa Cruz on forms | LOW |
| **Graham** | 38K | **A** | graham.az.gov/781/Superior-Court-Forms | County hosts forms on DocumentCenter | LOW |
| **Apache** | 66K | **A/C** | azcourthelp.org | No dedicated county forms page | LOW |
| **La Paz** | 16K | **C** | azcourthelp.org | Refers to state resources only | LOW |
| **Greenlee** | 9K | **C** | azcourthelp.org | Smallest county, refers to state resources | LOW |

---

## Template Type Summary

- **Type A** (State-standard forms): 8 counties — Navajo, Yavapai, Coconino, Cochise, Gila, Santa Cruz, Graham, Pinal*
- **Type B** (County-custom forms): 5 counties — Maricopa, Pima, Mohave, Yuma, Pinal*
- **Type C** (No local PDFs, refers to state/eFileAZ): 3 counties — La Paz, Greenlee, Apache*

*Pinal straddles A/B — county-hosted but may use state-standard fields. Needs field-level verification.

---

## Recommended Integration Phases

1. **Phase 1 — State-Standard Engine**: Generalize existing Navajo template to accept any county name. Instantly covers ~8 counties (11% of AZ population beyond Navajo).
2. **Phase 2 — Maricopa**: Build DRES-series template. Covers 4.4M population (58% of AZ). Highest ROI.
3. **Phase 3 — Pima**: Build Pima-branded template. Covers 1.0M population (13% of AZ).
4. **Phase 4 — Mohave + Yuma**: County-specific kits. Yuma needs bilingual support.
5. **Phase 5 — Type C counties**: Direct users to eFileAZ.

**After Phases 1-3, Themis covers ~82% of Arizona's population.**

---

## Key Form Download URLs

| County | Form | URL |
|--------|------|-----|
| Maricopa | Petition DRES11f | superiorcourt.maricopa.gov/media/todbhemj/dres11fz.pdf |
| Pima | Family Court Forms | sc.pima.gov/law-library/forms |
| Pinal | Establish CS Packet | coscpinalcountyaz.gov/DocumentCenter/View/225 |
| State Standard | Establishing CS | azcourts.gov/selfservicecenter/Child-Support-Family-Law |
| AZ Court Help | Child Support | azcourthelp.org/forms/child-support |

---

## State-Level Resources

| Resource | URL |
|----------|-----|
| AZ Courts Self-Service Center | azcourts.gov/selfservicecenter |
| AZ Court Help — Child Support | azcourthelp.org/forms/child-support |
| eFileAZ (all 15 counties) | efile.azcourts.gov |
| AZ Court Filing Fees | azcourts.gov/courtfilingfees |

---

## Filing Fee Notes

Governed by A.R.S. 12-284 and ACJA 3-404. County boards may add local fees per A.R.S. 11-251.08. Fee waivers/payment plans available for low-income filers. Exact amounts vary by county and should be verified before integration.

---

*TCP-WO-008 Complete — Agent B County Templates Team*
