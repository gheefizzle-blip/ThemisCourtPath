"""
Child Support Intake — Web Application
========================================
Flask-based web frontend for the Navajo County
Child Support Petition intake and PDF filling process.

TCP-WO-200 (Auth System) integrated:
- /api/submit and /api/download require an authenticated session

TCP-WO-201A (Encrypted Storage) integrated:
- Intake data is encrypted with Fernet before persistence
- Filings are owned by user_id; cross-user reads are rejected

TCP-WO-202 (Secure Document Handling) integrated:
- PDFs and validation notes are NEVER written to disk
- /api/submit returns filing_id + download URLs
- /api/download/<filing_id>/<doc_type> regenerates documents in memory
  on each request from the encrypted intake source-of-truth
- No OUTPUT_DIR; no temp files; no plaintext document persistence

TCP-WO-300 (Stripe Payment Gating) integrated:
- POST /api/create-checkout-session creates a Stripe session for a filing
- /success verifies the returned session and marks filing as paid
- /api/download is gated: returns 403 if payment_status != 'paid'

Usage: python app.py
Then open http://localhost:5000 in Chrome.
"""

import os
from datetime import datetime, timedelta
from io import BytesIO

import fitz  # PyMuPDF
from flask import (
    Flask, render_template, request, jsonify,
    send_file, session, redirect, url_for, abort
)

from auth import auth_bp, init_db as init_auth_db, close_db, login_required
from storage import (
    init_db as init_storage_db,
    save_filing, load_filing,
    get_payment_status, set_stripe_session, mark_payment_status,
    lookup_filing_by_session,
)
import payments

app = Flask(__name__)

# ── Session configuration ─────────────────────────────────
# SECRET_KEY: from env in production (rotates without losing data),
# random per-process in dev. NEVER hardcoded.
app.secret_key = os.environ.get("SECRET_KEY") or os.urandom(32)

_IS_PROD = os.environ.get("FLASK_ENV") == "production"

app.config.update(
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE="Lax",
    SESSION_COOKIE_SECURE=_IS_PROD,           # HTTPS-only in prod
    PERMANENT_SESSION_LIFETIME=timedelta(hours=24),
    MAX_CONTENT_LENGTH=2 * 1024 * 1024,       # 2 MB cap on submissions
)

# ── Configuration ─────────────────────────────────────────
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Source PDF — bundled into the container image in production,
# resolved from a configurable env var, with a sensible dev fallback.
# Read-only at runtime; never modified.
SOURCE_PDF = os.environ.get(
    "SOURCE_PDF",
    os.path.join(BASE_DIR, "Petition_to_Establish_Child_Support.pdf"),
)

# Doc types that /api/download can serve. Keep this small and explicit.
_VALID_DOC_TYPES = {"editable", "filled", "validation"}

# ── Auth blueprint + DB lifecycle ─────────────────────────
app.register_blueprint(auth_bp)
app.teardown_appcontext(close_db)

with app.app_context():
    init_auth_db()
    init_storage_db()

# Stripe init: warns if STRIPE_SECRET_KEY missing; payment endpoints
# return 503 until configured. Does NOT block app startup.
payments.init_stripe()


# ── Routes ────────────────────────────────────────────────

@app.route("/")
def index():
    """Landing page. Does NOT clear session (auth survives nav home)."""
    return render_template("index.html")


@app.route("/intake")
@login_required
def intake():
    """Main intake form — multi-step wizard. Requires login."""
    return render_template("intake.html")


@app.route("/api/submit", methods=["POST"])
@login_required
def submit_intake():
    """
    Receive the completed intake JSON, encrypt and persist it under
    the authenticated user's id, validate that PDF generation succeeds
    in memory, and return the filing_id plus download URLs.

    TCP-WO-202: nothing is written to disk. PDFs are regenerated in
    memory on demand via /api/download/<filing_id>/<doc_type>.
    """
    data = request.get_json(silent=True)
    if not data:
        return jsonify({"error": "No data received"}), 400

    user_id = session.get("user_id")
    if not user_id:
        # Belt and suspenders — login_required already enforced this.
        return jsonify({"error": "Authentication required"}), 401

    # TCP-WO-320: extract the non-sensitive fee-waiver flag. This is a
    # plaintext column on the filings row (not part of the encrypted
    # payload). Accepted values: "yes", "no". Default: "no".
    fee_waiver_requested = str(data.pop("fee_waiver_requested", "no")).lower()
    if fee_waiver_requested not in ("yes", "no"):
        fee_waiver_requested = "no"

    # Tag with the authenticated user
    data["generated"] = datetime.now().strftime("%Y-%m-%d %H:%M")
    data["form"] = "Navajo County Petition to Establish Child Support"
    data["_user_id"] = user_id

    # Encrypt and persist as the source of truth. PDFs are regenerated
    # on demand from this — they are not the persistence layer.
    try:
        filing_id = save_filing(
            user_id, data, fee_waiver_requested=fee_waiver_requested
        )
    except Exception:
        app.logger.exception("save_filing failed")
        return jsonify({"error": "Could not save filing"}), 500

    # Smoke-validate that PDF generation succeeds in memory.
    # Bytes are discarded immediately — nothing written to disk.
    # Mirror what load_filing() does so the smoke path exercises the
    # same validation-note branch a real download will hit.
    data["_fee_waiver_requested"] = fee_waiver_requested
    try:
        smoke = fill_petition_pdf(data)
    except Exception:
        app.logger.exception("PDF smoke generation failed")
        return jsonify({"error": "Filing saved but document generation failed"}), 500

    fields_filled = smoke.get("count", 0)
    warnings = smoke.get("warnings", [])
    # Drop the bytes immediately; download endpoint regenerates as needed.
    smoke = None

    # Build a friendly filename base for the eventual download attachment.
    pet_last = data.get("petitioner", {}).get("last_name", "Unknown").replace(" ", "_")
    resp_last = data.get("respondent", {}).get("last_name", "Unknown").replace(" ", "_")
    child_first = data.get("child", {}).get("first_name", "Child").replace(" ", "_")
    base_name = f"{pet_last}_vs_{resp_last}_{child_first}"

    return jsonify({
        "success": True,
        "filing_id": filing_id,
        "base_name": base_name,
        "pdf_editable": f"/api/download/{filing_id}/editable",
        "pdf_filled":   f"/api/download/{filing_id}/filled",
        "validation":   f"/api/download/{filing_id}/validation",
        "fields_filled": fields_filled,
        "warnings": warnings,
    })


@app.route("/api/download/<filing_id>/<doc_type>")
@login_required
def download_file(filing_id, doc_type):
    """
    Regenerate a document in memory from the encrypted intake and stream
    it to the authenticated owner. Nothing is written to disk; the
    BytesIO buffer is GC'd at request end.

    TCP-WO-202: this endpoint replaces the prior filename-based one.
    TCP-WO-300: this endpoint is gated on payment_status == 'paid'.
    """
    user_id = session.get("user_id")
    if not user_id:
        return jsonify({"error": "Authentication required"}), 401

    if doc_type not in _VALID_DOC_TYPES:
        # Generic 404 — do not leak which doc_types exist.
        abort(404)

    # TCP-WO-300: gate on payment status. Cross-user lookups raise
    # LookupError → 404 (no existence leak).
    try:
        pay_status = get_payment_status(filing_id, user_id)
    except (LookupError, ValueError):
        abort(404)
    if pay_status != "paid":
        return jsonify({"error": "Payment required", "payment_status": pay_status}), 403

    # Load+decrypt the source-of-truth intake. This raises LookupError
    # for both not-found and wrong-owner — same message in both cases.
    try:
        data = load_filing(filing_id, user_id)
    except (LookupError, ValueError):
        abort(404)
    except Exception:
        app.logger.exception("load_filing failed")
        return jsonify({"error": "Could not load filing"}), 500

    # Regenerate in memory.
    try:
        result = fill_petition_pdf(data)
    except Exception:
        app.logger.exception("PDF regeneration failed")
        return jsonify({"error": "Document generation failed"}), 500

    pet_last = data.get("petitioner", {}).get("last_name", "Unknown").replace(" ", "_")
    resp_last = data.get("respondent", {}).get("last_name", "Unknown").replace(" ", "_")
    child_first = data.get("child", {}).get("first_name", "Child").replace(" ", "_")
    base_name = f"{pet_last}_vs_{resp_last}_{child_first}"

    if doc_type == "editable":
        payload = result.get("editable_bytes")
        if not payload:
            abort(500)
        return send_file(
            BytesIO(payload),
            mimetype="application/pdf",
            as_attachment=True,
            download_name=f"{base_name}_COMPLETE_EDITABLE.pdf",
        )

    if doc_type == "filled":
        payload = result.get("filled_bytes")
        if not payload:
            abort(500)
        return send_file(
            BytesIO(payload),
            mimetype="application/pdf",
            as_attachment=True,
            download_name=f"{base_name}_COMPLETE_FILLED.pdf",
        )

    # validation
    text = result.get("validation_text") or ""
    return send_file(
        BytesIO(text.encode("utf-8")),
        mimetype="text/plain; charset=utf-8",
        as_attachment=True,
        download_name=f"{base_name}_Validation.txt",
    )


@app.route("/api/create-checkout-session", methods=["POST"])
@login_required
def create_checkout_session():
    """
    TCP-WO-300: create a Stripe Checkout session for the authenticated
    user's filing and return its URL. The browser then redirects to
    Stripe-hosted checkout.
    """
    if not payments.is_configured():
        return jsonify({"error": "Payments not configured"}), 503

    user_id = session.get("user_id")
    if not user_id:
        return jsonify({"error": "Authentication required"}), 401

    body = request.get_json(silent=True) or {}
    filing_id = body.get("filing_id")
    if not filing_id:
        return jsonify({"error": "filing_id required"}), 400

    # Verify the user owns this filing. Cross-user → 404 (no leak).
    try:
        get_payment_status(filing_id, user_id)
    except (LookupError, ValueError):
        abort(404)

    # Build URLs for Stripe to redirect back to.
    success_url = url_for("success", _external=True) + "?session_id={CHECKOUT_SESSION_ID}"
    cancel_url = url_for("intake", _external=True)

    try:
        result = payments.create_checkout_session(
            filing_id=filing_id,
            user_id=user_id,
            success_url=success_url,
            cancel_url=cancel_url,
        )
    except Exception:
        app.logger.exception("Stripe session creation failed")
        return jsonify({"error": "Could not create payment session"}), 502

    # Persist session_id BEFORE returning so /success can correlate it
    # back to the filing even if the redirect arrives before the user's
    # browser sees the response.
    try:
        set_stripe_session(filing_id, user_id, result["session_id"])
    except Exception:
        app.logger.exception("set_stripe_session failed")
        return jsonify({"error": "Could not record payment session"}), 500

    return jsonify({"checkout_url": result["checkout_url"]})


@app.route("/success")
@login_required
def success():
    """
    Success page. If a Stripe session_id is present in the query string,
    verify the session, mark the filing as paid, and render the page
    with download links. Otherwise render a generic success view.

    TCP-WO-300: payment confirmation is server-side. The client cannot
    fake a paid state — we re-fetch the session from Stripe.
    """
    user_id = session.get("user_id")
    session_id = request.args.get("session_id")
    download_links = None
    payment_state = None
    error = None

    if session_id and payments.is_configured():
        try:
            verified = payments.verify_payment(session_id)
        except Exception:
            app.logger.exception("Stripe verify_payment failed")
            verified = None

        if verified is None:
            error = "Could not verify payment session."
        else:
            # The session metadata MUST match the filing we have in DB
            # AND match the currently-logged-in user.
            session_user = verified.get("user_id")
            session_filing = verified.get("filing_id")
            if session_user != user_id:
                error = "Payment session does not belong to this account."
            else:
                payment_state = verified.get("payment_status")
                if payment_state == "paid":
                    try:
                        mark_payment_status(session_filing, user_id, "paid")
                        download_links = {
                            "pdf_editable": f"/api/download/{session_filing}/editable",
                            "pdf_filled":   f"/api/download/{session_filing}/filled",
                            "validation":   f"/api/download/{session_filing}/validation",
                        }
                    except Exception:
                        app.logger.exception("mark_payment_status failed")
                        error = "Payment verified but could not unlock download."

    return render_template(
        "success.html",
        download_links=download_links,
        payment_state=payment_state,
        error=error,
        has_session=bool(session_id),
    )


# ── PDF Filling Engine ────────────────────────────────────

def build_field_maps(data):
    """
    Build the TEXT_FIELDS and CHECKBOXES maps from intake data.
    This mirrors the logic in fill_child_support_packet.py but
    is now driven by the dynamic intake data instead of hardcoded values.
    """
    pet = data.get("petitioner", {})
    resp = data.get("respondent", {})
    child = data.get("child", {})
    rel = data.get("relationship", {})
    support = data.get("support", {})
    arrears = data.get("arrears", {})
    emp = data.get("employment", {})
    pet_emp = data.get("petitioner_employment", {})
    options = data.get("options", {})
    venue = data.get("venue", {})

    # Construct composite values
    pet_full = pet.get("full_name", "")
    resp_full = resp.get("full_name", "")
    child_full = child.get("full_name", "")
    child_dob = child.get("dob", "")

    pet_addr = pet.get("address", "")
    pet_csz = f"{pet.get('city', '')}, {pet.get('state', '')} {pet.get('zip', '')}"
    resp_addr = resp.get("address", "")
    resp_csz = f"{resp.get('city', '')}, {resp.get('state', '')} {resp.get('zip', '')}"

    pet_dob = pet.get("dob", "")
    resp_dob = resp.get("dob", "")

    support_amount = support.get("monthly_amount", "")
    med_pet_pct = support.get("pet_medical_pct", "")
    med_resp_pct = support.get("resp_medical_pct", "")
    if med_pet_pct and not med_pet_pct.endswith("%"):
        med_pet_pct += "%"
    if med_resp_pct and not med_resp_pct.endswith("%"):
        med_resp_pct += "%"

    employer_name = emp.get("employer_name", "")
    employer_addr = emp.get("employer_address", "")
    employer_city = emp.get("employer_city", "")
    employer_state = emp.get("employer_state", "")
    employer_zip = emp.get("employer_zip", "")
    employer_phone = emp.get("employer_phone", "")
    employment_type = emp.get("employment_type", "")
    job_title = emp.get("job_title", "")

    # Build occupation string
    resp_occupation = ""
    if employer_name and employment_type:
        type_labels = {"w2": "Employee", "1099": "Independent Contractor", "self": "Self-employed", "other": ""}
        resp_occupation = f"{employer_name} - {type_labels.get(employment_type, employment_type)}"
    elif employer_name:
        resp_occupation = employer_name

    pet_county = venue.get("county", "Navajo")

    # Determine respondent county from their city (simplified)
    resp_county = ""
    resp_city_lower = resp.get("city", "").lower()
    if "mesa" in resp_city_lower or "phoenix" in resp_city_lower or "tempe" in resp_city_lower or "scottsdale" in resp_city_lower or "chandler" in resp_city_lower or "gilbert" in resp_city_lower or "glendale" in resp_city_lower:
        resp_county = "Maricopa"
    elif "tucson" in resp_city_lower:
        resp_county = "Pima"
    elif "flagstaff" in resp_city_lower:
        resp_county = "Coconino"
    else:
        resp_county = ""

    # Representation
    rep_text = "Self"
    if pet.get("has_attorney"):
        rep_text = pet.get("attorney_name", "")

    # Build paternity statement
    paternity_text = ""
    if rel.get("paternity_established"):
        paternity_text = "Paternity has been legally established by court order."
    elif rel.get("paternity_acknowledged"):
        paternity_text = "Paternity has been acknowledged via signed acknowledgment form."
    elif rel.get("on_birth_cert"):
        paternity_text = "Respondent is listed on the birth certificate."
    else:
        paternity_text = "Respondent has acknowledged parentage but is not listed on the birth certificate. Paternity has not yet been legally established."

    if rel.get("contesting_paternity"):
        paternity_text += " Respondent is contesting paternity."

    # Child gender label
    child_gender_label = "Male" if child.get("gender") == "m" else "Female"

    # Child residence info
    child_addr = child.get("address", pet_addr)
    child_city_state = f"{child.get('city', pet.get('city', ''))}, {child.get('state', pet.get('state', ''))}"

    # Petitioner's own employment/occupation
    pet_employer_name = pet_emp.get("employer_name", "")
    pet_employment_type = pet_emp.get("employment_type", "")
    pet_occupation = ""
    if pet_employer_name and pet_employment_type:
        type_labels = {"w2": "Employee", "1099": "Independent Contractor", "self": "Self-employed", "other": ""}
        pet_occupation = f"{pet_employer_name} - {type_labels.get(pet_employment_type, '')}".strip(" -")
    elif pet_employer_name:
        pet_occupation = pet_employer_name

    # Determine who pays child support (from Step 5)
    support_payor = support.get("payor", "resp")  # 'pet' or 'resp'

    # ── TEXT FIELDS ──
    text_fields = {}

    # ─── Shared header fields (propagate across multiple pages) ───
    if pet_full:
        text_fields["Name of Person Filing 1"] = pet_full
        text_fields["Name of Person Filing 2"] = pet.get("email", "")  # misnamed email field on pg 4
        text_fields["Name of Petitioner"] = pet_full
    if resp_full:
        text_fields["Name of Respondent"] = resp_full

    if pet_addr and not options.get("address_protection"):
        text_fields["Address if not protected"] = pet_addr
    elif options.get("safe_address"):
        text_fields["Address if not protected"] = options["safe_address"]

    if pet_csz.strip(", "):
        text_fields["City State Zip Code"] = pet_csz

    text_fields["Representing    Self or    Lawyer for"] = rep_text

    # Top-header phone/email (pages 4, 9, 18, 20)
    if pet.get("phone"):
        text_fields["Telephone Number"] = pet["phone"]
        text_fields["Telephone Numbers"] = pet["phone"]
        text_fields["Daytime Telephone Numbers"] = pet["phone"]
    if pet.get("email"):
        text_fields["Email Address"] = pet["email"]

    # ═════════════════════════════════════════════════════════
    # PAGE 4 — Sensitive Data Sheet
    # ═════════════════════════════════════════════════════════
    # Row meanings (from field position analysis):
    #   Personal Info Table: Name | Gender | DOB | SSN | Driver's License
    #   Address Table: Mailing | City/State/Zip | Contact Phone | Email |
    #                  Current Employer | Employer Addr | Employer City/State/Zip

    # Row: Date of Birth
    if pet_dob:
        text_fields["Date of Birth MonthDayYear 1"] = pet_dob
    if resp_dob:
        text_fields["1"] = resp_dob  # respondent DOB field (by position)

    # Row: Social Security Number
    # NOTE: "Date of Birth MonthDayYear 2" is actually the PETITIONER SSN field
    # (misleadingly named). "2" is the RESPONDENT SSN field.
    if pet.get("ssn"):
        text_fields["Date of Birth MonthDayYear 2"] = pet["ssn"]
    if resp.get("ssn"):
        text_fields["2"] = resp["ssn"]

    # Row: Driver's License Number
    if pet.get("dl_number"):
        text_fields["Drivers License Number"] = pet["dl_number"]
    if resp.get("dl_number"):
        text_fields["3"] = resp["dl_number"]

    # Row: Mailing Address
    if pet_addr:
        text_fields["REQUESTING ADDRESS PROTECTION 1"] = pet_addr
    if pet_csz.strip(", "):
        text_fields["REQUESTING ADDRESS PROTECTION 2"] = pet_csz
    if resp_addr:
        text_fields["1_2"] = resp_addr
    if resp_csz.strip(", "):
        text_fields["2_2"] = resp_csz

    # Row: Contact Phone (different from top "Telephone Number")
    if pet.get("phone"):
        text_fields["REQUESTING ADDRESS PROTECTION 3"] = pet["phone"]
    if resp.get("phone"):
        text_fields["3_2"] = resp["phone"]

    # Row: Email Address
    if pet.get("email"):
        text_fields["REQUESTING ADDRESS PROTECTION 4"] = pet["email"]
    if resp.get("email"):
        text_fields["4"] = resp["email"]

    # Row: Current Employer Name (petitioner and respondent)
    if pet_employer_name:
        text_fields["REQUESTING ADDRESS PROTECTION 5"] = pet_employer_name
    if employer_name:
        text_fields["5"] = employer_name

    # Row: Employer Address
    if employer_addr:
        text_fields["6"] = employer_addr

    # Row: Employer City, State, Zip — ONLY populate if employer data exists
    if employer_name and (employer_city or employer_state or employer_zip):
        parts = [p for p in [employer_city, employer_state, employer_zip] if p]
        text_fields["7"] = ", ".join([employer_city, f"{employer_state} {employer_zip}".strip()]).strip(", ") if employer_city else f"{employer_state} {employer_zip}".strip()
    if pet_employer_name:
        # Petitioner employer city/state/zip
        text_fields["Employer City State Zip Code"] = ""  # leave blank unless provided

    # ═════════════════════════════════════════════════════════
    # PAGE 5 — Child Info on Sensitive Data Sheet
    # ═════════════════════════════════════════════════════════
    if child_full:
        text_fields["Child NameRow1"] = child_full
    if child_gender_label:
        text_fields["Gender Child Social Security Number Child Date of BirthRow1"] = child_gender_label
    if child_dob:
        text_fields["Child Date of Birth 1"] = child_dob
    if child.get("ssn"):
        text_fields["Child Social Security Number 1"] = child["ssn"]

    # ═════════════════════════════════════════════════════════
    # PAGE 6 — Family Court Cover Sheet
    # ═════════════════════════════════════════════════════════
    # CORRECTED field mapping (discovered via position analysis):
    #   Text2  = Pet Address         Text7  = Resp Address
    #   Text3  = Pet City/State/Zip  Text8  = Resp City/State/Zip
    #   Text4  = Pet Phone           Text9  = Resp Phone
    #   Text5  = Pet EMAIL           Text10 = Resp EMAIL
    #   Text6  = Pet DOB             Text11 = Resp DOB
    if pet_addr:
        text_fields["Text2"] = pet_addr
    if pet_csz.strip(", "):
        text_fields["Text3"] = pet_csz
    if pet.get("phone"):
        text_fields["Text4"] = pet["phone"]
    if pet.get("email"):
        text_fields["Text5"] = pet["email"]
    if pet_dob:
        text_fields["Text6"] = pet_dob

    if resp_addr:
        text_fields["Text7"] = resp_addr
    if resp_csz.strip(", "):
        text_fields["Text8"] = resp_csz
    if resp.get("phone"):
        text_fields["Text9"] = resp["phone"]
    if resp.get("email"):
        text_fields["Text10"] = resp["email"]
    if resp_dob:
        text_fields["Text11"] = resp_dob

    # ═════════════════════════════════════════════════════════
    # PAGE 8 — Children on cover sheet
    # ═════════════════════════════════════════════════════════
    if child_full and child_dob:
        text_fields["DATE OF BIRTH 1"] = f"{child_full}    {child_dob}"

    # ═════════════════════════════════════════════════════════
    # PAGE 9-13 — Petition to Establish Child Support
    # ═════════════════════════════════════════════════════════
    if pet_addr and pet_csz.strip(", "):
        text_fields["Address"] = f"{pet_addr}, {pet_csz}"
    if pet_county:
        text_fields["County of Residence"] = pet_county
    if pet_dob:
        text_fields["Date of Birth"] = pet_dob
    if pet_occupation:
        text_fields["Occupation"] = pet_occupation  # Petitioner occupation

    if resp_addr and resp_csz.strip(", "):
        text_fields["Address_2"] = f"{resp_addr}, {resp_csz}"
    if resp_county:
        text_fields["County of Residence_2"] = resp_county
    if resp_dob:
        text_fields["Date of Birth_2"] = resp_dob
    if resp_occupation:
        text_fields["Occupation_2"] = resp_occupation

    # Child section of petition (Section 5 "Information About Minor Children")
    if child_full:
        text_fields["Childs Name"] = child_full
    if child_dob:
        text_fields["Date of Birth_3"] = child_dob
    if child_addr:
        text_fields["Current Address"] = child_addr
    if child_city_state.strip(", "):
        text_fields["City State"] = child_city_state
    if pet_county:
        text_fields["County"] = pet_county

    text_fields["How long at this address"] = "Since birth"

    # Paternity — "stating that" free-text field
    if paternity_text:
        text_fields["stating that"] = paternity_text

    # ═════════════════════════════════════════════════════════
    # PAGE 18-19 — Order to Appear
    # ═════════════════════════════════════════════════════════
    if resp_full:
        text_fields["To 1"] = resp_full
    if resp_addr and resp_csz.strip(", "):
        text_fields["To 2"] = f"{resp_addr}, {resp_csz}"

    # ═════════════════════════════════════════════════════════
    # PAGE 20-28 — Child Support Order
    # ═════════════════════════════════════════════════════════
    if child_full:
        text_fields["Name 1"] = child_full
    if child_dob:
        text_fields["Date of Birth 1"] = child_dob

    if support_amount:
        # Amount appears on multiple pages of the CS Order
        text_fields["Respondent in the amount of"] = support_amount     # pg 20
        text_fields["Respondent in the amount of_2"] = support_amount   # pg 21
        text_fields["in the sum of"] = support_amount                    # pg 23

        # Page 24 — monthly total calculation
        try:
            cs_amt = float(support_amount)
            clearinghouse_fee = 8.00
            total_monthly = cs_amt + clearinghouse_fee
            text_fields["payments to    Petitioner    Respondent of"] = f"{total_monthly:.2f}"
            text_fields["undefined_6"] = f"{cs_amt:.2f}"       # Current child support
            text_fields["undefined_9"] = f"{total_monthly:.2f}"  # Total monthly payment
        except (ValueError, TypeError):
            pass

    # Medical expenses split on page 25
    if med_pet_pct:
        text_fields["be shared as follows Petitioner"] = med_pet_pct
    if med_resp_pct:
        text_fields["Respondent_4"] = med_resp_pct

    # NON-COVERED MEDICAL EXPENSES (page 25 top section)
    if med_pet_pct:
        text_fields["NONCOVERED MEDICAL EXPENSES    Petitioner is ordered to pay"] = med_pet_pct
    if med_resp_pct:
        text_fields["Respondent is ordered to pay"] = med_resp_pct

    # ═════════════════════════════════════════════════════════
    # PAGE 26 — Tax Exemptions Table
    # ═════════════════════════════════════════════════════════
    # The tax exemption table has 6 rows. Each row has:
    #   - Child Name field (1_4, 2_5, 3_4, 4_2, 5_2, 6_2)
    #   - Petitioner checkbox (Check Box133-138)
    #   - Respondent checkbox (Check Box139-144)
    #   - "For Calendar Year" text field (Petitioner    Respondent, _2, _3, _4, _5, _6)
    #
    # We fill up to 6 years based on the tax_exemption_to setting:
    #   - "pet": All years to Petitioner
    #   - "resp": All years to Respondent
    #   - "alt": Alternating starting with Petitioner in current year

    tax_option = options.get("tax_exemption_to", "")
    tax_rows = []  # list of (child_name_field, pet_cb, resp_cb, year_field)
    if options.get("request_tax_exemption") and tax_option and child_full:
        tax_rows = [
            ("1_4", "Check Box133", "Check Box139", "Petitioner    Respondent"),
            ("2_5", "Check Box134", "Check Box140", "Petitioner    Respondent_2"),
            ("3_4", "Check Box135", "Check Box141", "Petitioner    Respondent_3"),
            ("4_2", "Check Box136", "Check Box142", "Petitioner    Respondent_4"),
            ("5_2", "Check Box137", "Check Box143", "Petitioner    Respondent_5"),
            ("6_2", "Check Box138", "Check Box144", "Petitioner    Respondent_6"),
        ]
        current_year = datetime.now().year
        child_label = f"{child_full}  DOB {child_dob}" if child_dob else child_full

        # Deferred to checkbox section below — we'll record the decisions here
        # and apply them in the checkboxes block.
        tax_checkboxes_to_add = set()
        for i, (name_field, pet_cb, resp_cb, year_field) in enumerate(tax_rows):
            text_fields[name_field] = child_label
            text_fields[year_field] = str(current_year + i)

            if tax_option == "pet":
                tax_checkboxes_to_add.add(pet_cb)
            elif tax_option == "resp":
                tax_checkboxes_to_add.add(resp_cb)
            elif tax_option == "alt":
                # Alternate: even offset = petitioner, odd = respondent
                if i % 2 == 0:
                    tax_checkboxes_to_add.add(pet_cb)
                else:
                    tax_checkboxes_to_add.add(resp_cb)
    else:
        tax_checkboxes_to_add = set()

    # ═════════════════════════════════════════════════════════
    # PAGE 29 — Employer Information Sheet
    # ═════════════════════════════════════════════════════════
    # Always set Obligor (payor) from relationship data
    payor_name = resp_full if support_payor == "resp" else pet_full
    if payor_name:
        text_fields["OBLIGORPAYOR"] = payor_name

    # Only populate employer fields when the payor's employer data is available
    # Assume payor is respondent (most common case)
    if support_payor == "resp":
        if employer_name:
            text_fields["CURRENT EMPLOYER NAME 1"] = employer_name
            if employment_type:
                type_labels = {"w2": "W-2 Employee", "1099": "Independent Contractor", "self": "Self-employed", "other": ""}
                text_fields["CURRENT EMPLOYER NAME 2"] = type_labels.get(employment_type, "")
            if employer_city:
                text_fields["CITY"] = employer_city
            if employer_state:
                text_fields["STATE"] = employer_state
            if employer_zip:
                text_fields["ZIP CODE"] = employer_zip
            if employer_phone:
                text_fields["EMPLOYER TELEPHONE 1"] = employer_phone

    # ── CHECKBOXES ──
    checkboxes = set()
    checkboxes_uncheck = set()  # Explicitly uncheck these

    pet_role = rel.get("petitioner_role", "")
    resp_role = rel.get("respondent_role", "")

    # ─── Gender checkboxes (page 4) ───
    # Field names: "Male or" / "Female" (petitioner), "Male or_2" / "Female_2" (respondent)
    if pet.get("gender") == "f":
        checkboxes.add("Female")
        checkboxes_uncheck.add("Male or")
    elif pet.get("gender") == "m":
        checkboxes.add("Male or")
        checkboxes_uncheck.add("Female")

    if resp.get("gender") == "m":
        checkboxes.add("Male or_2")
        checkboxes_uncheck.add("Female_2")
    elif resp.get("gender") == "f":
        checkboxes.add("Female_2")
        checkboxes_uncheck.add("Male or_2")

    # ─── Representation (page 4) ───
    if not pet.get("has_attorney"):
        checkboxes.add("Representing Self No Attorney")
    else:
        checkboxes.add("Represented by Attorney")

    # ─── Cover Sheet case type (page 6) ───
    # Check Paternity/Maternity if paternity not established
    if not rel.get("paternity_established"):
        checkboxes.add("PaternityMaternity")
    checkboxes.add("Establish Support")

    # ─── PETITION Page 9: "I am the..." (Check Box16/17/18) ───
    if pet_role == "mother":
        checkboxes.add("Check Box16")
    elif pet_role == "father":
        checkboxes.add("Check Box17")
    else:
        checkboxes.add("Check Box18")  # Other

    # ─── PETITION Page 10: "Respondent is the..." (Check Box19/20/21) ───
    if resp_role == "mother":
        checkboxes.add("Check Box19")
    elif resp_role == "father":
        checkboxes.add("Check Box20")
    else:
        checkboxes.add("Check Box21")  # Other

    # ─── PETITION Page 10: VENUE (Check Box22, NOT Check Box19) ───
    checkboxes.add("Check Box22")

    # ─── PETITION Page 12: Requests of the Court ───
    # Section A - Child Support: main box + payor + payee
    checkboxes.add("Check Box42")  # Main "Order that child support be paid by"
    if support_payor == "pet":
        checkboxes.add("Check Box47")  # Petitioner pays
        checkboxes.add("Check Box50")  # ...to Respondent
    else:
        checkboxes.add("Check Box48")  # Respondent pays
        checkboxes.add("Check Box49")  # ...to Petitioner

    # Section B - Medical Insurance (based on Step 5 who_provides_insurance)
    insurance_provider = support.get("who_provides_insurance", "")
    if insurance_provider == "pet":
        checkboxes.add("Check Box44")   # Petitioner provides insurance
        checkboxes.add("Check Box51")   # Medical
        checkboxes.add("Check Box52")   # Dental
        checkboxes.add("Check Box53")   # Vision
    elif insurance_provider == "resp":
        checkboxes.add("Check Box45")   # Respondent provides insurance
        checkboxes.add("Check Box54")   # Medical
        checkboxes.add("Check Box55")   # Dental
        checkboxes.add("Check Box56")   # Vision
    checkboxes.add("Check Box46")  # Both share unreimbursed medical

    # ─── CHILD SUPPORT ORDER Page 20: main payor/payee line ───
    checkboxes.add("Check Box57")  # Main "without deviation" box
    if support_payor == "pet":
        checkboxes.add("Check Box58")  # Petitioner pays
        checkboxes.add("Check Box61")  # to Respondent
    else:
        checkboxes.add("Check Box59")  # Respondent pays
        checkboxes.add("Check Box60")  # to Petitioner

    # ─── CHILD SUPPORT ORDER Page 21: "without deviation" block ───
    checkboxes.add("Check Box62")  # Main "without deviation"
    if support_payor == "pet":
        checkboxes.add("Check Box66")  # Petitioner
        checkboxes.add("Check Box75")  # to Respondent
    else:
        checkboxes.add("Check Box67")  # Respondent
        checkboxes.add("Check Box74")  # to Petitioner

    # ─── CHILD SUPPORT ORDER Page 22: No past support (default) ───
    if not arrears.get("requesting_past_support"):
        checkboxes.add("Check Box82")  # The court finds no child support arrearages due
        checkboxes.add("Check Box86")  # The court finds no past support amount due
        checkboxes.add("Check Box88")  # No temporary/voluntary payments made
        checkboxes.add("Check Box89")  # No evidence presented for past support

    # ─── CHILD SUPPORT ORDER Page 23: Main IT IS ORDERED ───
    checkboxes.add("Check Box96")  # Main "child support shall pay" box
    if support_payor == "pet":
        checkboxes.add("Check Box101")  # Petitioner shall pay
        checkboxes.add("Check Box104")  # to Respondent
    else:
        checkboxes.add("Check Box102")  # Respondent shall pay
        checkboxes.add("Check Box103")  # to Petitioner
    if not arrears.get("requesting_past_support"):
        checkboxes.add("Check Box100")  # No judgment for past support

    # ─── Page 8: Agreement on parenting (default No) ───
    # This was in the original script as "No_8"
    checkboxes.add("No_8")

    # ─── Page 7: Legal Disclosure Radio Buttons ───
    # These are radio button groups where the Yes and No buttons share a field name.
    # The radio_selections dict maps field_name -> 'yes' or 'no', and the fill loop
    # uses the widget's ON state value to determine which button to select.
    radio_selections = {}
    disclosures = data.get("disclosures", {})
    radio_selections["children or me"] = "yes" if disclosures.get("public_assistance") else "no"
    radio_selections["I have a case with the Division of Child Support Enforcement"] = \
        "yes" if disclosures.get("dcse_case") else "no"
    radio_selections["Do you currently have ANY other Pinal County Superior Court cases"] = \
        "yes" if disclosures.get("current_other_cases") else "no"
    radio_selections["Have you ever had ANY other Pinal County Superior Court cases"] = \
        "yes" if disclosures.get("past_other_cases") else "no"
    radio_selections["The respondent is being served by publication"] = \
        "yes" if disclosures.get("served_by_publication") else "no"

    # ─── Page 26: Tax Exemption Table ───
    # Add all tax exemption checkboxes decided above
    for cb in tax_checkboxes_to_add:
        checkboxes.add(cb)

    # If tax exemption was requested, add the conditional-on-current-support
    # checkbox (Check Box145 = main, Check Box146 = Petitioner, Check Box147 = Respondent).
    # This means the recipient can only claim the exemption if they are current
    # on support/arrears as of December 31 of that year.
    if options.get("request_tax_exemption") and tax_option:
        # Default: only if current on support
        # The condition applies to the paying parent (if they're current, they can claim)
        # But typically this applies to whoever has been allocated an exemption year.
        checkboxes.add("Check Box145")  # Main "may claim only if current" box
        # Both Pet and Resp are subject to this condition if they share years (alt)
        # or the single recipient is subject for "pet"/"resp" choices.
        if tax_option in ("pet", "alt"):
            checkboxes.add("Check Box146")  # Petitioner
        if tax_option in ("resp", "alt"):
            checkboxes.add("Check Box147")  # Respondent

    # ─── Page 29: Employer Info Notification ───
    # Always check for initial filings
    checkboxes.add("Notification")

    # ─── PETITION Page 10: Jurisdiction (Check Box23-28) ───
    jurisdiction = data.get("jurisdiction", {})
    if jurisdiction.get("resident"):
        checkboxes.add("Check Box23")
    if jurisdiction.get("serve"):
        checkboxes.add("Check Box24")
    if jurisdiction.get("agrees"):
        checkboxes.add("Check Box25")
    if jurisdiction.get("lived_with_child"):
        checkboxes.add("Check Box26")
    if jurisdiction.get("prebirth"):
        checkboxes.add("Check Box27")
    if jurisdiction.get("child_lives"):
        checkboxes.add("Check Box28")

    # ─── PETITION Page 11: Item 6 Paternity Method ───
    # Check Box29 = Court Order for Paternity
    # Check Box30 = Acknowledgment of Paternity (hospital program)
    # Check Box31 = Parties were legally married
    legal = data.get("legal", {})
    paternity_method = legal.get("paternity_method", "")
    if paternity_method == "court_order":
        checkboxes.add("Check Box29")
    elif paternity_method == "acknowledgment":
        checkboxes.add("Check Box30")
    elif paternity_method == "married":
        checkboxes.add("Check Box31")

    # ─── PETITION Page 11: Item 7 Child Support Status ───
    # Check Box32 = "To my knowledge there is no child support order"
    # Check Box33 = "Petitioner/Respondent made voluntary/direct support payments"
    if legal.get("no_current_order", True):
        checkboxes.add("Check Box32")
    if legal.get("voluntary_payments"):
        checkboxes.add("Check Box33")

    return text_fields, checkboxes, checkboxes_uncheck, radio_selections


def fill_worksheet_pages(doc, data):
    """
    Overlay text onto the static worksheet pages (15-17, 0-indexed 14-16).
    These pages have no form fields — we write directly onto the page.
    Returns list of (page, field_label, value) for the validation log.
    """
    pet = data.get("petitioner", {})
    resp = data.get("respondent", {})
    child = data.get("child", {})
    ws = data.get("worksheet", {})
    support = data.get("support", {})
    venue = data.get("venue", {})
    rel = data.get("relationship", {})

    filled = []
    font = "helv"  # Helvetica
    size = 10

    def put(page_idx, x, y, text, sz=None):
        """Insert text at coordinates on the given page."""
        if not text:
            return
        page = doc[page_idx]
        page.insert_text(
            fitz.Point(x, y),
            str(text),
            fontname=font,
            fontsize=sz or size,
            color=(0, 0, 0.4),  # Dark blue so it's clearly "filled" data
        )
        filled.append((page_idx + 1, f"Worksheet overlay ({x:.0f},{y:.0f})", str(text)))

    def put_check(page_idx, x, y):
        """Draw a checkmark / X at checkbox coordinates."""
        page = doc[page_idx]
        page.insert_text(
            fitz.Point(x, y),
            "X",
            fontname=font,
            fontsize=11,
            color=(0, 0, 0.4),
        )

    def dollar(val):
        """
        Format a value as a dollar string WITHOUT the '$' sign.
        The form template already has "$" printed to the left of input areas,
        so we only provide the numeric part (with comma formatting).
        """
        if not val:
            return ""
        try:
            return f"{float(val):,.2f}"
        except (ValueError, TypeError):
            return str(val).replace("$", "")

    # Determine Father/Mother mapping
    # Petitioner role determines which column they go in
    pet_role = rel.get("petitioner_role", "mother")
    if pet_role in ("mother",):
        # Petitioner = Mother (right column), Respondent = Father (left column)
        father_prefix = "resp"
        mother_prefix = "pet"
    else:
        # Petitioner = Father (left column), Respondent = Mother (right column)
        father_prefix = "pet"
        mother_prefix = "resp"

    def get_ws(key, default=""):
        return ws.get(key, default)

    # Column X positions for Father / Mother on pages 16-17.
    # The form template has "$" printed at:
    #   - Two-column rows: Father $ at x=387-397, Mother $ at x=484-493
    #   - Single-column rows (lines 20, 21, 22, 28, 29): $ at x=421-431
    # Our text is placed to the RIGHT of the "$" label.
    FATHER_X = 400   # Just after Father column $
    MOTHER_X = 497   # Just after Mother column $
    SINGLE_X = 434   # Just after single-column $ (lines 20, 21, 22, 28, 29)

    # ═══════════════════════════════════════════════════════
    # PAGE 15 (index 14) — Header & child info
    # ═══════════════════════════════════════════════════════

    # (1) Name of Person Filing — top header area
    put(14, 200, 80, pet.get("full_name", ""))
    # Address
    put(14, 145, 98, pet.get("address", ""))
    # City State Zip
    put(14, 205, 116, f"{pet.get('city', '')}, {pet.get('state', '')} {pet.get('zip', '')}")
    # Phone
    put(14, 200, 135, pet.get("phone", ""))

    # (3) Name of Petitioner
    put(14, 88, 325, pet.get("full_name", ""))
    # (4) Name of Respondent
    put(14, 88, 365, resp.get("full_name", ""))

    # (7) Name of parent filing
    put(14, 200, 403, pet.get("full_name", ""))
    # (8) Date prepared
    put(14, 165, 419, datetime.now().strftime("%m/%d/%Y"))

    # (9) I am the — check Petitioner
    put_check(14, 180, 438)

    # (10) Time-sharing arrangement
    time_sharing = get_ws("time_sharing", "")
    if time_sharing == "equal":
        put_check(14, 225, 454)
    elif time_sharing == "mostly_father":
        put_check(14, 343, 454)
    elif time_sharing == "mostly_mother":
        put_check(14, 460, 454)

    # Number of minor children
    put(14, 242, 637, get_ws("num_minor_children", "1"))
    # Number over 12
    put(14, 438, 637, get_ws("num_children_over_12", "0"))

    # (11) Child name, DOB, Age
    child_dob = child.get("dob", "")
    age_str = ""
    if child_dob:
        try:
            dob_dt = datetime.strptime(child_dob, "%m/%d/%Y")
            age_str = str((datetime.now() - dob_dt).days // 365)
        except ValueError:
            pass

    put(14, 92, 495, child.get("full_name", ""))
    put(14, 412, 495, child_dob)
    put(14, 515, 495, age_str)

    # (12) Income type for other parent
    income_type = get_ws("other_parent_income_type", "estimated")
    if income_type == "actual":
        put_check(14, 93, 685)
    elif income_type == "estimated":
        put_check(14, 93, 710)
    elif income_type == "attributed":
        put_check(14, 93, 736)

    # ═══════════════════════════════════════════════════════
    # PAGE 16 (index 15) — Income & calculation worksheet
    # ═══════════════════════════════════════════════════════

    # (13) Gross Monthly Income
    put(15, FATHER_X, 100, dollar(get_ws("father_gross_monthly")))
    put(15, MOTHER_X, 100, dollar(get_ws("mother_gross_monthly")))

    # (14) Spousal maintenance paid
    put(15, FATHER_X, 118, dollar(get_ws("father_spousal_paid", "0")))
    put(15, MOTHER_X, 118, dollar(get_ws("mother_spousal_paid", "0")))

    # (15) Spousal maintenance received
    put(15, FATHER_X, 136, dollar(get_ws("father_spousal_received", "0")))
    put(15, MOTHER_X, 136, dollar(get_ws("mother_spousal_received", "0")))

    # (16) Custodial parent of other children — deduction
    put(15, FATHER_X, 173, dollar(get_ws("father_other_children_deduct", "0")))
    put(15, MOTHER_X, 173, dollar(get_ws("mother_other_children_deduct", "0")))

    # (17) Court-ordered CS for other children
    put(15, FATHER_X, 200, dollar(get_ws("father_other_cs_paid", "0")))
    put(15, MOTHER_X, 200, dollar(get_ws("mother_other_cs_paid", "0")))

    # (18) Other children not subject of court order — deduction
    put(15, FATHER_X, 243, dollar(get_ws("father_other_nat_deduct", "0")))
    put(15, MOTHER_X, 243, dollar(get_ws("mother_other_nat_deduct", "0")))

    # (19) Adjusted Gross Monthly Income
    put(15, FATHER_X, 304, dollar(get_ws("father_adjusted_gross")))
    put(15, MOTHER_X, 304, dollar(get_ws("mother_adjusted_gross")))

    # (20) Combined Adjusted Gross Income — single column (x=SINGLE_X)
    put(15, SINGLE_X, 322, dollar(get_ws("combined_adjusted_gross")))

    # (21) Basic Child Support Obligation — single column
    num_children = get_ws("num_minor_children", "1")
    put(15, 260, 340, num_children)
    put(15, SINGLE_X, 340, dollar(get_ws("basic_cs_obligation")))

    # (22) Adjustment for children over 12 — single column
    put(15, SINGLE_X, 375, dollar(get_ws("over_12_adjustment", "0")))

    # (23) Medical insurance paid
    put(15, FATHER_X, 393, dollar(get_ws("father_medical_insurance", "0")))
    put(15, MOTHER_X, 393, dollar(get_ws("mother_medical_insurance", "0")))

    # (24) Monthly childcare costs
    put(15, FATHER_X, 410, dollar(get_ws("father_childcare", "0")))
    put(15, MOTHER_X, 410, dollar(get_ws("mother_childcare", "0")))

    # (25) Extra education expenses
    put(15, FATHER_X, 445, dollar(get_ws("father_education", "0")))
    put(15, MOTHER_X, 445, dollar(get_ws("mother_education", "0")))

    # (26) Extraordinary child expenses
    put(15, FATHER_X, 475, dollar(get_ws("father_extraordinary", "0")))
    put(15, MOTHER_X, 475, dollar(get_ws("mother_extraordinary", "0")))

    # (27) Subtotal
    put(15, FATHER_X, 490, dollar(get_ws("father_subtotal")))
    put(15, MOTHER_X, 490, dollar(get_ws("mother_subtotal")))

    # (28) Total Adjustments for Costs — single column
    put(15, SINGLE_X, 507, dollar(get_ws("total_adjustments")))

    # (29) Total Child Support Obligation — single column
    put(15, SINGLE_X, 525, dollar(get_ws("total_cs_obligation")))

    # (30) Each parent's proportionate percentage
    put(15, FATHER_X, 548, get_ws("father_pct", "") + ("%" if get_ws("father_pct") else ""))
    put(15, MOTHER_X, 548, get_ws("mother_pct", "") + ("%" if get_ws("mother_pct") else ""))

    # (31) Each parent's proportionate share
    put(15, FATHER_X, 578, dollar(get_ws("father_share")))
    put(15, MOTHER_X, 578, dollar(get_ws("mother_share")))

    # (32) Less paying parent's costs
    put(15, FATHER_X, 596, dollar(get_ws("father_less_costs")))
    put(15, MOTHER_X, 596, dollar(get_ws("mother_less_costs")))

    # (33) Parenting time costs
    # Write Table A/B selection and day counts
    parenting_table = get_ws("parenting_table", "A")
    father_days = get_ws("father_overnights", "0")
    mother_days = get_ws("mother_overnights", "0")
    if parenting_table == "A":
        put_check(15, 365, 614)  # Table A checkbox position
    else:
        put_check(15, 445, 614)  # Table B checkbox position

    # "No. of days" line — write day counts
    put(15, 150, 632, father_days)

    put(15, FATHER_X, 640, dollar(get_ws("father_parenting_time")))
    put(15, MOTHER_X, 640, dollar(get_ws("mother_parenting_time")))

    # (34) Adjustments subtotal
    put(15, FATHER_X, 665, dollar(get_ws("father_adj_subtotal")))
    put(15, MOTHER_X, 665, dollar(get_ws("mother_adj_subtotal")))

    # (35) Preliminary Child Support Amount — only in the payor's column
    if get_ws("father_preliminary_cs"):
        put(15, FATHER_X, 683, dollar(get_ws("father_preliminary_cs")))
    if get_ws("mother_preliminary_cs"):
        put(15, MOTHER_X, 683, dollar(get_ws("mother_preliminary_cs")))

    # ═══════════════════════════════════════════════════════
    # PAGE 17 (index 16) — Self-support reserve & final
    # ═══════════════════════════════════════════════════════

    # (36) Self-Support Reserve Test — only populate if user provided values.
    # These are optional adjustments that only apply when the payor's income
    # falls below the self-support reserve threshold ($1,115/month).
    if get_ws("father_line16"):
        put(16, FATHER_X, 132, dollar(get_ws("father_line16")))
    if get_ws("mother_line16"):
        put(16, MOTHER_X, 132, dollar(get_ws("mother_line16")))
    if get_ws("father_less_arrears"):
        put(16, FATHER_X, 150, dollar(get_ws("father_less_arrears")))
    if get_ws("mother_less_arrears"):
        put(16, MOTHER_X, 150, dollar(get_ws("mother_less_arrears")))

    # (37) Child support amount to be paid by — checkbox for payor
    cs_paid_by = get_ws("cs_paid_by", "")
    if cs_paid_by == "father":
        put_check(16, 260, 206)
    elif cs_paid_by == "mother":
        put_check(16, 325, 206)

    # (37) Final dollar amount — aligned to checkbox row (y=205)
    if get_ws("father_cs_amount"):
        put(16, FATHER_X, 205, dollar(get_ws("father_cs_amount")))
    if get_ws("mother_cs_amount"):
        put(16, MOTHER_X, 205, dollar(get_ws("mother_cs_amount")))

    # (38) Travel percentages
    pet_travel = support.get("pet_travel_pct", "")
    resp_travel = support.get("resp_travel_pct", "")
    if pet_role in ("mother",):
        put(16, FATHER_X, 225, (resp_travel + "%" if resp_travel else ""))
        put(16, MOTHER_X, 225, (pet_travel + "%" if pet_travel else ""))
    else:
        put(16, FATHER_X, 225, (pet_travel + "%" if pet_travel else ""))
        put(16, MOTHER_X, 225, (resp_travel + "%" if resp_travel else ""))

    # (39) Medical not paid by insurance
    pet_med = support.get("pet_medical_pct", "")
    resp_med = support.get("resp_medical_pct", "")
    if pet_role in ("mother",):
        put(16, FATHER_X, 252, (resp_med + "%" if resp_med else ""))
        put(16, MOTHER_X, 252, (pet_med + "%" if pet_med else ""))
    else:
        put(16, FATHER_X, 252, (pet_med + "%" if pet_med else ""))
        put(16, MOTHER_X, 252, (resp_med + "%" if resp_med else ""))

    return filled


def fill_petition_pdf(data):
    """
    Fill the Petition PDF with intake data, in memory only.
    Returns dict with PDF bytes and validation string. No disk writes.

    TCP-WO-202: all output is held in memory and returned to the caller.
    """
    warnings = []

    if not os.path.exists(SOURCE_PDF):
        return {
            "editable_bytes": None,
            "filled_bytes": None,
            "validation_text": None,
            "count": 0,
            "warnings": [f"Source PDF not found at: {SOURCE_PDF}"]
        }

    text_fields, checkboxes, checkboxes_uncheck, radio_selections = build_field_maps(data)

    filled_fields = []

    def _fill_doc(doc, track_fields=False):
        """Apply all text fields, checkboxes, radios, unchecks, and worksheet overlays."""
        for pg_num in range(len(doc)):
            page = doc[pg_num]
            for widget in page.widgets():
                fname = widget.field_name
                ftype = widget.field_type_string

                if ftype == "Text" and fname in text_fields:
                    value = text_fields[fname]
                    if value:
                        widget.field_value = value
                        widget.update()
                        if track_fields:
                            filled_fields.append((pg_num + 1, fname, value))

                elif ftype == "RadioButton" and fname in radio_selections:
                    # Radio groups share names. The "Yes" widget has an ON state
                    # like "Yes_2" and "No" widget has "No_2". We set the widget
                    # to True only if its state matches the desired answer.
                    desired = radio_selections[fname]  # "yes" or "no"
                    try:
                        states = widget.button_states()
                        normal_states = states.get("normal", [])
                        on_state = next((s for s in normal_states if s != "Off"), None)
                        if on_state:
                            if desired == "yes" and on_state.lower().startswith("yes"):
                                widget.field_value = on_state
                                widget.update()
                                if track_fields:
                                    filled_fields.append((pg_num + 1, fname, f"YES ({on_state})"))
                            elif desired == "no" and on_state.lower().startswith("no"):
                                widget.field_value = on_state
                                widget.update()
                                if track_fields:
                                    filled_fields.append((pg_num + 1, fname, f"NO ({on_state})"))
                    except Exception:
                        pass

                elif ftype in ("CheckBox", "RadioButton"):
                    if fname in checkboxes:
                        widget.field_value = True
                        widget.update()
                        if track_fields:
                            filled_fields.append((pg_num + 1, fname, "CHECKED"))
                    elif fname in checkboxes_uncheck:
                        # Explicitly uncheck fields we don't want set
                        widget.field_value = False
                        widget.update()

        # Overlay worksheet data on pages 15-17
        ws_filled = fill_worksheet_pages(doc, data)
        if track_fields:
            filled_fields.extend(ws_filled)

    # Fill editable version (with field tracking) -> bytes
    doc = fitz.open(SOURCE_PDF)
    _fill_doc(doc, track_fields=True)
    editable_bytes = doc.tobytes()
    doc.close()

    # Fill second copy (no tracking) -> bytes
    doc2 = fitz.open(SOURCE_PDF)
    _fill_doc(doc2, track_fields=False)
    filled_bytes = doc2.tobytes()
    doc2.close()

    # Generate validation text in memory
    validation_text = generate_validation(data, filled_fields)

    return {
        "editable_bytes": editable_bytes,
        "filled_bytes": filled_bytes,
        "validation_text": validation_text,
        "count": len(filled_fields),
        "warnings": warnings,
    }


def generate_validation(data, filled_fields):
    """
    Build a validation note string. TCP-WO-202: returns text only,
    never writes to disk.
    """
    pet = data.get("petitioner", {})
    resp = data.get("respondent", {})
    child = data.get("child", {})
    support = data.get("support", {})

    v = []
    v.append("=" * 70)
    v.append("VALIDATION NOTE")
    v.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    v.append("Generated by: Themis Court Path - themiscourtpath.com")
    v.append("=" * 70)
    v.append("")
    v.append("CASE:")
    v.append(f"  Petitioner: {pet.get('full_name', 'N/A')}")
    v.append(f"  Respondent: {resp.get('full_name', 'N/A')}")
    v.append(f"  Child: {child.get('full_name', 'N/A')} (DOB: {child.get('dob', 'N/A')})")
    v.append("")
    v.append("-" * 70)
    v.append("COURT-ONLY FIELDS LEFT BLANK")
    v.append("-" * 70)
    v.append("  - Case Number (all instances)")
    v.append("  - ATLAS Number (all instances)")
    v.append("  - Judge name (all instances)")
    v.append("  - Hearing date and time")
    v.append("  - All judicial signature blocks")
    v.append("  - Clerk use only sections")
    v.append("  - Payment commencement date")
    v.append("")
    v.append("-" * 70)
    v.append("DATA ENTERED")
    v.append("-" * 70)
    v.append(f"  Petitioner: {pet.get('full_name', '')}, DOB {pet.get('dob', '')}")
    v.append(f"  Address: {pet.get('address', '')}, {pet.get('city', '')}, {pet.get('state', '')} {pet.get('zip', '')}")
    v.append(f"  Respondent: {resp.get('full_name', '')}, DOB {resp.get('dob', '')}")
    v.append(f"  Address: {resp.get('address', '')}, {resp.get('city', '')}, {resp.get('state', '')} {resp.get('zip', '')}")
    v.append(f"  Child: {child.get('full_name', '')}, DOB {child.get('dob', '')}")
    if support.get("monthly_amount"):
        v.append(f"  Monthly support: ${support['monthly_amount']}")
    if support.get("pet_medical_pct"):
        v.append(f"  Medical split: {support['pet_medical_pct']}% / {support.get('resp_medical_pct', '')}%")
    v.append("")
    v.append("-" * 70)
    v.append("FILLED FIELDS LOG")
    v.append("-" * 70)
    for pg, fname, val in filled_fields:
        display_val = val if len(str(val)) <= 60 else str(val)[:57] + "..."
        v.append(f"  pg{pg:2d} | {fname:55s} | {display_val}")
    v.append("")
    v.append("-" * 70)
    v.append("BEFORE FILING - PETITIONER MUST:")
    v.append("-" * 70)
    v.append("  1. Review ALL filled fields for accuracy")
    v.append("  2. Complete Parent's Worksheet with income data")
    v.append("  3. Fill any blank fields the clerk requires")
    v.append("  4. Sign and date the Petition")
    v.append("  5. File with the Clerk of Court")
    v.append("  6. Handle filing fee (pay, defer, or waive)")
    v.append("")

    # TCP-WO-320: if the user indicated intent to apply for a court fee
    # waiver during intake, surface that in the validation note so they
    # remember to include the waiver application when filing.
    if data.get("_fee_waiver_requested") == "yes":
        v.append("-" * 70)
        v.append("COURT FILING FEE WAIVER")
        v.append("-" * 70)
        v.append("  User indicated intent to apply for court fee waiver.")
        v.append("  Include fee waiver application when filing.")
        v.append("  Arizona waiver / deferral forms are available from the")
        v.append("  Clerk of Superior Court in your county, or online at")
        v.append("  azcourts.gov/selfservicecenter (Fee Waiver / Deferral).")
        v.append("")
        v.append("  Themis Court Path does not determine whether you qualify")
        v.append("  for a fee waiver. The court will make that decision based")
        v.append("  on your application.")
        v.append("")

    v.append("=" * 70)
    v.append("END OF VALIDATION NOTE")
    v.append("=" * 70)

    return "\n".join(v)


# ── Run ───────────────────────────────────────────────────

if __name__ == "__main__":
    print()
    print("=" * 55)
    print("  Child Support Intake — Web Application")
    print("  Open Chrome and go to: http://localhost:5000")
    print("=" * 55)
    print()
    app.run(debug=not _IS_PROD, port=int(os.environ.get("PORT", 5000)))
