# Themis Court Path — SOC 2 Type II Readiness Checklist
## Document ID: TCP-COMP-001 Rev A
## Date: 2026-04-22
## Authority: Commander Gary Spear

---

## Purpose

Track progress toward SOC 2 Type II audit readiness. Each item maps to a Trust Services Criterion (TSC) under one of the five categories. Themis targets:
- **Security** (mandatory)
- **Availability** (recommended for SaaS)
- **Confidentiality** (recommended for legal data)
- *Privacy* and *Processing Integrity* (Phase 6+ when revenue justifies)

---

## Audit Timeline

| Milestone | Target |
|-----------|--------|
| Foundation built (Phase 0 complete) | Week 3 |
| Begin observation period | Week 4 (post-Phase 0 sign-off) |
| Complete 6 months of observation with controls operating | Month 6 |
| SOC 2 Type I audit (point-in-time) | Month 6 |
| Complete 12-month observation period | Month 12 |
| SOC 2 Type II audit | Month 13 |
| Type II report issued | Month 14 |

---

## TSC: Security (CC — Common Criteria)

### CC1 — Control Environment

- [ ] CC1.1 — Organizational chart documented; roles and responsibilities defined
- [ ] CC1.2 — Board oversight (Commander serves as board for closely-held entity)
- [ ] CC1.3 — Code of conduct / acceptable use policy
- [ ] CC1.4 — Hiring practices documented (background checks for staff with data access)
- [ ] CC1.5 — Performance management process

### CC2 — Communication and Information

- [ ] CC2.1 — Policies communicated to staff (intranet/wiki)
- [ ] CC2.2 — Communications with customers (status page, security disclosures)
- [ ] CC2.3 — Communication channels for whistleblower / security disclosures (`security@themiscourtpath.com`)

### CC3 — Risk Assessment

- [ ] CC3.1 — Risk register maintained at `00_ARCHITECTURE/RISK_REGISTER.md`
- [ ] CC3.2 — Risks reviewed annually (or on material changes)
- [ ] CC3.3 — Vendor risk assessment process
- [ ] CC3.4 — Fraud risk assessment

### CC4 — Monitoring Activities

- [ ] CC4.1 — Continuous monitoring (Cloud Monitoring + alerting)
- [ ] CC4.2 — Internal audit cadence (quarterly)

### CC5 — Control Activities

- [ ] CC5.1 — Logical access controls (RBAC + MFA)
- [ ] CC5.2 — Change management (PR reviews, deploy approvals)
- [ ] CC5.3 — Segregation of duties (engineering ≠ compliance ≠ break-glass approver)

### CC6 — Logical and Physical Access

- [ ] CC6.1 — Logical access provisioning (formal request, time-limited)
- [ ] CC6.2 — Logical access removal (offboarding within 24h)
- [ ] CC6.3 — Authentication strength (MFA mandatory for elevated roles)
- [ ] CC6.4 — Network access controls (VPC, private IP for DB)
- [ ] CC6.5 — Encryption at rest and in transit
- [ ] CC6.6 — System hardening (no unused services, patching)
- [ ] CC6.7 — Secure data disposal (cryptographic erasure)
- [ ] CC6.8 — Vulnerability management (Dependabot, Trivy, periodic pen test)

### CC7 — System Operations

- [ ] CC7.1 — Detection of security events (Cloud Logging + Security Command Center)
- [ ] CC7.2 — Monitoring of anomalies
- [ ] CC7.3 — Evaluation of security incidents
- [ ] CC7.4 — Incident response plan documented and tested
- [ ] CC7.5 — Recovery from incidents (DR procedures)

### CC8 — Change Management

- [ ] CC8.1 — Code review required for production changes
- [ ] CC8.2 — Testing before deployment (CI gates)
- [ ] CC8.3 — Deployment approval (production gate)

### CC9 — Risk Mitigation

- [ ] CC9.1 — Vendor selection process (DPA review)
- [ ] CC9.2 — Backup and recovery plans

---

## TSC: Availability (A)

- [ ] A1.1 — Capacity planning (Cloud Run autoscaling, monitoring)
- [ ] A1.2 — Backup and recovery testing (quarterly DR drill)
- [ ] A1.3 — Environmental protections (cloud provider responsibility, documented)

---

## TSC: Confidentiality (C)

- [ ] C1.1 — Confidential information identified (data classification policy)
- [ ] C1.2 — Confidential information protected during retention (encryption + access controls)
- [ ] C1.3 — Confidential information disposed of securely (cryptographic erasure)

---

## Evidence Collection Strategy

SOC 2 audits are fundamentally about **evidence**: showing the auditor that controls operated effectively over the observation period. Strategies:

### Automated Evidence Collection

Use **Vanta** or **Drata** for compliance automation (recommended for Phase 1):
- Connects to GCP, GitHub, Stripe, etc.
- Auto-collects evidence (e.g., MFA status of all users)
- Generates the SOC 2 report drafts
- Cost: $15K-25K/year, but saves 100+ hours of manual evidence collection

### Manual Evidence Categories

| Evidence Type | Source | Frequency |
|--------------|--------|-----------|
| Access reviews | Quarterly export of all user permissions | Quarterly |
| Change tickets | GitHub PR records | Continuous |
| Incident reports | INCIDENT_RUNBOOK.md history | As occur |
| DR drill results | Documented in runbook | Quarterly |
| Pen test reports | Third-party reports | Annually |
| Vendor reviews | Vendor risk register | Annually |
| Training records | Security training completion | Annually per staff |
| Background checks | HR records (for staff with data access) | On hire |

---

## Vendor Compliance Requirements

| Vendor | Required Evidence |
|--------|-------------------|
| Google Cloud | SOC 2 Type II report (publicly available) |
| Stripe | SOC 1 + SOC 2 + PCI DSS reports (NDA available) |
| SiteGround | Verify SOC 2 report availability |
| GitHub | SOC 1 + SOC 2 reports (publicly available) |
| Email provider (TBD) | Must have SOC 2 before adoption |

---

## Common SOC 2 Findings (We Want to Avoid)

| Finding | Prevention |
|---------|-----------|
| Standing access for engineers to production data | Break-glass model |
| MFA not enforced for all privileged users | Mandatory for `themis_*` roles |
| Audit logs deletable | BigQuery with explicit deny on DELETE |
| No documented incident response | INCIDENT_RUNBOOK.md |
| No DR testing | Quarterly drills documented |
| Untested backups | Restore tests |
| Vague vendor agreements | DPA with every vendor touching PII |
| Unencrypted backups | CMEK on all backups |
| Generic passwords / shared accounts | Per-user accounts, MFA |
| No vulnerability management | Patch SLAs in ARCHITECTURE.md §11.4 |

---

## Pre-Audit Self-Assessment

Before engaging an auditor for Type I, run through:

1. [ ] All Phase 0 work orders complete and tested
2. [ ] All policies documented and signed
3. [ ] All controls implemented per ARCHITECTURE.md
4. [ ] 30 days of clean audit log evidence
5. [ ] Incident response plan tested via tabletop exercise
6. [ ] DR drill completed in last 90 days
7. [ ] Penetration test completed and findings remediated
8. [ ] Vendor DPAs all in place
9. [ ] Staff trained on security policies
10. [ ] Vanta/Drata showing >95% control coverage

---

## Audit Firm Selection

When ready to engage an auditor:

### Recommended Firms (SaaS-focused, reasonable for small companies)

1. **A-LIGN** — Mid-tier, SaaS-focused, fixed-fee available
2. **Sensiba San Filippo** — Tech-focused, good for early-stage
3. **Schellman** — Higher-end, often required by enterprise customers

### Costs (Approximate)

| Audit | Cost |
|-------|------|
| SOC 2 Type I (point-in-time) | $15K-30K |
| SOC 2 Type II (year observation) | $25K-50K |
| Compliance automation tooling | $15K-25K/yr |
| Pen test (annual) | $8K-20K |
| **Total Year 1 compliance budget** | **$60K-125K** |

This is a real cost but necessary for B2B sales above ~$10K ACV.

---

## Status Dashboard

Maintain a status spreadsheet at `00_ARCHITECTURE/SOC2_STATUS.xlsx` (or equivalent) tracking:
- Each control: Owner, Status, Evidence Location, Last Tested
- Open findings
- Remediation deadlines

---

*TCP-COMP-001 Rev A — SOC 2 Type II Readiness Checklist*
*Authority: Commander Gary Spear*
