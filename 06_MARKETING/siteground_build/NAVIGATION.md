# NAVIGATION

Source: TCP-WO-311 - SiteGround front-end build
Status: DRAFT - REQUIRES COMMANDER REVIEW

---

## Header Navigation (Desktop)

Layout, left to right:

| Slot | Element | Link / Action |
|------|---------|---------------|
| 1 (left) | Logo + brand mark | / (Home) |
| 2 (center) | Primary nav: Home | / |
| 2 | Primary nav: How It Works | /how-it-works |
| 2 | Primary nav: Pricing | /pricing |
| 2 | Primary nav: FAQ | /faq |
| 2 | Primary nav: Contact | /contact |
| 3 (right) | Sign In link (text) | https://app.themiscourtpath.com/auth/login |
| 4 (right) | Start Filing button (primary CTA) | https://app.themiscourtpath.com |

Notes:
- The Start Filing button must be visually distinct (filled primary color) and present on every page.
- The Sign In link is a plain text link, less visual weight than the Start Filing button.
- The header should stick to the top of the viewport on scroll.
- In Neve: Appearance -> Customize -> Layout -> Header (Header Builder). Use the "Button" component to add the Start Filing CTA in the right slot.

---

## Header Navigation (Mobile)

Layout:

| Slot | Element | Link / Action |
|------|---------|---------------|
| Left | Logo (slightly smaller than desktop) | / |
| Right | Hamburger menu icon | Opens mobile menu |
| Right | Start Filing button (compact) | https://app.themiscourtpath.com |

Mobile menu (when hamburger is tapped):

| Order | Item | Link |
|-------|------|------|
| 1 | Home | / |
| 2 | How It Works | /how-it-works |
| 3 | Pricing | /pricing |
| 4 | FAQ | /faq |
| 5 | Contact | /contact |
| 6 | Sign In | https://app.themiscourtpath.com/auth/login |
| 7 | Start Filing (large CTA at bottom of menu) | https://app.themiscourtpath.com |

---

## Footer Navigation

See FOOTER.md for the full footer content. The footer-level link groups are:

| Group | Items |
|-------|-------|
| Product | Start Filing, How It Works, Pricing |
| Resources | FAQ, Contact |
| Legal | Privacy, Terms, Disclaimer |

---

## CTA Button Placement Rules

| Page | Top of page | Mid-page | Bottom of page |
|------|-------------|----------|----------------|
| Home | YES (hero) | YES (after pricing teaser) | YES (final CTA section) |
| How It Works | YES | NO (Step 1 has its own Create Account button) | YES |
| Pricing | NO (CTA is on the card) | YES (on pricing card) | YES (bottom CTA) |
| FAQ | NO | NO | YES |
| Contact | NO (form is the focus) | NO | YES (Go to the App link) |
| Legal pages | NO | NO | NO (no CTAs on legal pages) |

---

## Forbidden Navigation Patterns

The following must NOT appear anywhere in the marketing site navigation:

- Links to internal app routes other than /, /auth/login, and /auth/register
- "My Account" or "Dashboard" links (those belong inside the app)
- Login/register forms in the header
- Cart icons or shopping flows (single $99 fee handled in app)
- Language pickers (English only for Phase 1)

---

*NAVIGATION.md - TCP-WO-311 deliverable*
