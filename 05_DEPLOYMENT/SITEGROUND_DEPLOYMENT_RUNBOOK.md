# SiteGround Deployment Runbook (TCP-WO-312)

## Status

DRAFT - REQUIRES COMMANDER EXECUTION

This runbook is the executable companion to the TCP-WO-311 content package and the TCP-WO-310 deployment plan. It is the operational checklist for Commander to bring the marketing site live on SiteGround.

## Why This Is a Runbook (not Claude-executed)

Building a WordPress site requires browser-based actions inside the SiteGround admin UI:

- Logging in to my.siteground.com with Commander's credentials
- Provisioning the WordPress install
- Installing and activating themes / plugins via the WordPress admin
- Pasting page content into the WordPress page editor
- Uploading media (logo, favicon)
- Configuring the contact form plugin's email destination
- Setting up the navigation menus
- Testing the live site

Claude Code does not have credentials to SiteGround and cannot drive a browser. This runbook gives Commander everything needed to perform those actions in roughly 90 minutes.

---

## Source Authority

Content to paste into WordPress pages comes from:

| WordPress page | Source file in repo |
|----------------|---------------------|
| Home | `06_MARKETING/siteground_build/HOME.md` |
| How It Works | `06_MARKETING/siteground_build/HOW_IT_WORKS.md` |
| Pricing | `06_MARKETING/siteground_build/PRICING.md` |
| FAQ | `06_MARKETING/siteground_build/FAQ.md` |
| Contact | `06_MARKETING/siteground_build/CONTACT.md` |
| Privacy Policy | `06_MARKETING/siteground_build/PRIVACY_PLACEHOLDER.md` |
| Terms of Service | `06_MARKETING/siteground_build/TERMS_PLACEHOLDER.md` |
| Disclaimer | `06_MARKETING/siteground_build/DISCLAIMER_PLACEHOLDER.md` |

Cross-cutting:

| Element | Source file |
|---------|-------------|
| Header / footer nav | `06_MARKETING/siteground_build/NAVIGATION.md` |
| Footer content | `06_MARKETING/siteground_build/FOOTER.md` |
| Brand colors / typography / button labels | `06_MARKETING/siteground_build/STYLE_GUIDE.md` |

All four required copy corrections from TCP-WO-312 have been applied to these source files (see "Verification Snapshot" below).

---

# PHASE A — Site Provisioning (Commander, ~30 min)

## A.1 Log in

- [ ] Open https://my.siteground.com
- [ ] Sign in with Commander credentials

## A.2 Create the WordPress site

- [ ] In your hosting plan, navigate to: Websites -> New Website
- [ ] Choose "Existing Domain" -> enter `themiscourtpath.com`
- [ ] Choose "Start a New Website" -> WordPress
- [ ] Set:
  - Admin email: a Themis-internal email address (NOT Commander's primary inbox)
  - Admin username: NOT "admin" (anything else)
  - Admin password: long, unique, store in password manager
- [ ] Skip the SG Site Scanner upsell unless desired
- [ ] Click Finish; wait for provisioning

## A.3 Confirm SSL on the root domain

- [ ] Site Tools -> Security -> SSL Manager
- [ ] Select Let's Encrypt -> Install
- [ ] Site Tools -> Security -> HTTPS Enforce -> On
- [ ] Browser test: open `https://themiscourtpath.com` -> default WordPress page should load over HTTPS

## A.4 Confirm app subdomain CNAME (already done, verify)

- [ ] Site Tools -> Domain -> DNS Zone Editor
- [ ] Confirm CNAME exists: `app` -> `ghs.googlehosted.com`
- [ ] If missing: add it. TTL 300.

---

# PHASE B — Theme + Plugins (~20 min)

## B.1 WordPress admin login

- [ ] Open `https://themiscourtpath.com/wp-admin`
- [ ] Sign in with the admin credentials from A.2

## B.2 Install Astra theme

- [ ] Appearance -> Themes -> Add New Theme
- [ ] Search: Astra (by Brainstorm Force)
- [ ] Install -> Activate

## B.3 Install required plugins

For each, Plugins -> Add New -> search -> Install -> Activate:

- [ ] WPForms Lite (contact form)
- [ ] WP Super Cache (page cache)
- [ ] Yoast SEO (sitemap.xml + meta tags)

Skip Astra Starter Templates unless you want to use a pre-built design as a starting point. Phase D builds pages directly from the source content.

## B.4 Baseline settings

- [ ] Settings -> Permalinks -> Post name (clean URLs)
- [ ] Settings -> Reading -> Search engine visibility -> UNCHECK "Discourage search engines from indexing this site"

---

# PHASE C — Brand Assets (~10 min)

## C.1 Compress logo before upload

- [ ] Take `06_MARKETING/Themis_Court_Path_logo.png` (~2.7 MB raw)
- [ ] Compress to under 150 KB using one of:
  - https://tinypng.com (drag and drop, no account needed)
  - https://squoosh.app (Google's open-source compressor)
- [ ] Save as `themis-logo-web.png` (recommended)

## C.2 Generate favicon variants

- [ ] Visit https://realfavicongenerator.net
- [ ] Upload the compressed logo
- [ ] Download the favicon package
- [ ] Extract: keep at minimum the 32x32 PNG and 180x180 (Apple touch)

## C.3 Upload to WordPress

- [ ] Media -> Add New Media File -> upload:
  - `themis-logo-web.png`
  - 32x32 favicon (rename to `favicon-32x32.png`)
  - 180x180 favicon (rename to `apple-touch-icon.png`)

## C.4 Set logo + favicon in WordPress

- [ ] Appearance -> Customize -> Site Identity
- [ ] Logo: select `themis-logo-web.png`
- [ ] Site Title: `Themis Court Path`
- [ ] Tagline: `Your guided path through the court system`
- [ ] Site Icon: select the 32x32 favicon
- [ ] Publish

## C.5 Set brand colors

- [ ] Appearance -> Customize -> Global -> Colors
- [ ] Set:
  - Primary: `#1a3a5c`
  - Secondary: `#2c5282`
  - Accent: `#c9a84c`
  - Background: `#f7fafc`
- [ ] Publish

---

# PHASE D — Pages (~60 min)

For each of the 8 pages below, repeat this sub-procedure:

## D.x Per-page sub-procedure

- [ ] Pages -> Add New Page
- [ ] Set the Title from the table below
- [ ] Set the URL slug (Permalink section) from the table
- [ ] Open the source `.md` file from `06_MARKETING/siteground_build/`
- [ ] Copy content into the WordPress block editor
  - For tables in Markdown, use the WordPress "Table" block
  - For lists, use the "List" block
  - For headings, match the heading level
  - For buttons, use a "Button" block; set Link to the URL given
- [ ] Verify any CTA button URL matches the source file exactly
- [ ] Set Page Attributes -> Order (left-to-right header order):
  - 10 = Home
  - 20 = How It Works
  - 30 = Pricing
  - 40 = FAQ
  - 50 = Contact
  - 90 = Privacy / Terms / Disclaimer (footer-only)
- [ ] Publish

## D.0 Page-by-page table

| Title | Slug | Source file |
|-------|------|-------------|
| Home | `/` (set as Settings -> Reading -> Static Front Page) | `HOME.md` |
| How It Works | `/how-it-works` | `HOW_IT_WORKS.md` |
| Pricing | `/pricing` | `PRICING.md` |
| FAQ | `/faq` | `FAQ.md` |
| Contact | `/contact` | `CONTACT.md` |
| Privacy Policy | `/privacy` | `PRIVACY_PLACEHOLDER.md` |
| Terms of Service | `/terms` | `TERMS_PLACEHOLDER.md` |
| Disclaimer | `/disclaimer` | `DISCLAIMER_PLACEHOLDER.md` |

## D.9 Set the Home page as the front page

- [ ] Settings -> Reading -> Your homepage displays: A static page
- [ ] Homepage: Home
- [ ] Save Changes

## D.10 Build the navigation menus

Per `06_MARKETING/siteground_build/NAVIGATION.md`:

### Header Menu

- [ ] Appearance -> Menus -> Create new menu -> name "Primary Menu"
- [ ] Add menu items in this order:
  1. Home (page link)
  2. How It Works (page link)
  3. Pricing (page link)
  4. FAQ (page link)
  5. Contact (page link)
  6. Sign In (custom link to `https://app.themiscourtpath.com/auth/login`)
  7. Start Filing (custom link to `https://app.themiscourtpath.com`)
- [ ] Set Display Location: Primary Menu
- [ ] Save Menu

To make "Start Filing" appear as a button, use the Astra header button option in Appearance -> Customize -> Header Builder, with URL `https://app.themiscourtpath.com` and label "Start Filing".

### Footer Menu (per `FOOTER.md`)

- [ ] Appearance -> Menus -> Create new menu -> name "Footer Legal"
- [ ] Add menu items: Privacy Policy, Terms of Service, Disclaimer
- [ ] Set Display Location: Footer Menu
- [ ] Save Menu

For the multi-column footer (Product / Resources / Legal), use Astra's Footer Builder under Appearance -> Customize -> Footer Builder, configured per `FOOTER.md`.

## D.11 Configure the Contact form

- [ ] WPForms -> Add New -> select "Simple Contact Form"
- [ ] Configure fields per `CONTACT.md`:
  - Your name (Single-Line Text, required, max 100 chars)
  - Email address (Email, required)
  - Subject (Dropdown: Question / Bug report / Press / Other)
  - Message (Paragraph Text, required, max 2000 chars)
- [ ] Settings -> Notifications:
  - Send To: `support@themiscourtpath.com`
  - Subject: `[Themis Contact] {Subject}`
- [ ] Save form
- [ ] On the Contact page, insert the WPForms block and select this form
- [ ] Confirm both warning blocks (above and below the form) match `CONTACT.md`

---

# PHASE E — Verification (~15 min)

## E.1 Page rendering

For each page, open in a browser and confirm:

- [ ] Page loads over HTTPS
- [ ] Page title is correct
- [ ] Top disclaimer strip present
- [ ] Bottom footer present
- [ ] No layout broken on mobile (Chrome DevTools responsive mode at 375px width)
- [ ] No console errors (F12)

## E.2 CTA routing audit (CRITICAL)

Open each page and confirm every CTA button or link target is one of these three URLs (and nothing else):

- `https://app.themiscourtpath.com`
- `https://app.themiscourtpath.com/auth/login`
- `https://app.themiscourtpath.com/auth/register`

Quick test: right-click any "Start Filing" / "Sign In" / "Create Account" button -> Copy Link Address -> verify.

## E.3 Forbidden patterns audit

- [ ] No email or password input fields anywhere on the marketing site
- [ ] No payment / credit card / Stripe Buy buttons
- [ ] No SSN / DOB / address input fields
- [ ] No file upload widgets (the contact form must be text-only)
- [ ] No "My Account" or "Dashboard" links

## E.4 Contact form delivery test

- [ ] Submit a test message through the contact form on the live site
- [ ] Verify it arrives at `support@themiscourtpath.com`

## E.5 Performance baseline

- [ ] Run https://pagespeed.web.dev against `https://themiscourtpath.com`
- [ ] Target: Performance score > 90 on mobile
- [ ] If score is low, common fixes:
  - Re-compress images
  - Disable any unused plugins
  - Enable WP Super Cache (Settings -> WP Super Cache -> Caching On)

## E.6 Legal page banners

- [ ] Privacy, Terms, and Disclaimer pages each show "DRAFT - PENDING LEGAL REVIEW" banner at top
- [ ] All three pages link to the others in their footer area

---

# PHASE F — Post-Launch (within 7 days)

- [ ] Submit `https://themiscourtpath.com/sitemap_index.xml` to Google Search Console
- [ ] Verify Yoast SEO meta tags on each page
- [ ] Decide on analytics: Plausible (privacy-friendly, $9/mo) OR Google Analytics 4 (free, more invasive)
- [ ] Schedule the 3 SEO blog posts from `06_MARKETING/website_copy/blog/` for first month

---

# Verification Snapshot (As of TCP-WO-312 Commit)

These four corrections from TCP-WO-312 are applied to the source content files:

| # | Correction | File | Status |
|---|-----------|------|--------|
| 1 | Home headline replaced | `siteground_build/HOME.md` | DONE |
| 2 | Attorney cost comparisons softened | `siteground_build/HOME.md` and `siteground_build/PRICING.md` | DONE |
| 3 | FAQ security language simplified (removed "Fernet / AES") | `siteground_build/FAQ.md` | DONE |
| 4 | Contact plugin language simplified | `siteground_build/CONTACT.md` | DONE |

ASCII-only verification: PASSED across all 11 source files.
CTA routing verification: PASSED. Only the three permitted URLs appear as link targets.

---

# What This Runbook Does NOT Cover

- DNS A record changes for `themiscourtpath.com` to point at the SiteGround IP. SiteGround typically handles this automatically when the domain is added to a hosting plan; verify in SiteGround "Domains" before launch. If a DNS cutover is needed, that is a Commander-controlled action (it can take up to 24 hours to propagate).
- Email setup (MX / SPF / DMARC / DKIM). Out of scope; covered by future TCP-WO-004 (Google Workspace).
- Final legal page wording. Privacy / Terms / Disclaimer remain as PLACEHOLDER until counsel reviews the drafts in `07_COMPLIANCE/`.
- Final Commander/Sam disposition of the live site after Phase E completes.

---

# Estimated Total Time

| Phase | Time | Owner |
|-------|------|-------|
| A - Provisioning | 30 min | Commander |
| B - Theme + plugins | 20 min | Commander |
| C - Brand assets | 10 min | Commander |
| D - Pages (8 pages + nav + form) | 60 min | Commander (or Claude pair-programming through chat) |
| E - Verification | 15 min | Commander |
| **Total to live site** | **~135 min** | |
| F - Post-launch (background) | ongoing | Commander |

---

*SITEGROUND_DEPLOYMENT_RUNBOOK.md - TCP-WO-312 deliverable*
*Companion: 06_MARKETING/siteground_build/ (TCP-WO-311 content package, with TCP-WO-312 corrections applied)*
