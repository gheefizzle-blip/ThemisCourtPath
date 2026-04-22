# Themis Court Path — System Architecture
## Document ID: TCP-ARCH-001 Rev A
## Status: APPROVED — Foundation Architecture
## Date: 2026-04-22
## Authority: Commander Gary Spear

---

## Purpose of This Document

This document defines the foundational architecture for Themis Court Path. It is the **source of truth** for all infrastructure, security, and data-handling decisions. All subsequent work orders must comply with this architecture. Changes to this document require Commander approval.

The architecture is designed to satisfy:
- **SOC 2 Type II** controls (system trust)
- **PCI DSS** (via Stripe offload)
- **CCPA / Arizona A.R.S. 18-552** (privacy + breach notification)
- **Attorney work product confidentiality** (legal sensitivity)
- **Acquisition due diligence** (clean technical IP)

---

## 1. Executive Summary

### 1.1 Architectural Tenets

1. **Defense in depth** — never rely on a single layer for security
2. **Tenant isolation by default** — opt-in to share, never opt-out
3. **Least privilege everywhere** — including for Themis employees
4. **Auditable by design** — every privileged action leaves a trail
5. **Encryption at every layer** — at rest, in transit, application-level for sensitive fields
6. **Customer data sovereignty** — "We cannot read your data without leaving evidence"
7. **Acquisition-ready** — clean trail of decisions, no shortcuts that haunt diligence

### 1.2 The Three Pillars

| Pillar | Mechanism | Verification |
|--------|-----------|--------------|
| **Access Control** | Casbin RBAC + PostgreSQL RLS + per-request scoping | Automated authz tests on every deploy |
| **Audit Logging** | BigQuery append-only with hash-chained entries | Tamper detection on log replay |
| **Tenant Isolation** | RLS + per-tenant KMS keys + per-org Cloud Storage buckets | Cross-tenant access tests on every deploy |

---

## 2. Compliance Framework

### 2.1 Frameworks That Apply

| Framework | Applies | Why | Action |
|-----------|---------|-----|--------|
| **SOC 2 Type II** | YES | Standard for SaaS trust; required for B2B sales and acquisition | Design to it from day 1; audit at month 12 |
| **PCI DSS** | YES (offloaded) | Credit card processing | Use Stripe; never touch card data |
| **CCPA** | YES | Any California consumer | Honor deletion, export, opt-out requests |
| **Arizona A.R.S. 18-552** | YES | Breach notification within 45 days | Documented incident response plan |
| **GLBA Safeguards** | LIKELY | Income/financial data collection | Implement WISP (written info security plan) |
| **State Bar Rules** | YES (Arizona) | Attorney referral fees, UPL boundaries | See compliance package |
| **HIPAA** | NO | Not health data | Confirm in legal review |

### 2.2 Compliance Roles

| Role | Responsibility |
|------|---------------|
| **Commander Gary Spear** | Final accountability, designates DPO, approves policy changes |
| **Data Protection Officer (DPO)** | TBD — may be Commander initially | Privacy requests, breach response, vendor reviews |
| **Security Lead** | TBD | Vulnerability management, incident response |
| **Compliance Tooling** | Vanta or Drata (Phase 2) | Automated SOC 2 control evidence |

---

## 3. Data Classification

### 3.1 Sensitivity Tiers

| Tier | Examples | Storage | Encryption | Access |
|------|----------|---------|------------|--------|
| **Tier 0 — Critical** | SSN, Driver's License, Financial Account Numbers | Cloud SQL (encrypted blob) | Per-tenant KMS key | App roles only with scope check; audit on every read |
| **Tier 1 — Highly Sensitive** | Income, employer details, court documents, children's PII | Cloud SQL or Cloud Storage | Per-tenant KMS (CMEK) | App roles only; audit on every read |
| **Tier 2 — Sensitive** | Names, DOB, addresses, phone, email | Cloud SQL | DB-level encryption at rest | App roles with tenant scope; audit on writes |
| **Tier 3 — Internal** | User IDs, session IDs, internal events | Cloud SQL or BigQuery | DB-level encryption at rest | App or analytics roles |
| **Tier 4 — Public** | Marketing pages, blog posts, FAQs | Cloud Storage / WordPress | TLS in transit | Public read |

### 3.2 Tier 0 Data Handling Rules

- **Never logged in plaintext** anywhere (app logs, audit logs, error messages)
- **Always tokenized** in URLs (e.g., `case_id=f_abc123`, never SSN)
- **Always masked in UI** by default (e.g., `***-**-1234`); full reveal requires explicit user action + audit entry
- **Never sent in email** (use secure portal references)
- **Per-tenant KMS keys** ensure that even DBAs cannot decrypt one customer's data using another customer's key
- **Field-level encryption** in addition to disk-level encryption (defense in depth)

---

## 4. Multi-Tenant Architecture

### 4.1 Tenancy Model: Shared Schema with Row-Level Security (RLS)

**Decision**: Single PostgreSQL database, single schema, with `organization_id` and `user_id` discriminator columns and PostgreSQL RLS policies enforced at the database layer.

**Why not database-per-tenant?**
- Operational overhead grows linearly with customers (unsustainable past 100 tenants)
- Schema migrations become a project per customer
- Backup/restore complexity multiplies

**Why not schema-per-tenant?**
- Same migration problem at scale
- PostgreSQL has 65,535 schema limit (theoretical, but practical issues at 1,000+)

**Why shared schema with RLS?**
- One schema to maintain
- RLS enforced by database, not by trust in application code
- Battle-tested at scale (used by Notion, Heroku, GitLab, etc.)
- Migration to per-DB later possible for enterprise tier

### 4.2 The Tenant Hierarchy

```
Organization (tenant root)
├── Owner Users (org_owner)
├── Admin Users (org_admin)
├── Member Users (org_attorney, org_paralegal)
└── Cases / Filings (owned by users, scoped to organization)

Consumer Users (no organization)
├── Personal Cases (owned by user only)
└── Optional Collaborators (limited scope, specific case)
```

### 4.3 RLS Implementation Pattern

Every tenant-scoped table follows this pattern:

```sql
CREATE TABLE filings (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    organization_id UUID,             -- NULL for consumer-direct
    owner_user_id UUID NOT NULL,
    case_data BYTEA,                  -- encrypted blob (Tier 0/1)
    created_at TIMESTAMPTZ DEFAULT NOW(),
    -- ...
);

ALTER TABLE filings ENABLE ROW LEVEL SECURITY;

CREATE POLICY filings_tenant_isolation ON filings
  FOR ALL
  USING (
    -- Org user: see filings in their org
    (organization_id = current_setting('app.current_org_id', true)::uuid)
    OR
    -- Consumer: see only filings they own
    (owner_user_id = current_setting('app.current_user_id')::uuid AND organization_id IS NULL)
  );
```

**Application contract**: Every database connection MUST set `app.current_user_id` and `app.current_org_id` (if applicable) at the start of every request. The connection pool middleware enforces this.

### 4.4 Cross-Tenant Operations

The only operations that legitimately cross tenants:
- **Themis admin support actions** — require ticket reference + audit entry
- **Aggregate analytics** — anonymized, aggregated counts only (no individual records)
- **System cron jobs** — use service account with explicit scope, audit logged

All cross-tenant queries must be code-reviewed and explicitly tagged `# CROSS-TENANT-OK: <reason>`.

---

## 5. Identity & Access Management (RBAC)

### 5.1 The Permission Model

```
Permission = Role × Scope × Action × Resource

Example resolved permission:
  "org_paralegal at org_abc can READ filings WHERE filing.owner_user_id IN (org_abc.users)"
```

### 5.2 Built-in Roles

| Role | Scope | Default Permissions |
|------|-------|---------------------|
| `themis_super_admin` | Global | All — but every action logged + alerts |
| `themis_engineer` | Production: NO data; Logs: YES | Code deploys, infra changes (audit logged) |
| `themis_support` | Customer data with ticket | Read with ticket binding + MFA + audit |
| `themis_sales` | Aggregate only | Counts, conversion metrics (no PII) |
| `org_owner` | Their organization | All within org, billing, member management |
| `org_admin` | Their organization | Member management, case visibility, no billing |
| `org_attorney` | Cases assigned to them | Read/write assigned cases |
| `org_paralegal` | Cases assigned to them | Read/write assigned cases (no billing) |
| `consumer` | Their own cases | Read/write own cases only |
| `consumer_collaborator` | Specific case, limited fields | Future: ex-spouse co-signing, etc. |

### 5.3 MFA Requirements

| Role | MFA |
|------|-----|
| All `themis_*` roles | **Mandatory** (TOTP minimum, hardware key recommended) |
| `org_owner`, `org_admin` | **Mandatory** |
| `org_attorney`, `org_paralegal` | **Strongly recommended; mandatory by Phase 2** |
| `consumer` | Optional but encouraged |

### 5.4 Authentication Methods

| Method | Available For | Notes |
|--------|--------------|-------|
| Email + password | All roles | bcrypt hashed (cost 12), password rules enforced |
| Google OAuth | Consumers, org members | Reduces password fatigue |
| Microsoft OAuth | Org members (Phase 2) | For firms on Microsoft 365 |
| SAML SSO | Org enterprise tier (Phase 3) | For large law firms |
| Magic link | Consumers | Optional passwordless |

### 5.5 Session Management

- Session tokens: HttpOnly, Secure, SameSite=Strict cookies
- Access token lifetime: 1 hour
- Refresh token lifetime: 30 days, rotating on each use
- Concurrent session limit: 5 per user (configurable per role)
- Session invalidation on password change, role change, or suspicious activity

### 5.6 Themis Employee Access ("Break-Glass")

To support customers, Themis support may need to view a customer's data. This is governed:

1. Support agent receives customer ticket
2. Agent submits "data access request" with: customer ID, ticket ID, business reason, time-boxed duration
3. Approver (rotating shift lead) approves or denies
4. On approval: short-lived access token issued, scoped to that customer only
5. Every read action during the session is logged
6. Customer is notified by email after the session closes
7. Audit log entry includes the ticket reference and approver

**No standing access to production customer data exists for any Themis employee.**

---

## 6. Audit Logging Architecture

### 6.1 The Architecture

```
[Flask App] ──writes──▶ [Cloud SQL: app data]
     │
     └──Pub/Sub──▶ [Audit Service] ──writes──▶ [BigQuery: audit_log]
                                                   │
                                                   ├── partitioned by date (YYYY-MM-DD)
                                                   ├── append-only (no DELETE/UPDATE perms)
                                                   ├── retention: 7 years
                                                   ├── separate IAM (different service account)
                                                   └── nightly hash-chain verification job
```

### 6.2 Schema (BigQuery)

```sql
CREATE TABLE audit_log (
    audit_id STRING NOT NULL,         -- UUID v7 (time-ordered)
    timestamp TIMESTAMP NOT NULL,
    actor_user_id STRING,
    actor_role STRING,
    actor_auth_method STRING,
    actor_ip_address STRING,
    actor_user_agent STRING,
    actor_geo STRING,                  -- "US-AZ-Show Low" (city-level)
    session_id STRING,
    request_id STRING,                 -- correlate to app logs
    action STRING NOT NULL,            -- e.g., "filing.read", "user.login"
    resource_type STRING,              -- e.g., "filing", "user"
    resource_id STRING,
    resource_owner_user_id STRING,
    organization_id STRING,
    result STRING NOT NULL,            -- "success", "denied", "error"
    failure_reason STRING,
    data_classification ARRAY<STRING>, -- which tiers were accessed
    fields_accessed ARRAY<STRING>,     -- e.g., ["ssn:masked", "dob:full"]
    metadata JSON,                     -- action-specific context
    previous_audit_id STRING,          -- chain pointer
    previous_hash STRING,              -- SHA-256 of previous entry
    current_hash STRING,               -- SHA-256 of this entry
    ticket_reference STRING            -- support ticket if break-glass
)
PARTITION BY DATE(timestamp)
CLUSTER BY actor_user_id, action;
```

### 6.3 What Triggers an Audit Entry

| Action Class | Examples | Logged |
|--------------|----------|--------|
| **Authentication** | login, logout, MFA challenge, password change | Always |
| **Authorization** | permission denied, role change | Always |
| **Tier 0 read** | View SSN, DL, account number (full or partial) | Always with field detail |
| **Tier 1 read** | View income, employer, court documents | Always |
| **Any write** | Create, update, delete on customer data | Always |
| **Export** | Download PDF, generate report | Always |
| **Admin actions** | User invite, role assignment, billing change | Always |
| **Themis employee access** | Break-glass session start/end, every read within | Always with ticket ref |
| **System events** | Backup, restore, deployment | Always |

### 6.4 Hash Chain (Tamper Detection)

Each entry includes:
- `previous_hash` — SHA-256 of the previous entry's `current_hash`
- `current_hash` — SHA-256 of (this entry's content + previous_hash)

Nightly job: walks the chain, verifies every hash. Any break triggers a P0 alert.

### 6.5 Why BigQuery (Not Cloud SQL)

- **Different IAM** — engineering team has zero access; only Compliance Lead and DPO
- **Append-only by design** — DELETE requires special permissions never granted to app accounts
- **Query at scale** — billions of rows, sub-second queries, $0.02/GB stored
- **7-year retention** is cheap (vs. expanding Cloud SQL)
- **Separate failure domain** — if Cloud SQL is compromised, audit log is intact

### 6.6 Log Retention

| Log Type | Retention | Storage |
|----------|-----------|---------|
| Audit log (BigQuery) | 7 years | Hot 90 days, cold remainder |
| Application logs (Cloud Logging) | 30 days | Standard |
| Access logs (Load Balancer) | 90 days | Standard |
| Security events (Cloud Logging filtered) | 7 years | Cold storage |

---

## 7. Encryption Strategy

### 7.1 At Rest

| Layer | Mechanism | Key |
|-------|-----------|-----|
| Cloud SQL disk | AES-256 (Google-managed) | Auto-rotated by Google |
| Cloud SQL with CMEK (Phase 2) | AES-256 with customer-managed key | Cloud KMS, manually rotated |
| Cloud Storage | AES-256 (Google-managed by default) | Per-bucket |
| Cloud Storage with CMEK | AES-256 (CMEK) | Per-organization KMS key |
| BigQuery audit log | AES-256 (Google-managed) | Auto-managed |

### 7.2 In Transit

- All external traffic: TLS 1.3 minimum
- Internal Google Cloud traffic: encrypted by default (Google-managed)
- Cloud Run ↔ Cloud SQL: TLS 1.3 over private IP via VPC connector

### 7.3 Application-Level (Field Encryption)

Tier 0 fields (SSN, DL) are encrypted in the application layer before persistence:

```python
# Pseudocode
def store_ssn(user_id, ssn_plaintext, organization_id):
    key = kms_client.get_key(f"tenant-{organization_id or user_id}-ssn")
    encrypted = key.encrypt(ssn_plaintext)
    db.execute(
        "UPDATE users SET ssn_encrypted = $1 WHERE id = $2",
        encrypted, user_id
    )
```

**Per-tenant key isolation**: If an attacker dumps the database, decrypting any one tenant's data does not help decrypt another tenant's data.

### 7.4 Key Management

| Key Type | Stored In | Rotation |
|----------|-----------|----------|
| Per-tenant data encryption keys | Cloud KMS | Annual or on-demand |
| Application secrets (DB password, Stripe keys) | Secret Manager | Quarterly |
| TLS certificates | Cloud Run automatic / Let's Encrypt | Auto-renewed every 90 days |
| OAuth signing keys | Secret Manager | Annual |
| Audit log signing key | Secret Manager (HSM-backed) | Annual |

---

## 8. Network Architecture

### 8.1 Topology

```
Internet
    │
    ▼
[Cloud Armor — WAF + DDoS]
    │
    ▼
[Global HTTPS Load Balancer]
    │
    ├─▶ [Cloud Run: Themis App]
    │        │
    │        ├─VPC connector──▶ [VPC: themis-prod]
    │        │                       │
    │        │                       ├─▶ [Cloud SQL — private IP only]
    │        │                       └─▶ [Memorystore Redis (Phase 2)]
    │        │
    │        ├──────────────▶ [Secret Manager]
    │        ├──────────────▶ [Cloud KMS]
    │        ├──────────────▶ [Cloud Storage (per-org buckets)]
    │        └──────────────▶ [Cloud Pub/Sub] ──▶ [BigQuery: audit_log]
    │
    └─▶ [Cloud CDN: WordPress assets]
            │
            └─▶ [SiteGround — themiscourtpath.com (marketing)]
```

### 8.2 VPC Configuration

- **VPC**: `themis-prod` (us-west1)
- **Subnet**: `themis-prod-subnet` (10.10.0.0/24)
- **Cloud SQL**: private IP only (no public IP)
- **Cloud Run**: connects via VPC Serverless Connector
- **Egress**: restricted to known endpoints (Stripe API, KMS, Secret Manager)
- **Firewall rules**: deny-all by default, allow-list explicit

### 8.3 DDoS & WAF Protection

- **Cloud Armor**: enabled with OWASP Top 10 ruleset
- **Rate limiting**: per-IP at the LB layer (in addition to app-layer)
- **Bot detection**: reCAPTCHA Enterprise on signup and submission endpoints
- **Geo restrictions**: US/Canada only initially (configurable)

### 8.4 DNS

- **themiscourtpath.com**: A/AAAA record → SiteGround (WordPress marketing)
- **app.themiscourtpath.com**: CNAME → Cloud Run domain mapping
- **api.themiscourtpath.com**: CNAME → Cloud Run (Phase 2 API)
- **Email**: MX → Google Workspace (Phase 2)

---

## 9. Secrets Management

**Rule**: No secrets in source code. No secrets in environment variables outside Secret Manager. No secrets in container images.

### 9.1 Secret Categories

| Secret | Stored In | Accessed By |
|--------|-----------|-------------|
| Cloud SQL password | Secret Manager | Cloud Run service account at startup |
| Stripe live secret key | Secret Manager | Cloud Run only, never logged |
| Stripe webhook signing secret | Secret Manager | Webhook handler only |
| Flask SECRET_KEY (session signing) | Secret Manager | Cloud Run at startup |
| OAuth client secrets | Secret Manager | Auth handler |
| KMS service account JSON | Workload Identity (no key file) | Cloud Run native |
| Audit log signing key | Secret Manager (HSM) | Audit service only |

### 9.2 Rotation Policy

| Secret | Rotation |
|--------|----------|
| DB password | Quarterly + on staff departure |
| Stripe keys | Quarterly + on suspected exposure |
| Flask SECRET_KEY | Annual + on suspected exposure (invalidates sessions) |
| OAuth secrets | Annual |
| TLS | Auto every 90 days (Let's Encrypt) |
| KMS encryption keys | Annual |

---

## 10. Backup & Disaster Recovery

### 10.1 Backup Strategy

| Asset | Backup Frequency | Retention | Encryption |
|-------|------------------|-----------|------------|
| Cloud SQL | Automated daily + transaction log | 30 days | CMEK |
| Cloud SQL point-in-time | Continuous | 7 days | CMEK |
| Cloud Storage (documents) | Versioning enabled + cross-region replication | Indefinite | CMEK |
| BigQuery audit log | Cross-region snapshot weekly | 7 years | Google-managed |
| Configuration (Terraform state) | Git + Cloud Storage | Indefinite | Encrypted |

### 10.2 RTO / RPO Targets

| Severity | RTO | RPO |
|----------|-----|-----|
| Single Cloud Run instance failure | < 30 sec (auto-recover) | 0 |
| Cloud SQL failover | < 5 min (HA replica in different zone) | < 1 min |
| Region failure | < 4 hours | < 15 min |
| Catastrophic loss | < 24 hours | < 1 hour |

### 10.3 DR Testing

Quarterly DR drill:
- Restore Cloud SQL from backup to staging
- Verify application can run against restored data
- Document recovery time
- Update runbook based on findings

---

## 11. Software Development Lifecycle (SDLC)

### 11.1 Code Repository

- **Hosting**: GitHub (private repo)
- **Branch strategy**: trunk-based; feature branches → PR → main
- **Required reviews**: 1 reviewer for non-Tier 0/1 code, 2 reviewers for sensitive code
- **Required checks**: lint, type check, unit tests, security scan, secrets scan

### 11.2 CI/CD Pipeline

```
PR opened ──▶ CI runs:
              ├── lint (ruff, eslint)
              ├── type check (mypy, tsc)
              ├── unit tests
              ├── integration tests
              ├── authorization tests (cross-tenant)
              ├── encryption tests
              ├── security scan (snyk, bandit)
              ├── secrets scan (gitleaks)
              └── container vulnerability scan (trivy)
                    │
                    ▼
              Merge to main ──▶ Deploy to staging ──▶ E2E tests
                                     │
                                     ▼
                               Manual approval ──▶ Deploy to production
                                                       │
                                                       └── Smoke tests
```

### 11.3 Mandatory Test Categories

| Test Type | Purpose | Frequency |
|-----------|---------|-----------|
| Unit | Function correctness | Every PR |
| Integration | Component interaction | Every PR |
| Authorization | RBAC + RLS enforcement | Every PR |
| Cross-tenant | Tenant isolation | Every PR |
| Encryption | Field-level encryption works | Every PR |
| End-to-end | User flows | Pre-deploy |
| Load | Performance under load | Weekly |
| Penetration | Security posture | Quarterly (third-party) |

### 11.4 Vulnerability Management

| Severity | Patch SLA |
|----------|-----------|
| Critical (RCE, auth bypass) | 24 hours |
| High | 7 days |
| Medium | 30 days |
| Low | Next release |

Automated scanning: Dependabot for libraries, Trivy for containers, Cloud Web Security Scanner for live endpoints.

---

## 12. Incident Response

### 12.1 Severity Levels

| Sev | Definition | Response Time | Notification |
|-----|------------|---------------|--------------|
| **SEV-1** | Production down OR confirmed customer data exposure | < 15 min | All hands, customer comms within 4h |
| **SEV-2** | Partial production impact OR suspected data exposure | < 1 hour | On-call lead, customer comms TBD |
| **SEV-3** | Degraded performance, no data risk | < 4 hours | Engineering team |
| **SEV-4** | Minor issue, scheduled fix | Next business day | Ticket queue |

### 12.2 Customer Notification Triggers

Per Arizona A.R.S. 18-552, notify affected customers within **45 days** of confirmed breach involving:
- SSN
- Driver's License
- Financial account number + access credential
- Medical information
- Online account credentials

Internal target: notify within **72 hours** (more aggressive than statute).

### 12.3 Runbook

Maintained at `Z:\SE_T1\THEMIS\00_ARCHITECTURE\INCIDENT_RUNBOOK.md` (to be created in Phase 0).

---

## 13. Vendor & Third-Party Management

### 13.1 Approved Vendors (with BAAs/DPAs as applicable)

| Vendor | Purpose | Data Touched | Agreement |
|--------|---------|--------------|-----------|
| Google Cloud Platform | Hosting, DB, KMS, audit log | All (encrypted) | Cloud DPA signed |
| Stripe | Payment processing | Payment card (we never see) | Stripe DPA signed |
| SiteGround | WordPress hosting | Marketing only (no PII) | SiteGround DPA signed |
| GitHub | Source code | No customer data | DPA signed |
| Email provider (TBD: SendGrid or Postmark) | Transactional email | Customer name, email | DPA required before use |
| Monitoring (TBD: Sentry?) | Error tracking | App errors (PII scrubbed) | DPA required, scrubbing rules |
| Analytics (TBD: Plausible or self-hosted) | Marketing analytics | No PII | Self-hosted preferred |

### 13.2 Vendor Review Cadence

- Annual review of all vendors with PII access
- Triggered review on news of vendor incidents
- Updated DPA on contract renewals

---

## 14. Phased Rollout

### Phase 0 — Foundation (NEW)
**Goal**: Stand up the secure multi-tenant foundation before adding features

Work orders TCP-WO-100 through TCP-WO-108 (see TCP-WO-MASTER-002).

### Phase 1 — Core Auth + Filing Reconnect
- Connect existing Flask filing wizard to new auth + tenant model
- Migrate existing PDF filing to use encrypted storage

### Phase 2 — Payments + Subscriptions
- Stripe integration with one-time and recurring billing
- Subscription tiers (Self-File, Self-File Plus, Firm Subscription)

### Phase 3 — Calendar System
- Built-in calendar with court date tracking
- .ics export (Google/Apple/Outlook compatible)
- Optional Google Calendar OAuth integration

### Phase 4 — Marketing Site (WordPress)
- Build the marketing site at themiscourtpath.com
- Content already drafted in `06_MARKETING/website_copy/`

### Phase 5 — Launch & SOC 2 Type I
- Beta test with 5-10 users
- Address findings
- Public launch
- Engage SOC 2 Type I auditor (point-in-time controls audit)

### Phase 6 (Month 12) — SOC 2 Type II
- Year-long observation period auditor
- Achieve Type II certification (gold standard for SaaS trust)

---

## 15. Decision Log

| Date | Decision | Rationale | Approved By |
|------|----------|-----------|-------------|
| 2026-04-22 | Adopt SOC 2 Type II as compliance target | Standard for SaaS trust + acquisition readiness | Commander Spear |
| 2026-04-22 | Shared schema with RLS for multi-tenancy | Scalability + battle-tested + operational simplicity | Commander Spear |
| 2026-04-22 | BigQuery for audit logs | Separation of concerns + scale + retention economics | Commander Spear |
| 2026-04-22 | Per-tenant KMS keys for Tier 0 data | Defense in depth + data sovereignty claim | Commander Spear |
| 2026-04-22 | Casbin for policy engine | Flexible RBAC+ABAC, mature, well-supported | Commander Spear |
| 2026-04-22 | Pause feature dev for Phase 0 foundation work | Right to do once than rebuild later | Commander Spear |

---

## 16. Approval Signatures

This architecture document requires signature before any Phase 0 work begins:

- **Commander Gary Spear** (Final Authority): _________________ Date: _______
- **Lead Architect (Agent B)**: _________________ Date: 2026-04-22

Once signed, this document becomes the authoritative reference. All work orders must comply. Deviations require a documented amendment to this architecture.

---

*TCP-ARCH-001 Rev A — Themis Court Path System Architecture*
*Prepared by Agent B (Claude Code — Lead Architect)*
*Authority: Commander Gary Spear*
