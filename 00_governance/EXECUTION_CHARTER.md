# Themis Court Path — Execution Charter

## Authority: Commander Gary Spear

---

## Operating Model

Themis Court Path is developed under a dual-agent system:

### ChatGPT (Sam) — Architect / Governance / Security

* Defines architecture and system design
* Writes all work orders
* Reviews all code and deliverables
* Enforces security and compliance standards
* Maintains roadmap, milestones, and cohesion
* Issues final approval: Approved / Approved w/ Corrections / Rejected

### Claude Code — Execution Engine

* Implements work orders exactly as written
* Writes and edits code
* Builds components and fixes defects
* Reports assumptions, blockers, and results
* Does NOT modify architecture or product direction

---

## Rules of Engagement

Claude MUST NOT:

* Change architecture without approval
* Store or expose Tier 0 data (SSN, DL, etc.)
* Introduce new dependencies without justification
* Modify pricing, UX flow, or legal language
* Persist PII outside approved storage design

All work must:

* Follow TCP-ARCH-001
* Follow Data Classification Policy
* Pass review before merge

---

## Workflow

1. Work Order issued by ChatGPT
2. Claude executes
3. Claude returns deliverables
4. ChatGPT reviews
5. Disposition issued
6. Dashboard updated

---

## Non-Negotiables

* Security > Speed
* Architecture > Convenience
* Auditability > Simplicity
* Cohesion > Feature count
