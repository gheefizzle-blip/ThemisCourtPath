# Themis Court Path — Data Classification Policy
## Document ID: TCP-POL-001 Rev A
## Date: 2026-04-22
## Authority: Commander Gary Spear

---

## Purpose

Define how Themis Court Path classifies data, what controls each classification requires, and how to handle each tier in code, storage, transmission, logging, and human access.

This policy is **binding on all code and operations**. Violations are treated as P1 incidents.

---

## Classification Tiers

### Tier 0 — Critical
**Definition**: Data that, if exposed, causes severe identity-theft or financial fraud risk to the customer. Often covered by specific privacy statutes.

**Examples**:
- Social Security Numbers
- Driver's License Numbers
- Bank account numbers
- Credit card numbers (we do not store; Stripe holds these)
- Tax ID numbers
- Authentication secrets (passwords, MFA secrets, API keys)

**Required Controls**:
| Control | Requirement |
|---------|-------------|
| Storage | Encrypted with per-tenant KMS-derived DEK in BYTEA column |
| Transmission | TLS 1.3 only |
| Logging | NEVER plaintext anywhere |
| URL exposure | NEVER in URLs (use opaque tokens) |
| UI display | Masked by default (`***-**-1234`); reveal requires explicit user action + audit |
| Database backup | Encrypted blob; backup keys in separate KMS keyring |
| Access | App roles only with explicit scope + audit on every read |
| Audit log | Every read and write logged with `fields_accessed: [field:masked|full]` |
| Themis employee access | Break-glass only with ticket + customer notification |
| Retention | Until customer deletion request OR 7 years post case-close (whichever first) |

### Tier 1 — Highly Sensitive
**Definition**: Data that identifies the customer's life circumstances or financial position in detail.

**Examples**:
- Full income, employer details
- Court documents (entire petition packets)
- Children's PII (name, DOB, SSN — children's SSN is also Tier 0)
- Medical insurance details
- Address protection requests
- Domestic violence indicators
- Custody dispute details

**Required Controls**:
| Control | Requirement |
|---------|-------------|
| Storage | Cloud SQL encrypted at rest (DB-level); CMEK in Phase 2 |
| Transmission | TLS 1.3 only |
| Logging | NEVER in plaintext logs |
| URL exposure | NOT in URLs |
| UI display | Visible to authorized users only |
| Database backup | Encrypted at rest |
| Access | App roles only + audit on every read |
| Audit log | Every read and write logged |
| Themis employee access | Break-glass only with ticket |
| Retention | Same as Tier 0 |

### Tier 2 — Sensitive
**Definition**: Data identifying the customer but not directly enabling identity theft.

**Examples**:
- Full names
- Date of birth (alone)
- Mailing address
- Phone numbers
- Email addresses (but required for account)
- IP addresses
- User agent strings

**Required Controls**:
| Control | Requirement |
|---------|-------------|
| Storage | Cloud SQL encrypted at rest |
| Transmission | TLS 1.3 only |
| Logging | Email and IP allowed in audit log; full address only when relevant |
| URL exposure | User IDs (UUIDs) okay; no PII |
| UI display | Visible to user themselves and authorized roles |
| Audit log | Writes always; reads tracked at session-level |
| Themis employee access | Standing read access for support roles with audit |
| Retention | Account lifetime + 90 days post-deletion request |

### Tier 3 — Internal
**Definition**: Operational data with no privacy implications.

**Examples**:
- User IDs (UUIDs)
- Session IDs
- Internal event timestamps
- Feature flag states
- Aggregate counts and metrics
- Internal logs and traces

**Required Controls**:
| Control | Requirement |
|---------|-------------|
| Storage | Cloud SQL or BigQuery, encryption at rest |
| Transmission | TLS within Google Cloud; TLS 1.3 if external |
| Logging | Free use in app logs |
| Access | App and operations roles |
| Audit log | Selective (system events only) |
| Retention | 30-90 days for logs; indefinite for entity IDs |

### Tier 4 — Public
**Definition**: Data intended for public consumption.

**Examples**:
- Marketing pages
- Blog posts
- Public FAQs
- Aggregate marketing statistics
- Open-source code components

**Required Controls**:
| Control | Requirement |
|---------|-------------|
| Storage | Anywhere appropriate |
| Transmission | TLS in transit |
| Logging | Free |
| Access | Public read |
| Audit log | None required |
| Retention | As long as relevant |

---

## Special Categories

### Children's Data (Under 18)

Themis collects children's data because court forms require it (children are subjects of child support cases). Special handling:

- Children's SSN: **Tier 0**, with additional restriction that even authorized users see masked by default
- Children's DOB and name: Tier 1 sensitivity (identifying minors)
- Never used for marketing or analytics, even aggregate
- Never sold or shared with third parties under any circumstance
- Special audit log flag: `involves_minor: true` for any access

### Payment Card Data (Tier 0 — but NEVER stored)

We do not store payment card data. All card data flows directly from the user's browser to Stripe via Stripe Elements (or Checkout). Themis backend receives only:
- Stripe customer ID (`cus_XXX`)
- Stripe payment method ID (`pm_XXX`) — a tokenized reference
- Last 4 digits, brand, expiry month/year (for display)

Anyone proposing to store full card data must escalate to Commander. This is a hard-line rule (PCI scope reduction depends on it).

### Attorney-Client Privileged Communications

If/when attorney consultation feature ships:
- Communications between user and matched attorney are Tier 1 + privileged
- Stored encrypted with per-case DEK
- Themis employees have NO access (not even break-glass) without subpoena AND legal review
- Distinct retention policy (until case closure + 5 years OR per attorney's records retention policy)

---

## Data Lifecycle

### Collection

| Principle | Implementation |
|-----------|----------------|
| Collect minimum necessary | Each form field justified against court requirements |
| Inform user at collection | Tooltips and privacy notices |
| Lawful basis | Contract performance (preparing court documents) + consent |

### Use

| Principle | Implementation |
|-----------|----------------|
| Use only for stated purpose | Document preparation only — no marketing use |
| No new uses without consent | Privacy policy update + opt-in for new uses |
| Aggregate analytics okay | Counts, rates, anonymous metrics |

### Storage

| Principle | Implementation |
|-----------|----------------|
| Encrypted at rest (all tiers) | Cloud SQL DB encryption + Tier 0/1 field encryption |
| Encrypted in transit | TLS 1.3 |
| Tenant isolation | RLS + per-tenant keys |
| Backup encryption | Same controls as primary |

### Transmission

| Principle | Implementation |
|-----------|----------------|
| TLS 1.3 minimum | Enforced at LB |
| Certificate pinning | Phase 2 (mobile apps if/when built) |
| No PII in query strings | Path params with UUIDs only |
| No PII in error messages to user | Generic errors; details in audit log |

### Retention

| Data | Retention | Trigger for Deletion |
|------|-----------|---------------------|
| Active case data | Indefinite while case active | Customer deletion request |
| Closed case data | 7 years from close | Customer deletion request OR statute |
| Account info (no cases) | 1 year of inactivity | Auto-deletion notification |
| Audit log | 7 years | Compliance |
| Marketing analytics | 13 months (Google standard) | Auto-rotation |
| Backups | 30 days standard, 90 days for monthly | Auto-rotation |
| Cookies | Per cookie type (see Privacy Policy) | Auto-expiry |

### Deletion

| Right | Implementation |
|-------|----------------|
| User-initiated deletion | Self-service in account settings; processed within 30 days |
| GDPR/CCPA right to delete | Honored within 30 days of request |
| Mandatory deletion (e.g., breach) | Within 7 days of decision |
| Backup deletion | Backups containing deleted data are purged within 60 days |
| Audit log retention | Audit log entries about a deleted user are retained (anonymized identity) for 7 years |

### Sharing / Third Parties

| Recipient | Data Shared | Authorization | DPA |
|-----------|------------|---------------|-----|
| Google Cloud | All app data (encrypted) | Necessary infrastructure | Google Cloud DPA |
| Stripe | Payment card + customer name/email | User-initiated payment | Stripe DPA |
| eFileAZ (Phase 4+) | Court filing data | User-authorized filing | Tyler Tech agreement |
| Email provider | User name, email, message content | Transactional email | DPA required before adding |
| Error monitoring | Stack traces (PII scrubbed) | Operational necessity | DPA required |
| Government / law enforcement | As compelled by valid subpoena/warrant | Legal compulsion | Logged |

**No data sale. No advertising data sharing. No data brokers. Ever.**

---

## Logging Rules

### What MAY Appear in Logs

- User IDs (UUIDs)
- Session IDs
- Request IDs
- IP addresses
- HTTP methods, paths, status codes
- Latency, error codes
- Stack traces (with sensitive variables redacted)

### What MUST NEVER Appear in Logs

- Tier 0 data in plaintext (SSN, DL, account numbers, secrets)
- Tier 1 data in plaintext (income, court document content, children's PII)
- Full URLs containing search queries with PII
- Email body content
- Form submission contents (use IDs only)
- Decrypted field values

### Enforcement

- Code-level: secrets-scanner pre-commit hook
- Runtime: log filter middleware that scrubs known patterns (SSN format, etc.)
- Periodic: random sample of production logs reviewed by DPO

---

## Roles & Responsibilities

| Role | Responsibility |
|------|----------------|
| **All engineers** | Apply tiers correctly in new code; flag uncertainty in PR |
| **Lead Architect** | Maintain this policy; review classifications in code reviews |
| **DPO** | Annual review of classifications; respond to data requests |
| **Commander** | Approve policy changes; final escalation |
| **Compliance Lead** | Map classifications to SOC 2 controls |

---

## Review Cadence

This policy is reviewed:
- Annually (full review)
- On material changes to product features
- On change of compliance frameworks
- On any incident involving misclassification

---

## Amendment Log

| Date | Change | Approved By |
|------|--------|-------------|
| 2026-04-22 | Initial policy creation | Commander Spear |

---

*TCP-POL-001 Rev A — Data Classification Policy*
*Authority: Commander Gary Spear*
