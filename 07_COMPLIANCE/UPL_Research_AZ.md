# Unauthorized Practice of Law (UPL) Research — Arizona
## DRAFT — REQUIRES COMMANDER REVIEW
**Date**: 2026-04-17
**Work Order**: TCP-WO-010

---

## Governing Rules

### Arizona Supreme Court Rule 31
Defines who may practice law in Arizona. Key provisions:
- Only members of the State Bar of Arizona may practice law
- "Practice of law" includes giving legal advice, preparing legal documents for others, and representing others in court
- **Exception**: Document preparation by certified Legal Document Preparers (LDPs)

### Arizona Legal Document Preparer (LDP) — A.R.S. 12-2801 et seq. / ACJA 7-208
- LDPs may prepare legal documents at the specific direction of a client
- LDPs may NOT give legal advice, recommend courses of action, or exercise legal judgment
- LDP certification requires: application, background check, exam, bond ($5,000), annual renewal
- LDPs must display certification number on all documents

---

## Does Themis Need LDP Certification?

### The Software Distinction

**Key question**: Is automated document assembly software "preparing legal documents" under the statute?

**Precedents suggest NO**:
- **LegalZoom**: Operated in Arizona without LDP certification. Faced challenges but settled — continued operating as software platform, not LDP.
- **Rocket Lawyer**: Same approach — software generates documents from user input without human legal judgment.
- **TurboTax analogy**: Tax preparation software is not considered "practicing accounting" — it's a tool the user operates.

### Themis's Position
Themis Court Path is **software** that:
- Presents official court form fields as a guided questionnaire
- Accepts user input (facts only — names, dates, amounts)
- Performs mathematical calculations (AZ Guidelines schedule lookup)
- Populates official court PDF forms with user-provided data
- Does NOT recommend legal strategies, evaluate claims, or exercise judgment

**This is document assembly, not legal document preparation.**

---

## What Themis CAN and CANNOT Do

### CAN Do (Safe Activities)
- Present court form fields as questions
- Accept factual information from users
- Perform mathematical calculations (child support guidelines)
- Look up values in official tables (AZ Schedule, Table A/B)
- Auto-fill official court forms with user-provided data
- Explain what each form field means (factual/procedural information)
- Provide general information about court processes
- Link to official court resources and self-help centers

### CANNOT Do (UPL Risk)
- Recommend whether to file for child support (legal advice)
- Advise which jurisdiction to select (legal judgment)
- Suggest which paternity method applies (legal analysis)
- Recommend whether to request arrears (strategic advice)
- Tell a user their case is strong/weak (case evaluation)
- Suggest specific dollar amounts for support (beyond calculator output)
- Draft custom legal arguments or statements
- Represent users in court or at hearings

---

## Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| AZ Bar complaint | LOW | MEDIUM | Clear disclaimers, no legal advice |
| LDP enforcement action | LOW | LOW | We're software, not a person preparing docs |
| User claiming reliance on "legal advice" | MEDIUM | HIGH | Prominent disclaimers, Terms of Service |
| Competitor complaint | LOW | LOW | Operating within established precedents |

**Overall risk**: LOW — provided disclaimers are prominent and consistent.

---

## Required Protective Language

Every instance of potential legal judgment in the app must be preceded by:

> **This is not legal advice.** Themis Court Path is a document preparation tool, not a law firm. The information presented is general and procedural. For advice about your specific situation, consult a licensed Arizona attorney.

Specific high-risk screens:
- Paternity method selection
- Jurisdiction checkbox selection
- Arrears/past support decisions
- Tax exemption allocation
- Any "what should I choose?" moment

---

## Recommendations

1. **Do NOT apply for LDP certification** — software platforms don't need it, and getting it could imply we're acting as an LDP (creating obligations we don't want)
2. **Maintain clear software-as-tool positioning** in all marketing and legal documents
3. **Add disclaimers at every decision point** in the intake wizard
4. **Offer attorney referral** at every point where legal judgment is involved
5. **Monitor AZ Bar opinions** for any changes to software/UPL guidance
6. **Consider ABS registration** (Rule 31.1) in Phase 4+ if we add deeper legal services

---

*UPL Research — Agent B Compliance Team*
