# Themis Court Path — Master Work Order Package
# Document ID: TCP-WO-MASTER-001 Rev A
# Authority: Commander Gary Spear
# Date: 2026-04-16
# Status: ACTIVE — Ready for Teams Session Execution

---

## Project Overview

**Product**: Themis Court Path
**Domain**: themiscourtpath.com (TO BE REGISTERED)
**Parent Company**: Athena Intelligence (subsidiary of Atlas Systems Group)
**NAS Location**: `Z:\SE_T1\THEMIS\`
**Working Dev Location**: `I:\child_support_app\`
**Current State**: MVP functional on localhost:5000 — needs rebranding completion, logo, deployment, and infrastructure setup

---

## Work Order Index

| WO # | Title | Priority | Depends On | Estimated Hours |
|------|-------|----------|------------|-----------------|
| TCP-WO-001 | Register Domain + DNS Planning | CRITICAL | None | 1 |
| TCP-WO-002 | Create Themis Logo | HIGH | None | 2-3 |
| TCP-WO-003 | Google Cloud Project Setup | HIGH | TCP-WO-001 | 1-2 |
| TCP-WO-004 | Google Workspace Email Setup | HIGH | TCP-WO-001, TCP-WO-003 | 1-2 |
| TCP-WO-005 | Cloud Run Deployment Package | HIGH | TCP-WO-003 | 3-4 |
| TCP-WO-006 | Production App Hardening | HIGH | TCP-WO-005 | 2-3 |
| TCP-WO-007 | PDF Accuracy Audit + Fixes | HIGH | None | 4-6 |
| TCP-WO-008 | Statewide County Template Collection | MEDIUM | None | 4-6 |
| TCP-WO-009 | eFileAZ API Research | MEDIUM | TCP-WO-003 | 3-4 |
| TCP-WO-010 | Compliance Package (ToS, Privacy, UPL) | MEDIUM | None | 3-4 |
| TCP-WO-011 | Athena Intelligence Marketing Site | MEDIUM | TCP-WO-001, TCP-WO-002 | 6-8 |
| TCP-WO-012 | Stripe Payment Integration | MEDIUM | TCP-WO-005, TCP-WO-006 | 3-4 |
| TCP-WO-013 | User Authentication System | MEDIUM | TCP-WO-005 | 4-6 |
| TCP-WO-014 | Process Server Marketplace Research | LOW | None | 2-3 |
| TCP-WO-015 | Attorney Network Partnership Model | LOW | None | 2-3 |

---

# TCP-WO-001: Register Domain + DNS Planning
**Priority**: CRITICAL — Do immediately before someone else takes it
**Assigned to**: Commander (manual action required)
**Estimated time**: 1 hour

## Objective
Register themiscourtpath.com and plan the DNS record structure for all services.

## Tasks

### 1.1 Register themiscourtpath.com
- **Registrar**: Recommend Namecheap or Google Domains (NOT SiteGround — keep domain registration separate from hosting for flexibility)
- **Duration**: 1 year with auto-renew enabled
- **Privacy**: Enable WHOIS privacy protection
- **Cost**: ~$12/year

### 1.2 Also register these defensive domains (optional but recommended)
- themiscourtpath.net (~$12)
- themiscourtpath.org (~$12)
- themis.law (~$100/year — premium TLD, worth it for email credibility)

### 1.3 Document the planned DNS configuration (DO NOT configure yet — just plan)

| Record Type | Host | Value | Purpose | When to Add |
|---|---|---|---|---|
| A | @ | SiteGround IP | Main marketing site (if hosting there) | Phase 2 |
| CNAME | www | themiscourtpath.com | www redirect | Phase 2 |
| CNAME | aegis | ghs.googlehosted.com | Aegis app subdomain (if needed) | Later |
| CNAME | app | ghs.googlehosted.com | Themis app on Cloud Run | TCP-WO-005 |
| MX | @ | (Google Workspace values) | Email routing | TCP-WO-004 |
| TXT | @ | google-site-verification=... | Domain verification | TCP-WO-004 |
| TXT | @ | v=spf1 include:_spf.google.com ~all | Email SPF | TCP-WO-004 |
| CNAME | _dmarc | (Google value) | Email DMARC | TCP-WO-004 |

### 1.4 Decide: Do we want AthenaIntelligence.com as the main corporate site with Themis as a subdomain?

**Option A**: Standalone domains
- athenaintelligence.com → Corporate site (SiteGround WordPress)
- themiscourtpath.com → Themis product app (Google Cloud Run)

**Option B**: Subdomain under Athena
- athenaintelligence.com → Corporate site
- themis.athenaintelligence.com → Themis product app

**Recommendation**: Option A — standalone domains give each product its own SEO authority and brand presence. Link them visually through shared Athena Intelligence parent branding.

## Deliverables
- [ ] themiscourtpath.com registered
- [ ] DNS configuration plan documented
- [ ] Decision recorded on Option A vs B

## Acceptance Criteria
Domain is registered, WHOIS privacy enabled, auto-renew on, login credentials stored securely.

---

# TCP-WO-002: Create Themis Logo
**Priority**: HIGH
**Assigned to**: Agent (image generation or design tool)
**Estimated time**: 2-3 hours
**Dependencies**: None

## Objective
Create a professional logo for Themis Court Path that:
- Matches the blue/silver palette of the Aegis logo and Athena Intelligence branding
- Incorporates scales of justice (Themis's iconic symbol)
- Optionally includes a subtle Hellenistic/Greek visual motif
- Works at multiple sizes: favicon (32px), header (44px height), landing page (120px), print (600dpi)

## Design Brief

### Visual Requirements
- **Primary symbol**: Scales of justice — the defining symbol of Themis
- **Optional elements**: Greek column, laurel wreath, subtle circuit/tech pattern (connecting legal tradition to modern software)
- **Typography**: "THEMIS" in bold, clean sans-serif; "COURT PATH" below in lighter weight
- **Colors**: Match existing palette:
  - Primary blue: #1a3a5c (dark navy)
  - Secondary blue: #2c5282 (medium blue)
  - Accent: #c9a84c (gold)
  - Silver/light: #cbd5e0
  - White background
- **Style**: Professional, trustworthy, modern but not trendy. Think law firm meets tech startup. NOT clip-art. NOT overly complex.

### Reference Logos (for style consistency)
- `Z:\SE_T1\ASSETS\LOGOS\Aegis Logo.PNG` — sister product, use as visual family reference
- `Z:\SE_T1\ASSETS\LOGOS\Athena_Intelligence.png` — parent company

### Deliverables
- [ ] `themis_logo_full.png` — Full logo with text (600dpi, transparent background)
- [ ] `themis_logo_icon.png` — Icon only, no text (for favicon, mobile, small uses)
- [ ] `themis_logo_header.png` — Sized for web header (44px height, transparent)
- [ ] `themis_logo_landing.png` — Sized for landing page (120px height, transparent)
- [ ] Copy all deliverables to:
  - `Z:\SE_T1\ASSETS\LOGOS\Themis_Court_Path.png` (alongside other company logos)
  - `I:\child_support_app\static\themis-logo.png` (app static dir, replacing placeholder)
  - `Z:\SE_T1\THEMIS\01_APPLICATION\static\themis-logo.png` (NAS app copy)
  - `Z:\SE_T1\THEMIS\06_MARKETING\` (source files)

### Acceptance Criteria
Logo renders cleanly at 32px and 600dpi. Visually harmonious when placed next to Aegis and Athena logos. Passes the "would this look credible on a court document?" test.

---

# TCP-WO-003: Google Cloud Project Setup
**Priority**: HIGH
**Assigned to**: Commander (requires billing account) + Agent (guidance)
**Estimated time**: 1-2 hours
**Dependencies**: TCP-WO-001 (domain registered)

## Objective
Create the Google Cloud project that will host the Themis Court Path application on Cloud Run.

## Step-by-Step Instructions

### 3.1 Go to [console.cloud.google.com](https://console.cloud.google.com)
- Sign in with your Google account (or create a Google account for business use)

### 3.2 Create a new project
- Click the project selector dropdown (top bar)
- Click "New Project"
- **Project name**: `Themis Court Path`
- **Project ID**: `themis-court-path` (or `themis-courtpath-prod`)
- **Organization**: Leave as "No organization" unless you've set up Google Workspace first
- **Billing account**: Link to your Google billing account (requires a credit card — you won't be charged until you exceed free tier)

### 3.3 Enable required APIs
Navigate to **APIs & Services → Library** and enable:
- [ ] Cloud Run API
- [ ] Cloud Build API
- [ ] Artifact Registry API (for container images)
- [ ] Secret Manager API
- [ ] Cloud SQL Admin API (for Phase 2)
- [ ] Cloud Storage API

### 3.4 Install Google Cloud CLI (if not already installed)
Download from: https://cloud.google.com/sdk/docs/install
Run: `gcloud init` and select the new project.

### 3.5 Create an Artifact Registry repository
```bash
gcloud artifacts repositories create themis-app \
  --repository-format=docker \
  --location=us-west1 \
  --description="Themis Court Path container images"
```

### 3.6 Verify setup
```bash
gcloud config list
# Should show project = themis-court-path
# Should show account = your-email@...
```

## Deliverables
- [ ] Google Cloud project created with ID `themis-court-path` (or similar)
- [ ] Billing account linked
- [ ] Required APIs enabled
- [ ] Artifact Registry repository created
- [ ] gcloud CLI installed and authenticated
- [ ] Project ID documented in `Z:\SE_T1\THEMIS\05_DEPLOYMENT\cloud_config.md`

## Acceptance Criteria
`gcloud run deploy --help` runs without error. Artifact Registry accepts test pushes.

---

# TCP-WO-004: Google Workspace Email Setup
**Priority**: HIGH
**Assigned to**: Commander (requires payment + domain verification)
**Estimated time**: 1-2 hours
**Dependencies**: TCP-WO-001 (domain registered), TCP-WO-003 (Google account)

## Objective
Set up Google Workspace for business email on themiscourtpath.com (and optionally athenaintelligence.com).

## Tasks

### 4.1 Sign up for Google Workspace
- Go to [workspace.google.com](https://workspace.google.com)
- **Plan**: Business Standard ($14/user/month) — recommended
- **Business name**: Athena Intelligence (or Atlas Systems Group)
- **Domain**: themiscourtpath.com
- **Admin email**: gary@themiscourtpath.com (this will be the first account)

### 4.2 Verify domain ownership
Google will ask you to add a TXT record to your DNS. At your domain registrar:
- Add TXT record: `@ → google-site-verification=XXXXXXXXXX` (Google provides the value)

### 4.3 Configure MX records at your domain registrar
Delete any existing MX records, then add:

| Priority | Host | Value |
|----------|------|-------|
| 1 | @ | ASPMX.L.GOOGLE.COM |
| 5 | @ | ALT1.ASPMX.L.GOOGLE.COM |
| 5 | @ | ALT2.ASPMX.L.GOOGLE.COM |
| 10 | @ | ALT3.ASPMX.L.GOOGLE.COM |
| 10 | @ | ALT4.ASPMX.L.GOOGLE.COM |

### 4.4 Configure SPF, DKIM, DMARC (email authentication — critical for deliverability)
- **SPF** (TXT record): `@ → v=spf1 include:_spf.google.com ~all`
- **DKIM**: Follow Google Admin Console → Apps → Gmail → Authenticate Email. Add the CNAME record provided.
- **DMARC** (TXT record): `_dmarc → v=DMARC1; p=quarantine; rua=mailto:gary@themiscourtpath.com`

### 4.5 Create email accounts
- `gary@themiscourtpath.com` — Primary admin / personal
- `info@themiscourtpath.com` — Public contact (alias or group)
- `support@themiscourtpath.com` — Customer support (alias or group)
- `legal@themiscourtpath.com` — For legal notices / ToS / compliance
- `billing@themiscourtpath.com` — Payment inquiries (alias or group)

### 4.6 Optional: Add athenaintelligence.com as a secondary domain
In Google Workspace Admin → Domains → Add domain. Then repeat MX/SPF/DKIM/DMARC for that domain. This lets you use `gary@athenaintelligence.com` from the same Workspace.

## Deliverables
- [ ] Google Workspace active with Business Standard plan
- [ ] Domain verified
- [ ] MX records configured and email flowing
- [ ] SPF, DKIM, DMARC configured
- [ ] 5 email accounts/aliases created
- [ ] Credentials stored securely
- [ ] Configuration documented in `Z:\SE_T1\THEMIS\05_DEPLOYMENT\workspace_config.md`

## Acceptance Criteria
Can send and receive email at gary@themiscourtpath.com. SPF/DKIM/DMARC passes (test at mail-tester.com).

---

# TCP-WO-005: Cloud Run Deployment Package
**Priority**: HIGH
**Assigned to**: Agent B (Claude Code)
**Estimated time**: 3-4 hours
**Dependencies**: TCP-WO-003 (Google Cloud project exists)

## Objective
Create all files needed to deploy the Themis Court Path Flask application to Google Cloud Run.

## Deliverables

### 5.1 `Dockerfile`
```
Location: Z:\SE_T1\THEMIS\05_DEPLOYMENT\Dockerfile
Also copy to: I:\child_support_app\Dockerfile
```
Requirements:
- Python 3.13 base image
- Install Flask, PyMuPDF, gunicorn
- Copy application code + static files + templates
- Bundle the Navajo County PDF template into the image
- Expose port via `$PORT` environment variable (Cloud Run injects this)
- CMD: gunicorn with appropriate workers

### 5.2 `requirements.txt`
```
Flask==3.1.3
PyMuPDF==1.26.7
gunicorn==22.0.0
```

### 5.3 `.dockerignore`
Exclude: `__pycache__`, `output/`, `.git/`, `*.pyc`, test files

### 5.4 `deploy.sh`
Shell script that:
1. Builds the container image
2. Pushes to Artifact Registry
3. Deploys to Cloud Run
4. Outputs the live URL

### 5.5 `cloudbuild.yaml` (optional — for CI/CD later)
Google Cloud Build config for automatic deployments on code push.

### 5.6 `cloud_config.md`
Document the Cloud Run service configuration:
- Region: us-west1 (closest to Arizona)
- Memory: 512MB (PyMuPDF needs memory for PDF operations)
- CPU: 1
- Max instances: 10 (scale limit for Phase 1)
- Min instances: 0 (scale to zero when idle)
- Timeout: 300 seconds (PDF generation can take a few seconds)
- Concurrency: 80

## Acceptance Criteria
Running `deploy.sh` from a machine with gcloud CLI authenticated successfully deploys the app and returns a working `*.run.app` URL that serves the Themis intake form.

---

# TCP-WO-006: Production App Hardening
**Priority**: HIGH
**Assigned to**: Agent B (Claude Code)
**Estimated time**: 2-3 hours
**Dependencies**: TCP-WO-005

## Objective
Make the Flask app production-ready (it currently runs in debug mode for development).

## Tasks

### 6.1 Environment-aware configuration
- Read `PORT` from environment (Cloud Run requirement)
- Disable Flask debug mode in production
- Use gunicorn as WSGI server (not Flask dev server)
- Set `SECRET_KEY` from environment variable or Secret Manager
- Set `FLASK_ENV=production`

### 6.2 Output directory handling
- Cloud Run containers have read-only filesystem except `/tmp`
- Change output directory to `/tmp/themis_output/` in production
- Generated PDFs are served immediately to the user and NOT persisted (Phase 1 design)

### 6.3 Source PDF bundling
- Bundle the Navajo County petition PDF into the Docker image at a fixed path
- Make `SOURCE_PDF` configurable by environment variable (for multi-county later)

### 6.4 Security headers
Add to every response:
- `X-Content-Type-Options: nosniff`
- `X-Frame-Options: DENY`
- `Strict-Transport-Security: max-age=31536000` (HTTPS only)
- `Content-Security-Policy: default-src 'self'`

### 6.5 Error handling
- Custom 404 and 500 error pages (branded with Themis)
- No stack traces shown to users in production
- Log errors to Cloud Run's built-in logging (stdout/stderr)

### 6.6 Rate limiting (basic)
- Limit `/api/submit` to 10 requests per minute per IP
- Prevents abuse of PDF generation (CPU-intensive)

## Deliverables
- [ ] Updated `app.py` with production configuration
- [ ] Error page templates
- [ ] Security headers middleware
- [ ] Rate limiting on submit endpoint
- [ ] Tested locally in both dev and production modes

## Acceptance Criteria
App runs correctly with `gunicorn app:app` (not `python app.py`). No debug info leaks. Error pages render with branding.

---

# TCP-WO-007: PDF Accuracy Audit + Fixes
**Priority**: HIGH
**Assigned to**: Agent B (Claude Code)
**Estimated time**: 4-6 hours
**Dependencies**: None

## Objective
Complete deep-scan audit of all 29 PDF pages. Fix every remaining field placement error and missing field.

## Known Outstanding Issues (from prior scan sessions)

### Critical Fixes
- [ ] Page 7: Radio button groups for legal disclosure questions — verify YES/NO selection logic works for all 5 questions + pregnancy question
- [ ] Page 10: Verify all 6 jurisdiction checkboxes (Check Box23-28) respond to user input correctly
- [ ] Page 11: Verify paternity method checkbox (Check Box29-31) responds correctly
- [ ] Page 11: Verify child support status checkbox (Check Box32-33) responds correctly
- [ ] Page 16: Verify lines 20, 21, 29 now render in SINGLE_X column (not FATHER_X)
- [ ] Page 16: Verify dollar signs don't double-up ($ prefix removed from overlay)
- [ ] Page 26: Verify tax exemption table populates correctly for "alternating years" selection

### Full Page-by-Page Re-Scan Required
- Generate a new test PDF with ALL fields populated (use a comprehensive test data set)
- Render all 29 pages as images
- Compare every rendered field against expected value
- Document any remaining misalignments in a validation report

### Test Data Set
Create a comprehensive test case that exercises EVERY field:
- Both parties with full info (SSN, DL, phone, email, employer, occupation)
- Child with SSN
- Both incomes provided
- Medical/travel split non-50/50 (e.g., 35/65)
- Arrears requested
- Tax exemption = alternating years
- All legal disclosures answered YES (to verify those render)
- All jurisdiction boxes checked
- Paternity = married
- Time-sharing = specific day counts with Table B

## Deliverables
- [ ] Test data JSON file at `Z:\SE_T1\THEMIS\01_APPLICATION\tests\full_test_data.json`
- [ ] Generated test PDF
- [ ] Validation report with page-by-page screenshots
- [ ] All fixes applied to `app.py` and synced to Z: drive

## Acceptance Criteria
Every field on every page is either correctly populated or intentionally blank (court-only fields). No data placement errors. No doubled $ signs. No wrong checkboxes.

---

# TCP-WO-008: Statewide County Template Collection
**Priority**: MEDIUM
**Assigned to**: Agent (research + download)
**Estimated time**: 4-6 hours
**Dependencies**: None

## Objective
Collect child support petition PDF templates for all 15 Arizona counties and create field maps for each.

## Arizona Counties (15 total)

| County | Population | Court Website | Priority |
|--------|-----------|---------------|----------|
| Maricopa | 4.4M | superiorcourt.maricopa.gov | HIGHEST |
| Pima | 1.0M | sc.pima.gov | HIGH |
| Pinal | 425K | pinalcountyaz.gov | HIGH |
| Yavapai | 232K | yavapai.us | MEDIUM |
| Mohave | 212K | mohavecourts.com | MEDIUM |
| Yuma | 203K | yumacountyaz.gov | MEDIUM |
| Coconino | 145K | coconino.az.gov | MEDIUM |
| Navajo | 110K | navajocountyaz.gov | DONE |
| Cochise | 126K | cochise.az.gov | LOW |
| Gila | 53K | gilacountyaz.gov | LOW |
| Santa Cruz | 46K | santacruzcountyaz.gov | LOW |
| Graham | 38K | graham.az.gov | LOW |
| La Paz | 16K | lapazcountyaz.gov | LOW |
| Apache | 66K | apachecountyaz.gov | LOW |
| Greenlee | 9K | greenlee.az.gov | LOW |

## Tasks Per County

### 8.1 Download the packet
- Find the child support petition packet on each county's court website
- Many counties link to the state-standard forms at azcourts.gov
- Some (Maricopa, Pima, Pinal) have their own custom packets

### 8.2 Categorize the template
- **Type A**: Uses state-standard forms (same field names as azcourts.gov)
- **Type B**: Uses county-custom forms (different field names — needs its own mapping)
- **Type C**: Points users to eFileAZ with no downloadable PDF (no template needed)

### 8.3 Create field map (for Type B counties only)
- Run the same widget inspection script used for Navajo
- Document all field names, positions, and types
- Map to intake data fields

### 8.4 Store templates
- Save to `Z:\SE_T1\THEMIS\03_COUNTY_TEMPLATES\{county_name}\`
- Include field map as `field_map.json`
- Include a `README.md` per county noting any county-specific local rules

## Deliverables
- [ ] PDF template downloaded for each county (or documented as Type C)
- [ ] Categorization table (Type A/B/C per county)
- [ ] Field maps for Type B counties
- [ ] All stored at `Z:\SE_T1\THEMIS\03_COUNTY_TEMPLATES\`

## Acceptance Criteria
At minimum Maricopa, Pima, and Pinal (covering 75% of AZ population) have working field maps. Remaining counties categorized.

---

# TCP-WO-009: eFileAZ API Research
**Priority**: MEDIUM
**Assigned to**: Agent (research)
**Estimated time**: 3-4 hours
**Dependencies**: TCP-WO-003 (Google Cloud project — for test environment)

## Objective
Research the eFileAZ electronic filing system API and document the integration pathway.

## Key URLs
- **Portal**: https://efile.azcourts.gov
- **Vendor**: Tyler Technologies (Odyssey File & Serve platform)
- **User account**: GarySpear (Reg #138804, Individual/Unaffiliated)

## Research Tasks

### 9.1 Document the manual filing workflow
- Log in to efile.azcourts.gov
- Walk through creating a test filing (DO NOT SUBMIT — just document the screens)
- Document: case types available, counties available, required fields, upload format
- Screenshot each step

### 9.2 Research Tyler Odyssey File & Serve API
- Tyler Technologies publishes an EFM (Electronic Filing Manager) API
- Documentation may be at: developer.tylertech.com or similar
- Look for: REST API endpoints, OAuth2 auth flow, submission payload format
- Determine: is API access available to individual registrants or only to approved vendors?

### 9.3 Research Arizona-specific EFM documentation
- Arizona Administrative Office of the Courts (AOC) may publish integration guides
- Contact: AZ AOC IT department (if needed) to request API access for a software vendor
- Check if a "Filing Service Provider" (FSP) registration is required

### 9.4 Identify alternative integration paths
- If direct API isn't available to us:
  - Browser automation (Selenium/Playwright) as a fallback
  - Partnership with an existing Filing Service Provider
  - Apply to become a registered EFM vendor

## Deliverables
- [ ] Manual workflow documentation with screenshots
- [ ] Tyler Odyssey API documentation summary
- [ ] Assessment: Can we integrate directly, or do we need vendor registration?
- [ ] Recommended integration path (API / browser automation / FSP partnership)
- [ ] All documentation stored at `Z:\SE_T1\THEMIS\02_LEGAL_RESEARCH\eFileAZ_Integration\`

## Acceptance Criteria
Clear go/no-go recommendation on API integration with timeline and cost estimate for implementation.

---

# TCP-WO-010: Compliance Package (ToS, Privacy, UPL)
**Priority**: MEDIUM
**Assigned to**: Agent (research + drafting)
**Estimated time**: 3-4 hours
**Dependencies**: None

## Objective
Draft the legal compliance documents required before going live.

## Deliverables

### 10.1 Terms of Service
- [ ] Platform description and limitations
- [ ] "This is NOT legal advice" disclaimer (prominent, repeated)
- [ ] User responsibilities (accuracy of information entered)
- [ ] Payment terms and refund policy
- [ ] Limitation of liability
- [ ] Dispute resolution (arbitration clause)
- [ ] Governing law: Arizona

### 10.2 Privacy Policy
- [ ] What data we collect (PII: names, DOBs, SSNs, addresses, income)
- [ ] How we use it (document preparation only)
- [ ] How we store it (encrypted, Cloud SQL, retained for X days)
- [ ] Who we share with (nobody — except e-filing portal as authorized by user)
- [ ] User rights (deletion, export, access)
- [ ] CCPA compliance (if serving California users later)
- [ ] Cookie policy

### 10.3 Unauthorized Practice of Law (UPL) Research
- [ ] Arizona Supreme Court Rule 31 — who can practice law in AZ
- [ ] Arizona Legal Document Preparer (LDP) rules — A.R.S. 12-2801 et seq
- [ ] Research: Do we need to register as an LDP?
- [ ] Research: What can software do that an LDP cannot? (Important distinction)
- [ ] Document: What our platform CAN and CANNOT say to users
- [ ] Draft: In-app disclaimers for specific decision points

### 10.4 In-App Disclaimer Language
- [ ] Landing page disclaimer
- [ ] Before each section that involves legal judgment (paternity method, jurisdiction, etc.)
- [ ] Before PDF generation: "Review all information — you are responsible for accuracy"
- [ ] Before e-filing (Phase 3): "This is a legal filing — once submitted it becomes a court record"

## Deliverables stored at
`Z:\SE_T1\THEMIS\07_COMPLIANCE\`

## Acceptance Criteria
ToS and Privacy Policy are complete enough to publish at launch. UPL research clearly identifies our legal boundaries. In-app disclaimers are ready to insert into HTML templates.

---

# TCP-WO-011: Athena Intelligence Marketing Site
**Priority**: MEDIUM
**Assigned to**: Agent (content) + Commander (WordPress implementation)
**Estimated time**: 6-8 hours
**Dependencies**: TCP-WO-001 (domain), TCP-WO-002 (logo)

## Objective
Build the corporate website for Athena Intelligence on SiteGround WordPress, featuring both Aegis Software and Themis Court Path as product divisions.

## Site Structure

```
AthenaIntelligence.com
├── Home
│   ├── Hero: "Intelligent Systems for the Real World"
│   ├── Two product cards: Aegis + Themis
│   └── CTA: Learn More about each
├── About
│   ├── Athena Intelligence mission
│   ├── Atlas Systems Group parent
│   └── Team / leadership
├── Products
│   ├── Aegis Software (infrastructure engineering platform)
│   │   ├── Overview
│   │   ├── Features
│   │   └── Contact for demo
│   └── Themis Court Path (legal filing platform)
│       ├── Overview + screenshots
│       ├── Features (intake wizard, calculator, e-filing)
│       ├── Pricing tiers
│       └── "Start Filing →" button → themiscourtpath.com
├── Pricing (Themis-focused)
│   ├── Self-File: $99
│   ├── Self-File Plus: $149
│   └── Professional plans
├── Resources
│   ├── Blog (SEO content: "How to file for child support in Arizona" etc.)
│   └── FAQ
├── Contact
│   ├── Contact form
│   ├── Email: info@athenaintelligence.com
│   └── Physical address (optional)
├── Legal
│   ├── Terms of Service
│   ├── Privacy Policy
│   └── Disclaimer
└── Footer
    ├── Athena Intelligence logo
    ├── Product links
    ├── Social media (if applicable)
    └── "Powered by Atlas Systems Group"
```

## WordPress Theme Recommendation
- **Astra** (free, fast, highly customizable) or
- **Flavor** (clean, professional, good for SaaS products)
- Use Elementor or Gutenberg for page building

## Deliverables
- [ ] Site structure document (this WO)
- [ ] Page content drafts (copy) for each page — stored at `Z:\SE_T1\THEMIS\06_MARKETING\website_copy\`
- [ ] Product screenshots from the live Themis app
- [ ] Pricing page content
- [ ] Blog post drafts (2-3 seed articles for SEO):
  - "How to File for Child Support in Arizona Without a Lawyer"
  - "Arizona Child Support Calculator: How the Guidelines Work"
  - "What to Expect When Filing a Petition to Establish Child Support"

## Acceptance Criteria
WordPress site is live on SiteGround at AthenaIntelligence.com with at least the Home, About, Products, and Pricing pages functional. Themis Court Path featured prominently with "Start Filing" button linking to the Cloud Run app.

---

# TCP-WO-012: Stripe Payment Integration
**Priority**: MEDIUM
**Assigned to**: Agent B (Claude Code)
**Estimated time**: 3-4 hours
**Dependencies**: TCP-WO-005, TCP-WO-006

## Objective
Add Stripe Checkout to the Themis app so users pay before generating documents.

## Flow
```
User completes intake → Review page → "Generate Documents — $99" button
→ Stripe Checkout session opens (hosted by Stripe — PCI compliant)
→ User pays → Stripe redirects back to /success?session_id=xxx
→ App verifies payment → Generates PDF → Serves download
```

## Tasks
- [ ] Create Stripe account at stripe.com
- [ ] Install `stripe` Python package
- [ ] Add Stripe publishable key + secret key as environment variables
- [ ] Create `/api/create-checkout-session` endpoint
- [ ] Create `/api/payment-success` webhook endpoint
- [ ] Update the "Generate Documents" button to initiate Stripe Checkout
- [ ] Handle successful payment → trigger PDF generation
- [ ] Handle failed/cancelled payment → return to review page
- [ ] Test with Stripe test keys (4242 4242 4242 4242)

## Deliverables
- [ ] Updated `app.py` with Stripe integration
- [ ] Updated `intake.html` with payment flow
- [ ] Stripe webhook secret stored in Google Secret Manager
- [ ] Test mode working end-to-end

## Acceptance Criteria
Complete flow: intake → pay $99 → PDF generated → download. Stripe dashboard shows test payments.

---

# TCP-WO-013: User Authentication System
**Priority**: MEDIUM
**Assigned to**: Agent B (Claude Code)
**Estimated time**: 4-6 hours
**Dependencies**: TCP-WO-005

## Objective
Add user accounts so customers can log in, view past filings, and manage their cases.

## Implementation
- Google OAuth 2.0 (Sign in with Google) — simplest for users
- Email/password fallback (Flask-Login + Werkzeug password hashing)
- PostgreSQL user table on Cloud SQL
- Session management via Flask sessions (backed by server-side storage)

## Deliverables
- [ ] Login / Register pages (branded with Themis)
- [ ] Google OAuth flow
- [ ] User database model (PostgreSQL via SQLAlchemy)
- [ ] "My Cases" dashboard page
- [ ] Session persistence
- [ ] Password reset flow

## Acceptance Criteria
User can register, log in, complete a filing, and see it listed in "My Cases" upon return.

---

# TCP-WO-014: Process Server Marketplace Research
**Priority**: LOW (Phase 2)
**Assigned to**: Agent (research)
**Estimated time**: 2-3 hours
**Dependencies**: None

## Objective
Research the process server marketplace opportunity in Arizona and outline the integration plan.

## Tasks
- [ ] Identify process server companies operating in Navajo, Maricopa, Pima, Pinal counties
- [ ] Research typical pricing for service of process in AZ ($50-200 range expected)
- [ ] Identify any licensing requirements for process servers in AZ
- [ ] Research existing process server marketplaces (ServeNow.com, ABC Legal, etc.)
- [ ] Outline the Themis marketplace feature (job posting, acceptance, proof of service upload)
- [ ] Draft partnership pitch for process server recruitment
- [ ] Document revenue share model (15-25% commission)

## Deliverables
- [ ] Research report at `Z:\SE_T1\THEMIS\04_BUSINESS\process_server_marketplace.md`
- [ ] List of 10+ process server companies in AZ with contact info
- [ ] Partnership pitch document

---

# TCP-WO-015: Attorney Network Partnership Model
**Priority**: LOW (Phase 2-3)
**Assigned to**: Agent (research + drafting)
**Estimated time**: 2-3 hours
**Dependencies**: None

## Objective
Design the attorney consultation + conversion revenue model and draft partnership materials.

## Tasks
- [ ] Research Arizona State Bar rules on attorney referral fees (AZ Rule 7.2)
- [ ] Research existing attorney referral platforms (Avvo, LegalMatch, Unbundled Attorney)
- [ ] Design the consultation flow (user → Themis → attorney matching → 20-min Zoom)
- [ ] Design the conversion fee structure (flat $750 vs 12% first-year)
- [ ] Draft attorney partnership agreement template
- [ ] Draft attorney recruitment pitch (email + one-pager)
- [ ] Identify 5-10 family law attorneys in Navajo/Maricopa counties for pilot

## Deliverables
- [ ] Revenue model document at `Z:\SE_T1\THEMIS\04_BUSINESS\attorney_network.md`
- [ ] Partnership agreement template at `Z:\SE_T1\THEMIS\07_COMPLIANCE\attorney_partnership_template.md`
- [ ] Attorney recruitment pitch at `Z:\SE_T1\THEMIS\06_MARKETING\attorney_pitch.md`
- [ ] Pilot attorney target list (5-10 names + contact info)

---

# Execution Priority Matrix

## Phase 1 — Launch MVP (Weeks 1-3)
Execute these work orders to get a paid product live:

| WO | Title | Owner |
|----|-------|-------|
| TCP-WO-001 | Register Domain | Commander |
| TCP-WO-002 | Create Logo | Agent |
| TCP-WO-003 | Google Cloud Project | Commander + Agent |
| TCP-WO-005 | Cloud Run Deployment | Agent |
| TCP-WO-006 | Production Hardening | Agent |
| TCP-WO-007 | PDF Accuracy Audit | Agent |
| TCP-WO-010 | Compliance (ToS minimum) | Agent |

## Phase 2 — Monetize (Weeks 4-8)
| WO | Title | Owner |
|----|-------|-------|
| TCP-WO-004 | Google Workspace Email | Commander |
| TCP-WO-012 | Stripe Payments | Agent |
| TCP-WO-013 | User Authentication | Agent |
| TCP-WO-011 | Marketing Site | Commander + Agent |

## Phase 3 — Scale (Months 3-6)
| WO | Title | Owner |
|----|-------|-------|
| TCP-WO-008 | County Templates | Agent |
| TCP-WO-009 | eFileAZ Integration | Agent |
| TCP-WO-014 | Process Server Marketplace | Agent |
| TCP-WO-015 | Attorney Network | Agent |

---

*End of Master Work Order Package*
*TCP-WO-MASTER-001 Rev A*
*Prepared by: Agent B (Claude Code)*
*Approved by: Commander Gary Spear*
