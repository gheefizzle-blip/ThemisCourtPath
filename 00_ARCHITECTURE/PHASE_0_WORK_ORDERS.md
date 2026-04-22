# Phase 0 Work Orders — Foundation Sprint
## Themis Court Path — Architectural Foundation
## Document ID: TCP-WO-PHASE0-001 Rev A
## Date: 2026-04-22

All Phase 0 work orders implement the architecture defined in `TCP-ARCH-001 Rev A` (`ARCHITECTURE.md`).

---

# TCP-WO-100: GitHub Repository + Branch Protection

**Priority**: CRITICAL | **Estimated**: 1 hour | **Dependencies**: None

## Objective
Establish version control and code review discipline as the first foundation step.

## Tasks
1. Create private GitHub repo: `themis-court-path/themis-app`
2. Push existing code from `Z:\SE_T1\THEMIS\01_APPLICATION\`
3. Configure branch protection on `main`:
   - Require PR before merge
   - Require 1 approving review
   - Require status checks (will be added in TCP-WO-110)
   - Require linear history
   - No force pushes, no deletions
4. Configure CODEOWNERS file
5. Create `.github/PULL_REQUEST_TEMPLATE.md` with security checklist
6. Add `SECURITY.md` (responsible disclosure policy)
7. Add `.gitignore` and verify no secrets in history (use gitleaks)

## Deliverables
- [ ] Private GitHub repo created
- [ ] Existing code pushed
- [ ] Branch protection configured
- [ ] CODEOWNERS, SECURITY.md, PR template in place
- [ ] gitleaks scan passed (no secrets in history)

## Acceptance Criteria
Cannot push directly to main. PR template loads on every PR. Repository visible only to authorized collaborators.

---

# TCP-WO-101: VPC + Cloud SQL (Private IP)

**Priority**: CRITICAL | **Estimated**: 3 hours | **Dependencies**: TCP-WO-100

## Objective
Provision the production database in a private network with no public access.

## Tasks
1. Create VPC: `themis-prod` in `us-west1`
2. Create subnet: `themis-prod-subnet` (10.10.0.0/24)
3. Create VPC Serverless Connector for Cloud Run
4. Provision Cloud SQL for PostgreSQL 16:
   - Instance: `themis-prod-db`
   - Tier: `db-custom-1-3840` (1 vCPU, 3.75GB) — sized for early growth
   - Region: us-west1 with HA replica in us-west1-b
   - Private IP only (no public IP)
   - Automated backups: daily, 30-day retention
   - Point-in-time recovery: enabled
   - Maintenance window: Sunday 03:00-04:00 MST
5. Configure firewall rules (deny all by default; allow Cloud Run subnet to DB)
6. Enable database flags: `cloudsql.iam_authentication=on`, `log_statement=ddl`
7. Create databases: `themis_prod`, `themis_staging`
8. Create roles: `themis_app_role`, `themis_readonly_role`, `themis_migration_role`
9. Document connection strings in Secret Manager (TCP-WO-102)

## Deliverables
- [ ] VPC + subnet + connector provisioned
- [ ] Cloud SQL HA instance running with private IP
- [ ] Backup policy verified
- [ ] Cloud Run can reach DB; public internet cannot
- [ ] Database roles created with least privilege
- [ ] Network architecture diagram updated in ARCHITECTURE.md

## Acceptance Criteria
- `psql` from outside VPC: connection refused
- `psql` from Cloud Run via connector: succeeds with IAM auth
- Backup taken automatically; manual restore test passes

## Estimated Cost Impact
$25-50/month for HA Cloud SQL + connector + private IP

---

# TCP-WO-102: Cloud KMS + Secret Manager Setup

**Priority**: CRITICAL | **Estimated**: 2 hours | **Dependencies**: TCP-WO-100

## Objective
Establish the cryptographic foundation: keys for field-level encryption and a secure store for application secrets.

## Tasks
1. Create KMS keyring: `themis-keyring` in `us-west1`
2. Create master keys:
   - `tenant-data-master` (HSM-backed) — used to derive per-tenant DEKs
   - `audit-signing` (HSM-backed) — for audit hash chain signing
   - `cmek-cloudsql` — customer-managed key for Cloud SQL (Phase 2)
3. Configure key rotation: annual auto-rotation
4. Create IAM policies:
   - `themis-app-sa` can `Encrypt`/`Decrypt` with `tenant-data-master`
   - `themis-audit-sa` can `Encrypt` with `audit-signing` only (no decrypt)
   - No human user has direct decrypt access
5. Provision secrets in Secret Manager:
   - `themis-db-password`
   - `themis-flask-secret-key`
   - `themis-stripe-secret-key` (placeholder, populated in Phase 2)
   - `themis-stripe-webhook-secret` (placeholder)
   - `themis-google-oauth-client-secret` (placeholder)
6. Configure Workload Identity for Cloud Run to access secrets without key files

## Deliverables
- [ ] KMS keyring + master keys created with HSM protection
- [ ] Annual rotation policy configured
- [ ] IAM least-privilege policies in place
- [ ] Secret Manager populated with placeholders
- [ ] Workload Identity binding for Cloud Run service account
- [ ] Documentation of who-can-access-what

## Acceptance Criteria
Cloud Run can fetch secrets and encrypt/decrypt via KMS without long-lived credentials. No human user can decrypt customer data without an audit log entry.

## Estimated Cost Impact
$1-3/key/month + minimal Secret Manager cost

---

# TCP-WO-103: BigQuery Audit Log Dataset

**Priority**: CRITICAL | **Estimated**: 2 hours | **Dependencies**: TCP-WO-100

## Objective
Create the immutable audit log infrastructure separated from app data.

## Tasks
1. Create BigQuery dataset: `themis_audit` (us-west1, 7-year retention)
2. Create table `audit_log` with schema from ARCHITECTURE.md §6.2
3. Configure partitioning (by `DATE(timestamp)`) and clustering (by `actor_user_id`, `action`)
4. Create dedicated service account: `themis-audit-writer-sa`
   - Grant `bigquery.dataEditor` on `themis_audit` dataset (insert only)
   - **Explicitly deny** `bigquery.jobs.delete`, `bigquery.tables.delete`, `bigquery.tables.update`
5. Create read-only role: `themis-audit-reader-sa` for compliance/DPO
6. Create Pub/Sub topic: `themis-audit-events`
7. Create Pub/Sub subscription with Cloud Function or Cloud Run service to drain events to BigQuery
8. Configure log sink for Cloud Audit Logs (admin actions on infra) → same BigQuery dataset
9. Create scheduled query: nightly hash-chain verification job
10. Set up alerting: P0 alert if hash chain breaks

## Deliverables
- [ ] BigQuery dataset + audit_log table created
- [ ] Service accounts with strict IAM (insert only for writer)
- [ ] Pub/Sub pipeline operational
- [ ] Cloud Audit Logs piped in
- [ ] Hash-chain verification scheduled query
- [ ] P0 alert configured

## Acceptance Criteria
- Test event written via Pub/Sub appears in BigQuery within 60 seconds
- Audit writer cannot DELETE or UPDATE rows (verified by attempted operation)
- Hash chain verification job runs successfully
- 7-year retention configured at table level

## Estimated Cost Impact
$0-5/month at expected volume

---

# TCP-WO-104: Multi-Tenant Data Model + Migrations

**Priority**: CRITICAL | **Estimated**: 4-6 hours | **Dependencies**: TCP-WO-101

## Objective
Design the multi-tenant database schema and migration framework.

## Tasks
1. Choose migration tool: **Alembic** (Python ecosystem, integrates with Flask)
2. Design tables with tenant scoping:

```sql
-- Organizations (tenant root for B2B)
CREATE TABLE organizations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name TEXT NOT NULL,
    type TEXT CHECK (type IN ('law_firm', 'legal_aid', 'enterprise')),
    billing_email TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    deleted_at TIMESTAMPTZ
);

-- Users (consumer or organization member)
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email TEXT UNIQUE NOT NULL,
    email_verified BOOLEAN DEFAULT FALSE,
    password_hash TEXT,                    -- bcrypt; NULL if OAuth-only
    organization_id UUID REFERENCES organizations(id),
    role TEXT NOT NULL,                     -- consumer, org_owner, etc.
    full_name TEXT,                          -- Tier 2
    phone TEXT,                              -- Tier 2
    mfa_enabled BOOLEAN DEFAULT FALSE,
    mfa_secret_encrypted BYTEA,              -- Tier 0
    created_at TIMESTAMPTZ DEFAULT NOW(),
    last_login_at TIMESTAMPTZ,
    deleted_at TIMESTAMPTZ
);

-- Cases (filings)
CREATE TABLE cases (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    organization_id UUID REFERENCES organizations(id),  -- NULL for consumer
    owner_user_id UUID NOT NULL REFERENCES users(id),
    case_type TEXT NOT NULL,                 -- 'child_support_petition'
    case_status TEXT NOT NULL,               -- 'draft', 'filed', 'closed'
    county TEXT,
    case_number TEXT,                        -- Court-assigned, after filing
    intake_data_encrypted BYTEA,             -- Tier 0/1: full intake JSON encrypted
    intake_data_iv BYTEA,                    -- IV for encryption
    intake_data_key_id TEXT,                 -- Which KMS key encrypted this
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    filed_at TIMESTAMPTZ,
    deleted_at TIMESTAMPTZ
);

-- Documents (PDFs and uploads)
CREATE TABLE documents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    case_id UUID NOT NULL REFERENCES cases(id),
    organization_id UUID,                    -- denormalized for RLS efficiency
    owner_user_id UUID NOT NULL,
    document_type TEXT NOT NULL,             -- 'petition', 'worksheet', 'proof_of_service'
    storage_uri TEXT NOT NULL,               -- gs://themis-docs-org-X/cases/Y/file.pdf
    storage_key_id TEXT,                     -- Which KMS CMEK encrypted the bucket
    sha256 TEXT NOT NULL,                    -- File integrity check
    size_bytes BIGINT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    deleted_at TIMESTAMPTZ
);

-- Sessions
CREATE TABLE sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id),
    refresh_token_hash TEXT NOT NULL,
    ip_address INET,
    user_agent TEXT,
    expires_at TIMESTAMPTZ NOT NULL,
    revoked_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- (More tables: roles, permissions, calendar_events, etc. — added per WO)
```

3. Write Alembic migration scripts (versioned, reversible)
4. Create staging database for migration testing
5. Document data dictionary in `00_ARCHITECTURE/DATA_MODEL.md`

## Deliverables
- [ ] Alembic configured
- [ ] Initial migration scripts (000_initial_schema.py)
- [ ] All tenant-scoped tables include `organization_id` and/or `owner_user_id`
- [ ] Tier 0 fields modeled as BYTEA with `_iv` and `_key_id` companions
- [ ] DATA_MODEL.md documenting every table, column, sensitivity tier
- [ ] Migration tested forward + reverse on staging DB

## Acceptance Criteria
Migration runs cleanly on empty staging database. Schema review by Lead Architect signs off.

---

# TCP-WO-105: Casbin RBAC Policy Engine

**Priority**: CRITICAL | **Estimated**: 4-6 hours | **Dependencies**: TCP-WO-104

## Objective
Implement the policy-driven authorization layer.

## Tasks
1. Add `casbin` and `casbin-sqlalchemy-adapter` to `requirements.txt`
2. Define Casbin model (`rbac_model.conf`):
```
[request_definition]
r = sub, obj, act, ctx

[policy_definition]
p = sub, obj, act, eft

[role_definition]
g = _, _

[policy_effect]
e = some(where (p.eft == allow)) && !some(where (p.eft == deny))

[matchers]
m = g(r.sub, p.sub) && keyMatch(r.obj, p.obj) && r.act == p.act
```

3. Define initial policy file (`policies.csv`) covering all roles in ARCHITECTURE.md §5.2
4. Create `themis.auth.policy` module with `enforce(user, resource, action, context)` function
5. Wrap Flask routes with `@require_permission('cases.read')` decorator
6. Build admin UI to view policies (read-only initially)
7. Write authz unit tests covering every (role × action × resource) combination
8. Document the permission grammar in `00_ARCHITECTURE/PERMISSIONS.md`

## Deliverables
- [ ] Casbin integrated and policies loaded
- [ ] Decorators on every protected route
- [ ] Authz test suite passing (100+ test cases)
- [ ] PERMISSIONS.md as authoritative reference
- [ ] Audit log entry on every authz decision (allow + deny)

## Acceptance Criteria
Removing a permission from a policy correctly denies the next request. Authz tests run in <2 seconds and cover full role matrix.

---

# TCP-WO-106: PostgreSQL RLS + Per-Request Scoping

**Priority**: CRITICAL | **Estimated**: 4 hours | **Dependencies**: TCP-WO-104

## Objective
Add database-level tenant isolation as defense in depth.

## Tasks
1. Enable RLS on every tenant-scoped table:
```sql
ALTER TABLE cases ENABLE ROW LEVEL SECURITY;
ALTER TABLE documents ENABLE ROW LEVEL SECURITY;
ALTER TABLE calendar_events ENABLE ROW LEVEL SECURITY;
-- etc.
```

2. Create RLS policies per ARCHITECTURE.md §4.3 pattern
3. Build SQLAlchemy session middleware that sets `app.current_user_id` and `app.current_org_id` at the start of every request
4. Build a "system context" mechanism for cron jobs / background tasks that explicitly sets a service principal
5. Add `pytest` fixtures that test RLS enforcement (try to read cross-tenant; must fail at DB level)
6. Document the RLS pattern in `00_ARCHITECTURE/RLS_PATTERNS.md`

## Deliverables
- [ ] RLS enabled on all tenant-scoped tables
- [ ] Policies created per pattern
- [ ] Session middleware sets context vars per request
- [ ] Cross-tenant query tests fail at DB layer (not just app layer)
- [ ] RLS_PATTERNS.md documented
- [ ] System context mechanism for legitimate cross-tenant ops (audit logged)

## Acceptance Criteria
Set context to user A's session, query for case owned by user B → returns 0 rows. Confirmed at PostgreSQL EXPLAIN level (filter applied at DB).

---

# TCP-WO-107: Field-Level Encryption (Tier 0)

**Priority**: CRITICAL | **Estimated**: 3-4 hours | **Dependencies**: TCP-WO-102

## Objective
Encrypt SSN, DL, and other Tier 0 fields with per-tenant keys before persistence.

## Tasks
1. Create `themis.crypto.field_encryption` module
2. Implement `EncryptedField` SQLAlchemy custom type:
   - On write: encrypt with tenant DEK, store ciphertext + IV + key version
   - On read: decrypt with same key
   - Audit log every decryption (action: `field.decrypt`, fields_accessed)
3. Implement key derivation: per-tenant DEK derived from KMS master key + tenant_id
4. Implement key versioning: support rotation without re-encrypting all data immediately
5. Mask helper: `mask_ssn("123-45-6789")` → `"***-**-6789"` for UI default display
6. Write tests:
   - Round-trip encrypt/decrypt
   - Cross-tenant key isolation (decrypting tenant A's SSN with tenant B's key fails)
   - Key rotation does not break old data
   - Audit log entry created on every decrypt

## Deliverables
- [ ] Crypto module with EncryptedField type
- [ ] Per-tenant key derivation
- [ ] Masking helper
- [ ] Test suite with 100% coverage on crypto paths
- [ ] Documentation in `00_ARCHITECTURE/ENCRYPTION.md`

## Acceptance Criteria
Tier 0 columns store ciphertext only (verified by raw SQL inspection). UI displays masked by default. Decryption requires explicit user action and is audit logged.

---

# TCP-WO-108: Audit Log Middleware + Hash Chain

**Priority**: CRITICAL | **Estimated**: 4-5 hours | **Dependencies**: TCP-WO-103

## Objective
Wire audit logging into the application so every privileged action is recorded.

## Tasks
1. Create `themis.audit` module with `AuditLogger` class
2. Implement `audit(action, resource, result, fields_accessed=[], **metadata)` function
3. Implement Pub/Sub publishing with retry + DLQ
4. Implement hash chain:
   - Cache last entry hash in Redis (Memorystore — Phase 2; in-process for now)
   - Each new entry includes previous_hash; current_hash = sha256(content + previous_hash)
5. Add Flask middleware that auto-logs:
   - Authentication events (login, logout, failed login, MFA challenge)
   - Authorization decisions (allow/deny)
   - Field decryption (Tier 0 fields)
   - Document download
6. Add explicit `@audit_action(...)` decorator for non-auto-logged operations
7. Implement nightly hash chain verification scheduled query
8. Implement P0 alert on chain break

## Deliverables
- [ ] Audit module with hash chain
- [ ] Auto-logging middleware
- [ ] Decorator for explicit logging
- [ ] Pub/Sub publishing with DLQ
- [ ] Hash chain verifier
- [ ] P0 alert wired up
- [ ] Documentation in `00_ARCHITECTURE/AUDIT.md`

## Acceptance Criteria
Test login → audit entry visible in BigQuery within 60s with proper hash. Manually break chain in dev → verifier detects and alerts.

---

# TCP-WO-109: Cross-Tenant Test Suite

**Priority**: CRITICAL | **Estimated**: 3-4 hours | **Dependencies**: TCP-WO-105, 106, 107

## Objective
Build the automated test suite that proves tenant isolation on every deploy.

## Tasks
1. Create `tests/security/` directory
2. Write tests:
   - **Cross-tenant API access**: User A's session, request user B's case ID → 404 (not 403, to avoid leaking existence)
   - **Cross-tenant DB query**: Set RLS context to user A, raw query for user B's data → 0 rows
   - **Cross-tenant decryption**: Try to decrypt user B's SSN with user A's key → exception
   - **Cross-tenant Cloud Storage**: User A's session, attempt to fetch URL from user B's bucket → 403
   - **Privilege escalation**: User without `admin` role attempts admin endpoint → 403
   - **Direct object reference**: Manipulate URL/case ID to access another user's resource → 404
   - **JWT tampering**: Modify JWT claims (role) → signature verification fails
   - **Session hijack**: Use another user's session token → fails (IP binding optional, mandatory by Phase 2)
3. Wire into CI: PR fails if any security test fails
4. Add quarterly review checklist for the test suite

## Deliverables
- [ ] 50+ security tests passing
- [ ] Tests run on every PR
- [ ] PR cannot merge if any security test fails
- [ ] Quarterly review process documented

## Acceptance Criteria
Removing an RLS policy or Casbin rule causes specific tests to fail. Tests cover all role combinations and resource types.

---

# TCP-WO-110: CI/CD Pipeline with Security Gates

**Priority**: HIGH | **Estimated**: 3 hours | **Dependencies**: TCP-WO-100, 109

## Objective
Automate testing, security scanning, and deployment.

## Tasks
1. Configure GitHub Actions workflows:
   - `lint.yml`: ruff, eslint, mypy
   - `test.yml`: unit + integration + authz + security
   - `scan.yml`: gitleaks, bandit, snyk, trivy
   - `deploy-staging.yml`: on merge to main
   - `deploy-production.yml`: manual approval, on tag
2. Configure required status checks on `main` branch protection
3. Set up GitHub secrets: GCP credentials (Workload Identity Federation, no key files)
4. Configure Cloud Build trigger for production deploys (with IAM-gated approval)
5. Add smoke tests post-deploy (curl /health, verify response)
6. Add deployment audit log entry (action: `system.deploy`)

## Deliverables
- [ ] All workflows running on PRs
- [ ] Status checks blocking merge if any fail
- [ ] Workload Identity Federation (no service account keys in GitHub)
- [ ] Staging auto-deploys; production gated by approval
- [ ] Smoke tests after every deploy
- [ ] Deploy audit logged

## Acceptance Criteria
PR with failing test cannot merge. Push to staging → app deployed within 5 minutes. Production deploy requires explicit approval.

---

# TCP-WO-111: Cloud Armor (WAF) + DDoS

**Priority**: HIGH | **Estimated**: 2 hours | **Dependencies**: TCP-WO-101

## Objective
Add web application firewall and DDoS protection at the edge.

## Tasks
1. Configure Global HTTPS Load Balancer in front of Cloud Run
2. Attach Cloud Armor security policy:
   - OWASP Top 10 ruleset (managed)
   - SQL injection rules
   - XSS rules
   - Per-IP rate limiting: 100 req/min for static, 10 req/min for /api/submit
   - Geo restriction: US/CA only initially
3. Enable Cloud Armor adaptive protection (ML-based DDoS)
4. Configure reCAPTCHA Enterprise on signup and high-cost endpoints
5. Set up alerting: spike in 4xx/5xx, geo anomalies

## Deliverables
- [ ] LB with Cloud Armor in front of Cloud Run
- [ ] OWASP rules active
- [ ] Rate limiting enforced
- [ ] reCAPTCHA on sensitive endpoints
- [ ] Alerts configured

## Acceptance Criteria
Synthetic attack (curl with sql injection payload) is blocked at LB. Rate limit triggers correctly under load test.

## Estimated Cost Impact
$5-30/month depending on traffic

---

# TCP-WO-112: Backup + DR Drill

**Priority**: HIGH | **Estimated**: 2 hours | **Dependencies**: TCP-WO-101

## Objective
Verify backups work and team knows how to restore.

## Tasks
1. Verify automated Cloud SQL backups running
2. Verify point-in-time recovery enabled
3. Test restore: take a backup, restore to a test instance, verify data integrity
4. Verify Cloud Storage versioning + cross-region replication
5. Verify Terraform state backed up in Cloud Storage with versioning
6. Document recovery procedures in `00_ARCHITECTURE/INCIDENT_RUNBOOK.md`
7. Run first full DR drill: simulate region failure, restore in different region, document RTO

## Deliverables
- [ ] Backups verified across all data stores
- [ ] First restore test successful
- [ ] DR drill documented
- [ ] INCIDENT_RUNBOOK.md created
- [ ] RTO/RPO measured against targets

## Acceptance Criteria
Restored database matches source byte-for-byte (modulo timestamps). Documentation enables a new engineer to perform a restore unassisted.

---

## Phase 0 Sign-Off Checklist

Before declaring Phase 0 complete and moving to Phase 1:

- [ ] All 13 work orders complete
- [ ] All security tests passing in CI
- [ ] Architecture review by Commander
- [ ] Penetration test against staging (third-party or scripted)
- [ ] Documentation complete (ARCHITECTURE.md, DATA_MODEL.md, PERMISSIONS.md, ENCRYPTION.md, AUDIT.md, RLS_PATTERNS.md, INCIDENT_RUNBOOK.md)
- [ ] First DR drill completed
- [ ] Hash chain verifier ran successfully for 7 consecutive nights
- [ ] No secrets in source code (gitleaks clean)
- [ ] Commander signs Phase 0 acceptance

---

*TCP-WO-PHASE0-001 Rev A — Phase 0 Foundation Work Orders*
*Architect: Agent B (Claude Code)*
*Authority: Commander Gary Spear*
