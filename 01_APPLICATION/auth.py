"""
Themis Court Path — Authentication Module
==========================================
TCP-WO-200 Phase 0 implementation.

Provides user registration, login, logout, and session-based auth.
Uses SQLite for the users table (Phase 0 only — PostgreSQL with RLS
in Phase 1 per TCP-ARCH-001).

Security notes:
- Passwords hashed with bcrypt (cost 12)
- Sessions use Flask signed cookies via app.secret_key
- HttpOnly + SameSite=Lax + Secure (in production) cookies
- No PII beyond email is stored in the users table
- Generic auth error messages (no email enumeration)
- Constant-time check against dummy hash on missing user
- Intake data is NOT persisted — encryption layer is TCP-WO-201
"""

import os
import re
import sqlite3
import uuid
from datetime import datetime, timezone
from functools import wraps

import bcrypt
from flask import (
    Blueprint, render_template, request, jsonify,
    session, redirect, url_for, g, current_app,
)

auth_bp = Blueprint("auth", __name__, url_prefix="/auth")


# ── Database (Phase 0 SQLite — Phase 1 will move to PostgreSQL) ──

def _get_db_path() -> str:
    """SQLite path. /tmp in production (Cloud Run), local in dev."""
    if os.environ.get("FLASK_ENV") == "production":
        return "/tmp/themis_users.db"
    return os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "themis_users.db",
    )


def get_db() -> sqlite3.Connection:
    """Get a SQLite connection scoped to the current request."""
    if "db" not in g:
        g.db = sqlite3.connect(_get_db_path())
        g.db.row_factory = sqlite3.Row
    return g.db


def close_db(_exc=None) -> None:
    """Close the request-scoped SQLite connection."""
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_db() -> None:
    """Create users table if it does not exist. Idempotent."""
    conn = sqlite3.connect(_get_db_path())
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS users (
            id            TEXT PRIMARY KEY,
            email         TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            created_at    TEXT NOT NULL
        )
        """
    )
    conn.commit()
    conn.close()


# ── Validation ───────────────────────────────────────────────

_EMAIL_RE = re.compile(r"^[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}$")


def _is_valid_email(email: str) -> bool:
    return bool(email) and len(email) <= 254 and bool(_EMAIL_RE.match(email))


def _is_valid_password(password: str) -> bool:
    """Phase 0 policy: 12+ chars, at least one letter and one digit."""
    if not password or len(password) < 12 or len(password) > 128:
        return False
    has_letter = any(c.isalpha() for c in password)
    has_digit = any(c.isdigit() for c in password)
    return has_letter and has_digit


# ── Timing-attack mitigation ─────────────────────────────────
# A fixed dummy hash so that login attempts for non-existent emails
# spend roughly the same CPU time as real lookups.
_DUMMY_HASH = bcrypt.hashpw(
    b"timing_attack_mitigation", bcrypt.gensalt(rounds=12)
)


# ── Decorators ───────────────────────────────────────────────

def login_required(fn):
    """Reject requests that lack a valid session.

    JSON / API requests get a 401 JSON response.
    Browser requests get a 302 redirect to /auth/login.
    """
    @wraps(fn)
    def wrapper(*args, **kwargs):
        if "user_id" not in session:
            wants_json = (
                request.is_json
                or request.path.startswith("/api/")
                or "application/json" in (request.headers.get("Accept") or "")
            )
            if wants_json:
                return jsonify({"error": "Authentication required"}), 401
            return redirect(url_for("auth.login_page"))
        return fn(*args, **kwargs)

    return wrapper


# ── Routes ───────────────────────────────────────────────────

@auth_bp.route("/register", methods=["GET"])
def register_page():
    if "user_id" in session:
        return redirect(url_for("intake"))
    return render_template("register.html")


@auth_bp.route("/register", methods=["POST"])
def register():
    data = request.form if request.form else (request.get_json(silent=True) or {})
    email = (data.get("email") or "").strip().lower()
    password = data.get("password") or ""

    if not _is_valid_email(email):
        return _form_error("register.html", "Please enter a valid email address.", email=email)
    if not _is_valid_password(password):
        return _form_error(
            "register.html",
            "Password must be at least 12 characters and contain a letter and a number.",
            email=email,
        )

    db = get_db()
    existing = db.execute(
        "SELECT id FROM users WHERE email = ?", (email,)
    ).fetchone()
    if existing:
        # Generic message — do not confirm whether the email exists
        return _form_error(
            "register.html",
            "Could not create account with that email.",
            email=email,
        )

    pw_hash = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt(rounds=12))
    user_id = str(uuid.uuid4())
    now_iso = datetime.now(timezone.utc).isoformat()
    db.execute(
        "INSERT INTO users (id, email, password_hash, created_at) VALUES (?, ?, ?, ?)",
        (user_id, email, pw_hash.decode("utf-8"), now_iso),
    )
    db.commit()

    session.clear()
    session["user_id"] = user_id
    session["email"] = email
    session.permanent = True

    return redirect(url_for("intake"))


@auth_bp.route("/login", methods=["GET"])
def login_page():
    if "user_id" in session:
        return redirect(url_for("intake"))
    return render_template("login.html")


@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.form if request.form else (request.get_json(silent=True) or {})
    email = (data.get("email") or "").strip().lower()
    password = data.get("password") or ""

    if not email or not password:
        return _form_error("login.html", "Email and password are required.", email=email)

    db = get_db()
    row = db.execute(
        "SELECT id, password_hash FROM users WHERE email = ?", (email,)
    ).fetchone()

    generic = _form_error("login.html", "Invalid email or password.", email=email)

    if row is None:
        # Constant-time mitigation: bcrypt check against a known dummy.
        bcrypt.checkpw(password.encode("utf-8"), _DUMMY_HASH)
        return generic

    if not bcrypt.checkpw(password.encode("utf-8"), row["password_hash"].encode("utf-8")):
        return generic

    session.clear()
    session["user_id"] = row["id"]
    session["email"] = email
    session.permanent = True
    return redirect(url_for("intake"))


@auth_bp.route("/logout", methods=["GET", "POST"])
def logout():
    session.clear()
    return redirect(url_for("index"))


# ── Helpers ──────────────────────────────────────────────────

def _form_error(template: str, message: str, **ctx):
    """Render a form template with an error message and 400 status."""
    return render_template(template, error=message, **ctx), 400
