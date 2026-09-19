#!/usr/bin/env python3
"""
Phase 2 Comprehensive Automated Verification Suite for RelayCX:
"Client-Aware Ticket Context & Structured Ticket References"

Evaluates all 11 real-data and evaluator edge criteria defined in the implementation plan:
1. Canonical Seed Dataset Integrity (7 tickets, 18 notes, structured TKT-{CLIENT}-{ISSUE}-{SEQ:04d}).
2. Priya Nair (Aura D2C) - ANA Relevance Suppression (HTTP 204 suppresses ecommerce face cream order).
3. Priya Nair - Issue Correction Workflow (PATCH to ORD reveals cream order; ticket_id & intake_issue_type immutable).
4. Dev Malhotra (Nova Audio) - Technical Account Ingress Context (INT returns SUB-DEV-902; ORD returns 204).
5. Rohan Kapoor - Strict Cross-Client Isolation (UrbanFit Joggers vs Nova Audio Speakers vs Aura D2C zero leakage).
6. Customer History Panel Audit (Single-brand isolation, ticket self-exclusion, zero cross-brand contamination).
7. Structured Reference Invariance Across All State Machine Transitions (Open -> In Progress -> Closed -> Open).
8. Sequence Allocation Preservation After Classification Correction (Monotonic incrementing, no sequence collision).
9. Dynamic Client Code Derivation & Collision Safety for Unknown Brands (e.g. ZEP vs ZE1).
10. Weighted Classifier Scorer on Complex Multi-Keyword Evaluator Prompts (INT vs PAY, ACC vs PAY, ANA vs ORD).
11. Defensive Boundaries & HTTP Error Codes (422 on invalid taxonomy, 404 on missing tickets, 204 on unknown records).

Usage:
    cd backend && ../.venv/bin/python tests/verify_phase2.py
    or from root: python verify_phase2.py
"""

import os
import re
import sys
from urllib.parse import quote
from fastapi.testclient import TestClient

# Ensure backend directory is in sys.path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from app.database import Base, engine, SessionLocal
from app.models import Ticket, Note
from app.main import app
from app.service import classify_issue
from seed import seed_database


def run_phase2_verification():
    print("=" * 76)
    print("STARTING PHASE 2 AUTOMATED VERIFICATION SUITE: CLIENT-AWARE CONTEXT & REFS")
    print("=" * 76)

    try:
        # Step 0: Ensure fresh canonical dataset
        print("\n[SETUP] Initializing canonical demo dataset...")
        seed_database()
        client = TestClient(app)
        print("PASS: Canonical dataset loaded.")

        # ---------------------------------------------------------------------
        # CHECK 1: Seeded Canonical Dataset Integrity
        # ---------------------------------------------------------------------
        print("\n[CHECK 1] Verifying Seeded Canonical Dataset Integrity & Structured References...")
        with SessionLocal() as db:
            tickets = db.query(Ticket).all()
            notes = db.query(Note).all()

            assert len(tickets) == 7, f"Expected 7 tickets, got {len(tickets)}"
            assert len(notes) == 18, f"Expected 18 notes, got {len(notes)}"

            ref_regex = re.compile(r"^TKT-[A-Z]{3}-[A-Z]{3}-\d{4}$")
            for t in tickets:
                assert ref_regex.match(t.ticket_id), f"Ticket ID {t.ticket_id} format mismatch"
                assert t.intake_issue_type in {"ORD", "PAY", "ACC", "TEC", "INT", "ANA", "PRD", "GEN"}
                assert t.issue_type in {"ORD", "PAY", "ACC", "TEC", "INT", "ANA", "PRD", "GEN"}
                assert t.ticket_sequence >= 1
        print("PASS: All 7 tickets and 18 notes verified with valid structured IDs (TKT-{CLIENT}-{ISSUE}-{SEQ:04d}).")

        # ---------------------------------------------------------------------
        # CHECK 2: Priya Nair Relevance Suppression (ANA Ticket)
        # ---------------------------------------------------------------------
        print("\n[CHECK 2] Testing Priya Nair (Aura D2C) Domain Relevance Suppression...")
        # Priya has ticket TKT-AUR-ANA-0001 (Analytics). She also has cream order ORD-3918.
        # When queried with issue_type=ANA, cream order MUST be suppressed (HTTP 204 No Content).
        resp = client.get(
            f"/api/customers/{quote('Aura D2C')}/{quote('priya.nair@datalens.ai')}/context?issue_type=ANA"
        )
        assert resp.status_code == 204, f"Expected 204 No Content for ANA issue, got {resp.status_code}"
        assert resp.text == "", "HTTP 204 response body must be empty"
        print("PASS: Irrelevant ecommerce order ORD-3918 cleanly suppressed for analytics ticket (HTTP 204 No Content).")

        # ---------------------------------------------------------------------
        # CHECK 3: Priya Nair Issue Correction Lifecycle
        # ---------------------------------------------------------------------
        print("\n[CHECK 3] Testing Issue Correction Lifecycle (PATCH issue-type -> context dynamically revealed)...")
        ticket_id = "TKT-AUR-ANA-0001"

        # 3a. Correct issue_type to ORD
        patch_resp = client.patch(f"/api/tickets/{ticket_id}/issue-type", json={"issue_type": "ORD"})
        assert patch_resp.status_code == 200, f"PATCH failed: {patch_resp.text}"
        pdata = patch_resp.json()
        assert pdata["ticket_id"] == ticket_id, "ticket_id MUST remain strictly immutable"
        assert pdata["intake_issue_type"] == "ANA", "intake_issue_type MUST remain strictly immutable"
        assert pdata["issue_type"] == "ORD", "issue_type must update to ORD"

        # 3b. Query context with ORD now reveals cream order
        context_ord = client.get(
            f"/api/customers/{quote('Aura D2C')}/{quote('priya.nair@datalens.ai')}/context?issue_type=ORD"
        )
        assert context_ord.status_code == 200, f"Expected 200 for ORD issue, got {context_ord.status_code}"
        cord_data = context_ord.json()
        assert cord_data["order_id"] == "ORD-3918"
        assert cord_data["item_name"] == "Aura Luxury Botanical Restorative Cream Duo"
        assert cord_data["total_amount"] == "₹3,199"

        # 3c. Revert classification back to ANA
        revert_resp = client.patch(f"/api/tickets/{ticket_id}/issue-type", json={"issue_type": "ANA"})
        assert revert_resp.status_code == 200
        assert revert_resp.json()["issue_type"] == "ANA"

        # 3d. Verify context suppressed again
        context_ana_revert = client.get(
            f"/api/customers/{quote('Aura D2C')}/{quote('priya.nair@datalens.ai')}/context?issue_type=ANA"
        )
        assert context_ana_revert.status_code == 204
        print("PASS: Issue correction dynamically updates relevant context while keeping ticket_id and intake_issue_type immutable.")

        # ---------------------------------------------------------------------
        # CHECK 4: Dev Malhotra Developer Account Ingress Context
        # ---------------------------------------------------------------------
        print("\n[CHECK 4] Testing Dev Malhotra (Nova Audio) Technical Developer Context...")
        # INT query returns SUB-DEV-902
        dev_int = client.get(
            f"/api/customers/{quote('Nova Audio')}/{quote('dev.malhotra@hypergrid.net')}/context?issue_type=INT"
        )
        assert dev_int.status_code == 200
        dev_data = dev_int.json()
        assert dev_data["order_id"] == "SUB-DEV-902"
        assert dev_data["account_type"] == "developer"
        assert "Rate Limit Throttled" in dev_data["shipping_status"]
        assert "Backlog: 120k events" in dev_data["estimated_delivery"]
        assert dev_data["technical_details"]["quota"] == "5,000,000 req/mo"

        # ORD query returns 204 (developer account is irrelevant for ecommerce order issues)
        dev_ord = client.get(
            f"/api/customers/{quote('Nova Audio')}/{quote('dev.malhotra@hypergrid.net')}/context?issue_type=ORD"
        )
        assert dev_ord.status_code == 204
        print("PASS: Developer API account SUB-DEV-902 returned for INT; suppressed for ORD (HTTP 204).")

        # ---------------------------------------------------------------------
        # CHECK 5: Rohan Kapoor Strict Cross-Client Isolation
        # ---------------------------------------------------------------------
        print("\n[CHECK 5] Testing Rohan Kapoor Multi-Brand Cross-Client Isolation...")
        email = "rohan.kapoor@novabanking.com"

        # UrbanFit with ACC: 204 (2FA lockout suppresses shipment)
        uf_acc = client.get(f"/api/customers/{quote('UrbanFit')}/{quote(email)}/context?issue_type=ACC")
        assert uf_acc.status_code == 204

        # UrbanFit with ORD: Returns Training Joggers ORD-6104
        uf_ord = client.get(f"/api/customers/{quote('UrbanFit')}/{quote(email)}/context?issue_type=ORD")
        assert uf_ord.status_code == 200
        assert uf_ord.json()["order_id"] == "ORD-6104"
        assert uf_ord.json()["item_name"] == "UrbanFit AeroDry Training Joggers (Charcoal / M)"
        assert "Nova Studio Monitor Speakers" not in str(uf_ord.json())

        # Nova Audio with ORD: Returns Studio Monitor Speakers ORD-5520
        nov_ord = client.get(f"/api/customers/{quote('Nova Audio')}/{quote(email)}/context?issue_type=ORD")
        assert nov_ord.status_code == 200
        assert nov_ord.json()["order_id"] == "ORD-5520"
        assert nov_ord.json()["item_name"] == "Nova Studio Monitor Speakers (Pair)"
        assert "UrbanFit AeroDry Training Joggers" not in str(nov_ord.json())

        # Aura D2C with ORD: 204 (Zero cross-client leakage)
        aur_ord = client.get(f"/api/customers/{quote('Aura D2C')}/{quote(email)}/context?issue_type=ORD")
        assert aur_ord.status_code == 204
        print("PASS: Cross-client isolation verified: UrbanFit (ORD-6104) and Nova Audio (ORD-5520) strictly isolated; Aura D2C returns 204.")

        # ---------------------------------------------------------------------
        # CHECK 6: Customer History Audit Panel
        # ---------------------------------------------------------------------
        print("\n[CHECK 6] Testing Customer History Panel Scoping & Exclusion...")
        # UrbanFit history for Rohan without exclusion -> 1 prior ticket
        h_all = client.get(f"/api/tickets/customer-history?client_brand=UrbanFit&customer_email={quote(email)}").json()
        assert len(h_all) == 1
        assert h_all[0]["ticket_id"] == "TKT-URB-ACC-0001"

        # UrbanFit history with self-exclusion -> 0 tickets
        h_excl = client.get(
            f"/api/tickets/customer-history?client_brand=UrbanFit&customer_email={quote(email)}&exclude_ticket_id=TKT-URB-ACC-0001"
        ).json()
        assert len(h_excl) == 0

        # Nova Audio history -> 0 tickets (UrbanFit tickets never appear under Nova Audio)
        h_nov = client.get(
            f"/api/tickets/customer-history?client_brand=Nova%20Audio&customer_email={quote(email)}"
        ).json()
        assert len(h_nov) == 0
        print("PASS: Customer history strictly scoped to brand domain with valid ticket self-exclusion.")

        # ---------------------------------------------------------------------
        # CHECK 7: Reference Stability Across All State Machine Transitions
        # ---------------------------------------------------------------------
        print("\n[CHECK 7] Testing Reference Stability Across All Lifecycle Transitions...")
        test_ticket = client.post("/api/tickets", json={
            "customer_name": "State Tester",
            "customer_email": "state.tester@example.com",
            "subject": "Payment processed twice on card",
            "description": "Double charge on checkout.",
            "client_brand": "UrbanFit"
        }).json()
        t_id = test_ticket["ticket_id"]
        t_intake = test_ticket["intake_issue_type"]
        t_seq = test_ticket["ticket_sequence"]
        assert test_ticket["status"] == "Open"

        # Note -> In Progress
        r_note = client.put(f"/api/tickets/{t_id}", json={"note_text": "Investigating logs."}).json()
        assert r_note["status"] == "In Progress"
        assert r_note["ticket_id"] == t_id

        # Resolve -> Closed
        r_close = client.put(f"/api/tickets/{t_id}", json={"status": "Closed", "note_text": "Refunded."}).json()
        assert r_close["status"] == "Closed"
        assert r_close["ticket_id"] == t_id

        # Reopen -> Open
        r_open = client.put(f"/api/tickets/{t_id}", json={"status": "Open"}).json()
        assert r_open["status"] == "Open"
        assert r_open["ticket_id"] == t_id

        # Final detail check
        detail = client.get(f"/api/tickets/{t_id}").json()
        assert detail["ticket_id"] == t_id, "ticket_id must be completely invariant"
        assert detail["intake_issue_type"] == t_intake, "intake_issue_type must be invariant"
        assert detail["ticket_sequence"] == t_seq, "ticket_sequence must be invariant"
        print("PASS: Reference, intake family, and sequence invariant through Open -> In Progress -> Closed -> Open.")

        # ---------------------------------------------------------------------
        # CHECK 8: Sequence Preservation After Issue Correction
        # ---------------------------------------------------------------------
        print("\n[CHECK 8] Testing Sequence Preservation After Issue Correction...")
        # Correct current issue_type of TKT-AUR-ANA-0001 to ORD
        client.patch("/api/tickets/TKT-AUR-ANA-0001/issue-type", json={"issue_type": "ORD"})

        # Now create new ticket for Aura D2C that classifies as ANA
        new_ana = client.post("/api/tickets", json={
            "customer_name": "New Analytics User",
            "customer_email": "new.analytics@datalens.ai",
            "subject": "CSV export timeout in dashboard reporting",
            "description": "Lambda timeout error.",
            "client_brand": "Aura D2C"
        }).json()
        assert new_ana["intake_issue_type"] == "ANA"
        assert new_ana["ticket_sequence"] == 2, f"Expected sequence 2, got {new_ana['ticket_sequence']}"
        assert new_ana["ticket_id"] == "TKT-AUR-ANA-0002"

        # Revert TKT-AUR-ANA-0001 back to ANA
        client.patch("/api/tickets/TKT-AUR-ANA-0001/issue-type", json={"issue_type": "ANA"})
        print("PASS: Sequence preserved: TKT-AUR-ANA-0002 generated without collisions after correction.")

        # ---------------------------------------------------------------------
        # CHECK 9: Dynamic Client Code Generation & Collision Safety
        # ---------------------------------------------------------------------
        print("\n[CHECK 9] Testing Dynamic Client Code Generation & Collision Safety...")
        # Unknown brand 1: 'Quantum Cloud' -> 'QUA'
        q1 = client.post("/api/tickets", json={
            "customer_name": "Quinn",
            "customer_email": "quinn@quantumcloud.net",
            "subject": "Delivery tracking delay",
            "description": "Package order delivery.",
            "client_brand": "Quantum Cloud"
        }).json()
        assert q1["ticket_id"].startswith("TKT-QUA-ORD-0001"), f"Expected TKT-QUA-ORD-0001, got {q1['ticket_id']}"

        # Unknown brand 2: 'Quantum Corp' (first 3 chars 'QUA' collides) -> derives 'QU1'
        q2 = client.post("/api/tickets", json={
            "customer_name": "Quincy",
            "customer_email": "quincy@quantumcorp.net",
            "subject": "Delivery shipment question",
            "description": "Package delivery status.",
            "client_brand": "Quantum Corp"
        }).json()
        assert q2["ticket_id"].startswith("TKT-QU1-ORD-0001"), f"Expected TKT-QU1-ORD-0001, got {q2['ticket_id']}"

        # Second ticket for 'Quantum Cloud' reuses 'QUA'
        q3 = client.post("/api/tickets", json={
            "customer_name": "Quinn Two",
            "customer_email": "quinn2@quantumcloud.net",
            "subject": "Second tracking inquiry",
            "description": "Order package.",
            "client_brand": "Quantum Cloud"
        }).json()
        assert q3["ticket_id"] == "TKT-QUA-ORD-0002"
        print("PASS: Dynamic client codes generated cleanly with collision resolution: QUA vs QU1.")

        # ---------------------------------------------------------------------
        # CHECK 10: Weighted Classifier on Complex Evaluator Prompts
        # ---------------------------------------------------------------------
        print("\n[CHECK 10] Testing Weighted Classifier Scorer on Multi-Keyword Prompts...")
        assert classify_issue("Refund webhook returns HTTP 500", "webhook failure") == "INT"
        assert classify_issue("Customer 2FA lockout on billing portal", "locked out") == "ACC"
        assert classify_issue("CSV export lambda timeout on order analytics", "reporting") == "ANA"
        assert classify_issue("Vague question about my experience", "no keywords here") == "GEN"
        assert classify_issue("CSV export broken in reporting", "I want a refund for the billing issue") == "ANA"
        print("PASS: Weighted scoring (subject 2x, desc 1x) and tie-break hierarchy verified.")

        # ---------------------------------------------------------------------
        # CHECK 11: Defensive Boundaries & HTTP Error Handling
        # ---------------------------------------------------------------------
        print("\n[CHECK 11] Testing Defensive Boundaries & HTTP Error Handling...")
        # 11a. Invalid taxonomy code on PATCH -> 422
        assert client.patch("/api/tickets/TKT-URB-INT-0001/issue-type", json={"issue_type": "XYZ"}).status_code == 422
        # 11b. Non-existent ticket on PATCH -> 404
        assert client.patch("/api/tickets/TKT-URB-GEN-9999/issue-type", json={"issue_type": "ORD"}).status_code == 404
        # 11c. Invalid email on POST -> 422
        assert client.post("/api/tickets", json={"customer_name": "X", "customer_email": "bad", "subject": "S", "description": "D"}).status_code == 422
        # 11d. Unknown brand / email on context endpoint -> 204
        assert client.get(f"/api/customers/UnknownBrand/{quote('fake@example.com')}/context?issue_type=ORD").status_code == 204
        # 11e. Context with GEN issue type -> 204
        assert client.get(f"/api/customers/UrbanFit/{quote(email)}/context?issue_type=GEN").status_code == 204
        print("PASS: Defensive boundaries correctly return HTTP 422, 404, and 204.")

        print("\n" + "=" * 76)
        print("ALL 11 PHASE 2 VERIFICATION CHECKS PASSED CLEANLY ON REAL DATA & EDGES!")
        print("=" * 76)

    finally:
        # Re-seed database cleanly so demo environment is in pristine state for user showcase
        print("\n[CLEANUP] Restoring canonical demo dataset for UI showcase...")
        seed_database()
        print("PASS: Database restored to pristine demo state.")


if __name__ == "__main__":
    run_phase2_verification()
