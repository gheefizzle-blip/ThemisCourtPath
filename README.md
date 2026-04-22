# Themis Court Path

**A Legal Filing Platform by Athena Intelligence**

A division of Atlas Systems Group
Domain: [themiscourtpath.com](https://themiscourtpath.com)

---

## Product Vision

Themis Court Path is an end-to-end self-help legal filing platform. It guides
self-represented litigants (pro-se parties), paralegals, and attorneys
through the process of preparing, calculating, and electronically filing
family court documents.

Named for **Themis**, the Greek goddess of divine law, order, and justice —
the product carries her scales in its visual identity.

### Current Capability (MVP — Arizona Child Support)

- Multi-step intake wizard (11 steps)
- Arizona Child Support Guidelines calculator with Schedule lookup (Line 21)
- Parenting time schedule builder with Table A/B automatic selection
- Live worksheet calculations (Lines 19-37)
- PDF form fill for Navajo County Petition to Establish Child Support
- Unified output document combining petition + worksheet

### Near-Term Roadmap

- **Phase 1**: Rebrand + Cloud Run deployment + user accounts + Stripe payments
- **Phase 2**: eFileAZ integration (statewide Arizona electronic filing)
- **Phase 3**: Case calendar + deadline tracking + email/SMS reminders
- **Phase 4**: Divorce, protective orders, custody modification modules
- **Phase 5**: Multi-state expansion (Tyler Odyssey states first)

---

## Directory Structure

| Folder | Purpose |
|--------|---------|
| `00_ARCHITECTURE/` | **System architecture, data classification, SOC 2 readiness, Phase 0 work orders** |
| `01_APPLICATION/` | Live Flask application codebase |
| `02_LEGAL_RESEARCH/` | AZ Guidelines, statutes, reference documents |
| `03_COUNTY_TEMPLATES/` | Per-county PDF form templates and field maps |
| `04_BUSINESS/` | Pricing, revenue models, customer personas |
| `05_DEPLOYMENT/` | Cloud Run, Docker, CI/CD configs |
| `06_MARKETING/` | Website copy, brand assets, product marketing |
| `07_COMPLIANCE/` | ToS, privacy, UPL research, disclaimers |
| `99_ARCHIVE/` | Historical versions |

**Master work order plan**: `TCP-WO-MASTER-002.md` (supersedes TCP-WO-MASTER-001)
**Architecture authority**: `00_ARCHITECTURE/ARCHITECTURE.md` (TCP-ARCH-001 Rev A)

---

## Brand Identity

- **Product name**: Themis (short form) / Themis Court Path (full form)
- **Parent company**: Athena Intelligence (subsidiary of Atlas Systems Group)
- **Domain**: themiscourtpath.com
- **Tagline (working)**: *Your guided path through the court system*
- **Brand heritage**: Greek mythology — Themis, goddess of divine law, mother
  of Dike (justice), Eunomia (order), and Eirene (peace)

### Athena Intelligence Product Family

| Product | Division | Purpose |
|---------|----------|---------|
| Aegis Software | Infrastructure | 100-year infrastructure engineering database |
| Themis Court Path | Legal Tech | Self-help court filing platform |

Both products share:
- Greek mythology brand family
- Blue/silver visual palette
- Athena Intelligence parent branding

---

## Key Strategic Findings

### eFileAZ is a Statewide System
`efile.azcourts.gov` is the Arizona Supreme Court's official electronic
filing system — **not** a per-county portal. One integration covers all
15 Arizona counties. Built on Tyler Technologies' Odyssey File & Serve
platform (also used by ~30 other states), giving us a reusable integration
pathway for multi-state expansion.

### Primary Revenue Streams

1. **Self-File** ($49-99 per filing) — pro-se litigants
2. **Attorney Referral Network** — commission on consultations + conversions
3. **Process Server Integration** — marketplace fee on service requests
4. **Paralegal/Firm subscriptions** ($49-299/month)
5. **County/Legal Aid licensing** (white-label, $5K-15K/year per county)

---

## Technical Stack

- **Backend**: Python 3.13 + Flask
- **PDF engine**: PyMuPDF (fitz)
- **Frontend**: HTML/CSS/JS (vanilla)
- **Hosting** (planned): Google Cloud Run
- **Database** (planned): Cloud SQL (PostgreSQL)
- **Payments** (planned): Stripe
- **E-Filing** (planned): Tyler Odyssey API via eFileAZ
- **Marketing site**: WordPress on SiteGround (AthenaIntelligence.com)

---

## Compliance Notes

**Unauthorized Practice of Law (UPL)** is the primary legal risk.
Themis Court Path is a document preparation and filing tool — NOT a
substitute for legal advice. All user-facing communications must:

- Disclaim that the platform does not provide legal advice
- Offer clear pathways to licensed attorneys
- Limit AI/automated guidance to factual/procedural information
- Include state-appropriate Terms of Service

See `07_COMPLIANCE/` for full UPL research and disclaimer language.

---

*Last updated: Session in progress*
*Project owner: Commander Gary Spear*
