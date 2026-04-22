# Themis Court Path - Decision Context

## Strategic Decisions

### 2026-04-22
Decision:
GitHub is the system of record.

Reason:
The project needs version control, persistent governance, auditable state, and shared access between Commander, ChatGPT, and Claude.

Authority:
Commander + Sam

---

### 2026-04-22
Decision:
ChatGPT (Sam) is architecture, governance, review, and sequencing authority. Claude Code is execution engine.

Reason:
Prevents architecture drift, security shortcuts, and uncontrolled feature creep.

Authority:
Commander

---

### 2026-04-22
Decision:
Treat all test data as if it were real PII.

Reason:
Security discipline matters more than intent. Real-looking data in repos, logs, or active project trees creates audit and leak risk even when nominally dummy.

Authority:
Commander + Sam

---

### 2026-04-22
Decision:
Shared virtual memory is required and not optional.

Reason:
Project continuity cannot depend on chat history. Both AI roles need a shared, persistent, sanitized operational memory.

Authority:
Commander + Sam

---

### 2026-04-22
Decision:
Claude was correct to stop TCP-WO-150 when shared memory files were missing.

Reason:
The work order explicitly prohibited self-creation of governance/memory structure and required stop-and-report on missing memory files.

Authority:
Sam

---

### 2026-04-22
Decision:
Trigger system will be based on state-change events, not direct AI-to-AI communication.

Reason:
The clean control model is repo state -> detection -> commander notification -> explicit review/execution trigger. This preserves human oversight and avoids hidden automation.

Authority:
Commander + Sam

---

### 2026-04-22
Decision:
Claude Code execution remains local on GSA-1000. Mobile continuity will be achieved through GitHub, n8n, Telegram, and remote ChatGPT access.

Reason:
Claude Code is not a headless always-on service. Workflow must respect its local interactive execution constraint.

Authority:
Commander + Sam

---

## Rejected Approaches

### Rejected
Let Claude author governance memory files on his own.

Reason:
That would improperly move governance/state-authority into the execution layer.

---

### Rejected
Direct autonomous AI-to-AI signaling and auto-approval.

Reason:
Too much drift risk for a legal-tech platform handling highly sensitive data.

---

### Rejected
Skipping shared memory and relying on chat continuity alone.

Reason:
Not durable, not auditable, and not fit for long-running controlled execution.
