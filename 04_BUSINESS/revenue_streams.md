# Themis Court Path — Revenue Streams

**Last updated**: Session in progress

---

## Strategic Insight

The strongest revenue model for Themis is NOT a single pricing tier — it's
a **layered marketplace** where each customer interaction can generate
multiple revenue events:

1. **Document preparation** (base SaaS tier)
2. **E-filing** (transaction fee)
3. **Process service** (marketplace commission)
4. **Attorney consultation** (referral fee)
5. **Attorney full representation** (conversion fee)

One customer can move through all five layers as their needs escalate, with
Themis taking a cut at each stage.

---

## Revenue Stream Catalog

### Stream 1: Document Preparation (Self-File)

**Model**: One-time fee per filing
**Price**: $49-99
**Margin**: ~95% (software-only cost)

| Tier | Price | Includes |
|------|-------|----------|
| Self-File Basic | $49 | Intake wizard + PDF generation (download only) |
| Self-File Plus | $99 | + E-filing + deadline calendar + email reminders |
| Self-File Premium | $149 | + Process server included + priority support |

**Audience**: Pro-se litigants, lower-income families, DIY-oriented users

---

### Stream 2: E-Filing Transaction Fee

**Model**: Pass-through + service fee
**Price**: Court filing fee ($250-350) + our $15-25 service fee
**Margin**: ~100% on service fee portion (~$18 net per filing)

- Arizona court filing fee: ~$250-350 (depends on case type and county)
- Stripe processing: 2.9% + $0.30
- Our service fee: $15-25 (covers Stripe fee + provides margin)
- Integration: Tyler Odyssey API via eFileAZ

**Why customers pay it**: Saves a trip to the clerk's office, avoids
rejected filings (common with pro-se users), provides instant filing
confirmation.

---

### Stream 3: Process Server Marketplace ⭐ NEW

**Model**: Marketplace commission on service-of-process transactions
**Price**: $75-150 typical process server fee + our 15-25% commission
**Margin**: ~$18-37 per service

**How it works**:
After a petition is filed, the respondent must be legally served with the
documents. Many pro-se users don't know how to do this or don't have
access to a process server.

Themis becomes the marketplace connecting them:

```
User flow:
Petition filed → "Next step: Serve the respondent"
→ Themis shows 3-5 local process servers
→ Pricing displayed, reviews/ratings
→ One-click book + pay through Themis
→ Process server receives job via their dashboard
→ Server confirmation + proof of service uploaded to case
→ Themis takes 15-25% marketplace commission
```

**Why process servers want in**:
- No marketing cost — users come pre-qualified (already filed)
- Automated job dispatch (no phone tag)
- Payment already collected (no chasing invoices)
- Document package already digital (no paper shuffling)

**Recruitment strategy**:
- Contact AZ Association of Private Investigators (process servers often
  licensed as PIs)
- Reach out to existing process server companies in major AZ counties
- Target: 3-5 servers per county (redundancy + competition)

**Volume projection**:
- 50% of our filings will need process service
- At 2,500 filings/year → 1,250 service jobs
- Avg $30 commission → $37,500/year
- At 25,000 filings/year (mature) → $375,000/year

---

### Stream 4: Attorney Consultation Network ⭐ NEW

**Model**: Referral fee per consultation booked
**Price**: $50-150 consultation fee + our 20-30% commission
**Margin**: ~$15-40 per consultation

**How it works**:
Users often hit questions where they need real legal advice (not just form
help). Examples:
- "Should I contest paternity or not?"
- "What if I want to modify the tax exemption split?"
- "The other parent is in another state — is this still AZ jurisdiction?"

Themis becomes the smart router:

```
User hits decision point in intake
→ System detects "needs legal advice" moment
→ Offers: "Talk to an attorney — $75 for 20-minute consultation"
→ Matches with attorney in their area who handles this case type
→ Attorney gets pre-filled case summary (from intake data!)
→ 20-min Zoom/phone consult
→ Themis takes 25% commission ($18.75)
→ User gets answer, can continue self-filing
```

**Why attorneys want in**:
- Leads are pre-qualified (actively working on a case)
- Case context already known (Themis shares the intake summary)
- Low time commitment (20-min blocks)
- Conversion pipeline — some consults become full representation
- No marketing cost (Themis delivers the lead)

**The attorney's upsell opportunity**:
During the consultation, if the user decides "this is too complex, I need
representation" → attorney closes them as a client → Themis collects
conversion fee (see Stream 5).

---

### Stream 5: Attorney Full Representation Conversion ⭐ NEW

**Model**: Conversion fee when consultation → full representation
**Price**: $500-1,500 flat OR 10-15% of first-year legal fees
**Margin**: ~$500-1,500 per conversion (very high margin)

**How it works**:
When a consultation (Stream 4) leads to the user retaining the attorney
for full representation, Themis collects a one-time conversion fee.

```
Consultation booked → User decides to hire attorney
→ Attorney signs retainer agreement with user
→ Themis collects conversion fee (transparent to user — attorney pays)
→ Attorney gains a client worth $2,000-20,000 in fees
→ Themis gets a one-time bounty
```

**Pricing structures to offer attorneys**:
- **Option A**: Flat $750 conversion fee (attorney pays once)
- **Option B**: 12% of first-year billings (attorney pays over time)
- **Option C**: Subscription model — attorney pays $299/month for unlimited
  leads + no conversion fees

Most attorneys will pick whichever is cheapest in their case mix.

**Why this works for attorneys**:
- Client acquisition cost in family law: typically $500-2,000 via Google Ads
- Themis leads are already warm (they've filed or are filing)
- Themis provides the intake data — saves attorney 2-3 hours of initial
  case workup
- Better than BetterCall.com, LegalMatch, Avvo leads (those convert poorly)

**Volume projection (conservative)**:
- 5% of Self-File users upgrade to consultation (Stream 4)
- 20% of consultations convert to full representation (Stream 5)
- At 25,000 filings/year:
  - 1,250 consultations × $18 = $22,500 (Stream 4)
  - 250 conversions × $750 = $187,500 (Stream 5)

---

### Stream 6: Attorney Subscription (Tools & Leads)

**Model**: SaaS subscription for attorneys
**Price**: $99-499/month
**Margin**: ~90%

| Tier | Price | Includes |
|------|-------|----------|
| Solo Attorney | $99/month | Themis intake for own clients + 5 consult leads/mo |
| Small Firm | $299/month | 3 users + 20 leads/mo + white-label option |
| Large Firm | $499/month | Unlimited users + unlimited leads + API access |

**Pitch to attorneys**:
- Use Themis intake as your own client onboarding (faster than paper forms)
- Receive qualified leads from Themis marketplace
- White-label option — clients see *your firm's brand* using our software

---

### Stream 7: County/Legal Aid Licensing

**Model**: Annual white-label license
**Price**: $5,000-15,000/year per county/organization
**Margin**: ~70% (requires some support and customization)

**Audience**:
- County Superior Court self-help centers (all 15 AZ counties have them)
- Community Legal Services of Arizona
- Southern Arizona Legal Aid
- DNA People's Legal Services (Navajo Nation)

**Why they want it**:
- Their self-help centers are overwhelmed with pro-se users
- Paper forms + manual guidance doesn't scale
- Reduces clerk errors (rejected filings)
- Reduces caseload confusion

---

### Stream 8: Paralegal Subscription

**Model**: Per-paralegal seat license
**Price**: $79/month
**Margin**: ~90%

**Audience**: Independent paralegals / document preparation services

In Arizona, **Legal Document Preparers (LDPs)** are certified by the AZ
Supreme Court to prepare documents without attorney supervision — this is
a large and growing segment (~3,000 LDPs in AZ).

Themis is the obvious tool for them — currently they use Word templates
and hand-calculate worksheets. We 10x their productivity.

---

## Revenue Projection — Year 1 & Year 3

### Year 1 (Arizona child support only, ramping)

Assume 1,500 filings in Year 1 (modest capture of ~3% of AZ child support filings):

| Stream | Events | Avg Revenue | Total |
|--------|--------|-------------|-------|
| Self-File ($99 avg) | 1,500 | $99 | $148,500 |
| E-Filing fee | 1,200 | $18 | $21,600 |
| Process Server | 600 | $30 | $18,000 |
| Attorney Consultations | 75 | $18 | $1,350 |
| Attorney Conversions | 15 | $750 | $11,250 |
| Paralegal Subs (5) | 5×12mo | $79 | $4,740 |
| **Year 1 Total** | | | **~$205,440** |

### Year 3 (Full AZ family law — child support + divorce + protective orders)

Assume 15,000 filings in Year 3:

| Stream | Events | Avg Revenue | Total |
|--------|--------|-------------|-------|
| Self-File ($99 avg) | 15,000 | $99 | $1,485,000 |
| E-Filing fee | 12,000 | $18 | $216,000 |
| Process Server | 6,000 | $30 | $180,000 |
| Attorney Consultations | 750 | $18 | $13,500 |
| Attorney Conversions | 150 | $750 | $112,500 |
| Paralegal Subs (50) | 50×12mo | $79 | $47,400 |
| Attorney Subs (20) | 20×12mo | $199 | $47,760 |
| County Licenses (3) | 3 | $10,000 | $30,000 |
| **Year 3 Total** | | | **~$2,132,160** |

### Year 5 (Multi-state — AZ, TX, CA, FL + all family law forms)

Conservative estimate: **$8-12M annual revenue**

---

## Customer Lifetime Value Math

### Self-File Customer Journey

A typical Self-File customer:
1. **Buys document prep**: $99 (Stream 1)
2. **Pays e-filing fee**: $18 margin (Stream 2)
3. **Books process server**: $30 margin (Stream 3)

**Total value per Self-File customer**: $147

### Customer Who Escalates to Attorney

1. **Buys document prep**: $99
2. **Hits a complex question**, books consult: $18 margin (Stream 4)
3. **Converts to full representation**: $750 (Stream 5)

**Total value per Escalating customer**: $867

**Even better** — this customer may come BACK for modification filings later.

---

## Implementation Priority

**Phase 1 (MVP launch)**: Stream 1 only (Self-File)
**Phase 2 (3 months post-launch)**: Add Streams 2 + 3 (E-Filing + Process Server)
**Phase 3 (6 months)**: Add Streams 4 + 5 (Attorney Network)
**Phase 4 (12 months)**: Add Streams 6 + 7 + 8 (Subscriptions + Licensing)

---

## Open Questions for Commander

1. **Process Server Partnership**: Should we start recruiting process servers
   in Phase 1 (so they're ready at launch), or wait until Phase 2?

2. **Attorney Partnership**: Do you have existing relationships with AZ
   family law attorneys we could pilot with? If not, I recommend starting
   with 2-3 solo practitioners in Navajo/Maricopa counties who'd pilot the
   consultation system.

3. **Pricing psychology**: $99 vs $149 for Self-File Plus? $99 is the magic
   price point (below $100 is psychological barrier). $149 might reduce
   volume 30-40% for only 50% more revenue per transaction.

4. **Attorney conversion fee structure**: Flat fee ($750) vs revenue share
   (12% first year)? Flat is simpler but revenue share builds in more
   upside on big cases.
