"""
Themis Court Path — Production Web Application
================================================
Flask-based web frontend for Arizona child support
petition intake and PDF filling.

Production hardening includes:
- Environment-aware configuration (dev vs production)
- Security headers on all responses
- Rate limiting on submission endpoint
- Custom error pages
- Cloud Run compatibility (/tmp output, $PORT binding)

Local dev:   python app.py  → http://localhost:5000
Production:  gunicorn app:app  (Cloud Run handles this)
"""

import json
import os
import re
import shutil
import time
from collections import defaultdict
from datetime import datetime
from functools import wraps

import fitz  # PyMuPDF
from flask import (
    Flask, render_template, request, jsonify,
    send_file, session, redirect, url_for
)

app = Flask(__name__)

# ── Environment Detection ────────────────────────────────
IS_PRODUCTION = os.environ.get("FLASK_ENV") == "production"

# Secret key: use env var in production, random for dev
app.secret_key = os.environ.get("SECRET_KEY", os.urandom(24))

# ── Configuration ─────────────────────────────────────────
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

if IS_PRODUCTION:
    # Cloud Run: writable filesystem is /tmp only
    OUTPUT_DIR = "/tmp/themis_output"
else:
    # Local development
    OUTPUT_DIR = os.path.join(BASE_DIR, "output")

# Source PDF — configurable by environment variable
# Production: bundled in Docker image at /app/templates_pdf/
# Development: parent directory of the app
SOURCE_PDF = os.environ.get(
    "SOURCE_PDF",
    os.path.join(os.path.dirname(BASE_DIR), "Petition_to_Establish_Child_Support.pdf")
)

os.makedirs(OUTPUT_DIR, exist_ok=True)


# ── Security Headers ─────────────────────────────────────

@app.after_request
def add_security_headers(response):
    """Add security headers to every response."""
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    if IS_PRODUCTION:
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    response.headers["Content-Security-Policy"] = (
        "default-src 'self'; "
        "script-src 'self' 'unsafe-inline'; "
        "style-src 'self' 'unsafe-inline'; "
        "img-src 'self' data:; "
        "font-src 'self'"
    )
    return response


# ── Rate Limiting ─────────────────────────────────────────
# Simple in-memory rate limiter — no external dependencies.
# Limits /api/submit to 10 requests per minute per IP.

_rate_limit_store = defaultdict(list)  # IP -> list of timestamps
RATE_LIMIT_MAX = 10      # max requests
RATE_LIMIT_WINDOW = 60   # per 60 seconds


def rate_limit(f):
    """Decorator: limit requests per IP address."""
    @wraps(f)
    def decorated(*args, **kwargs):
        ip = request.remote_addr or "unknown"
        now = time.time()
        # Clean old entries
        _rate_limit_store[ip] = [
            t for t in _rate_limit_store[ip]
            if now - t < RATE_LIMIT_WINDOW
        ]
        if len(_rate_limit_store[ip]) >= RATE_LIMIT_MAX:
            return jsonify({
                "error": "Rate limit exceeded. Please wait a minute before trying again."
            }), 429
        _rate_limit_store[ip].append(now)
        return f(*args, **kwargs)
    return decorated


# ── Error Handlers ────────────────────────────────────────

@app.errorhandler(404)
def page_not_found(e):
    """Custom 404 page."""
    return render_template("404.html"), 404


@app.errorhandler(500)
def internal_error(e):
    """Custom 500 page — no stack traces in production."""
    if IS_PRODUCTION:
        return render_template("500.html"), 500
    else:
        # In dev, let Flask show the debugger
        raise e


# ── Routes ────────────────────────────────────────────────

@app.route("/")
def index():
    """Landing page — starts fresh intake."""
    session.clear()
    return render_template("index.html")


@app.route("/intake")
def intake():
    """Main intake form — multi-step wizard."""
    return render_template("intake.html")


@app.route("/api/submit", methods=["POST"])
@rate_limit
def submit_intake():
    """
    Receive the completed intake JSON from the frontend,
    save it, fill the PDF, and return download links.
    """
    data = request.get_json()
    if not data:
        return jsonify({"error": "No data received"}), 400

    # Add metadata
    data["generated"] = datetime.now().strftime("%Y-%m-%d %H:%M")
    data["form"] = "Navajo County Petition to Establish Child Support"

    # Build filenames from party names
    pet_last = data.get("petitioner", {}).get("last_name", "Unknown").replace(" ", "_")
    resp_last = data.get("respondent", {}).get("last_name", "Unknown").replace(" ", "_")
    child_first = data.get("child", {}).get("first_name", "Child").replace(" ", "_")
    base_name = f"{pet_last}_vs_{resp_last}_{child_first}"

    # Save JSON
    json_path = os.path.join(OUTPUT_DIR, f"{base_name}_intake.json")
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    # Fill PDFs
    result = fill_petition_pdf(data, base_name)

    return jsonify({
        "success": True,
        "base_name": base_name,
        "json_file": os.path.basename(json_path),
        "pdf_editable": result.get("editable"),
        "pdf_filled": result.get("filled"),
        "validation": result.get("validation"),
        "fields_filled": result.get("count", 0),
        "warnings": result.get("warnings", []),
    })


@app.route("/api/download/<filename>")
def download_file(filename):
    """Serve a generated file for download."""
    # Sanitize filename to prevent directory traversal
    safe_name = os.path.basename(filename)
    filepath = os.path.join(OUTPUT_DIR, safe_name)
    if not os.path.exists(filepath):
        return jsonify({"error": "File not found"}), 404
    return send_file(filepath, as_attachment=True)


@app.route("/success")
def success():
    """Success page with download links."""
    return render_template("success.html")


@app.route("/health")
def health():
    """Health check endpoint for Cloud Run."""
    return jsonify({"status": "ok", "service": "themis-court-path"}), 200


# ── PDF Filling Engine ────────────────────────────────────
# (Identical to development version — no changes needed)

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

    resp_occupation = ""
    if employer_name and employment_type:
        type_labels = {"w2": "Employee", "1099": "Independent Contractor", "self": "Self-employed", "other": ""}
        resp_occupation = f"{employer_name} - {type_labels.get(employment_type, employment_type)}"
    elif employer_name:
        resp_occupation = employer_name

    pet_county = venue.get("county", "Navajo")

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

    rep_text = "Self"
    if pet.get("has_attorney"):
        rep_text = pet.get("attorney_name", "")

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

    child_gender_label = "Male" if child.get("gender") == "m" else "Female"

    child_addr = child.get("address", pet_addr)
    child_city_state = f"{child.get('city', pet.get('city', ''))}, {child.get('state', pet.get('state', ''))}"

    pet_employer_name = pet_emp.get("employer_name", "")
    pet_employment_type = pet_emp.get("employment_type", "")
    pet_occupation = ""
    if pet_employer_name and pet_employment_type:
        type_labels = {"w2": "Employee", "1099": "Independent Contractor", "self": "Self-employed", "other": ""}
        pet_occupation = f"{pet_employer_name} - {type_labels.get(pet_employment_type, '')}".strip(" -")
    elif pet_employer_name:
        pet_occupation = pet_employer_name

    support_payor = support.get("payor", "resp")

    # ── TEXT FIELDS ──
    text_fields = {}

    if pet_full:
        text_fields["Name of Person Filing 1"] = pet_full
        text_fields["Name of Person Filing 2"] = pet.get("email", "")
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

    if pet.get("phone"):
        text_fields["Telephone Number"] = pet["phone"]
        text_fields["Telephone Numbers"] = pet["phone"]
        text_fields["Daytime Telephone Numbers"] = pet["phone"]
    if pet.get("email"):
        text_fields["Email Address"] = pet["email"]

    # PAGE 4 — Sensitive Data Sheet
    if pet_dob:
        text_fields["Date of Birth MonthDayYear 1"] = pet_dob
    if resp_dob:
        text_fields["1"] = resp_dob

    if pet.get("ssn"):
        text_fields["Date of Birth MonthDayYear 2"] = pet["ssn"]
    if resp.get("ssn"):
        text_fields["2"] = resp["ssn"]

    if pet.get("dl_number"):
        text_fields["Drivers License Number"] = pet["dl_number"]
    if resp.get("dl_number"):
        text_fields["3"] = resp["dl_number"]

    if pet_addr:
        text_fields["REQUESTING ADDRESS PROTECTION 1"] = pet_addr
    if pet_csz.strip(", "):
        text_fields["REQUESTING ADDRESS PROTECTION 2"] = pet_csz
    if resp_addr:
        text_fields["1_2"] = resp_addr
    if resp_csz.strip(", "):
        text_fields["2_2"] = resp_csz

    if pet.get("phone"):
        text_fields["REQUESTING ADDRESS PROTECTION 3"] = pet["phone"]
    if resp.get("phone"):
        text_fields["3_2"] = resp["phone"]

    if pet.get("email"):
        text_fields["REQUESTING ADDRESS PROTECTION 4"] = pet["email"]
    if resp.get("email"):
        text_fields["4"] = resp["email"]

    if pet_employer_name:
        text_fields["REQUESTING ADDRESS PROTECTION 5"] = pet_employer_name
    if employer_name:
        text_fields["5"] = employer_name

    if employer_addr:
        text_fields["6"] = employer_addr

    if employer_name and (employer_city or employer_state or employer_zip):
        text_fields["7"] = ", ".join([employer_city, f"{employer_state} {employer_zip}".strip()]).strip(", ") if employer_city else f"{employer_state} {employer_zip}".strip()
    if pet_employer_name:
        text_fields["Employer City State Zip Code"] = ""

    # PAGE 5 — Child Info
    if child_full:
        text_fields["Child NameRow1"] = child_full
    if child_gender_label:
        text_fields["Gender Child Social Security Number Child Date of BirthRow1"] = child_gender_label
    if child_dob:
        text_fields["Child Date of Birth 1"] = child_dob
    if child.get("ssn"):
        text_fields["Child Social Security Number 1"] = child["ssn"]

    # PAGE 6 — Cover Sheet
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

    # PAGE 8
    if child_full and child_dob:
        text_fields["DATE OF BIRTH 1"] = f"{child_full}    {child_dob}"

    # PAGES 9-13 — Petition
    if pet_addr and pet_csz.strip(", "):
        text_fields["Address"] = f"{pet_addr}, {pet_csz}"
    if pet_county:
        text_fields["County of Residence"] = pet_county
    if pet_dob:
        text_fields["Date of Birth"] = pet_dob
    if pet_occupation:
        text_fields["Occupation"] = pet_occupation

    if resp_addr and resp_csz.strip(", "):
        text_fields["Address_2"] = f"{resp_addr}, {resp_csz}"
    if resp_county:
        text_fields["County of Residence_2"] = resp_county
    if resp_dob:
        text_fields["Date of Birth_2"] = resp_dob
    if resp_occupation:
        text_fields["Occupation_2"] = resp_occupation

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

    if paternity_text:
        text_fields["stating that"] = paternity_text

    # PAGES 18-19 — Order to Appear
    if resp_full:
        text_fields["To 1"] = resp_full
    if resp_addr and resp_csz.strip(", "):
        text_fields["To 2"] = f"{resp_addr}, {resp_csz}"

    # PAGES 20-28 — Child Support Order
    if child_full:
        text_fields["Name 1"] = child_full
    if child_dob:
        text_fields["Date of Birth 1"] = child_dob

    if support_amount:
        text_fields["Respondent in the amount of"] = support_amount
        text_fields["Respondent in the amount of_2"] = support_amount
        text_fields["in the sum of"] = support_amount

        try:
            cs_amt = float(support_amount)
            clearinghouse_fee = 8.00
            total_monthly = cs_amt + clearinghouse_fee
            text_fields["payments to    Petitioner    Respondent of"] = f"{total_monthly:.2f}"
            text_fields["undefined_6"] = f"{cs_amt:.2f}"
            text_fields["undefined_9"] = f"{total_monthly:.2f}"
        except (ValueError, TypeError):
            pass

    if med_pet_pct:
        text_fields["be shared as follows Petitioner"] = med_pet_pct
    if med_resp_pct:
        text_fields["Respondent_4"] = med_resp_pct

    if med_pet_pct:
        text_fields["NONCOVERED MEDICAL EXPENSES    Petitioner is ordered to pay"] = med_pet_pct
    if med_resp_pct:
        text_fields["Respondent is ordered to pay"] = med_resp_pct

    # PAGE 26 — Tax Exemptions
    tax_option = options.get("tax_exemption_to", "")
    tax_rows = []
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

        tax_checkboxes_to_add = set()
        for i, (name_field, pet_cb, resp_cb, year_field) in enumerate(tax_rows):
            text_fields[name_field] = child_label
            text_fields[year_field] = str(current_year + i)

            if tax_option == "pet":
                tax_checkboxes_to_add.add(pet_cb)
            elif tax_option == "resp":
                tax_checkboxes_to_add.add(resp_cb)
            elif tax_option == "alt":
                if i % 2 == 0:
                    tax_checkboxes_to_add.add(pet_cb)
                else:
                    tax_checkboxes_to_add.add(resp_cb)
    else:
        tax_checkboxes_to_add = set()

    # PAGE 29 — Employer Info
    payor_name = resp_full if support_payor == "resp" else pet_full
    if payor_name:
        text_fields["OBLIGORPAYOR"] = payor_name

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
    checkboxes_uncheck = set()

    pet_role = rel.get("petitioner_role", "")
    resp_role = rel.get("respondent_role", "")

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

    if not pet.get("has_attorney"):
        checkboxes.add("Representing Self No Attorney")
    else:
        checkboxes.add("Represented by Attorney")

    if not rel.get("paternity_established"):
        checkboxes.add("PaternityMaternity")
    checkboxes.add("Establish Support")

    if pet_role == "mother":
        checkboxes.add("Check Box16")
    elif pet_role == "father":
        checkboxes.add("Check Box17")
    else:
        checkboxes.add("Check Box18")

    if resp_role == "mother":
        checkboxes.add("Check Box19")
    elif resp_role == "father":
        checkboxes.add("Check Box20")
    else:
        checkboxes.add("Check Box21")

    checkboxes.add("Check Box22")

    checkboxes.add("Check Box42")
    if support_payor == "pet":
        checkboxes.add("Check Box47")
        checkboxes.add("Check Box50")
    else:
        checkboxes.add("Check Box48")
        checkboxes.add("Check Box49")

    insurance_provider = support.get("who_provides_insurance", "")
    if insurance_provider == "pet":
        checkboxes.add("Check Box44")
        checkboxes.add("Check Box51")
        checkboxes.add("Check Box52")
        checkboxes.add("Check Box53")
    elif insurance_provider == "resp":
        checkboxes.add("Check Box45")
        checkboxes.add("Check Box54")
        checkboxes.add("Check Box55")
        checkboxes.add("Check Box56")
    checkboxes.add("Check Box46")

    checkboxes.add("Check Box57")
    if support_payor == "pet":
        checkboxes.add("Check Box58")
        checkboxes.add("Check Box61")
    else:
        checkboxes.add("Check Box59")
        checkboxes.add("Check Box60")

    checkboxes.add("Check Box62")
    if support_payor == "pet":
        checkboxes.add("Check Box66")
        checkboxes.add("Check Box75")
    else:
        checkboxes.add("Check Box67")
        checkboxes.add("Check Box74")

    if not arrears.get("requesting_past_support"):
        checkboxes.add("Check Box82")
        checkboxes.add("Check Box86")
        checkboxes.add("Check Box88")
        checkboxes.add("Check Box89")

    checkboxes.add("Check Box96")
    if support_payor == "pet":
        checkboxes.add("Check Box101")
        checkboxes.add("Check Box104")
    else:
        checkboxes.add("Check Box102")
        checkboxes.add("Check Box103")
    if not arrears.get("requesting_past_support"):
        checkboxes.add("Check Box100")

    checkboxes.add("No_8")

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

    for cb in tax_checkboxes_to_add:
        checkboxes.add(cb)

    if options.get("request_tax_exemption") and tax_option:
        checkboxes.add("Check Box145")
        if tax_option in ("pet", "alt"):
            checkboxes.add("Check Box146")
        if tax_option in ("resp", "alt"):
            checkboxes.add("Check Box147")

    checkboxes.add("Notification")

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

    legal = data.get("legal", {})
    paternity_method = legal.get("paternity_method", "")
    if paternity_method == "court_order":
        checkboxes.add("Check Box29")
    elif paternity_method == "acknowledgment":
        checkboxes.add("Check Box30")
    elif paternity_method == "married":
        checkboxes.add("Check Box31")

    if legal.get("no_current_order", True):
        checkboxes.add("Check Box32")
    if legal.get("voluntary_payments"):
        checkboxes.add("Check Box33")

    return text_fields, checkboxes, checkboxes_uncheck, radio_selections


def fill_worksheet_pages(doc, data):
    """Overlay text onto the static worksheet pages (15-17, 0-indexed 14-16)."""
    pet = data.get("petitioner", {})
    resp = data.get("respondent", {})
    child = data.get("child", {})
    ws = data.get("worksheet", {})
    support = data.get("support", {})
    venue = data.get("venue", {})
    rel = data.get("relationship", {})

    filled = []
    font = "helv"
    size = 10

    def put(page_idx, x, y, text, sz=None):
        if not text:
            return
        page = doc[page_idx]
        page.insert_text(
            fitz.Point(x, y), str(text),
            fontname=font, fontsize=sz or size, color=(0, 0, 0.4),
        )
        filled.append((page_idx + 1, f"Worksheet overlay ({x:.0f},{y:.0f})", str(text)))

    def put_check(page_idx, x, y):
        page = doc[page_idx]
        page.insert_text(
            fitz.Point(x, y), "X",
            fontname=font, fontsize=11, color=(0, 0, 0.4),
        )

    def dollar(val):
        if not val:
            return ""
        try:
            return f"{float(val):,.2f}"
        except (ValueError, TypeError):
            return str(val).replace("$", "")

    pet_role = rel.get("petitioner_role", "mother")

    def get_ws(key, default=""):
        return ws.get(key, default)

    FATHER_X = 400
    MOTHER_X = 497
    SINGLE_X = 434

    # PAGE 15 (index 14)
    put(14, 200, 80, pet.get("full_name", ""))
    put(14, 145, 98, pet.get("address", ""))
    put(14, 205, 116, f"{pet.get('city', '')}, {pet.get('state', '')} {pet.get('zip', '')}")
    put(14, 200, 135, pet.get("phone", ""))
    put(14, 88, 325, pet.get("full_name", ""))
    put(14, 88, 365, resp.get("full_name", ""))
    put(14, 200, 403, pet.get("full_name", ""))
    put(14, 165, 419, datetime.now().strftime("%m/%d/%Y"))
    put_check(14, 180, 438)

    time_sharing = get_ws("time_sharing", "")
    if time_sharing == "equal":
        put_check(14, 225, 454)
    elif time_sharing == "mostly_father":
        put_check(14, 343, 454)
    elif time_sharing == "mostly_mother":
        put_check(14, 460, 454)

    put(14, 242, 637, get_ws("num_minor_children", "1"))
    put(14, 438, 637, get_ws("num_children_over_12", "0"))

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

    income_type = get_ws("other_parent_income_type", "estimated")
    if income_type == "actual":
        put_check(14, 93, 685)
    elif income_type == "estimated":
        put_check(14, 93, 710)
    elif income_type == "attributed":
        put_check(14, 93, 736)

    # PAGE 16 (index 15)
    put(15, FATHER_X, 100, dollar(get_ws("father_gross_monthly")))
    put(15, MOTHER_X, 100, dollar(get_ws("mother_gross_monthly")))
    put(15, FATHER_X, 118, dollar(get_ws("father_spousal_paid", "0")))
    put(15, MOTHER_X, 118, dollar(get_ws("mother_spousal_paid", "0")))
    put(15, FATHER_X, 136, dollar(get_ws("father_spousal_received", "0")))
    put(15, MOTHER_X, 136, dollar(get_ws("mother_spousal_received", "0")))
    put(15, FATHER_X, 173, dollar(get_ws("father_other_children_deduct", "0")))
    put(15, MOTHER_X, 173, dollar(get_ws("mother_other_children_deduct", "0")))
    put(15, FATHER_X, 200, dollar(get_ws("father_other_cs_paid", "0")))
    put(15, MOTHER_X, 200, dollar(get_ws("mother_other_cs_paid", "0")))
    put(15, FATHER_X, 243, dollar(get_ws("father_other_nat_deduct", "0")))
    put(15, MOTHER_X, 243, dollar(get_ws("mother_other_nat_deduct", "0")))
    put(15, FATHER_X, 304, dollar(get_ws("father_adjusted_gross")))
    put(15, MOTHER_X, 304, dollar(get_ws("mother_adjusted_gross")))
    put(15, SINGLE_X, 322, dollar(get_ws("combined_adjusted_gross")))

    num_children = get_ws("num_minor_children", "1")
    put(15, 260, 340, num_children)
    put(15, SINGLE_X, 340, dollar(get_ws("basic_cs_obligation")))
    put(15, SINGLE_X, 375, dollar(get_ws("over_12_adjustment", "0")))

    put(15, FATHER_X, 393, dollar(get_ws("father_medical_insurance", "0")))
    put(15, MOTHER_X, 393, dollar(get_ws("mother_medical_insurance", "0")))
    put(15, FATHER_X, 410, dollar(get_ws("father_childcare", "0")))
    put(15, MOTHER_X, 410, dollar(get_ws("mother_childcare", "0")))
    put(15, FATHER_X, 445, dollar(get_ws("father_education", "0")))
    put(15, MOTHER_X, 445, dollar(get_ws("mother_education", "0")))
    put(15, FATHER_X, 475, dollar(get_ws("father_extraordinary", "0")))
    put(15, MOTHER_X, 475, dollar(get_ws("mother_extraordinary", "0")))
    put(15, FATHER_X, 490, dollar(get_ws("father_subtotal")))
    put(15, MOTHER_X, 490, dollar(get_ws("mother_subtotal")))
    put(15, SINGLE_X, 507, dollar(get_ws("total_adjustments")))
    put(15, SINGLE_X, 525, dollar(get_ws("total_cs_obligation")))

    put(15, FATHER_X, 548, get_ws("father_pct", "") + ("%" if get_ws("father_pct") else ""))
    put(15, MOTHER_X, 548, get_ws("mother_pct", "") + ("%" if get_ws("mother_pct") else ""))
    put(15, FATHER_X, 578, dollar(get_ws("father_share")))
    put(15, MOTHER_X, 578, dollar(get_ws("mother_share")))
    put(15, FATHER_X, 596, dollar(get_ws("father_less_costs")))
    put(15, MOTHER_X, 596, dollar(get_ws("mother_less_costs")))

    parenting_table = get_ws("parenting_table", "A")
    father_days = get_ws("father_overnights", "0")
    if parenting_table == "A":
        put_check(15, 365, 614)
    else:
        put_check(15, 445, 614)

    put(15, 150, 632, father_days)
    put(15, FATHER_X, 640, dollar(get_ws("father_parenting_time")))
    put(15, MOTHER_X, 640, dollar(get_ws("mother_parenting_time")))
    put(15, FATHER_X, 665, dollar(get_ws("father_adj_subtotal")))
    put(15, MOTHER_X, 665, dollar(get_ws("mother_adj_subtotal")))

    if get_ws("father_preliminary_cs"):
        put(15, FATHER_X, 683, dollar(get_ws("father_preliminary_cs")))
    if get_ws("mother_preliminary_cs"):
        put(15, MOTHER_X, 683, dollar(get_ws("mother_preliminary_cs")))

    # PAGE 17 (index 16)
    if get_ws("father_line16"):
        put(16, FATHER_X, 132, dollar(get_ws("father_line16")))
    if get_ws("mother_line16"):
        put(16, MOTHER_X, 132, dollar(get_ws("mother_line16")))
    if get_ws("father_less_arrears"):
        put(16, FATHER_X, 150, dollar(get_ws("father_less_arrears")))
    if get_ws("mother_less_arrears"):
        put(16, MOTHER_X, 150, dollar(get_ws("mother_less_arrears")))

    cs_paid_by = get_ws("cs_paid_by", "")
    if cs_paid_by == "father":
        put_check(16, 260, 206)
    elif cs_paid_by == "mother":
        put_check(16, 325, 206)

    if get_ws("father_cs_amount"):
        put(16, FATHER_X, 205, dollar(get_ws("father_cs_amount")))
    if get_ws("mother_cs_amount"):
        put(16, MOTHER_X, 205, dollar(get_ws("mother_cs_amount")))

    pet_travel = support.get("pet_travel_pct", "")
    resp_travel = support.get("resp_travel_pct", "")
    if pet_role in ("mother",):
        put(16, FATHER_X, 225, (resp_travel + "%" if resp_travel else ""))
        put(16, MOTHER_X, 225, (pet_travel + "%" if pet_travel else ""))
    else:
        put(16, FATHER_X, 225, (pet_travel + "%" if pet_travel else ""))
        put(16, MOTHER_X, 225, (resp_travel + "%" if resp_travel else ""))

    pet_med = support.get("pet_medical_pct", "")
    resp_med = support.get("resp_medical_pct", "")
    if pet_role in ("mother",):
        put(16, FATHER_X, 252, (resp_med + "%" if resp_med else ""))
        put(16, MOTHER_X, 252, (pet_med + "%" if pet_med else ""))
    else:
        put(16, FATHER_X, 252, (pet_med + "%" if pet_med else ""))
        put(16, MOTHER_X, 252, (resp_med + "%" if resp_med else ""))

    return filled


def fill_petition_pdf(data, base_name):
    """Fill the Petition PDF with intake data, including worksheet overlays."""
    warnings = []

    if not os.path.exists(SOURCE_PDF):
        return {
            "editable": None, "filled": None, "validation": None,
            "count": 0,
            "warnings": [f"Source PDF not found at: {SOURCE_PDF}"]
        }

    text_fields, checkboxes, checkboxes_uncheck, radio_selections = build_field_maps(data)

    editable_path = os.path.join(OUTPUT_DIR, f"{base_name}_COMPLETE_EDITABLE.pdf")
    filled_path = os.path.join(OUTPUT_DIR, f"{base_name}_COMPLETE_FILLED.pdf")
    validation_path = os.path.join(OUTPUT_DIR, f"{base_name}_Validation.txt")

    filled_fields = []

    def _fill_doc(doc, track_fields=False):
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
                    desired = radio_selections[fname]
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
                        widget.field_value = False
                        widget.update()

        ws_filled = fill_worksheet_pages(doc, data)
        if track_fields:
            filled_fields.extend(ws_filled)

    doc = fitz.open(SOURCE_PDF)
    _fill_doc(doc, track_fields=True)
    doc.save(editable_path)
    doc.close()

    doc2 = fitz.open(SOURCE_PDF)
    _fill_doc(doc2, track_fields=False)
    doc2.save(filled_path)
    doc2.close()

    generate_validation(data, filled_fields, validation_path)

    return {
        "editable": os.path.basename(editable_path),
        "filled": os.path.basename(filled_path),
        "validation": os.path.basename(validation_path),
        "count": len(filled_fields),
        "warnings": warnings,
    }


def generate_validation(data, filled_fields, filepath):
    """Write a validation note text file."""
    pet = data.get("petitioner", {})
    resp = data.get("respondent", {})
    child = data.get("child", {})
    support = data.get("support", {})

    v = []
    v.append("=" * 70)
    v.append("VALIDATION NOTE")
    v.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    v.append("Generated by: Themis Court Path — themiscourtpath.com")
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
    v.append("BEFORE FILING — PETITIONER MUST:")
    v.append("-" * 70)
    v.append("  1. Review ALL filled fields for accuracy")
    v.append("  2. Complete Parent's Worksheet with income data")
    v.append("  3. Fill any blank fields the clerk requires")
    v.append("  4. Sign and date the Petition")
    v.append("  5. File with the Clerk of Court")
    v.append("  6. Handle filing fee (pay, defer, or waive)")
    v.append("")
    v.append("=" * 70)
    v.append("END OF VALIDATION NOTE")
    v.append("=" * 70)

    with open(filepath, "w", encoding="utf-8") as f:
        f.write("\n".join(v))


# ── Run ───────────────────────────────────────────────────

if __name__ == "__main__":
    print()
    print("=" * 55)
    print("  Themis Court Path — Web Application")
    print("  Open Chrome and go to: http://localhost:5000")
    print("=" * 55)
    print()
    app.run(debug=True, port=5000)
