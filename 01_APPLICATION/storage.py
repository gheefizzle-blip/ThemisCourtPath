"""
Themis Court Path - Encrypted Storage Module
=============================================
TCP-WO-201A Phase 0 implementation.

Encrypts intake data with Fernet (AES-128-CBC + HMAC-SHA256) and stores
ciphertext in SQLite. Each filing is associated with the user_id of the
authenticated submitter. Cross-user access is rejected.

Security:
- Encryption BEFORE persistence (no plaintext writes to disk for intake JSON)
- Key from THEMIS_ENCRYPTION_KEY env var; dev fallback warns loudly
- user_id required for every read/write
- load_filing returns the same generic error for "not found" and
  "wrong owner" so existence is not leaked across users

Phase 0 limitations (acceptable per scope, will be replaced in Phase 1):
- SQLite (Cloud Run /tmp ephemeral in production)
- Single application-level key (per-tenant KMS keys are TCP-ARCH-001 §7,
  to be implemented in a later WO)
- Encrypted PDFs are out of scope for this WO; see deliverable notes.
"""

import json
import os
import sqlite3
import sys
import uuid
from datetime import datetime, timezone

from cryptography.fernet import Fernet, InvalidToken


# ── Key management ───────────────────────────────────────────

def _load_key() -> bytes:
    """Load encryption key from env, or generate a dev key with a loud warning."""
    raw = os.environ.get("THEMIS_ENCRYPTION_KEY")
    if raw:
        return raw.encode("utf-8") if isinstance(raw, str) else raw
    # Dev fallback. Generated per-process; will not survive restart.
    sys.stderr.write(
        "WARNING: THEMIS_ENCRYPTION_KEY not set. "
        "DEV KEY GENERATED - NOT FOR PRODUCTION\n"
    )
    return Fernet.generate_key()


_KEY = _load_key()
_FERNET = Fernet(_KEY)


# ── Database ─────────────────────────────────────────────────

def _get_db_path() -> str:
    """SQLite path. /tmp in production (Cloud Run), local in dev."""
    if os.environ.get("FLASK_ENV") == "production":
        return "/tmp/themis_filings.db"
    return os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "themis_filings.db",
    )


def init_db() -> None:
    """Create the filings table if it does not exist. Idempotent.

    TCP-WO-300: filings table extended with payment_status and
    stripe_session_id columns. Migration is additive and safe to
    re-run on an existing database.
    """
    conn = sqlite3.connect(_get_db_path())
    try:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS filings (
                id                TEXT PRIMARY KEY,
                user_id           TEXT NOT NULL,
                encrypted_payload TEXT NOT NULL,
                created_at        TEXT NOT NULL,
                payment_status    TEXT NOT NULL DEFAULT 'pending',
                stripe_session_id TEXT
            )
            """
        )
        conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_filings_user ON filings(user_id, created_at DESC)"
        )
        # Additive migration for pre-WO-300 databases.
        existing_cols = {r[1] for r in conn.execute("PRAGMA table_info(filings)").fetchall()}
        if "payment_status" not in existing_cols:
            conn.execute(
                "ALTER TABLE filings ADD COLUMN payment_status TEXT NOT NULL DEFAULT 'pending'"
            )
        if "stripe_session_id" not in existing_cols:
            conn.execute("ALTER TABLE filings ADD COLUMN stripe_session_id TEXT")
        conn.commit()
    finally:
        conn.close()


# ── Crypto primitives ────────────────────────────────────────

def encrypt_data(data: dict) -> str:
    """Encrypt a dict to a Fernet token string."""
    if not isinstance(data, dict):
        raise TypeError("data must be a dict")
    payload = json.dumps(data, ensure_ascii=False).encode("utf-8")
    return _FERNET.encrypt(payload).decode("utf-8")


def decrypt_data(token: str) -> dict:
    """Decrypt a Fernet token string back to a dict."""
    if not isinstance(token, str) or not token:
        raise InvalidToken("empty or non-string token")
    payload = _FERNET.decrypt(token.encode("utf-8"))
    return json.loads(payload.decode("utf-8"))


# ── Storage operations ──────────────────────────────────────

def save_filing(user_id: str, data: dict) -> str:
    """Encrypt and persist a filing for a user. Returns the new filing_id."""
    if not user_id or not isinstance(user_id, str):
        raise ValueError("user_id required")
    if not isinstance(data, dict):
        raise TypeError("data must be a dict")

    filing_id = str(uuid.uuid4())
    now_iso = datetime.now(timezone.utc).isoformat()
    encrypted = encrypt_data(data)

    conn = sqlite3.connect(_get_db_path())
    try:
        conn.execute(
            "INSERT INTO filings (id, user_id, encrypted_payload, created_at) "
            "VALUES (?, ?, ?, ?)",
            (filing_id, user_id, encrypted, now_iso),
        )
        conn.commit()
    finally:
        conn.close()
    return filing_id


def load_filing(filing_id: str, user_id: str) -> dict:
    """Decrypt and return a filing for a user.

    Raises LookupError when not found OR when the filing belongs to a
    different user (same error in both cases — do not leak existence).
    """
    if not filing_id or not isinstance(filing_id, str):
        raise ValueError("filing_id required")
    if not user_id or not isinstance(user_id, str):
        raise ValueError("user_id required")

    conn = sqlite3.connect(_get_db_path())
    conn.row_factory = sqlite3.Row
    try:
        row = conn.execute(
            "SELECT user_id, encrypted_payload FROM filings WHERE id = ?",
            (filing_id,),
        ).fetchone()
    finally:
        conn.close()

    if row is None or row["user_id"] != user_id:
        raise LookupError("filing not found")

    return decrypt_data(row["encrypted_payload"])


def list_user_filings(user_id: str) -> list:
    """Return a list of {id, created_at} dicts for the user. No payload."""
    if not user_id or not isinstance(user_id, str):
        raise ValueError("user_id required")

    conn = sqlite3.connect(_get_db_path())
    conn.row_factory = sqlite3.Row
    try:
        rows = conn.execute(
            "SELECT id, created_at FROM filings WHERE user_id = ? "
            "ORDER BY created_at DESC",
            (user_id,),
        ).fetchall()
    finally:
        conn.close()
    return [{"id": r["id"], "created_at": r["created_at"]} for r in rows]


# ── Payment status (TCP-WO-300) ─────────────────────────────

VALID_PAYMENT_STATUSES = ("pending", "paid", "failed")


def get_payment_status(filing_id: str, user_id: str) -> str:
    """Return 'pending'|'paid'|'failed' for a user's filing.

    Raises LookupError when filing is missing OR owned by a different
    user — same error in both cases (no existence leak).
    """
    if not filing_id or not isinstance(filing_id, str):
        raise ValueError("filing_id required")
    if not user_id or not isinstance(user_id, str):
        raise ValueError("user_id required")

    conn = sqlite3.connect(_get_db_path())
    conn.row_factory = sqlite3.Row
    try:
        row = conn.execute(
            "SELECT user_id, payment_status FROM filings WHERE id = ?",
            (filing_id,),
        ).fetchone()
    finally:
        conn.close()

    if row is None or row["user_id"] != user_id:
        raise LookupError("filing not found")
    return row["payment_status"] or "pending"


def set_stripe_session(filing_id: str, user_id: str, session_id: str) -> None:
    """Attach a Stripe checkout session id to a filing owned by user_id."""
    if not filing_id or not user_id or not session_id:
        raise ValueError("filing_id, user_id, session_id all required")

    conn = sqlite3.connect(_get_db_path())
    try:
        cur = conn.execute(
            "UPDATE filings SET stripe_session_id = ? "
            "WHERE id = ? AND user_id = ?",
            (session_id, filing_id, user_id),
        )
        conn.commit()
        if cur.rowcount == 0:
            raise LookupError("filing not found")
    finally:
        conn.close()


def mark_payment_status(filing_id: str, user_id: str, status: str) -> None:
    """Set payment_status for a user's filing. Status must be in VALID_PAYMENT_STATUSES."""
    if status not in VALID_PAYMENT_STATUSES:
        raise ValueError(f"invalid payment status: {status!r}")
    if not filing_id or not user_id:
        raise ValueError("filing_id and user_id required")

    conn = sqlite3.connect(_get_db_path())
    try:
        cur = conn.execute(
            "UPDATE filings SET payment_status = ? "
            "WHERE id = ? AND user_id = ?",
            (status, filing_id, user_id),
        )
        conn.commit()
        if cur.rowcount == 0:
            raise LookupError("filing not found")
    finally:
        conn.close()


def lookup_filing_by_session(session_id: str) -> dict | None:
    """Return {filing_id, user_id, payment_status} for a Stripe session, or None.

    Used at /success to identify the filing from a returned session_id
    BEFORE we know which user is logged in (we then verify the logged-in
    user matches).
    """
    if not session_id or not isinstance(session_id, str):
        return None

    conn = sqlite3.connect(_get_db_path())
    conn.row_factory = sqlite3.Row
    try:
        row = conn.execute(
            "SELECT id, user_id, payment_status FROM filings "
            "WHERE stripe_session_id = ?",
            (session_id,),
        ).fetchone()
    finally:
        conn.close()
    if row is None:
        return None
    return {
        "filing_id": row["id"],
        "user_id": row["user_id"],
        "payment_status": row["payment_status"] or "pending",
    }
