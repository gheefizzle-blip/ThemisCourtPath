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
    """Create the filings table if it does not exist. Idempotent."""
    conn = sqlite3.connect(_get_db_path())
    try:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS filings (
                id                TEXT PRIMARY KEY,
                user_id           TEXT NOT NULL,
                encrypted_payload TEXT NOT NULL,
                created_at        TEXT NOT NULL
            )
            """
        )
        conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_filings_user ON filings(user_id, created_at DESC)"
        )
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
