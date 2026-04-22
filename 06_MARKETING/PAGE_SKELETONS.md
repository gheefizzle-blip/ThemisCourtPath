# Themis Court Path — Page Skeletons (TCP-WO-310)

## Status

DRAFT — REQUIRES COMMANDER REVIEW
Skeletons only. Final copy lives separately in `website_copy/` (TCP-WO-011 long-form drafts).

## Authoritative Routing Rules (TCP-WO-310)

- All primary CTAs MUST point to `https://app.themiscourtpath.com`
- No SSN, DOB, case data, login, or payment fields on this site
- Marketing site = pure conversion layer

---

# 1. Home Page

**Purpose**: Convert visitor → click "Start Filing" → land in the secure app

## Layout

| Section | Purpose | Length |
|---------|---------|--------|
| Hero | Above-fold value prop + CTA | 1 screen |
| How It Works (mini) | 3-step icons | 1 screen |
| Why Themis | 3 trust pillars | 1 screen |
| Pricing teaser | Single $99 card | 0.5 screen |
| Final CTA | Repeat hero CTA | 0.5 screen |

## Hero Section

```
[Themis logo]                                          [Sign In ▸ app subdomain]

H1:    File for Child Support in Arizona — Without the $3,000 Lawyer Fee

H2:    Themis Court Path guides you through court paperwork, calculates support
       per Arizona Guidelines, and delivers court-ready documents. $99 flat.

[ Start Filing → ]   ← primary CTA, routes to https://app.themiscourtpath.com
[ How It Works ]     ← scroll anchor

Trust strip: "Built for Arizona. Not a law firm. Your data is encrypted end-to-end."
```

## How It Works (mini)

3 icon cards: **Answer questions** → **We build your documents** → **You file with the court**
"See full process" link → /how-it-works

## Why Themis (3 trust pillars)

1. **Encrypted, end-to-end** — your information is encrypted before it touches our systems
2. **Built for Arizona courts** — Navajo County today; statewide rolling out
3. **Save thousands** — $99 vs $2,000–3,000 attorney fee for the same paperwork

## Pricing teaser

Single card showing $99 / Self-File. Button → /pricing.

## Final CTA

Reinforces: "Most users finish in 25 minutes." Button → app subdomain.

## Footer

Logo • brief disclaimer • Privacy Policy • Terms • Contact

---

# 2. How It Works

**Purpose**: Build confidence by showing the full workflow

## Layout

5-step vertical scroller, one section per step.

```
Step 1 — Create your account                       [Create Account → app subdomain]
        Brief: email + password. No credit check, no commitment.

Step 2 — Complete the guided intake                [What you'll need (expand)]
        Brief: 11 short sections, ~25 minutes. Save your progress anytime.
        What you'll need: names + DOBs of both parents, child info,
        respondent's employer info, monthly income (if known).

Step 3 — Pay the $99 filing fee                    [Pricing details]
        Brief: secure Stripe checkout. Documents unlock immediately after payment.

Step 4 — Download your court-ready documents       [What you get (expand)]
        Brief: editable petition + court-ready PDF + validation report.
        What you get: 29-page Navajo County petition packet, AZ Schedule
        worksheet (Lines 13-37 auto-calculated), validation note.

Step 5 — File with the court                       [Filing fee help]
        Brief: print, take to your county clerk OR e-file via eFileAZ.
        Filing fee help: AZ offers fee deferrals/waivers if you can't afford
        the court's $200-350 filing fee.

[ Start Filing → ]   ← bottom of page, app subdomain
```

---

# 3. Pricing

**Purpose**: Eliminate price-shock objection; show what's included

## Layout

```
H1: $99 to file. Period.

Single card (centered):

  ┌─────────────────────────────────────┐
  │  Self-File                          │
  │  $99  one-time                      │
  │                                     │
  │  ✓ Guided 11-step intake            │
  │  ✓ AZ Child Support Calculator      │
  │  ✓ Parenting time builder           │
  │  ✓ Editable petition PDF            │
  │  ✓ Court-ready filled PDF           │
  │  ✓ Validation report                │
  │  ✓ Encrypted storage of your data   │
  │                                     │
  │  [ Start Filing → ] (app subdomain) │
  └─────────────────────────────────────┘

Comparison table below:

  | Option              | Cost         | Time        |
  | ------------------- | ------------ | ----------- |
  | Hire attorney       | $2,000-3,000 | 2-4 weeks   |
  | Document preparer   | $300-500     | 1-2 weeks   |
  | Themis Court Path   | $99          | 30 minutes  |
  | DIY from scratch    | Free + fee   | hours       |

Fine print:
- Court filing fee ($200-350) is paid separately to the court.
- No subscriptions. No hidden fees. Refund available before document generation.
```

---

# 4. FAQ

**Purpose**: Answer the 4 objections that block conversion

## Layout

Accordion or simple H3 + paragraph. 8-10 entries max for v1.

```
Q1. Is this legal advice?
A1. No. Themis Court Path is a document preparation tool. We do not
    provide legal advice or represent you in court. The documents we
    generate are the same official forms you would get from the court's
    self-help center — we just make filling them out faster and less
    error-prone. For legal advice, consult a licensed Arizona attorney.

Q2. Is my data secure?
A2. Yes. Your intake data is encrypted before it is stored. We use
    industry-standard encryption (Fernet / AES). Your documents are
    generated in memory and never written to disk in plaintext.
    We never see your card information — Stripe handles that directly.

Q3. Can I edit the documents after they are generated?
A3. Yes. We provide both an editable PDF and a court-ready filled PDF.
    You can review every field before filing.

Q4. What is your refund policy?
A4. Full refund available before documents are generated. After
    generation, the service has been delivered and refunds are not
    issued, except in cases of demonstrable software error.
    [PLACEHOLDER — final policy in /legal/refund-policy]

Q5. What courts do you support?
A5. Currently: Navajo County, Arizona. Expanding to all 15 Arizona
    counties. Maricopa, Pima, and Pinal next.

Q6. How do I file the documents after generating them?
A6. Print and take them to your county Clerk of Superior Court, OR
    use Arizona's electronic filing system (eFileAZ). We provide
    filing instructions inside the app.

Q7. What if I need help during the intake?
A7. Email support@themiscourtpath.com. Each intake question includes
    a tooltip explaining what's being asked.

Q8. Do I need a lawyer?
A8. Not for straightforward child support petitions. Many people file
    pro se (on their own) every year. If your case involves disputed
    paternity, complex custody, or domestic violence, we recommend
    consulting an attorney.
```

---

# 5. Legal Pages

**Purpose**: Required disclosures, link from footer

## Layout

3 separate pages, each linked in the global footer:

| URL slug | Source content | Notes |
|----------|----------------|-------|
| `/privacy` | `07_COMPLIANCE/Privacy_Policy_DRAFT.md` | Use existing draft — REQUIRES LEGAL REVIEW before publish |
| `/terms` | `07_COMPLIANCE/Terms_of_Service_DRAFT.md` | Use existing draft — REQUIRES LEGAL REVIEW |
| `/disclaimer` | `06_MARKETING/website_copy/legal/disclaimer.md` | Use existing draft |

Each page:
- Single-column readable layout
- "Last updated" date in header
- "Effective date" in header
- Link to other legal pages in footer of each
- "DRAFT — pending legal review" banner until counsel signs off

**Hard rule for TCP-WO-310 scope**: do not reproduce legal content here.
Final wording must come from licensed counsel. Skeleton only points to
the existing drafts in `07_COMPLIANCE/`.

---

# 6. Contact Page

**Purpose**: Reachable support, no PII collection

## Layout

```
H1: Get in Touch

Two-column layout:

Left column — Quick contact

  Support questions:    support@themiscourtpath.com
  Press / partnerships: hello@themiscourtpath.com
  Legal notices:        legal@themiscourtpath.com
  Hours:                Mon-Fri, 9 AM - 5 PM Arizona time

Right column — Contact form (NON-SENSITIVE FIELDS ONLY)

  Name:    [text]
  Email:   [text]
  Subject: [select: Question / Bug / Other]
  Message: [textarea, max 2000 chars]
  [ Send ]

  Form must NOT collect: SSN, DOB, address, case details, payment info
  Form should be a standard WordPress contact-form plugin (e.g., WPForms)
  configured to email support@themiscourtpath.com.

Footer note: "Need to file? Documents and case data are handled in our
secure app at app.themiscourtpath.com — please don't send case details
through this contact form."
```

---

# Footer (Global, All Pages)

```
[Logo] Themis Court Path                 © 2026 Athena Intelligence

  Product                Resources              Company
  Start Filing →         FAQ                    About
  How It Works           Filing Help            Contact
  Pricing                                       Press

  Legal: Privacy • Terms • Disclaimer

  Disclaimer (small): Themis Court Path is a document preparation
  service, not a law firm. We do not provide legal advice. Consult a
  licensed Arizona attorney for legal questions.
```

---

# Routing Summary (For Verification)

Every primary CTA in this skeleton routes to `https://app.themiscourtpath.com`:

| Page | Primary CTA | Target |
|------|-------------|--------|
| Home — Hero | "Start Filing" | `https://app.themiscourtpath.com` |
| Home — Pricing teaser | "Start Filing" | `https://app.themiscourtpath.com` |
| Home — Final CTA | "Start Filing" | `https://app.themiscourtpath.com` |
| Home — Sign In link | "Sign In" | `https://app.themiscourtpath.com/auth/login` |
| How It Works — Step 1 | "Create Account" | `https://app.themiscourtpath.com/auth/register` |
| How It Works — Bottom | "Start Filing" | `https://app.themiscourtpath.com` |
| Pricing — Card CTA | "Start Filing" | `https://app.themiscourtpath.com` |

No CTA on this site initiates intake, payment, or auth in-page.

---

*PAGE_SKELETONS.md — TCP-WO-310 deliverable*
*Companion: SITEGROUND_DEPLOYMENT_PLAN.md (sitemap, DNS, checklist)*
