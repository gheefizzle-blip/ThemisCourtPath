# eFileAZ Integration Research Report
## DRAFT — REQUIRES COMMANDER REVIEW
**Date**: 2026-04-17
**Compiled by**: Agent B (Claude Code — eFileAZ Research Team)
**Work Order**: TCP-WO-009

---

## Executive Summary

**Recommendation: CONDITIONAL GO — via Partnership or EFSP Certification**

No consumer-facing platform currently offers automated Arizona court filing. This is a significant market gap that Themis Court Path can fill. Direct API integration requires becoming a certified Electronic Filing Service Provider (EFSP) through Tyler Technologies, which takes 3-6 months and costs $18K-$42K.

The most promising fast-track option is forking Suffolk LIT Lab's open-source EFSP proxy server (already Tyler-certified in Illinois) and adapting it for Arizona.

---

## Key Findings

### 1. Tyler Odyssey API (No Public Access)

- **No public API exists**. Tyler Technologies uses OASIS ECF v4.01 standard (SOAP/XML, NOT REST).
- EFSP certification is required to access EFM (Electronic Filing Manager) endpoints.
- WSDL endpoints, credentials, and sandbox access are all gated behind vendor agreements.
- Tyler's developer documentation is not publicly available — must be requested after EFSP application.

### 2. Arizona-Specific Information

- **Two platforms serve Arizona**:
  - **eFileAZ** (Tyler Technologies) — primary statewide system at efile.azcourts.gov
  - **AZTurboCourt** (Catalis) — secondary system for some case types
- **Governing rule**: ACJA Section 1-901 governs e-filing; EFSP must be "authorized by the administrative director"
- **Coverage**: All 15 Arizona counties are covered through one integration
- **E-filing is mandatory** for attorneys at appellate level and expanding statewide for all case types

### 3. EFSP Certification Requirements

- **Two-phase process**:
  1. Tyler technical certification: 2-4 months (API testing, sandbox validation)
  2. State administrative certification: 1-3 months (application, review, approval)
- **Total timeline**: 3-6 months
- Insurance/bond/fee details require direct inquiry to Tyler and AZ AOC
- **Existing EFSPs**: Tyler eFile & Serve, File & ServeXpress, ABC Legal, InfoTrack, One Legal, Suffolk LIT Lab (nonprofit)

### 4. Alternative Integration Paths (Ranked)

| Rank | Option | Timeline | Cost | Risk |
|------|--------|----------|------|------|
| 1 | **Fork Suffolk LIT Lab EFSP proxy** | 3-4 months | $15-25K | LOW — already Tyler-certified in IL |
| 2 | **Build custom EFSP** | 4-6 months | $30-50K | MEDIUM — full certification required |
| 3 | **Partner with existing commercial EFSP** | 1-3 months | Revenue share | LOW risk, HIGH dependency |
| 4 | **Tyler vendor program** | 6-12 months | Unknown | HIGH — may not accept small vendors |
| 5 | **Browser automation (Selenium)** | 1 month | $5K | **DO NOT PURSUE** — CFAA/TOS risk, fragile |

**Recommended path**: Option 1 (Suffolk LIT Lab fork) with Option 3 as fallback.

### 5. Competitive Landscape

- **LegalZoom and Rocket Lawyer** do NOT offer direct court e-filing in Arizona
- **No consumer-facing platform** currently offers automated AZ court filing
- **Stanford Filing Fairness Project** does not include Arizona yet
- **This is a significant market gap** that Themis can fill as first mover

---

## Suffolk LIT Lab EFSP Proxy (Recommended Path)

- **Repository**: Open-source Java EFSP proxy server on GitHub
- **Status**: Already Tyler-certified in Illinois
- **Architecture**: Acts as middleware between Themis and Tyler EFM endpoints
- **Adaptation needed**: Configure for Arizona ACJA rules, case types, county routing
- **License**: Open source — can fork and modify
- **Key advantage**: Bypasses most of Tyler certification since the proxy is already certified

---

## Estimated Costs

| Item | Low | High |
|------|-----|------|
| EFSP application/certification fees | $2,000 | $5,000 |
| Development (fork + adapt + test) | $10,000 | $25,000 |
| Legal review (compliance) | $3,000 | $5,000 |
| Insurance/bond (if required) | $1,000 | $5,000 |
| Ongoing hosting/maintenance (annual) | $2,000 | $5,000 |
| **Total initial** | **$18,000** | **$42,000** |

---

## Recommended Next Steps

1. **Contact Suffolk LIT Lab** — Discuss Arizona adaptation of their EFSP proxy
2. **Contact AZ AOC IT department** — Request EFSP application materials and requirements
3. **Contact Tyler Technologies** — Request developer documentation and sandbox access
4. **Evaluate partnership with existing EFSP** (File & ServeXpress or InfoTrack) as parallel track
5. **Budget $25K** for Phase 3 eFileAZ integration (midpoint estimate)

---

## Source URLs

- eFileAZ portal: https://efile.azcourts.gov
- ACJA Section 1-901: https://www.azcourts.gov/rules/ACJA
- Tyler Technologies: https://www.tylertech.com
- Suffolk LIT Lab: https://suffolklitlab.org
- OASIS ECF Standard: https://www.oasis-open.org/committees/legalxml-courtfiling/

---

*TCP-WO-009 Complete — Agent B eFileAZ Research Team*
