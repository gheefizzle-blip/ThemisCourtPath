# Themis Court Path - Next Actions

## Immediate Priority Queue

### 1. Resume TCP-WO-150
Status: COMPLETE
Owner: Claude
Purpose:
- load shared memory files
- confirm memory integration
- append first compliant SESSION_HANDOFF entry
- confirm future execution protocol

### 2. Review TCP-WO-200
Status: COMPLETE
Owner: Sam
Disposition: APPROVED WITH CORRECTIONS
Purpose:
- review Claude's auth implementation
- issue disposition
- determine whether WO is approved, approved with corrections, or rejected

### 3. Define Trigger Protocol
Status: PENDING
Owner: Sam
Purpose:
- formalize trigger state model
- define human-in-the-loop review trigger
- define state transitions between Claude, Sam, Commander, GitHub, n8n, and Telegram

### 4. Issue TCP-WO-160
Status: PENDING
Owner: Sam
Purpose:
- formal trigger and notification protocol

### 5. Issue TCP-WO-161
Status: PENDING
Owner: Sam
Purpose:
- n8n Phase 1 notification workflow
- GitHub/VM watcher
- Telegram notification to Commander

---

## Secondary Queue

### Shared memory discipline
Status: ACTIVE
Owner: All
Notes:
- all meaningful work must be reflected in SESSION_HANDOFF.md
- no important state should live only in chat

### Progress dashboard update
Status: PENDING
Owner: Sam
Notes:
- update after TCP-WO-150 and TCP-WO-200 review

---

## Blocked Items

### TCP-WO-201
Status: COMPLETE
Reason:
- Issued and executed as TCP-WO-201A (commit 1878eab); APPROVED WITH MINOR FOLLOW-UP WORK

### TCP-WO-202
Status: COMPLETE
Reason:
- Secure document handling implemented (commit bf7dc27); APPROVED

### TCP-WO-300
Status: COMPLETE
Reason:
- Stripe payment gating implemented (commit f812aa7); APPROVED WITH CORRECTIONS

### Payment work
Status: COMPLETE (functional)
Reason:
- TCP-WO-300 implements payment gating; deployment hardening tracked under Carry Forward / Hardening below

### Launch/marketing acceleration
Status: BLOCKED
Reason:
- product is not yet safe to charge money at scale

---

## Carry Forward / Hardening

These are non-blocking items that must be addressed before live production traffic. They are tracked here without being authored as full work orders.

### CSRF protection
Scope:
- POST /api/create-checkout-session (TCP-WO-300 correction #1)
- All POST endpoints (TCP-WO-200 correction)
Owner: Sam (to issue future WO)

### Cloud Run environment provisioning
Scope:
- THEMIS_ENCRYPTION_KEY (required before any encrypted-storage traffic)
- STRIPE_SECRET_KEY (required before any payment traffic, test or live)
Owner: Commander (manual configuration)

### Webhook-based async payment confirmation
Scope:
- Replace or supplement sync /success verification with Stripe webhook
- Better resilience to dropped redirects and refund/dispute events
Owner: Sam (to issue future WO)

### Other carryovers from prior dispositions
- SQLite Phase 0 limit (Phase 1 PostgreSQL migration planned)
- Auth rate limiting (TCP-WO-200 correction)
- app.py vs app_production.py file consolidation (TCP-WO-200 correction)
- gcr.io vs Artifact Registry path alignment (TCP-WO-200 correction)
- Per-tenant KMS keys per TCP-ARCH-001 Section 7

---

## Commander Decision Queue

None currently required before TCP-WO-150 resume and TCP-WO-200 review.

---

## Execution Rule

Claude executes only:
- items explicitly issued as work orders
- work explicitly marked READY
- work consistent with CURRENT_STATE.md and architecture authority
