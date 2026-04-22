# Themis Court Path — Master Work Order Package (REVISED)
## Document ID: TCP-WO-MASTER-002 Rev A
## Supersedes: TCP-WO-MASTER-001 (still valid for marketing content drafts and research deliverables)
## Date: 2026-04-22
## Status: ACTIVE — Architectural Foundation Sprint

---

## Why This Revision

After deploying the initial app to Cloud Run on 2026-04-21, the Commander identified critical architectural requirements (RBAC, audit logging, tenant isolation, SOC 2 readiness) that must be in place from day one to support:
- Sale of the platform as an asset
- Enterprise (law firm) customers
- Customer trust with extreme PII (SSN, DL, financial)
- Acquisition due diligence

This revision reorders work to build the secure foundation **first**, then re-attach existing work (filing wizard, marketing content, deployment) on top.

---

## Architecture Reference

All work orders in this package must comply with **TCP-ARCH-001 Rev A** at:
`Z:\SE_T1\THEMIS\00_ARCHITECTURE\ARCHITECTURE.md`

Deviations require an amendment to that document.

---

## Phased Work Plan

### Phase 0 — Foundation (NEW — current sprint)

| WO | Title | Priority | Est. Hours | Dependencies |
|----|-------|----------|------------|--------------|
| TCP-WO-100 | GitHub repo setup + branch protection | CRITICAL | 1 | None |
| TCP-WO-101 | VPC + Cloud SQL (private IP) provisioning | CRITICAL | 3 | TCP-WO-100 |
| TCP-WO-102 | Cloud KMS key hierarchy + Secret Manager setup | CRITICAL | 2 | TCP-WO-100 |
| TCP-WO-103 | BigQuery audit log dataset + IAM segregation | CRITICAL | 2 | TCP-WO-100 |
| TCP-WO-104 | Multi-tenant data model design + migration scripts | CRITICAL | 4-6 | TCP-WO-101 |
| TCP-WO-105 | Casbin RBAC policy engine integration | CRITICAL | 4-6 | TCP-WO-104 |
| TCP-WO-106 | PostgreSQL RLS policies + per-request scoping middleware | CRITICAL | 4 | TCP-WO-104 |
| TCP-WO-107 | Field-level encryption library (Tier 0 fields) | CRITICAL | 3-4 | TCP-WO-102 |
| TCP-WO-108 | Audit log middleware + hash-chain implementation | CRITICAL | 4-5 | TCP-WO-103 |
| TCP-WO-109 | Cross-tenant test suite + authz test framework | CRITICAL | 3-4 | TCP-WO-105, 106, 107 |
| TCP-WO-110 | CI/CD pipeline with security gates | HIGH | 3 | TCP-WO-100, 109 |
| TCP-WO-111 | Cloud Armor (WAF) + DDoS configuration | HIGH | 2 | TCP-WO-101 |
| TCP-WO-112 | Backup + DR procedures + first restore drill | HIGH | 2 | TCP-WO-101 |

**Phase 0 Total**: ~37-46 hours over 2-3 weeks

### Phase 1 — Auth + Filing Reconnect

| WO | Title | Priority | Est. Hours | Dependencies |
|----|-------|----------|------------|--------------|
| TCP-WO-200 | User auth: email/password + Google OAuth + MFA | HIGH | 6-8 | Phase 0 complete |
| TCP-WO-201 | Migrate filing wizard to authenticated multi-tenant model | HIGH | 6-8 | TCP-WO-200 |
| TCP-WO-202 | Encrypted document storage (Cloud Storage + per-org buckets) | HIGH | 3-4 | TCP-WO-107 |
| TCP-WO-203 | Customer dashboard ("My Filings") | HIGH | 4-6 | TCP-WO-201 |

### Phase 2 — Payments + Subscriptions

| WO | Title | Priority | Est. Hours | Dependencies |
|----|-------|----------|------------|--------------|
| TCP-WO-300 | Stripe integration: customer + payment method | HIGH | 4 | Phase 1 complete |
| TCP-WO-301 | One-time payment ($99 filing fee) | HIGH | 3 | TCP-WO-300 |
| TCP-WO-302 | Subscription tiers (Self-File Plus monthly, Firm Subscription) | MEDIUM | 5-6 | TCP-WO-300 |
| TCP-WO-303 | Webhook handler with signature verification + audit | HIGH | 3 | TCP-WO-300 |
| TCP-WO-304 | Billing portal (invoices, payment history, receipts) | MEDIUM | 4 | TCP-WO-301 |

### Phase 3 — Calendar System

| WO | Title | Priority | Est. Hours | Dependencies |
|----|-------|----------|------------|--------------|
| TCP-WO-400 | Calendar data model (cases, events, reminders) | MEDIUM | 3 | Phase 1 complete |
| TCP-WO-401 | Built-in calendar UI (month/week/day views) | MEDIUM | 6-8 | TCP-WO-400 |
| TCP-WO-402 | .ics export endpoint (RFC 5545 compliant) | MEDIUM | 3 | TCP-WO-400 |
| TCP-WO-403 | Email reminder system (SendGrid/Postmark) | MEDIUM | 3-4 | TCP-WO-400 |
| TCP-WO-404 | Google Calendar OAuth integration (optional sync) | LOW | 4 | TCP-WO-402 |

### Phase 4 — Marketing Site (WordPress)

| WO | Title | Priority | Est. Hours | Dependencies |
|----|-------|----------|------------|--------------|
| TCP-WO-500 | Install Astra theme + Elementor on themiscourtpath.com | LOW | 1 | None |
| TCP-WO-501 | Build pages from drafted content (06_MARKETING/website_copy/) | LOW | 4-6 | TCP-WO-500 |
| TCP-WO-502 | Configure Yoast SEO + sitemap | LOW | 2 | TCP-WO-501 |
| TCP-WO-503 | Publish 3 seed blog posts | LOW | 2 | TCP-WO-501 |

### Phase 5 — Beta + Launch

| WO | Title | Priority | Est. Hours | Dependencies |
|----|-------|----------|------------|--------------|
| TCP-WO-600 | Recruit 5-10 beta users | HIGH | 2 | Phase 1-3 complete |
| TCP-WO-601 | Beta feedback cycle | HIGH | varies | TCP-WO-600 |
| TCP-WO-602 | Public launch | CRITICAL | 1 | TCP-WO-601 |
| TCP-WO-603 | Engage SOC 2 Type I auditor | HIGH | 2 (mgmt time) | TCP-WO-602 |

### Phase 6 — SOC 2 Type II (Month 12+)

| WO | Title | Priority | Est. Hours |
|----|-------|----------|------------|
| TCP-WO-700 | Compliance automation tooling (Vanta or Drata) | HIGH | 4 (setup) |
| TCP-WO-701 | Year-long observation period | HIGH | ongoing |
| TCP-WO-702 | SOC 2 Type II audit | HIGH | mgmt time |

---

## Status of Pre-Existing Work Orders

| Original WO | Status | Disposition |
|-------------|--------|-------------|
| TCP-WO-001 (Domain) | DONE | Stays |
| TCP-WO-002 (Logo) | DONE | Stays |
| TCP-WO-003 (GCP Setup) | DONE | Stays — extended in Phase 0 |
| TCP-WO-004 (Workspace Email) | PENDING | Re-scoped to Phase 1 |
| TCP-WO-005 (Cloud Run Deploy) | DONE | Replaced by Phase 0 + 1 deploy with proper architecture |
| TCP-WO-006 (Production Hardening) | PARTIAL | Superseded by Phase 0 |
| TCP-WO-007 (PDF Audit) | DONE | Findings carry into Phase 1 |
| TCP-WO-008 (County Templates) | RESEARCH DONE | Implementation in Phase 1+ |
| TCP-WO-009 (eFileAZ Research) | DONE | Implementation deferred to Phase 4+ |
| TCP-WO-010 (Compliance) | RESEARCH DONE | Updated for SOC 2 in Phase 0 |
| TCP-WO-011 (Marketing Site) | CONTENT DONE | Implementation in Phase 4 |
| TCP-WO-012 (Stripe) | PENDING | Re-scoped to Phase 2 |
| TCP-WO-013 (User Auth) | PENDING | Re-scoped to Phase 1 |
| TCP-WO-014 (Process Server) | RESEARCH DONE | Phase 4+ feature |
| TCP-WO-015 (Attorney Network) | RESEARCH DONE | Phase 4+ feature |

**No prior work is wasted.** Research, content drafts, and deployed app remain valuable. Phase 0 is the foundation that everything else attaches to properly.

---

## Current Production Status (Snapshot)

- **App URL**: https://themis-app-909223653643.us-west1.run.app (live, single-tenant, no auth)
- **Custom domain**: app.themiscourtpath.com (DNS configured, SSL pending)
- **Marketing site**: themiscourtpath.com (default WordPress install, awaiting content)
- **GCP project**: themis-court-path
- **Region**: us-west1
- **Status**: Demo-ready but **not production-ready for paying customers** until Phase 1 complete

---

## Decision Authority

| Decision Type | Decider |
|---------------|---------|
| Architecture changes | Commander (proposed by Lead Architect) |
| Work order priority | Commander |
| Sprint planning | Lead Architect (Agent B) |
| Implementation approach within a WO | Lead Architect |
| Customer-facing copy | Commander reviews |
| Pricing | Commander |
| Vendor selection (BAA/DPA required) | Commander |

---

## Sprint Cadence

- **Sprint 1** (week 1): TCP-WO-100, 101, 102, 103
- **Sprint 2** (week 2): TCP-WO-104, 105, 106
- **Sprint 3** (week 3): TCP-WO-107, 108, 109, 110, 111, 112
- **Phase 0 review**: end of week 3, Commander sign-off
- **Phase 1**: weeks 4-5
- **Phase 2**: week 6
- **Phase 3**: week 7
- **Phase 4**: week 7 (parallel)
- **Phase 5 launch**: week 8

Total: ~8 weeks to production launch with proper foundation.

---

*TCP-WO-MASTER-002 Rev A — Master Work Order Package (Revised)*
*Authority: Commander Gary Spear*
*Architect: Agent B (Claude Code)*
