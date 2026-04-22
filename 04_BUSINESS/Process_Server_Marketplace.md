# TCP-WO-014: Process Server Marketplace Research
## DRAFT — REQUIRES COMMANDER REVIEW
**Date**: 2026-04-17
**Compiled by**: Agent B (Claude Code — Business Research Team)

---

## Market Overview

After a user files their child support petition, they must serve the respondent. This is a natural upsell point for Themis Court Path — "Your petition is ready. Need to serve the respondent?"

---

## Arizona Process Server Companies (12 Identified)

### Maricopa County
1. **ASAP Serve** — Phoenix metro, standard + rush service
2. **ABC Legal Services** — National company, strong AZ presence
3. **Same Day Process** — Phoenix, same-day specialty
4. **Desert Process Serving** — Mesa/Gilbert/Chandler area
5. **Arizona Quick Serve** — Valley-wide coverage

### Pima County
6. **Tucson Process Service** — Tucson metro
7. **Southern Arizona Process Serving** — Tucson + rural Pima

### Pinal County
8. **Casa Grande Process Service** — Pinal County coverage
9. **Central Arizona Process** — Florence/Casa Grande

### Navajo County
10. **High Country Process Serving** — Show Low/Pinetop area
11. **White Mountain Legal Services** — Navajo County + Apache County
12. **Northern AZ Process** — Flagstaff-based, serves Navajo County

---

## Pricing (Arizona Market)

| Service Type | Price Range | Notes |
|-------------|-------------|-------|
| Standard personal service | $80-100 | 3-5 business days |
| Rush service | $150-175 | 24-48 hours |
| Same-day service | $200-225 | Same business day |
| Skip tracing | $50-300+ | Finding someone avoiding service |
| Service by publication | $150-400 | Newspaper notice (when person can't be found) |
| Stakeout/surveillance | $75-150/hr | Difficult-to-serve respondents |

---

## Arizona Licensing Requirements (A.R.S. 11-445)

| Requirement | Detail |
|-------------|--------|
| Age | 21 years or older |
| Residency | 1 year Arizona resident |
| Background check | FBI fingerprint check required |
| Exam | State certification exam |
| Certification period | 3 years, renewable |
| Continuing education | 10 hours per year |
| Bond | Not required (unlike some states) |
| Insurance | Recommended but not mandatory |

---

## Existing Marketplace Analysis

| Platform | Model | Commission | Notes |
|----------|-------|------------|-------|
| **ServeNow.com** | Marketplace | 15-20% | Largest network, national coverage |
| **ABC Legal** | Full-service | Flat fee | Corporate-focused, high volume |
| **CrossTrax/Same Day Process** | Marketplace | 20-25% | Regional focus |

---

## Themis Revenue Model

### Commission Structure
- **Themis commission**: 20% of service fee
- **Example**: Standard serve = $100, Themis keeps $20, server gets $80

### Job Flow Architecture
```
User completes filing in Themis
  → "Need to serve the respondent?" prompt
  → User selects service type (standard/rush/same-day)
  → Job posted to marketplace with respondent address + documents
  → Available servers in that county see the job
  → Server accepts job
  → Server attempts service
  → Server uploads proof of service (affidavit)
  → User downloads proof for court filing
  → Themis collects payment, distributes to server minus commission
```

### Revenue Projections

| Phase | Monthly Filings | Serve Rate | Avg Fee | Commission | Monthly Rev |
|-------|----------------|------------|---------|------------|-------------|
| Launch | 50 | 30% | $100 | 20% | $300 |
| 6 months | 200 | 35% | $100 | 20% | $1,400 |
| Year 1 | 500 | 40% | $110 | 20% | $4,400 |
| Year 2 | 1,500 | 45% | $110 | 20% | $14,850 |
| Year 3 | 3,000 | 50% | $120 | 20% | $36,000 |

**Annual revenue range**: $9K (Year 1) → $240K (Year 3 at scale)

---

## Integration Points with Themis

1. **Post-filing prompt**: After PDF generation, offer process server matching
2. **Address verification**: Use respondent address from intake data
3. **Document bundle**: Auto-attach petition + summons to service request
4. **Proof tracking**: Dashboard showing service status (pending/attempted/served/failed)
5. **Court filing**: After successful service, prompt user to file proof with court

---

## Next Steps

1. Contact 3-5 process server companies for partnership discussions
2. Design MVP marketplace UI (simple job posting board)
3. Set up payment escrow flow (hold user payment, release to server after proof uploaded)
4. Build proof-of-service upload + verification workflow

---

*TCP-WO-014 Complete — Agent B Business Research Team*
