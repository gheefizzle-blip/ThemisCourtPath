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
- Issued and executed as TCP-WO-201A (commit 1878eab); pending Sam review

### Payment work
Status: BLOCKED
Reason:
- Milestone 1 security work is not yet complete

### Launch/marketing acceleration
Status: BLOCKED
Reason:
- product is not yet safe to charge money at scale

---

## Commander Decision Queue

None currently required before TCP-WO-150 resume and TCP-WO-200 review.

---

## Execution Rule

Claude executes only:
- items explicitly issued as work orders
- work explicitly marked READY
- work consistent with CURRENT_STATE.md and architecture authority
