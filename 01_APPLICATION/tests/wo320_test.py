"""TCP-WO-320 E2E test runner. Covers the fee-disclosure flow end-to-end.

Tests both waiver=yes and waiver=no branches, verifies the DB column
persists, verifies payment is still required, verifies the validation
note surfaces the waiver reminder only when waiver=yes.
"""

import os
import sys
import sqlite3
from unittest.mock import patch, MagicMock

os.environ["FLASK_ENV"] = "development"
os.environ["SOURCE_PDF"] = "Petition_to_Establish_Child_Support.pdf"
os.environ["THEMIS_ENCRYPTION_KEY"] = ""
os.environ["STRIPE_SECRET_KEY"] = "sk_test_FAKE_KEY_FOR_TESTING"

sys.path.insert(0, ".")


def fake_session_create(**kwargs):
    s = MagicMock()
    s.id = "cs_test_FAKE_" + (kwargs.get("metadata", {}).get("filing_id", "X")[:8] or "X")
    s.url = "https://checkout.stripe.com/c/pay/" + s.id
    s.metadata = kwargs.get("metadata", {})
    return s


def make_fake_retrieve(payment_status="paid", metadata=None):
    def _retrieve(session_id):
        s = MagicMock()
        s.id = session_id
        s.payment_status = payment_status
        s.amount_total = 9900
        s.metadata = metadata or {}
        return s
    return _retrieve


def main():
    print("=== TCP-WO-320 E2E TEST (fee disclosure / waiver flow) ===\n")

    # Pre-clean DBs BEFORE importing app, so the app's init_*_db()
    # at import time sees a blank slate and creates the schema fresh.
    import auth as _auth_premod
    import storage as _storage_premod
    for p in [_auth_premod._get_db_path(), _storage_premod._get_db_path()]:
        if os.path.exists(p):
            os.remove(p)

    with patch("stripe.checkout.Session.create", side_effect=fake_session_create):
        from app import app
        import storage, auth
        client = app.test_client()

        # --- Verify schema migration ---
        conn = sqlite3.connect(storage._get_db_path())
        cols = {r[1] for r in conn.execute("PRAGMA table_info(filings)").fetchall()}
        conn.close()
        print(f"1. Schema cols: {sorted(cols)}")
        assert "fee_waiver_requested" in cols, "fee_waiver_requested column missing"
        print("   fee_waiver_requested column present: OK")

        # --- Register two users ---
        r = client.post("/auth/register", data={"email": "wavyes@example.com", "password": "WavYesPass1234!"})
        assert r.status_code == 302
        print("2. User A (waiver=yes) registered: OK")

        # --- Submit intake WITH fee_waiver_requested=yes ---
        sample_yes = {
            "petitioner": {"first_name": "Al", "last_name": "Payer", "full_name": "Al Payer"},
            "respondent": {"first_name": "Bo", "last_name": "Other", "full_name": "Bo Other"},
            "child": {"first_name": "Cy", "last_name": "Kid", "full_name": "Cy Kid"},
            "support": {"monthly_amount": "500"},
            "fee_waiver_requested": "yes",
        }
        r = client.post("/api/submit", json=sample_yes)
        assert r.status_code == 200, f"submit failed: {r.status_code} {r.data}"
        filing_yes = r.get_json()["filing_id"]
        print(f"3. Submit (waiver=yes): filing_id={filing_yes}")

        # --- Verify DB has fee_waiver_requested='yes' AND column is plaintext ---
        conn = sqlite3.connect(storage._get_db_path())
        row = conn.execute(
            "SELECT fee_waiver_requested, encrypted_payload FROM filings WHERE id=?",
            (filing_yes,),
        ).fetchone()
        conn.close()
        print(f"4. DB row waiver flag: {row[0]!r}")
        assert row[0] == "yes", "waiver flag did not persist as 'yes'"
        print(f"   encrypted_payload does NOT contain 'fee_waiver_requested': {('fee_waiver_requested' not in row[1])}")
        assert "fee_waiver_requested" not in row[1], "flag leaked into encrypted payload!"
        print("   flag is plaintext column only, not in encrypted payload: OK")

        # --- Payment still required (download should 403) ---
        r = client.get(f"/api/download/{filing_yes}/filled")
        print(f"5. Download before payment: {r.status_code} (expect 403)")
        assert r.status_code == 403

        # --- Complete checkout via Stripe mock ---
        real_user_yes = sqlite3.connect(storage._get_db_path()).execute(
            "SELECT user_id FROM filings WHERE id=?", (filing_yes,)
        ).fetchone()[0]

        r = client.post("/api/create-checkout-session", json={"filing_id": filing_yes})
        assert r.status_code == 200
        print(f"6. Checkout URL returned: {r.get_json()['checkout_url'][:60]}...")

        fake_retrieve_paid = make_fake_retrieve(
            payment_status="paid",
            metadata={"filing_id": filing_yes, "user_id": real_user_yes},
        )
        with patch("stripe.checkout.Session.retrieve", side_effect=fake_retrieve_paid):
            r = client.get(f"/success?session_id=cs_test_FAKE_{filing_yes[:8]}")
            assert r.status_code == 200
            print(f"7. /success verified payment: OK")

        # --- Download validation - should contain waiver reminder ---
        r = client.get(f"/api/download/{filing_yes}/validation")
        print(f"8. Download validation (waiver=yes): {r.status_code} {len(r.data)} bytes")
        assert r.status_code == 200
        body = r.data.decode("utf-8")
        assert "COURT FILING FEE WAIVER" in body, "Waiver section missing from validation note!"
        assert "User indicated intent to apply for court fee waiver" in body
        assert "Include fee waiver application when filing" in body
        print("   validation note contains COURT FILING FEE WAIVER section: OK")
        print("   validation note contains 'Include fee waiver application when filing': OK")

        # --- Now test waiver=no as a different user ---
        client.get("/auth/logout")
        client2 = app.test_client()
        r = client2.post("/auth/register", data={"email": "wavno@example.com", "password": "WavNoPass1234!"})
        assert r.status_code == 302
        print("\n9. User B (waiver=no) registered: OK")

        sample_no = dict(sample_yes, fee_waiver_requested="no")
        r = client2.post("/api/submit", json=sample_no)
        assert r.status_code == 200
        filing_no = r.get_json()["filing_id"]
        print(f"10. Submit (waiver=no): filing_id={filing_no}")

        conn = sqlite3.connect(storage._get_db_path())
        row = conn.execute(
            "SELECT fee_waiver_requested FROM filings WHERE id=?", (filing_no,)
        ).fetchone()
        conn.close()
        print(f"11. DB row waiver flag: {row[0]!r}")
        assert row[0] == "no"

        # --- Pay + download validation - should NOT contain waiver reminder ---
        real_user_no = sqlite3.connect(storage._get_db_path()).execute(
            "SELECT user_id FROM filings WHERE id=?", (filing_no,)
        ).fetchone()[0]
        r = client2.post("/api/create-checkout-session", json={"filing_id": filing_no})
        assert r.status_code == 200
        fake_retrieve_paid_no = make_fake_retrieve(
            payment_status="paid",
            metadata={"filing_id": filing_no, "user_id": real_user_no},
        )
        with patch("stripe.checkout.Session.retrieve", side_effect=fake_retrieve_paid_no):
            r = client2.get(f"/success?session_id=cs_test_FAKE_{filing_no[:8]}")
            assert r.status_code == 200

        r = client2.get(f"/api/download/{filing_no}/validation")
        assert r.status_code == 200
        body_no = r.data.decode("utf-8")
        print(f"12. Download validation (waiver=no): {r.status_code} {len(r.data)} bytes")
        assert "COURT FILING FEE WAIVER" not in body_no, "Waiver section INCORRECTLY present when waiver=no"
        assert "Include fee waiver application" not in body_no
        print("   validation note does NOT contain waiver section: OK")

        # --- Invalid waiver value defaults to 'no' ---
        client2.get("/auth/logout")
        client3 = app.test_client()
        client3.post("/auth/register", data={"email": "wavbad@example.com", "password": "WavBadPass1234!"})
        sample_bad = dict(sample_yes, fee_waiver_requested="maybe")
        r = client3.post("/api/submit", json=sample_bad)
        assert r.status_code == 200
        filing_bad = r.get_json()["filing_id"]
        conn = sqlite3.connect(storage._get_db_path())
        row = conn.execute(
            "SELECT fee_waiver_requested FROM filings WHERE id=?", (filing_bad,)
        ).fetchone()
        conn.close()
        print(f"\n13. Invalid waiver value 'maybe' coerced to: {row[0]!r}")
        assert row[0] == "no"

        # --- Omitted field defaults to 'no' ---
        client3.get("/auth/logout")
        client4 = app.test_client()
        client4.post("/auth/register", data={"email": "wavomit@example.com", "password": "WavOmitPass1234!"})
        sample_omit = {
            "petitioner": {"first_name": "X", "last_name": "Y", "full_name": "X Y"},
            "respondent": {"first_name": "A", "last_name": "B", "full_name": "A B"},
            "child": {"first_name": "M", "last_name": "N", "full_name": "M N"},
        }
        r = client4.post("/api/submit", json=sample_omit)
        assert r.status_code == 200
        filing_omit = r.get_json()["filing_id"]
        conn = sqlite3.connect(storage._get_db_path())
        row = conn.execute(
            "SELECT fee_waiver_requested FROM filings WHERE id=?", (filing_omit,)
        ).fetchone()
        conn.close()
        print(f"14. Omitted waiver field defaulted to: {row[0]!r}")
        assert row[0] == "no"

        # --- Stripe pricing unchanged ($9900 cents) ---
        client4.get("/auth/logout")
        client5 = app.test_client()
        client5.post("/auth/register", data={"email": "pricechk@example.com", "password": "PriceChk1234!"})
        sample5 = dict(sample_yes)
        r = client5.post("/api/submit", json=sample5)
        filing_5 = r.get_json()["filing_id"]
        captured = {}
        def capture_create(**kwargs):
            captured.update(kwargs)
            return fake_session_create(**kwargs)
        with patch("stripe.checkout.Session.create", side_effect=capture_create):
            client5.post("/api/create-checkout-session", json={"filing_id": filing_5})
        amount = captured.get("line_items", [{}])[0].get("price_data", {}).get("unit_amount")
        print(f"\n15. Stripe unit_amount on checkout create: {amount} (expect 9900)")
        assert amount == 9900, f"Stripe pricing changed! Got {amount}"

    # Cleanup
    for p in [auth._get_db_path(), storage._get_db_path()]:
        if os.path.exists(p):
            os.remove(p)

    print("\n=== ALL 15 TCP-WO-320 E2E CHECKS PASSED ===")


if __name__ == "__main__":
    main()
