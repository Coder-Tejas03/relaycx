"""
Phase 8: Comprehensive Automated Test Suite on Real Demo Data & Evaluator Edges.

This test suite evaluates the live application behavior against real seeded entities
and adversarial evaluator testing scenarios:
1. Canonical Seed Dataset Integrity (7 tickets, 18 notes, 3-character client codes).
2. Real Priya Nair Edge Case (Aura D2C ANA ticket suppresses face cream order ORD-3918).
3. Real Priya Nair Issue Correction Lifecycle (PATCH to ORD reveals cream order; revert to ANA suppresses it).
4. Real Dev Malhotra Developer Account Context (Nova Audio INT ticket displays SUB-DEV-902; ORD suppresses it).
5. Real Rohan Kapoor Cross-Client Data Isolation (UrbanFit Joggers ORD-6104 vs Nova Audio Speakers ORD-5520 vs Aura D2C zero leakage).
6. Customer History Audit Panel (single-brand isolation, ticket exclusion, multi-ticket order).
7. Structured Reference Stability Across All Lifecycle Transitions (Open -> In Progress -> Closed -> Open).
8. Intake Sequence Preservation After Classification Correction (prevents duplicate TKT sequences).
9. Dynamic Client Code Generation & Collision Safety on Unknown Brands (e.g. ZEP vs ZE1).
10. Weighted Classification Scorer on Complex Evaluator Prompts (competing keyword disambiguation).
11. Adversarial Casing, Whitespace Normalization, and HTTP Error Handling (422, 404, 204).
"""

import re
import unittest
from urllib.parse import quote
from fastapi.testclient import TestClient

from app.database import Base, engine, SessionLocal
from app.models import Ticket, Note
from app.main import app
from app.service import classify_issue
from seed import seed_database


class TestPhase8RealDataEdges(unittest.TestCase):
    """Automated verification suite testing real dataset behavior and evaluator edges."""

    @classmethod
    def setUpClass(cls):
        """Seed the canonical demo dataset before starting test suite."""
        seed_database()
        cls.client = TestClient(app)

    @classmethod
    def tearDownClass(cls):
        """Restore canonical demo dataset after all tests complete so the environment is pristine."""
        seed_database()

    # =========================================================================
    # SCENARIO 1: Canonical Seed Dataset Integrity
    # =========================================================================

    def test_01_seeded_canonical_dataset_integrity(self):
        """Verify the 7 canonical tickets, status counts, 18 notes, and structured references."""
        with SessionLocal() as db:
            tickets = db.query(Ticket).all()
            notes = db.query(Note).all()

            self.assertEqual(len(tickets), 7, f"Expected exactly 7 seeded tickets, found {len(tickets)}")
            self.assertEqual(len(notes), 18, f"Expected exactly 18 timeline notes, found {len(notes)}")

            # Status distribution
            open_count = len([t for t in tickets if t.status == "Open"])
            ip_count = len([t for t in tickets if t.status == "In Progress"])
            closed_count = len([t for t in tickets if t.status == "Closed"])

            self.assertEqual(open_count, 3, f"Expected 3 Open tickets, got {open_count}")
            self.assertEqual(ip_count, 2, f"Expected 2 In Progress tickets, got {ip_count}")
            self.assertEqual(closed_count, 2, f"Expected 2 Closed tickets, got {closed_count}")

            # Structured reference pattern: TKT-{CLIENT}-{ISSUE}-{SEQ:04d}
            ref_pattern = re.compile(r"^TKT-[A-Z]{3}-[A-Z]{3}-\d{4}$")
            for t in tickets:
                self.assertRegex(t.ticket_id, ref_pattern, f"Ticket {t.ticket_id} does not match structured format")
                self.assertIsNotNone(t.intake_issue_type, f"Missing intake_issue_type on {t.ticket_id}")
                self.assertIsNotNone(t.issue_type, f"Missing issue_type on {t.ticket_id}")
                self.assertIsNotNone(t.ticket_sequence, f"Missing ticket_sequence on {t.ticket_id}")
                self.assertGreaterEqual(t.ticket_sequence, 1)

    # =========================================================================
    # SCENARIO 2: Real Priya Nair Edge Case (Relevance Domain Suppression)
    # =========================================================================

    def test_02_priya_nair_domain_relevance_suppression(self):
        """
        Priya Nair (Aura D2C) has ticket TKT-AUR-ANA-0001 (analytics CSV export timeout).
        Although she has an ecommerce face cream order (ORD-3918) in Aura D2C,
        evaluating context with issue_type=ANA MUST return HTTP 204 No Content.
        """
        resp = self.client.get(
            f"/api/customers/{quote('Aura D2C')}/{quote('priya.nair@datalens.ai')}/context?issue_type=ANA"
        )
        self.assertEqual(resp.status_code, 204, "Priya with ANA ticket must receive HTTP 204 No Content")
        self.assertEqual(resp.text, "", "Response body for HTTP 204 must be empty")

    # =========================================================================
    # SCENARIO 3: Real Priya Nair Issue Correction Lifecycle
    # =========================================================================

    def test_03_priya_nair_issue_correction_lifecycle(self):
        """
        Test the complete issue correction lifecycle:
        1. Current classification is ANA -> Context is suppressed (HTTP 204).
        2. Correct issue_type to ORD -> ticket_id and intake_issue_type remain immutable.
        3. Query context with ORD -> HTTP 200 with face cream order ORD-3918.
        4. Revert classification to ANA -> Context suppressed again (HTTP 204).
        """
        ticket_id = "TKT-AUR-ANA-0001"

        # Step 1: Baseline check
        baseline_ticket = self.client.get(f"/api/tickets/{ticket_id}").json()
        self.assertEqual(baseline_ticket["intake_issue_type"], "ANA")
        self.assertEqual(baseline_ticket["issue_type"], "ANA")
        self.assertEqual(baseline_ticket["ticket_id"], ticket_id)

        # Step 2: Correct classification from ANA -> ORD
        patch_resp = self.client.patch(f"/api/tickets/{ticket_id}/issue-type", json={"issue_type": "ORD"})
        self.assertEqual(patch_resp.status_code, 200)
        patch_data = patch_resp.json()
        self.assertEqual(patch_data["ticket_id"], ticket_id, "ticket_id MUST remain invariant on correction")
        self.assertEqual(patch_data["intake_issue_type"], "ANA", "intake_issue_type MUST remain invariant")
        self.assertEqual(patch_data["issue_type"], "ORD", "issue_type MUST update to ORD")

        # Step 3: Context query for ORD now returns the cream order
        context_resp = self.client.get(
            f"/api/customers/{quote('Aura D2C')}/{quote('priya.nair@datalens.ai')}/context?issue_type=ORD"
        )
        self.assertEqual(context_resp.status_code, 200)
        context_data = context_resp.json()
        self.assertEqual(context_data["order_id"], "ORD-3918")
        self.assertEqual(context_data["item_name"], "Aura Luxury Botanical Restorative Cream Duo")
        self.assertEqual(context_data["total_amount"], "₹3,199")
        self.assertEqual(context_data["shipping_status"], "Delivered")

        # Step 4: Revert classification back to ANA
        revert_resp = self.client.patch(f"/api/tickets/{ticket_id}/issue-type", json={"issue_type": "ANA"})
        self.assertEqual(revert_resp.status_code, 200)
        self.assertEqual(revert_resp.json()["issue_type"], "ANA")

        # Step 5: Verify context query for ANA returns 204 again
        revert_context = self.client.get(
            f"/api/customers/{quote('Aura D2C')}/{quote('priya.nair@datalens.ai')}/context?issue_type=ANA"
        )
        self.assertEqual(revert_context.status_code, 204)

        # Step 6: Verify ticket in DB remains in canonical state
        final_check = self.client.get(f"/api/tickets/{ticket_id}").json()
        self.assertEqual(final_check["ticket_id"], ticket_id)
        self.assertEqual(final_check["intake_issue_type"], "ANA")
        self.assertEqual(final_check["issue_type"], "ANA")

    # =========================================================================
    # SCENARIO 4: Real Dev Malhotra Developer Account Context
    # =========================================================================

    def test_04_dev_malhotra_developer_account_context(self):
        """
        Dev Malhotra (Nova Audio) has ticket TKT-NOV-INT-0001 (rate limit 429).
        - With issue_type=INT: Returns HTTP 200 with Developer API Account SUB-DEV-902.
        - With issue_type=ORD: Returns HTTP 204 (developer account irrelevant for order inquiries).
        - With issue_type=ACC: Returns HTTP 204.
        """
        # Relevant INT domain
        int_resp = self.client.get(
            f"/api/customers/{quote('Nova Audio')}/{quote('dev.malhotra@hypergrid.net')}/context?issue_type=INT"
        )
        self.assertEqual(int_resp.status_code, 200)
        int_data = int_resp.json()
        self.assertEqual(int_data["order_id"], "SUB-DEV-902")
        self.assertEqual(int_data["account_type"], "developer")
        self.assertIn("Rate Limit Throttled", int_data["shipping_status"])
        self.assertIn("Backlog: 120k events", int_data["estimated_delivery"])
        self.assertEqual(int_data["technical_details"]["quota"], "5,000,000 req/mo")

        # Irrelevant ORD domain
        ord_resp = self.client.get(
            f"/api/customers/{quote('Nova Audio')}/{quote('dev.malhotra@hypergrid.net')}/context?issue_type=ORD"
        )
        self.assertEqual(ord_resp.status_code, 204)

        # Irrelevant ACC domain
        acc_resp = self.client.get(
            f"/api/customers/{quote('Nova Audio')}/{quote('dev.malhotra@hypergrid.net')}/context?issue_type=ACC"
        )
        self.assertEqual(acc_resp.status_code, 204)

    # =========================================================================
    # SCENARIO 5: Real Rohan Kapoor Cross-Client Data Isolation
    # =========================================================================

    def test_05_rohan_kapoor_cross_client_isolation(self):
        """
        Rohan Kapoor (rohan.kapoor@novabanking.com) exists in both UrbanFit and Nova Audio,
        but NOT in Aura D2C.
        - UrbanFit with ACC: HTTP 204 (2FA lockout suppresses shopping context).
        - UrbanFit with ORD: HTTP 200 with ORD-6104 (UrbanFit Training Joggers).
        - Nova Audio with ORD: HTTP 200 with ORD-5520 (Nova Pro Studio Monitor Speakers).
        - Never cross-contaminates between UrbanFit and Nova Audio orders!
        - Aura D2C with ORD: HTTP 204 (zero leakage for unassociated client).
        """
        email = "rohan.kapoor@novabanking.com"

        # 1. UrbanFit ACC ticket suppresses orders
        uf_acc = self.client.get(f"/api/customers/{quote('UrbanFit')}/{quote(email)}/context?issue_type=ACC")
        self.assertEqual(uf_acc.status_code, 204)

        # 2. UrbanFit ORD returns Joggers
        uf_ord = self.client.get(f"/api/customers/{quote('UrbanFit')}/{quote(email)}/context?issue_type=ORD")
        self.assertEqual(uf_ord.status_code, 200)
        uf_data = uf_ord.json()
        self.assertEqual(uf_data["order_id"], "ORD-6104")
        self.assertEqual(uf_data["item_name"], "UrbanFit AeroDry Training Joggers (Charcoal / M)")
        self.assertNotIn("Nova Studio Monitor Speakers", str(uf_data))

        # 3. Nova Audio ORD returns Speakers
        nov_ord = self.client.get(f"/api/customers/{quote('Nova Audio')}/{quote(email)}/context?issue_type=ORD")
        self.assertEqual(nov_ord.status_code, 200)
        nov_data = nov_ord.json()
        self.assertEqual(nov_data["order_id"], "ORD-5520")
        self.assertEqual(nov_data["item_name"], "Nova Studio Monitor Speakers (Pair)")
        self.assertNotIn("UrbanFit AeroDry Training Joggers", str(nov_data))

        # 4. Aura D2C returns 204 (Zero cross-client leakage)
        aur_ord = self.client.get(f"/api/customers/{quote('Aura D2C')}/{quote(email)}/context?issue_type=ORD")
        self.assertEqual(aur_ord.status_code, 204)

    # =========================================================================
    # SCENARIO 6: Customer History Audit Panel & Isolation
    # =========================================================================

    def test_06_customer_history_audit_and_exclusion(self):
        """
        Verify customer ticket history endpoint:
        - Scoped strictly to client_brand and customer_email.
        - Excludes current ticket when exclude_ticket_id is specified.
        - Cross-brand query for the same customer returns empty list.
        """
        email = "rohan.kapoor@novabanking.com"

        # Under UrbanFit without exclusion -> 1 prior ticket
        h1 = self.client.get(f"/api/tickets/customer-history?client_brand=UrbanFit&customer_email={quote(email)}")
        self.assertEqual(h1.status_code, 200)
        tickets_uf = h1.json()
        self.assertEqual(len(tickets_uf), 1)
        self.assertEqual(tickets_uf[0]["ticket_id"], "TKT-URB-ACC-0001")
        self.assertEqual(tickets_uf[0]["intake_issue_type"], "ACC")

        # Under UrbanFit with exclusion of TKT-URB-ACC-0001 -> 0 tickets
        h2 = self.client.get(
            f"/api/tickets/customer-history?client_brand=UrbanFit&customer_email={quote(email)}&exclude_ticket_id=TKT-URB-ACC-0001"
        )
        self.assertEqual(h2.status_code, 200)
        self.assertEqual(len(h2.json()), 0)

        # Under Nova Audio -> 0 prior tickets (Rohan has no tickets in Nova Audio)
        h3 = self.client.get(
            f"/api/tickets/customer-history?client_brand=Nova%20Audio&customer_email={quote(email)}"
        )
        self.assertEqual(h3.status_code, 200)
        self.assertEqual(len(h3.json()), 0)

        # Also test alternative route /api/customers/{brand}/{email}/history
        h4 = self.client.get(f"/api/customers/UrbanFit/{quote(email)}/history")
        self.assertEqual(h4.status_code, 200)
        self.assertEqual(len(h4.json()), 1)

    # =========================================================================
    # SCENARIO 7: Reference Stability Across All Lifecycle Transitions
    # =========================================================================

    def test_07_reference_stability_through_all_lifecycle_transitions(self):
        """
        Take a ticket through multiple status transitions and updates:
        Open -> (add note) In Progress -> (resolve) Closed -> (reopen) Open -> (note) In Progress -> (close) Closed
        Verify ticket_id, intake_issue_type, and ticket_sequence NEVER change.
        """
        # Create a dedicated test ticket for lifecycle transition testing
        create_resp = self.client.post("/api/tickets", json={
            "customer_name": "Lifecycle Tester",
            "customer_email": "lifecycle.test@example.com",
            "subject": "Testing state machine stability for checkout payment",
            "description": "Payment was processed twice on checkout gateway.",
            "client_brand": "UrbanFit",
            "channel": "Email"
        })
        self.assertEqual(create_resp.status_code, 201)
        created = create_resp.json()
        initial_id = created["ticket_id"]
        initial_intake = created["intake_issue_type"]
        initial_seq = created["ticket_sequence"]

        self.assertEqual(initial_intake, "PAY")
        self.assertEqual(created["status"], "Open")

        # Step 1: Note -> auto-advance to In Progress
        r1 = self.client.put(f"/api/tickets/{initial_id}", json={"note_text": "Investigating duplicate charge."})
        self.assertEqual(r1.status_code, 200)
        d1 = r1.json()
        self.assertEqual(d1["status"], "In Progress")
        self.assertEqual(d1["ticket_id"], initial_id)

        # Step 2: Explicit resolve to Closed
        r2 = self.client.put(f"/api/tickets/{initial_id}", json={"status": "Closed", "note_text": "Refund issued."})
        self.assertEqual(r2.status_code, 200)
        self.assertEqual(r2.json()["status"], "Closed")

        # Step 3: Re-open to Open
        r3 = self.client.put(f"/api/tickets/{initial_id}", json={"status": "Open", "note_text": "Customer reopened."})
        self.assertEqual(r3.status_code, 200)
        self.assertEqual(r3.json()["status"], "Open")

        # Step 4: Advance again to In Progress
        r4 = self.client.put(f"/api/tickets/{initial_id}", json={"status": "In Progress"})
        self.assertEqual(r4.status_code, 200)
        self.assertEqual(r4.json()["status"], "In Progress")

        # Step 5: Close again
        r5 = self.client.put(f"/api/tickets/{initial_id}", json={"status": "Closed"})
        self.assertEqual(r5.status_code, 200)
        self.assertEqual(r5.json()["status"], "Closed")

        # Step 6: Detail check after all transitions
        detail = self.client.get(f"/api/tickets/{initial_id}").json()
        self.assertEqual(detail["ticket_id"], initial_id, "Reference must be strictly invariant")
        self.assertEqual(detail["intake_issue_type"], initial_intake, "Intake issue type must be invariant")
        self.assertEqual(detail["ticket_sequence"], initial_seq, "Sequence number must be invariant")
        self.assertEqual(detail["status"], "Closed")

    # =========================================================================
    # SCENARIO 8: Sequence Preservation After Issue Correction
    # =========================================================================

    def test_08_sequence_preservation_after_issue_correction(self):
        """
        Verify that correcting a ticket's current classification from ANA to ORD
        does NOT reset or compromise sequence allocation for new ANA tickets.
        The next ANA ticket created must increment sequence monotonically (e.g. 0002).
        """
        brand = "Aura D2C"
        # Seeded Aura D2C ANA ticket: TKT-AUR-ANA-0001
        tkt_ana_1 = "TKT-AUR-ANA-0001"

        # Correct current issue_type of TKT-AUR-ANA-0001 to ORD
        self.client.patch(f"/api/tickets/{tkt_ana_1}/issue-type", json={"issue_type": "ORD"})

        # Now create a new ticket that classifies as ANA for Aura D2C
        new_resp = self.client.post("/api/tickets", json={
            "customer_name": "Analytics User",
            "customer_email": "analytics.user@datalens.ai",
            "subject": "CSV export timeout on monthly analytics report",
            "description": "Export empty file lambda timeout error.",
            "client_brand": brand,
            "channel": "Web"
        })
        self.assertEqual(new_resp.status_code, 201)
        new_data = new_resp.json()

        self.assertEqual(new_data["intake_issue_type"], "ANA")
        self.assertEqual(new_data["ticket_sequence"], 2, "Sequence must increment to 2, not reuse 1")
        self.assertEqual(new_data["ticket_id"], "TKT-AUR-ANA-0002")

        # Revert TKT-AUR-ANA-0001 back to ANA
        self.client.patch(f"/api/tickets/{tkt_ana_1}/issue-type", json={"issue_type": "ANA"})

    # =========================================================================
    # SCENARIO 9: Dynamic Client Code Derivation & Collision Safety
    # =========================================================================

    def test_09_dynamic_client_code_derivation_and_collision_resolution(self):
        """
        Test dynamic client code generation for unknown brands:
        - Unknown Brand 1 ('Zephyr Tech') -> Generates 'ZEP'.
        - Unknown Brand 2 ('Zephyr Sports') -> 'ZEP' collides -> derives 'ZE1'.
        - Successive tickets for both brands reuse their respective assigned codes!
        """
        # Brand 1: Zephyr Tech
        r1 = self.client.post("/api/tickets", json={
            "customer_name": "Alice Zephyr",
            "customer_email": "alice@zephyrtech.io",
            "subject": "Order tracking delay",
            "description": "Tracking package delivery status.",
            "client_brand": "Zephyr Tech"
        })
        self.assertEqual(r1.status_code, 201)
        d1 = r1.json()
        self.assertTrue(d1["ticket_id"].startswith("TKT-ZEP-ORD-"))

        # Brand 2: Zephyr Sports (first 3 letters 'ZEP' collide)
        r2 = self.client.post("/api/tickets", json={
            "customer_name": "Bob Zephyr",
            "customer_email": "bob@zephyrsports.com",
            "subject": "Order delivery question",
            "description": "Delivery package item query.",
            "client_brand": "Zephyr Sports"
        })
        self.assertEqual(r2.status_code, 201)
        d2 = r2.json()
        self.assertTrue(
            d2["ticket_id"].startswith("TKT-ZE1-ORD-"),
            f"Expected TKT-ZE1-ORD-xxxx, got {d2['ticket_id']}"
        )

        # Subsequent ticket for Zephyr Tech must reuse 'ZEP'
        r3 = self.client.post("/api/tickets", json={
            "customer_name": "Charlie Zephyr",
            "customer_email": "charlie@zephyrtech.io",
            "subject": "Second order query",
            "description": "Delivery package item.",
            "client_brand": "Zephyr Tech"
        })
        self.assertEqual(r3.status_code, 201)
        d3 = r3.json()
        self.assertEqual(d3["ticket_id"], "TKT-ZEP-ORD-0002", "Must reuse ZEP code and increment sequence")

        # Subsequent ticket for Zephyr Sports must reuse 'ZE1'
        r4 = self.client.post("/api/tickets", json={
            "customer_name": "Dave Zephyr",
            "customer_email": "dave@zephyrsports.com",
            "subject": "Second sports order query",
            "description": "Delivery package item.",
            "client_brand": "Zephyr Sports"
        })
        self.assertEqual(r4.status_code, 201)
        d4 = r4.json()
        self.assertEqual(d4["ticket_id"], "TKT-ZE1-ORD-0002", "Must reuse ZE1 code and increment sequence")

    # =========================================================================
    # SCENARIO 10: Weighted Classifier Scorer on Complex Evaluator Prompts
    # =========================================================================

    def test_10_classifier_stress_testing_adversarial_prompts(self):
        """
        Test classifier accuracy on ambiguous, multi-keyword phrases:
        1. 'Refund webhook returns HTTP 500' -> INT (score 13) beats PAY (score 4)
        2. 'Customer 2FA lockout on billing portal' -> ACC (score 12) beats PAY (score 4)
        3. 'CSV export lambda timeout on order analytics' -> ANA beats ORD
        4. Generic inquiry without keywords -> GEN
        5. Subject double-weighting overrides description
        """
        # 1. INT vs PAY: Refund webhook HTTP 500
        c1 = classify_issue("Refund webhook returns HTTP 500", "webhook events failing on gateway")
        self.assertEqual(c1, "INT", f"Expected INT, got {c1}")

        # 2. ACC vs PAY: 2FA lockout on billing portal
        c2 = classify_issue("2FA lockout on billing portal", "locked out of account verification code")
        self.assertEqual(c2, "ACC", f"Expected ACC, got {c2}")

        # 3. ANA vs ORD: CSV export lambda timeout on order analytics
        c3 = classify_issue("CSV export lambda timeout on order analytics", "reporting dashboard empty file")
        self.assertEqual(c3, "ANA", f"Expected ANA, got {c3}")

        # 4. GEN fallback: No domain keywords
        c4 = classify_issue("Hello question about my account", "Just wondering how things work")
        self.assertEqual(c4, "GEN", f"Expected GEN, got {c4}")

        # 5. Subject double-weighting: Subject has CSV export (ANA), description mentions refund (PAY)
        c5 = classify_issue("CSV export broken in reporting", "I want a refund for the billing issue")
        self.assertEqual(c5, "ANA", f"Subject double-weighting should make ANA win, got {c5}")

    # =========================================================================
    # SCENARIO 11: Adversarial Casing, Whitespace Normalization & Error Codes
    # =========================================================================

    def test_11_adversarial_casing_whitespace_and_error_codes(self):
        """
        Verify robust handling of whitespace, case insensitivity, and input errors:
        - Mixed casing and extra spaces in customer email and brand.
        - 422 Unprocessable Entity for invalid classification taxonomy code.
        - 404 Not Found for non-existent ticket PATCH.
        - 204 No Content for unknown brand or unknown customer context queries.
        - 204 No Content for GEN issue type.
        """
        # 1. Case-insensitivity & whitespace normalization in context endpoint
        context_casing = self.client.get(
            f"/api/customers/{quote('  UrbanFit  ')}/{quote('  ROHAN.KAPOOR@NOVABANKING.COM  ')}/context?issue_type=ORD"
        )
        self.assertEqual(context_casing.status_code, 200)
        self.assertEqual(context_casing.json()["order_id"], "ORD-6104")

        # 2. PATCH invalid taxonomy code -> 422
        bad_patch = self.client.patch("/api/tickets/TKT-URB-INT-0001/issue-type", json={"issue_type": "INVALID_CODE"})
        self.assertEqual(bad_patch.status_code, 422)

        # 3. PATCH non-existent ticket -> 404
        missing_patch = self.client.patch("/api/tickets/TKT-URB-GEN-9999/issue-type", json={"issue_type": "INT"})
        self.assertEqual(missing_patch.status_code, 404)

        # 4. Context for unknown brand -> 204
        unknown_brand = self.client.get(
            f"/api/customers/{quote('UnknownBrand')}/{quote('priya.nair@datalens.ai')}/context?issue_type=ORD"
        )
        self.assertEqual(unknown_brand.status_code, 204)

        # 5. Context for unknown email -> 204
        unknown_email = self.client.get(
            f"/api/customers/{quote('Aura D2C')}/{quote('unknown.customer@example.com')}/context?issue_type=ORD"
        )
        self.assertEqual(unknown_email.status_code, 204)

        # 6. Context for GEN issue type -> always 204
        gen_context = self.client.get(
            f"/api/customers/{quote('Aura D2C')}/{quote('priya.nair@datalens.ai')}/context?issue_type=GEN"
        )
        self.assertEqual(gen_context.status_code, 204)


if __name__ == "__main__":
    unittest.main()
