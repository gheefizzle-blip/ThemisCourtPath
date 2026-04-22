# Themis Court Path - Virtual Memory Index

## Purpose

This directory is the shared operational memory layer for Themis Court Path.

It exists so that:
- ChatGPT (Sam) can maintain architecture, governance, and sequencing
- Claude Code can execute against current state without drift
- Commander can review project state from a single source of truth

This memory system is part of governance. It is not optional.

---

## Files

### CURRENT_STATE.md
Authoritative snapshot of current project reality:
- what exists
- what is deployed
- what is approved
- what is blocked
- current milestone status
- current security posture

### NEXT_ACTIONS.md
Execution queue:
- next work orders
- dependencies
- immediate priorities
- blocked items
- commander decisions needed

### SESSION_HANDOFF.md
Cross-session relay log:
- what was completed
- what changed
- open issues
- next recommended action

### DECISION_CONTEXT.md
Why major decisions were made:
- architecture decisions
- sequencing decisions
- rejected options
- strategic constraints

---

## Update Authority

| File | ChatGPT | Claude | Commander |
|------|---------|--------|-----------|
| VM_INDEX.md | Yes | No | Yes |
| CURRENT_STATE.md | Yes | Limited | Yes |
| NEXT_ACTIONS.md | Yes | Limited | Yes |
| SESSION_HANDOFF.md | Yes | Yes | Yes |
| DECISION_CONTEXT.md | Yes | No unless directed | Yes |

---

## Claude Update Rules

Claude may:
- read all memory files
- append to SESSION_HANDOFF.md
- update CURRENT_STATE.md for implementation status only
- mark an item complete in NEXT_ACTIONS.md only if explicitly allowed

Claude may not:
- redefine milestones
- alter architecture posture
- author new strategic decisions
- create new execution priorities on his own

---

## Security Rules

No memory file may contain:
- SSNs
- driver's license numbers
- bank data
- secrets
- credentials
- real user-submitted case data

All entries must be abstracted and sanitized.

---

## Operating Principle

If it is not captured in this memory system or other approved governance files, it is not considered persistent project state.
