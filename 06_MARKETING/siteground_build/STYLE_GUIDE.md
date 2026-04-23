# STYLE GUIDE

Source: TCP-WO-311 - SiteGround front-end build
Status: DRAFT - REQUIRES COMMANDER REVIEW
Scope: Implementation guidance for the SiteGround marketing site only. The app at app.themiscourtpath.com has its own style.

---

## Brand Colors

These mirror TCP-WO-310 / the app palette so the marketing site and the app look like the same product.

| Token | Hex | Usage |
|-------|-----|-------|
| Primary navy | #1a3a5c | Headers, primary buttons, headings, brand strip |
| Medium blue | #2c5282 | Secondary headings, button hover, links |
| Accent gold | #c9a84c | Trust marks, small accents, divider strokes |
| Light surface | #f7fafc | Page background, card backgrounds |
| Text default | #1a202c | Body text |
| Text muted | #718096 | Secondary text, captions |
| Border | #cbd5e0 | Card borders, dividers |
| Error | #9b2c2c | Form validation errors |
| Success | #276749 | Confirmations |

WordPress theme guidance:
- Astra Customize -> Global -> Colors: paste these values into the theme color pickers.
- Do not introduce additional accent colors without updating this guide.

---

## Typography

| Use | Font family | Size | Weight |
|-----|-------------|------|--------|
| Page H1 (hero headline) | System sans-serif (Segoe UI, system-ui, -apple-system, sans-serif) | 36 - 48 px | 700 |
| Page H2 | Same | 28 - 32 px | 700 |
| H3 (section subheads) | Same | 20 - 24 px | 600 |
| Body | Same | 16 - 18 px | 400 |
| Small text / captions | Same | 13 - 14 px | 400 |

Do NOT load Google Fonts in production. Use system fonts. (Performance baseline target: page load under 2 seconds; Google Font loads add 200 - 500 ms.)

Line height: 1.5 - 1.7 for body. 1.2 - 1.3 for headings.

---

## Button Labels (canonical)

Use these exact strings. Do not improvise.

| Context | Label | URL |
|---------|-------|-----|
| Top-of-page primary CTA | Start Filing | https://app.themiscourtpath.com |
| Bottom-of-page primary CTA | Start Filing | https://app.themiscourtpath.com |
| Pricing card CTA | Start Filing - $99 | https://app.themiscourtpath.com |
| Pricing bottom CTA | Start Filing - $99 | https://app.themiscourtpath.com |
| How It Works Step 1 | Create Account | https://app.themiscourtpath.com/auth/register |
| Header secondary | Sign In | https://app.themiscourtpath.com/auth/login |
| Contact bottom CTA | Go to the App | https://app.themiscourtpath.com |

Forbidden labels: "Buy Now", "Order", "Cart", "Subscribe", "Free Trial", "Get Started Free". The product is a flat-fee service, not SaaS.

---

## Tone Rules

- Plain English. Sixth-grade reading level where possible.
- Direct. Short sentences. One idea per sentence.
- No legal overclaiming. We never imply we provide legal advice or representation.
- Empathetic but not condescending. Users are stressed adults navigating a court process.
- Honest about scope. We do document preparation. The user files the documents.

Avoid these words and phrases:
- "Lawyer in your pocket" (we are not a lawyer)
- "Guaranteed approval" (we cannot guarantee court outcomes)
- "Full-service legal" (we are not a law firm)
- "Easy" (court processes are stressful; this word reads as dismissive)
- "Just" (as in "just fill this out" - dismisses real difficulty)
- "Simple" (the same)

Use these words instead:
- "Step-by-step" instead of "easy"
- "Guided" instead of "simple"
- "Complete" instead of "just"

---

## CTA Rules

1. Every primary CTA points to one of these URLs and nothing else:
   - https://app.themiscourtpath.com
   - https://app.themiscourtpath.com/auth/login
   - https://app.themiscourtpath.com/auth/register

2. Primary CTAs use Primary navy fill, white text, slight rounded corners (6 - 8 px radius), 12 - 16 px vertical padding.

3. There is one primary CTA per visual section (hero, mid-page, footer area). Avoid stacking multiple primary buttons next to each other.

4. Secondary actions ("Sign In", "Learn More") are plain text links or outline buttons in Primary navy. Never as visually loud as the primary CTA.

5. CTAs MUST NOT initiate any of the following on the marketing site:
   - Account creation in-page
   - Payment in-page
   - Intake form submission in-page
   - File upload of any kind

---

## Disclaimer Placement Rules

| Location | Required disclaimer |
|----------|---------------------|
| Top of every page (slim strip) | Themis Court Path is a document preparation service, not a law firm. We do not provide legal advice. |
| Bottom of every page (footer block) | Full disclaimer paragraph from FOOTER.md |
| Pricing page (visible block above bottom CTA) | Full pricing disclaimer block from PRICING.md |
| Contact page (above and below the form) | Do not include personal, financial, or case details in this form. |
| Refund mentions | Always tag with "DRAFT - PENDING LEGAL REVIEW" until counsel finalizes |
| Legal pages | "DRAFT - PENDING LEGAL REVIEW" banner at top until counsel signs off |

Hard rule: no page may be missing the top disclaimer strip.

---

## Image and Asset Rules

- Logo: use Themis_Court_Path_logo.png from 06_MARKETING/. Compress to web-optimized PNG or WebP under 150 KB before upload.
- Favicon: 16x16, 32x32, and 180x180 PNG variants required for browsers and Apple touch.
- No stock photos of fake families, courthouses, or lawyers. Photo realism implies promises we don't make.
- Iconography: use a simple, single-color icon set (e.g., Heroicons outline at #1a3a5c). No emoji in production copy.

---

## Performance Rules

- No carousel/slider plugins.
- No autoplay video.
- WP Super Cache (or equivalent) enabled.
- Total page weight budget: < 500 KB per page on first load.
- Lighthouse Performance target: > 90.

---

## Content Update Rules

- Any change to a page's primary CTA URL must be reviewed against this guide.
- Any change to the disclaimer wording must be reviewed by Sam and counsel.
- Pricing changes must update PRICING.md in source first, then propagate to the site.
- New pages must add their CTA placement to NAVIGATION.md.

---

*STYLE_GUIDE.md - TCP-WO-311 deliverable*
