# SiteGround Front-End Deployment Plan (TCP-WO-310)

## Status

DRAFT — REQUIRES COMMANDER REVIEW

## Document Authority

This plan covers deliverables 2, 3, 4, and 5 from TCP-WO-310:
- Site map
- Domain + DNS configuration plan
- SiteGround deployment checklist
- CTA routing confirmation

Companion document: `06_MARKETING/PAGE_SKELETONS.md` (deliverable 1).

## Architectural Boundary (Reaffirmed)

```
┌─────────────────────────────────────────────────────────────┐
│  themiscourtpath.com (root)                                 │
│  www.themiscourtpath.com                                    │
│  ─────────────────────────────────────────────────────────  │
│  HOST: SiteGround (WordPress)                               │
│  PURPOSE: Marketing, SEO, conversion                        │
│  NEVER HANDLES: SSN, DOB, case data, auth, payments         │
│  ALL CTAs ROUTE TO: app.themiscourtpath.com                 │
└─────────────────────────────────────────────────────────────┘
                          │
                          │ click "Start Filing"
                          ▼
┌─────────────────────────────────────────────────────────────┐
│  app.themiscourtpath.com                                    │
│  ─────────────────────────────────────────────────────────  │
│  HOST: Google Cloud Run (themis-app service)                │
│  PURPOSE: Secure intake + filing workflow                   │
│  HANDLES: Auth (TCP-WO-200), encrypted intake               │
│           (TCP-WO-201A), in-memory PDFs (TCP-WO-202),       │
│           Stripe payments (TCP-WO-300)                      │
└─────────────────────────────────────────────────────────────┘
```

---

## 1. Site Map

```
themiscourtpath.com
│
├── /                       Home (hero, how-it-works, pricing teaser, CTA)
├── /how-it-works           5-step workflow
├── /pricing                $99 flat-fee card + comparison
├── /faq                    8-10 conversion-blocking objections
├── /contact                Email + non-PII contact form
│
├── /privacy                Privacy Policy (from 07_COMPLIANCE)
├── /terms                  Terms of Service (from 07_COMPLIANCE)
├── /disclaimer             Disclaimer (from website_copy/legal)
│
└── /blog/                  (Future, post-launch — content already drafted
                             in website_copy/blog/ from TCP-WO-011)
```

Phase 1 launch = 8 pages: Home, How It Works, Pricing, FAQ, Contact, Privacy,
Terms, Disclaimer. Blog deferred to post-launch SEO sprint.

---

## 2. Domain + DNS Configuration Plan

### Current state

| Domain | Status |
|--------|--------|
| `themiscourtpath.com` | Registered on SiteGround (per Session 30 work) |
| `www.themiscourtpath.com` | Auto-handled by SiteGround |
| `app.themiscourtpath.com` | DNS configured Apr 21; SSL pending Cloud Run mapping |
| Cloud Run service URL | `themis-app-909223653643.us-west1.run.app` (live) |

### DNS records required at SiteGround DNS Zone Editor

| Type | Host | Value | TTL | Purpose | Status |
|------|------|-------|-----|---------|--------|
| A    | `@`         | SiteGround server IP (auto-assigned by SiteGround when site is created) | 3600 | Root domain → SiteGround | Pending |
| CNAME | `www`      | `themiscourtpath.com` | 3600 | www → root | Pending |
| CNAME | `app`      | `ghs.googlehosted.com` | 300 | app → Cloud Run | DONE Apr 21 |
| MX   | `@`         | Google Workspace values | 3600 | Email (TCP-WO-004 — future) | Pending |
| TXT  | `@`         | `v=spf1 include:_spf.google.com ~all` | 3600 | Email SPF (future) | Pending |
| TXT  | `_dmarc`    | `v=DMARC1; p=quarantine; rua=mailto:legal@themiscourtpath.com` | 3600 | Email DMARC (future) | Pending |

### Notes

- SiteGround auto-creates the A record for the root domain when you add
  `themiscourtpath.com` as a Site under your hosting plan. You should
  not need to enter the A record manually.
- The existing `app` CNAME stays as-is — that subdomain is owned by
  Cloud Run.
- Email-related records (MX, SPF, DMARC) are out of scope for this WO.
  Add them when TCP-WO-004 (Workspace email) is executed.

---

## 3. SSL Configuration

| Surface | Mechanism | Action |
|---------|-----------|--------|
| `themiscourtpath.com` | SiteGround Let's Encrypt (free, auto-renew) | Enable in Site Tools → Security → SSL Manager → Let's Encrypt → Install. Then Site Tools → Security → HTTPS Enforce → On. |
| `www.themiscourtpath.com` | Same Let's Encrypt cert (SAN includes www) | Auto-included when issuing for the root |
| `app.themiscourtpath.com` | Google-managed cert via Cloud Run domain mapping | Already requested Apr 21; provisions automatically once domain mapping is created via `gcloud run domain-mappings create` |

Verification (after issuance):
```bash
curl -sI https://themiscourtpath.com    | head -1   # expect 200/301
curl -sI https://www.themiscourtpath.com| head -1   # expect 200/301
curl -sI https://app.themiscourtpath.com| head -1   # expect 200 (when SSL completes)
```

---

## 4. SiteGround Deployment Checklist

### Phase A — Site provisioning (Commander, ~30 min)

- [ ] Log in to SiteGround → Websites → New Website
- [ ] Choose "Existing Domain" → `themiscourtpath.com` (already registered)
- [ ] Select "Start a New Website" → WordPress
- [ ] Set admin email = a Themis-internal address (NOT Commander's primary)
- [ ] Set strong admin password and store in password manager
- [ ] Skip "SG Site Scanner" upsell (optional, $1.65/mo)

### Phase B — Theme + plugins (Commander or Claude, ~20 min)

- [ ] Appearance → Themes → Add New → install **Astra** (free, lightweight)
- [ ] Appearance → Themes → Activate Astra
- [ ] Plugins → Add New → install + activate:
  - [ ] **Astra Starter Templates** (one-click site templates)
  - [ ] **WPForms Lite** (contact form, supports email-only delivery)
  - [ ] **WP Super Cache** (page cache for performance baseline)
  - [ ] **Yoast SEO** (sitemap.xml + meta tags)
- [ ] Settings → Permalinks → Post name (clean URLs)
- [ ] Settings → Reading → Disable "Discourage search engines" (production)

### Phase C — Brand assets (Commander or Claude, ~10 min)

- [ ] Media → Upload `Themis_Court_Path_logo.png` from `06_MARKETING/`
- [ ] Customize → Site Identity → Logo → select Themis logo
- [ ] Customize → Site Identity → Site Title = "Themis Court Path"
- [ ] Customize → Site Identity → Tagline = "Your guided path through the court system"
- [ ] Customize → Site Identity → Site Icon (favicon) → upload favicon (32x32 PNG)
- [ ] Customize → Global → Colors:
  - Primary:    `#1a3a5c` (navy)
  - Secondary:  `#2c5282` (medium blue)
  - Accent:     `#c9a84c` (gold)
  - Background: `#f7fafc` (light)

### Phase D — Pages (Claude or Commander, ~60 min)

For each of the 8 pages in the sitemap:
- [ ] Pages → Add New → set title from PAGE_SKELETONS.md
- [ ] Paste structured layout from PAGE_SKELETONS.md (or use long-form
  drafts from `website_copy/` if desired)
- [ ] Configure CTA buttons → URL = `https://app.themiscourtpath.com`
- [ ] Set page slug to match sitemap (e.g., `/how-it-works`)
- [ ] Publish

Then:
- [ ] Appearance → Menus → Create "Primary Menu" with:
  Home / How It Works / Pricing / FAQ / Contact
- [ ] Assign menu to Header
- [ ] Create "Footer Menu": Privacy / Terms / Disclaimer
- [ ] Assign menu to Footer

### Phase E — Verification (Claude or Commander, ~15 min)

- [ ] All 8 pages load over HTTPS
- [ ] No broken links (check footer + nav)
- [ ] Every "Start Filing" / "Create Account" CTA points to `app.themiscourtpath.com`
- [ ] Contact form delivers to `support@themiscourtpath.com` (test send)
- [ ] Mobile responsive (test on phone width)
- [ ] Page load < 2 seconds on test device (PageSpeed Insights)
- [ ] No JavaScript errors in browser console
- [ ] Privacy Policy / Terms / Disclaimer marked "DRAFT — pending legal review"

### Phase F — Post-launch (within 7 days)

- [ ] Submit sitemap to Google Search Console
- [ ] Verify Yoast SEO meta tags on each page
- [ ] Set up Google Analytics OR Plausible (privacy-friendly alternative)
- [ ] Schedule 3 SEO blog posts from `website_copy/blog/`

---

## 5. Performance Baseline

| Metric | Target | Notes |
|--------|--------|-------|
| Page load (mobile) | < 2 seconds | Astra theme + WP Super Cache should hit this |
| Page weight | < 500 KB per page | Logo at 600dpi is 2.7MB — must compress to ~100KB for web |
| Total HTTP requests | < 30 per page | Skip plugin bloat |
| Lighthouse Performance score | > 90 | Test before launch |

Asset prep:
- [ ] Compress `Themis_Court_Path_logo.png` to web-optimized (~80-150 KB) PNG/WebP
- [ ] Generate favicon variants (16x16, 32x32, 180x180 for Apple touch)
- [ ] No carousel/slider plugins (kill performance)
- [ ] No font-loading from Google Fonts in production if avoidable (use system fonts)

---

## 6. CTA Routing Confirmation

**This is the security-critical deliverable.** Every interactive
element on the marketing site that initiates a filing/auth/payment
workflow MUST route to the secure app.

### Authoritative routing table

| Surface | CTA text | Target URL |
|---------|----------|-----------|
| Home — Hero | "Start Filing" | `https://app.themiscourtpath.com` |
| Home — Hero (secondary) | "Sign In" | `https://app.themiscourtpath.com/auth/login` |
| Home — Pricing teaser | "Start Filing" | `https://app.themiscourtpath.com` |
| Home — Final CTA | "Start Filing" | `https://app.themiscourtpath.com` |
| How It Works — Step 1 | "Create Account" | `https://app.themiscourtpath.com/auth/register` |
| How It Works — Bottom | "Start Filing" | `https://app.themiscourtpath.com` |
| Pricing — Card CTA | "Start Filing" | `https://app.themiscourtpath.com` |
| FAQ — Sidebar / Bottom CTA | "Start Filing" | `https://app.themiscourtpath.com` |
| Header — Persistent "Sign In" link | "Sign In" | `https://app.themiscourtpath.com/auth/login` |
| Header — Persistent "Start Filing" button | "Start Filing" | `https://app.themiscourtpath.com` |

### Negative confirmation (these MUST NOT exist on the marketing site)

| Anti-pattern | Why forbidden |
|--------------|---------------|
| Email + password fields anywhere | Auth happens only on app subdomain |
| Stripe Buy buttons / payment links | Payments only via app's `/api/create-checkout-session` |
| Intake form fields (name, DOB, SSN, address) | Intake only happens in encrypted app |
| File upload widgets | No user docs accepted on marketing site |
| Account dashboards / "My Filings" widgets | Belongs in app subdomain |

### Verification command

After launch, this command should return zero matches across all
production HTML on `themiscourtpath.com`:

```bash
# Run from a curl/wget against the live site
for path in / /how-it-works /pricing /faq /contact; do
  echo "=== $path ==="
  curl -s "https://themiscourtpath.com$path" \
    | grep -oE 'name=("|'"'"')(ssn|dob|password|payment|card)("|'"'"')' \
    | sort -u
done
# Expect: zero output for each path
```

---

## 7. Launch Sequence

```
T-7d  Phase A + B + C complete (site shell + theme + brand)
T-3d  Phase D complete (all 8 pages published)
T-1d  Phase E complete (verification + perf check)
T-0d  DNS A record live → site visible at themiscourtpath.com
       SSL certs verified
       Smoke test: every CTA reaches app subdomain
T+1d  Phase F kickoff (analytics, search console)
```

Hard launch dependency: `app.themiscourtpath.com` SSL must complete
before marketing site is publicly indexable. Otherwise users hit broken
HTTPS warnings on the CTA target. Verify with `curl -sI` before going
live.

---

## 8. Out-of-Scope Reaffirmed

This deployment plan does NOT include:

- Building the WordPress site (Commander or future WO executes the
  checklist)
- Writing final long-form copy (long-form drafts already exist in
  `website_copy/` from TCP-WO-011; can be reused or refined)
- Final legal page wording (requires licensed counsel review)
- Email (TCP-WO-004) — defer until Workspace is set up
- Blog content / SEO sprint — post-launch
- Analytics implementation specifics — post-launch

---

*SITEGROUND_DEPLOYMENT_PLAN.md — TCP-WO-310 deliverable*
*Companion: 06_MARKETING/PAGE_SKELETONS.md (page-by-page skeletons)*
