# Themis Court Path — Team Bootstrap Work Order
# Document ID: TCP-WO-000 Rev A
# Authority: Commander Gary Spear
# Date: 2026-04-16
# Classification: EXECUTION DIRECTIVE — Hand this entire file to a new Claude Code instance

---

## DIRECTIVE TO NEW CLAUDE CODE INSTANCE

You are being activated as the **Lead Architect** for the Themis Court Path project.
Your job is to read this document, understand the full project context, organize the
work, and deploy sub-agents to execute the work orders in parallel.

**You report to Commander Gary Spear.** He retains final decision authority on all
matters. Do not make financial, legal, or public-facing decisions without his approval.

---

## SECTION 1: PROJECT IDENTITY

| Field | Value |
|-------|-------|
| **Product Name** | Themis Court Path |
| **Full Brand** | Themis Court Path — an Athena Intelligence Division |
| **Parent Company** | Athena Intelligence (subsidiary of Atlas Systems Group) |
| **Domain** | themiscourtpath.com (TO BE REGISTERED — Commander action) |
| **Tagline** | "Your guided path through the court system" |
| **Named After** | Themis — Greek goddess of divine law, order, and justice |

### What This Product Does
Themis Court Path is an end-to-end self-help legal filing platform. It guides
self-represented litigants (pro-se parties), paralegals, and attorneys through
preparing, calculating, and electronically filing family court documents —
starting with Arizona child support petitions and expanding to divorce,
protective orders, custody modifications, and eventually all 50 US states.

### Why This Matters Commercially
- ~50,000 child support filings/year in Arizona alone
- ~25,000 divorce filings/year in Arizona
- Average attorney cost: $2,000-3,000 per filing
- Our price: $99 per filing
- Year 1 revenue target: ~$200K
- Year 3 revenue target: ~$2.1M
- Year 5 target (multi-state): $8-12M

---

## SECTION 2: WHAT ALREADY EXISTS

### Working Application (MVP)
A functional Flask web application has been built and tested. It runs on
localhost:5000 and generates filled PDF court documents from user input.

**Location on NAS**: `Z:\SE_T1\THEMIS\01_APPLICATION\`
**Dev working copy**: `I:\child_support_app\`

**Current capabilities**:
- 11-step intake wizard with elegant browser UI
- Arizona Child Support Guidelines calculator with AZ Schedule lookup (Line 21)
- Parenting time schedule builder with Table A/B automatic selection
- Live worksheet calculations (Lines 13-37 auto-compute)
- PDF form fill for Navajo County Petition to Establish Child Support
- Unified output: petition + worksheet merged into single PDF
- Auto-formatting for dates (MM/DD/YYYY), phone (XXX-XXX-XXXX), SSN (XXX-XX-XXXX)
- Legal disclosure questions, jurisdiction checkboxes, paternity method selection
- Tax exemption table population with alternating-year support

**Tech stack**:
- Python 3.13 + Flask 3.1.3
- PyMuPDF 1.26.7 (PDF form filling)
- Vanilla HTML/CSS/JS frontend (no framework)
- Currently runs as `python app.py` on localhost:5000

### Key Files

| File | Purpose |
|------|---------|
| `01_APPLICATION/app.py` | Flask backend — routes, PDF fill engine, worksheet overlay |
| `01_APPLICATION/templates/index.html` | Landing page |
| `01_APPLICATION/templates/intake.html` | 11-step intake wizard |
| `01_APPLICATION/templates/success.html` | Success/download page |
| `01_APPLICATION/static/css/style.css` | All styling |
| `01_APPLICATION/static/js/intake.js` | Wizard logic, validation, calculations, AZ Schedule table |
| `01_APPLICATION/static/themis-logo.png` | PLACEHOLDER — needs real logo (TCP-WO-002) |
| `01_APPLICATION/static/athena-logo.png` | Athena Intelligence parent logo |

### NAS Directory Structure

```
Z:\SE_T1\THEMIS\
├── 01_APPLICATION\        → Flask app (MAIN CODEBASE)
├── 02_LEGAL_RESEARCH\     → Statutes, guidelines, reference docs
├── 03_COUNTY_TEMPLATES\   → Per-county PDF templates
│   └── navajo\            → Navajo County petition (WORKING)
├── 04_BUSINESS\           → Revenue models, pricing, personas
│   └── revenue_streams.md → Full 8-stream revenue model
├── 05_DEPLOYMENT\         → Docker, Cloud Run, CI/CD (TO BE BUILT)
├── 06_MARKETING\          → Brand assets, website copy, pitches
├── 07_COMPLIANCE\         → ToS, privacy, UPL research (TO BE BUILT)
├── 99_ARCHIVE\            → Old versions
├── README.md              → Project overview
└── TCP-WO-001_MASTER_WORK_ORDERS.md → Detailed work orders (READ THIS)
```

### Source PDF Template
The blank Navajo County petition PDF is at:
- `I:\Petition_to_Establish_Child_Support.pdf` (original)
- `Z:\SE_T1\THEMIS\03_COUNTY_TEMPLATES\navajo\Petition_to_Establish_Child_Support_NAVAJO.pdf` (NAS copy)

This is a 29-page fillable PDF with form fields (text + checkbox) plus 3 static
worksheet pages (15-17) where we overlay calculated values using PyMuPDF insert_text().

### Company Logos
Located at `Z:\SE_T1\ASSETS\LOGOS\`:
- `Aegis Logo.PNG` — Sister product (infrastructure engineering)
- `Athena_Intelligence.png` — Parent company
- `Atlas_Systems_Group_cleaned_600dpi.png` — Corporate parent

### Brand Colors (existing palette)
- Primary navy: `#1a3a5c`
- Secondary blue: `#2c5282`
- Accent gold: `#c9a84c`
- Light bg: `#f7fafc`
- These are used consistently across the Aegis and Athena brands

### External Systems

| System | URL | Purpose |
|--------|-----|---------|
| eFileAZ | efile.azcourts.gov | Arizona statewide electronic court filing |
| SiteGround | siteground.com | Hosts AthenaIntelligence.com (GrowBig shared plan) |
| Google Cloud | console.cloud.google.com | Will host Themis app (Cloud Run) — PROJECT NOT YET CREATED |

**eFileAZ details**:
- Statewide system operated by AZ Supreme Court / Administrative Office of Courts
- Built on Tyler Technologies' Odyssey File & Serve platform
- One integration covers all 15 Arizona counties
- Tyler Odyssey is used by ~30 other US states — integration code is reusable
- Commander has an individual account (username: GarySpear, reg #138804)

---

## SECTION 3: EXISTING WORK ORDERS

The detailed work order package is at:
**`Z:\SE_T1\THEMIS\TCP-WO-001_MASTER_WORK_ORDERS.md`**

**READ THAT FILE IN FULL.** It contains 15 work orders (TCP-WO-001 through TCP-WO-015)
with complete specifications, task lists, deliverables, acceptance criteria, and
dependency chains.

### Summary of Work Orders

| WO | Title | Priority | Phase |
|----|-------|----------|-------|
| TCP-WO-001 | Register Domain + DNS Planning | CRITICAL | 1 |
| TCP-WO-002 | Create Themis Logo | HIGH | 1 |
| TCP-WO-003 | Google Cloud Project Setup | HIGH | 1 |
| TCP-WO-004 | Google Workspace Email Setup | HIGH | 2 |
| TCP-WO-005 | Cloud Run Deployment Package | HIGH | 1 |
| TCP-WO-006 | Production App Hardening | HIGH | 1 |
| TCP-WO-007 | PDF Accuracy Audit + Fixes | HIGH | 1 |
| TCP-WO-008 | Statewide County Template Collection | MEDIUM | 3 |
| TCP-WO-009 | eFileAZ API Research | MEDIUM | 3 |
| TCP-WO-010 | Compliance Package (ToS, Privacy, UPL) | MEDIUM | 1 |
| TCP-WO-011 | Athena Intelligence Marketing Site | MEDIUM | 2 |
| TCP-WO-012 | Stripe Payment Integration | MEDIUM | 2 |
| TCP-WO-013 | User Authentication System | MEDIUM | 2 |
| TCP-WO-014 | Process Server Marketplace Research | LOW | 3 |
| TCP-WO-015 | Attorney Network Partnership Model | LOW | 3 |

### Dependencies

```
TCP-WO-001 (Domain)
├── TCP-WO-003 (Google Cloud) → TCP-WO-005 (Deployment) → TCP-WO-006 (Hardening)
│                              → TCP-WO-009 (eFileAZ)     → TCP-WO-012 (Stripe)
│                                                          → TCP-WO-013 (Auth)
├── TCP-WO-004 (Workspace) — needs domain + Google Cloud
└── TCP-WO-011 (Marketing Site) — needs domain + logo

TCP-WO-002 (Logo) — no deps, can start immediately
TCP-WO-007 (PDF Audit) — no deps, can start immediately
TCP-WO-008 (County Templates) — no deps, can start immediately
TCP-WO-010 (Compliance) — no deps, can start immediately
TCP-WO-014 (Process Server Research) — no deps
TCP-WO-015 (Attorney Network Research) — no deps
```

---

## SECTION 4: YOUR MISSION AS LEAD ARCHITECT

### Step 1: Read and Internalize

Before deploying any sub-agents, you MUST read:
1. This document (you're reading it now)
2. `Z:\SE_T1\THEMIS\TCP-WO-001_MASTER_WORK_ORDERS.md` — the full work order details
3. `Z:\SE_T1\THEMIS\README.md` — project overview
4. `Z:\SE_T1\THEMIS\04_BUSINESS\revenue_streams.md` — monetization strategy
5. `Z:\SE_T1\THEMIS\01_APPLICATION\app.py` — understand the codebase

### Step 2: Verify Current State

Before starting any work, verify what exists:
```bash
# Check the app runs
cd "I:/child_support_app" && python app.py
# Open http://localhost:5000 and confirm it loads

# Check NAS structure
ls "Z:/SE_T1/THEMIS/"

# Check the source PDF exists
ls "I:/Petition_to_Establish_Child_Support.pdf"
```

### Step 3: Deploy Sub-Agents in Parallel

Launch teams sub-agents for work orders that have NO dependencies on each other.
The following can all run simultaneously from Day 1:

**Parallel Track A — Logo + Brand**
- Agent: TCP-WO-002 (Create Themis Logo)
- Skills needed: Image generation, brand design
- Deliverable: Logo files copied to application static directory

**Parallel Track B — PDF Audit + Fixes**
- Agent: TCP-WO-007 (PDF Accuracy Audit)
- Skills needed: PyMuPDF, coordinate mapping, PDF form field analysis
- Deliverable: All 29 pages verified correct, fixes applied to app.py
- CRITICAL CONTEXT: Read the "Deep Scan Results" section below — many issues
  were identified and partially fixed but need verification

**Parallel Track C — Compliance Research**
- Agent: TCP-WO-010 (ToS, Privacy Policy, UPL Research)
- Skills needed: Legal research, document drafting
- Deliverable: Draft legal documents in 07_COMPLIANCE/

**Parallel Track D — County Template Collection**
- Agent: TCP-WO-008 (Download templates for all 15 AZ counties)
- Skills needed: Web research, PDF analysis
- Deliverable: Templates + field maps in 03_COUNTY_TEMPLATES/

**Parallel Track E — eFileAZ Research**
- Agent: TCP-WO-009 (Tyler Odyssey API investigation)
- Skills needed: API research, web scraping analysis
- Deliverable: Integration feasibility report in 02_LEGAL_RESEARCH/

**Parallel Track F — Business Research**
- Agent: TCP-WO-014 + TCP-WO-015 (Process server + attorney marketplace)
- Skills needed: Market research, business model design
- Deliverable: Research reports in 04_BUSINESS/

### Step 4: Sequential Work (After Commander Actions)

These require Commander Gary Spear to take action first:

1. **Commander registers themiscourtpath.com** → unblocks TCP-WO-003, 004, 011
2. **Commander creates Google Cloud project** (with your guidance from TCP-WO-003) → unblocks TCP-WO-005
3. **You execute TCP-WO-005** (Deployment Package) → creates Dockerfile, deploy.sh
4. **You execute TCP-WO-006** (Production Hardening) → makes app Cloud Run ready
5. **Commander runs deploy.sh** → app goes live at *.run.app URL
6. **Commander configures DNS** → app accessible at app.themiscourtpath.com

### Step 5: Phase 2 Work (After App is Live)

Once the app is deployed and accessible:
1. TCP-WO-012 (Stripe Integration)
2. TCP-WO-013 (User Authentication)
3. TCP-WO-004 (Google Workspace)
4. TCP-WO-011 (Marketing Site)

---

## SECTION 5: CRITICAL CONTEXT FOR SUB-AGENTS

### Known PDF Issues (For TCP-WO-007 Agent)

The following issues have been identified in prior sessions. Some were fixed,
some need verification, some may still be outstanding:

**Fixed (needs verification)**:
- Page 4: Gender checkboxes — corrected field names to "Male or" / "Female" / "Male or_2" / "Female_2"
- Page 4: Respondent DOB was going to wrong field — reverted to field "1"
- Page 4: SSN fields mapped — petitioner = "Date of Birth MonthDayYear 2", respondent = "2"
- Page 4: Contact phone, email, employer fields now mapped
- Page 5: Child SSN field corrected to "Child Social Security Number 1"
- Page 6: Email/DOB swap FIXED — Text5=email, Text6=DOB (both parties)
- Page 10: Checkbox mapping corrected — Check Box19=Respondent is Mother (NOT venue), Check Box22=Venue
- Page 16: Single-column lines 20, 21, 29 moved to SINGLE_X=434 (from FATHER_X=390)
- Page 16: Dollar sign prefix removed from overlay text (form has printed $)
- Page 26: Tax exemption table now populates for alternating-year selections

**Needs full verification**:
- All 32+ checkboxes across pages 7, 8, 10, 11, 12, 20-23, 26, 29
- Radio button groups on page 7 (Yes_2/No_2, Yes_3/No_3 etc.)
- Parenting time day counts on page 16 Line 33
- All coordinate positions on worksheet pages 15-17

**Known architecture of app.py PDF engine**:
- `build_field_maps(data)` returns `(text_fields, checkboxes, checkboxes_uncheck, radio_selections)`
- `fill_worksheet_pages(doc, data)` overlays text on static pages 15-17 using coordinate-based insert_text()
- `_fill_doc(doc, track_fields)` iterates all widgets and applies text + checkboxes + radio selections
- Two-column worksheet values: FATHER_X=400, MOTHER_X=497
- Single-column worksheet values: SINGLE_X=434
- `dollar()` helper returns formatted number WITHOUT $ prefix (form already has $)

### Known Architecture Decisions

**Parenting Time Schedule Builder**:
- Frontend has a visual schedule builder (weeknights, weekends, holidays, summer, etc.)
- Auto-calculates annual overnight totals for Father and Mother
- Determines Table A (<110 non-custodial days) vs Table B (110+ days)
- Table A/B percentage lookup is hardcoded in calculateWorksheet() in intake.js
- Override option allows direct day-count entry

**AZ Child Support Schedule (Line 21)**:
- Full schedule table encoded in intake.js as AZ_CS_SCHEDULE array
- Covers $950-$30,000 combined monthly income, 1-6 children
- Linear interpolation between data points
- 2022 AZ Guidelines revision (effective Jan 2023)

**Tax Exemption Table (Page 26)**:
- 6 rows of child name, year, petitioner/respondent checkboxes
- Fields: 1_4 through 6_2 (names), Check Box133-144 (pet/resp), "Petitioner    Respondent" through _6 (years)
- Alternating years: even offset = petitioner, odd = respondent
- Conditional-on-current-support checkbox: Check Box145-147

**eFileAZ Integration Path**:
- Statewide system at efile.azcourts.gov
- Tyler Technologies Odyssey File & Serve platform
- Same vendor used by ~30 other US states
- Commander has account: GarySpear (reg #138804)
- Phase 3 feature — research first (TCP-WO-009), build later

### Operational Constraints

- **NAS path**: `Z:\SE_T1\THEMIS\` — all project files live here
- **Dev path**: `I:\child_support_app\` — working copy, currently served by Flask
- **Platform**: Windows 11 Pro, bash shell via Git Bash
- **Python**: 3.13.5
- **SiteGround**: GrowBig shared plan — PHP/WordPress only, cannot run Python
- **Google Cloud**: Account exists but NO project created yet for Themis
- **Hosting plan**: Google Cloud Run (Flask in Docker container)
- **Marketing site**: WordPress on SiteGround at AthenaIntelligence.com

### Commander Preferences (from CLAUDE.md)

- Gary is a novice coder — provide step-by-step instructions with explanations
- Explain concepts and goals BEFORE diving into implementation
- Do not assume coding knowledge — be helpful, encouraging, insightful
- Gary learns fast and has a sharp eye for inconsistencies
- Licensed general contractor with newspaper editing background — values professional presentation
- "Better to have it and not need it" — comprehensive preparation over iterative approaches

---

## SECTION 6: GOVERNANCE

### Decision Authority

| Decision Type | Who Decides |
|---|---|
| Architecture, code structure, tool selection | Lead Architect (you) |
| Financial commitments (domain, hosting, Stripe) | Commander only |
| Legal content (ToS, disclaimers) | Commander reviews, Agent drafts |
| Brand/visual decisions | Commander approves, Agent proposes |
| Feature scope changes | Commander approves |
| Deployment to production | Commander authorizes |
| Public-facing content | Commander approves before publish |

### Communication Protocol

- Sub-agents report to Lead Architect (you)
- Lead Architect reports to Commander (Gary)
- No sub-agent communicates directly with Commander unless escalated
- All deliverables go to the NAS paths specified in each work order
- Use task tracking (TaskCreate/TaskUpdate) for all work items

### Quality Standards

- All code must be tested before marking a work order complete
- All PDFs must be visually verified (render as images and inspect)
- All legal/compliance content must include "DRAFT — REQUIRES COMMANDER REVIEW" header
- Documentation must be written at a level a novice coder can follow
- No secrets, passwords, or API keys in code files — use environment variables

### File Naming Convention

- Work orders: `TCP-WO-NNN_TITLE.md`
- Code files: snake_case
- Documents: Title_Case_With_Underscores
- Logos: Product_Name_variant_resolution.png

---

## SECTION 7: SUCCESS CRITERIA

### Phase 1 Complete When:
- [ ] themiscourtpath.com is registered
- [ ] Themis logo exists and is deployed in the app
- [ ] App deploys successfully to Google Cloud Run
- [ ] All 29 PDF pages fill correctly (verified by visual audit)
- [ ] Terms of Service and Privacy Policy drafted
- [ ] App is accessible at app.themiscourtpath.com (or similar)

### Phase 2 Complete When:
- [ ] Users can pay $99 via Stripe and receive their filled PDF
- [ ] User accounts work (login, register, view past filings)
- [ ] Google Workspace email is active (gary@themiscourtpath.com)
- [ ] AthenaIntelligence.com marketing site is live with Themis featured
- [ ] At least 5 beta users have tested the full flow

### Phase 3 Complete When:
- [ ] At least 3 additional AZ counties have working templates (Maricopa, Pima, Pinal)
- [ ] eFileAZ integration feasibility is determined (go/no-go)
- [ ] Process server marketplace is designed (even if not built)
- [ ] Attorney network model is designed (even if not recruited)
- [ ] Divorce module intake is at least drafted

---

## SECTION 8: BEGIN

1. Read `Z:\SE_T1\THEMIS\TCP-WO-001_MASTER_WORK_ORDERS.md` in full
2. Read `Z:\SE_T1\THEMIS\01_APPLICATION\app.py` to understand the codebase
3. Verify the app runs at localhost:5000
4. Ask Commander which Phase 1 work orders to prioritize
5. Deploy sub-agents for parallel tracks A through F (Section 4 Step 3)
6. Track all progress via TaskCreate/TaskUpdate
7. Report status to Commander at each milestone

**You are the Lead Architect. Own the delivery. Ask questions when blocked.
Ship quality work. Make Themis Court Path real.**

---

*TCP-WO-000 Rev A — Team Bootstrap Work Order*
*Prepared by: Agent B (Claude Code — Opus 4.6)*
*Authority: Commander Gary Spear*
*Date: 2026-04-16*
