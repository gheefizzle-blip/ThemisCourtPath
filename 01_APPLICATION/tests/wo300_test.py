"""TCP-WO-300 E2E test runner. Mocks Stripe; exercises full payment flow."""

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
    s.id = "cs_test_FAKE_SESSION_001"
    s.url = "https://checkout.stripe.com/c/pay/cs_test_FAKE_SESSION_001"
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
    print("=== TCP-WO-300 E2E TEST ===\n")

    with patch("stripe.checkout.Session.create", side_effect=fake_session_create):
        from app import app
        import storage, auth
        client = app.test_client()

        # 1. Register
        r = client.post("/auth/register", data={"email": "pay@example.com", "password": "PayTestPass1234!"})
        print(f"1. Register: {r.status_code} (expect 302)")
        assert r.status_code == 302

        # 2. Submit intake
        sample = {
            "petitioner": {"first_name": "Alex", "last_name": "Petitioner", "full_name": "Alex Petitioner"},
            "respondent": {"first_name": "Bob",  "last_name": "Respondent", "full_name": "Bob Respondent"},
            "child":      {"first_name": "Cam",  "last_name": "Childname",  "full_name": "Cam Childname"},
            "support": {"monthly_amount": "500"},
        }
        r = client.post("/api/submit", json=sample)
        filing_id = r.get_json()["filing_id"]
        print(f"2. Submit: {r.status_code} filing_id={filing_id}")
        assert r.status_code == 200

        # 3. Try download BEFORE payment
        r = client.get(f"/api/download/{filing_id}/filled")
        print(f"3. Download before payment: {r.status_code} (expect 403)")
        assert r.status_code == 403
        body = r.get_json()
        assert body["payment_status"] == "pending"

        # 4. Create checkout session
        r = client.post("/api/create-checkout-session", json={"filing_id": filing_id})
        print(f"4. Create checkout: {r.status_code}")
        assert r.status_code == 200
        checkout_url = r.get_json()["checkout_url"]
        print(f"   checkout_url: {checkout_url}")
        assert "cs_test_FAKE_SESSION_001" in checkout_url

        # 5. Verify session stored
        conn = sqlite3.connect(storage._get_db_path())
        row = conn.execute("SELECT stripe_session_id, payment_status, user_id FROM filings WHERE id=?", (filing_id,)).fetchone()
        conn.close()
        print(f"5. DB after checkout: stripe_session_id={row[0]}, payment_status={row[1]}")
        assert row[0] == "cs_test_FAKE_SESSION_001"
        assert row[1] == "pending"
        real_user_id = row[2]

        # 6. Download still 403 before confirmation
        r = client.get(f"/api/download/{filing_id}/filled")
        print(f"6. Download after checkout (not confirmed): {r.status_code} (expect 403)")
        assert r.status_code == 403

        # 7. Simulate Stripe redirect with paid session
        fake_retrieve_paid = make_fake_retrieve(
            payment_status="paid",
            metadata={"filing_id": filing_id, "user_id": real_user_id},
        )
        with patch("stripe.checkout.Session.retrieve", side_effect=fake_retrieve_paid):
            r = client.get("/success?session_id=cs_test_FAKE_SESSION_001")
            print(f"7. /success?session_id=...: {r.status_code}")
            assert r.status_code == 200
            body = r.data.decode()
            assert "Payment received" in body
            assert filing_id in body

        # 8. DB shows paid
        conn = sqlite3.connect(storage._get_db_path())
        row = conn.execute("SELECT payment_status FROM filings WHERE id=?", (filing_id,)).fetchone()
        conn.close()
        print(f"8. DB after /success: payment_status={row[0]} (expect paid)")
        assert row[0] == "paid"

        # 9. Download after payment
        r = client.get(f"/api/download/{filing_id}/filled")
        print(f"9. Download after payment: {r.status_code} {r.mimetype} {len(r.data)} bytes")
        assert r.status_code == 200
        assert r.mimetype == "application/pdf"
        assert r.data[:4] == b"%PDF"
        r = client.get(f"/api/download/{filing_id}/editable")
        print(f"   editable:   {r.status_code} {len(r.data)} bytes")
        assert r.status_code == 200
        r = client.get(f"/api/download/{filing_id}/validation")
        print(f"   validation: {r.status_code} {len(r.data)} bytes")
        assert r.status_code == 200

        # 10. Cross-user denied
        client.get("/auth/logout")
        other = app.test_client()
        other.post("/auth/register", data={"email": "attacker@example.com", "password": "Attacker12345!"})
        r = other.get(f"/api/download/{filing_id}/filled")
        print(f"10. Cross-user download (paid filing): {r.status_code} (expect 404)")
        assert r.status_code == 404

        # 11. Mismatched session metadata
        client.get("/auth/logout")
        client2 = app.test_client()
        client2.post("/auth/register", data={"email": "unrelated@example.com", "password": "Unrelated12345!"})
        fake_retrieve_other = make_fake_retrieve(
            payment_status="paid",
            metadata={"filing_id": filing_id, "user_id": real_user_id},
        )
        with patch("stripe.checkout.Session.retrieve", side_effect=fake_retrieve_other):
            r = client2.get("/success?session_id=cs_test_FAKE_SESSION_999")
            body = r.data.decode()
            print(f"11. Other user opens /success: {r.status_code}, banner present: {'does not belong' in body}")
            assert "does not belong to this account" in body

        # 12. Anon download
        anon = app.test_client()
        r = anon.get(f"/api/download/{filing_id}/filled")
        print(f"12. Anon download: {r.status_code} (expect 401 or 302)")
        assert r.status_code in (401, 302)

        # 13. Anon checkout creation
        r = anon.post("/api/create-checkout-session", json={"filing_id": filing_id})
        print(f"13. Anon checkout: {r.status_code} (expect 401 or 302)")
        assert r.status_code in (401, 302)

        # 14. Stripe NOT configured returns 503
        anon2 = app.test_client()
        anon2.post("/auth/register", data={"email": "noStripe@example.com", "password": "NoStripe12345!"})
        with patch("payments.is_configured", return_value=False):
            r = anon2.post("/api/create-checkout-session", json={"filing_id": filing_id})
            print(f"14. Stripe not configured: {r.status_code} (expect 503)")
            assert r.status_code == 503

    # Cleanup
    for p in [auth._get_db_path(), storage._get_db_path()]:
        if os.path.exists(p):
            os.remove(p)

    print("\n=== ALL 14 PAYMENT E2E CHECKS PASSED ===")


if __name__ == "__main__":
    main()
