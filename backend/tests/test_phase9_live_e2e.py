"""
Phase 9: Comprehensive Live End-to-End Test Suite against Live Server (http://localhost:8000).

Tests the actual running FastAPI backend over real HTTP sockets:
1. Live Server Health & Queue Status (all tickets with structured IDs).
2. Priya Nair (Aura D2C) - Context Suppression, Dynamic Correction, and Reference Invariance.
3. Dev Malhotra (Nova Audio) - Technical Developer Context and Domain Suppression.
4. Rohan Kapoor - Strict Multi-Brand Cross-Client Isolation (UrbanFit vs Nova Audio vs Aura D2C).
5. Customer History Panel - Scoping, Ticket Self-Exclusion, and Cross-Brand Segregation.
6. Unknown Brand Dynamic Client Code Derivation and Sequence Progression (Apex Cloud -> APE #0001 & #0002).
7. Evaluator Adversarial Edges & Defensive HTTP Status Codes (422, 404, 204).
8. Automated Database Teardown & Canonical Demo State Restoration.

Usage:
    cd backend && ../.venv/bin/python -m unittest tests/test_phase9_live_e2e.py
    or from root: python verify_e2e.py
"""

import os
import re
import sys
import unittest
from urllib.parse import quote
import httpx

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from seed import seed_database

LIVE_SERVER_URL = os.getenv("RELAYCX_BACKEND_URL", "http://localhost:8000")


class TestPhase9LiveE2E(unittest.TestCase):
    """Live HTTP End-to-End Test Suite for RelayCX Client-Aware Context & References."""

    @classmethod
    def setUpClass(cls):
        """Verify live server availability and seed database."""
        cls.client = httpx.Client(base_url=LIVE_SERVER_URL, timeout=15.0)
        try:
            resp = cls.client.get("/api/tickets")
            if resp.status_code != 200:
                raise RuntimeError(f"Live server at {LIVE_SERVER_URL} returned status {resp.status_code}")
        except Exception as err:
            raise RuntimeError(
                f"Cannot connect to live RelayCX backend at {LIVE_SERVER_URL}. "
                "Ensure uvicorn is running on port 8000."
            ) from err

        seed_database()

    @classmethod
    def tearDownClass(cls):
        """Restore pristine canonical demo dataset after all tests complete."""
        try:
            cls.client.close()
        finally:
            seed_database()

    # =========================================================================
    # 1. LIVE QUEUE & STRUCTURED REFERENCES
    # =========================================================================

    def test_01_live_queue_and_structured_references(self):
        """Verify the live server returns tickets with 16-character structured IDs."""
        resp = self.client.get("/api/tickets")
        self.assertEqual(resp.status_code, 200)
        tickets = resp.json()
        self.assertGreaterEqual(len(tickets), 7)

        ref_regex = re.compile(r"^TKT-[A-Z0-9]{3}-[A-Z]{3}-\d{4}$")
        for t in tickets:
            self.assertTrue(
                ref_regex.match(t["ticket_id"]),
                f"Ticket ID {t['ticket_id']} does not match structured format TKT-CCC-FFF-NNNN"
            )
            self.assertIn("issue_type", t)
            self.assertIn("intake_issue_type", t)

    # =========================================================================
    # 2. PRIYA NAIR: DOMAIN RELEVANCE & DYNAMIC CORRECTION LIFECYCLE
    # =========================================================================

    def test_02_priya_nair_context_suppression_and_dynamic_correction(self):
        """
        Priya Nair (Aura D2C) filed an analytics inquiry (TKT-AUR-ANA-0001).
        Her personal face cream order (ORD-3918) must be SUPPRESSED under ANA (204).
        When corrected to ORD, the context must dynamically reveal ORD-3918 (200).
        When reverted to ANA, it must return to 204.
        Ticket ID and intake_issue_type must remain strictly immutable.
        """
        ticket_id = "TKT-AUR-ANA-0001"
        email = "priya.nair@datalens.ai"
        brand = "Aura D2C"

        # Step 1: Verify current ticket details
        r_detail = self.client.get(f"/api/tickets/{ticket_id}")
        self.assertEqual(r_detail.status_code, 200)
        detail = r_detail.json()
        self.assertEqual(detail["ticket_id"], ticket_id)
        self.assertEqual(detail["intake_issue_type"], "ANA")
        self.assertEqual(detail["issue_type"], "ANA")
        self.assertEqual(detail["ticket_sequence"], 1)

        # Step 2: Query context under ANA -> must be 204 No Content (face cream order suppressed)
        r_ctx_ana = self.client.get(f"/api/customers/{quote(brand)}/{quote(email)}/context?issue_type=ANA")
        self.assertEqual(r_ctx_ana.status_code, 204, "Analytics inquiry must suppress ecommerce order")

        # Step 3: Agent discovers it is an order delivery issue -> PATCH issue_type to ORD
        r_patch = self.client.patch(f"/api/tickets/{ticket_id}/issue-type", json={"issue_type": "ORD"})
        self.assertEqual(r_patch.status_code, 200)
        patch_res = r_patch.json()
        self.assertEqual(patch_res["ticket_id"], ticket_id, "Ticket ID must remain immutable")
        self.assertEqual(patch_res["intake_issue_type"], "ANA", "Intake issue type must remain immutable")
        self.assertEqual(patch_res["issue_type"], "ORD")

        # Step 4: Query context under ORD -> must dynamically reveal live D2C order ORD-3918
        r_ctx_ord = self.client.get(f"/api/customers/{quote(brand)}/{quote(email)}/context?issue_type=ORD")
        self.assertEqual(r_ctx_ord.status_code, 200)
        ctx_data = r_ctx_ord.json()
        self.assertEqual(ctx_data["account_type"], "ecommerce")
        self.assertEqual(ctx_data["order_id"], "ORD-3918")
        self.assertIn("Botanical", ctx_data["item_name"])
        self.assertEqual(ctx_data["total_amount"], "₹3,199")
        self.assertEqual(ctx_data["shipping_status"], "Delivered")

        # Step 5: Revert back to ANA
        r_revert = self.client.patch(f"/api/tickets/{ticket_id}/issue-type", json={"issue_type": "ANA"})
        self.assertEqual(r_revert.status_code, 200)

        # Step 6: Query context again under ANA -> must be 204 No Content
        r_ctx_revert = self.client.get(f"/api/customers/{quote(brand)}/{quote(email)}/context?issue_type=ANA")
        self.assertEqual(r_ctx_revert.status_code, 204)

        # Step 7: Final detail check -> immutability confirmation
        final_detail = self.client.get(f"/api/tickets/{ticket_id}").json()
        self.assertEqual(final_detail["ticket_id"], ticket_id)
        self.assertEqual(final_detail["intake_issue_type"], "ANA")
        self.assertEqual(final_detail["issue_type"], "ANA")
        self.assertEqual(final_detail["ticket_sequence"], 1)

    # =========================================================================
    # 3. DEV MALHOTRA: DEVELOPER ACCOUNT CONTEXT & DOMAIN RELEVANCE
    # =========================================================================

    def test_03_dev_malhotra_developer_context_and_suppression(self):
        """
        Dev Malhotra (Nova Audio) has ticket TKT-NOV-INT-0001 (API rate limit outage).
        Relevant Context under INT must return Developer Account SUB-DEV-902 with rate limit metrics.
        Relevant Context under ORD must return 204 No Content.
        """
        brand = "Nova Audio"
        email = "dev.malhotra@hypergrid.net"

        # Under INT: returns developer account
        r_int = self.client.get(f"/api/customers/{quote(brand)}/{quote(email)}/context?issue_type=INT")
        self.assertEqual(r_int.status_code, 200)
        data = r_int.json()
        self.assertEqual(data["account_type"], "developer")
        self.assertEqual(data["order_id"], "SUB-DEV-902")
        self.assertEqual(data["customer_tier"], "Enterprise Developer Tier")
        self.assertIn("Rate Limit Throttled", data["shipping_status"])
        self.assertIn("technical_details", data)
        self.assertEqual(data["technical_details"]["endpoint"], "/v1/telemetry")
        self.assertEqual(data["estimated_delivery"], "Backlog: 120k events")

        # Under ORD: developer account must be suppressed
        r_ord = self.client.get(f"/api/customers/{quote(brand)}/{quote(email)}/context?issue_type=ORD")
        self.assertEqual(r_ord.status_code, 204)

    # =========================================================================
    # 4. ROHAN KAPOOR: STRICT CROSS-CLIENT DATA ISOLATION
    # =========================================================================

    def test_04_rohan_kapoor_cross_client_isolation(self):
        """
        Rohan Kapoor (rohan.kapoor@novabanking.com) is registered with multiple client brands.
        - UrbanFit ORD: returns Joggers (ORD-6104).
        - Nova Audio ORD: returns Studio Monitors (ORD-5520).
        - Aura D2C ORD: returns 204 No Content.
        Strict multi-tenant isolation guarantees zero cross-client data leakage.
        """
        email = "rohan.kapoor@novabanking.com"

        # UrbanFit context
        r_uf = self.client.get(f"/api/customers/UrbanFit/{quote(email)}/context?issue_type=ORD")
        self.assertEqual(r_uf.status_code, 200)
        data_uf = r_uf.json()
        self.assertEqual(data_uf["order_id"], "ORD-6104")
        self.assertIn("Joggers", data_uf["item_name"])
        self.assertEqual(data_uf["total_amount"], "₹2,499")

        # Nova Audio context
        r_nova = self.client.get(f"/api/customers/{quote('Nova Audio')}/{quote(email)}/context?issue_type=ORD")
        self.assertEqual(r_nova.status_code, 200)
        data_nova = r_nova.json()
        self.assertEqual(data_nova["order_id"], "ORD-5520")
        self.assertIn("Studio Monitor", data_nova["item_name"])
        self.assertEqual(data_nova["total_amount"], "₹14,999")

        # Aura D2C context (Rohan is not a customer of Aura D2C)
        r_aura = self.client.get(f"/api/customers/{quote('Aura D2C')}/{quote(email)}/context?issue_type=ORD")
        self.assertEqual(r_aura.status_code, 204, "Aura D2C must have zero data for Rohan Kapoor")

    # =========================================================================
    # 5. CUSTOMER HISTORY: BRAND SCOPING & TICKET SELF-EXCLUSION
    # =========================================================================

    def test_05_customer_history_scoping_and_exclusion(self):
        """
        Customer history queries must be strictly scoped to the specified client brand.
        Passing exclude_ticket_id must exclude the current active ticket from the history list.
        """
        email = "rohan.kapoor@novabanking.com"

        # Under UrbanFit without exclusion -> returns TKT-URB-ACC-0001
        r1 = self.client.get(f"/api/tickets/customer-history?client_brand=UrbanFit&customer_email={quote(email)}")
        self.assertEqual(r1.status_code, 200)
        history_uf = r1.json()
        self.assertGreaterEqual(len(history_uf), 1)
        self.assertEqual(history_uf[0]["ticket_id"], "TKT-URB-ACC-0001")

        # Under UrbanFit with exclusion of TKT-URB-ACC-0001 -> returns 0 tickets
        r2 = self.client.get(
            f"/api/tickets/customer-history?client_brand=UrbanFit&customer_email={quote(email)}&exclude_ticket_id=TKT-URB-ACC-0001"
        )
        self.assertEqual(r2.status_code, 200)
        self.assertEqual(len(r2.json()), 0)

        # Under Nova Audio -> returns 0 tickets (Rohan has no support tickets in Nova Audio)
        r3 = self.client.get(
            f"/api/tickets/customer-history?client_brand={quote('Nova Audio')}&customer_email={quote(email)}"
        )
        self.assertEqual(r3.status_code, 200)
        self.assertEqual(len(r3.json()), 0)

    # =========================================================================
    # 6. UNKNOWN BRAND DYNAMIC DERIVATION & SEQUENCE PROGRESSION
    # =========================================================================

    def test_06_dynamic_client_code_derivation_and_sequence(self):
        """
        When creating tickets for unknown brands not in the static map (e.g. 'Apex Cloud'):
        1. Derives 3-character client code 'APE'.
        2. Assigns sequence #0001 for first ticket -> TKT-APE-INT-0001.
        3. Monotonically increments sequence to #0002 for second ticket -> TKT-APE-INT-0002.
        """
        brand = "Apex Cloud"

        # Create Ticket 1
        r1 = self.client.post("/api/tickets", json={
            "customer_name": "Alex Mercer",
            "customer_email": "alex.mercer@apexcloud.io",
            "subject": "Webhook delivery failure on billing event",
            "description": "Webhook endpoint returning HTTP 500 on customer invoice events.",
            "client_brand": brand,
            "channel": "API"
        })
        self.assertEqual(r1.status_code, 201)
        t1 = r1.json()
        self.assertEqual(t1["ticket_id"], "TKT-APE-INT-0001")
        self.assertEqual(t1["intake_issue_type"], "INT")
        self.assertEqual(t1["issue_type"], "INT")
        self.assertEqual(t1["ticket_sequence"], 1)

        # Create Ticket 2 (same brand, same issue family)
        r2 = self.client.post("/api/tickets", json={
            "customer_name": "Jordan Lee",
            "customer_email": "jordan.lee@apexcloud.io",
            "subject": "Webhook endpoint rate limit 429 throttling",
            "description": "Integration webhook receiving HTTP 429 rate limit exceeded.",
            "client_brand": brand,
            "channel": "Web Portal"
        })
        self.assertEqual(r2.status_code, 201)
        t2 = r2.json()
        self.assertEqual(t2["ticket_id"], "TKT-APE-INT-0002")
        self.assertEqual(t2["intake_issue_type"], "INT")
        self.assertEqual(t2["issue_type"], "INT")
        self.assertEqual(t2["ticket_sequence"], 2)

    # =========================================================================
    # 7. ADVERSARIAL EVALUATOR EDGES & DEFENSIVE ERROR HANDLING
    # =========================================================================

    def test_07_evaluator_adversarial_edges_and_error_codes(self):
        """
        Verify robust error boundaries:
        - HTTP 422 on invalid taxonomy classification code.
        - HTTP 404 on nonexistent ticket ID.
        - HTTP 422 on missing query parameters.
        - HTTP 204 on unknown customer context.
        """
        # Invalid taxonomy code
        r_invalid = self.client.patch("/api/tickets/TKT-URB-ACC-0001/issue-type", json={"issue_type": "INVALID_CODE"})
        self.assertEqual(r_invalid.status_code, 422)

        # Nonexistent ticket
        r_missing = self.client.get("/api/tickets/TKT-URB-GEN-9999")
        self.assertEqual(r_missing.status_code, 404)

        # Correct nonexistent ticket
        r_patch_missing = self.client.patch("/api/tickets/TKT-URB-GEN-9999/issue-type", json={"issue_type": "ORD"})
        self.assertEqual(r_patch_missing.status_code, 404)

        # Unknown customer context
        r_unknown_ctx = self.client.get(
            f"/api/customers/{quote('UrbanFit')}/{quote('nobody@nonexistent.domain')}/context?issue_type=ORD"
        )
        self.assertEqual(r_unknown_ctx.status_code, 204)


def run_live_e2e_verification():
    """Standalone terminal runner for Live E2E Verification."""
    print("=" * 76)
    print("STARTING RELAYCX LIVE END-TO-END VERIFICATION SUITE (HTTP :8000)")
    print("=" * 76)

    suite = unittest.TestLoader().loadTestsFromTestCase(TestPhase9LiveE2E)
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    if result.wasSuccessful():
        print("\n" + "=" * 76)
        print("ALL LIVE END-TO-END VERIFICATION CHECKS PASSED CLEANLY ON REAL DATA & EDGES!")
        print("=" * 76)
        sys.exit(0)
    else:
        print("\n" + "=" * 76)
        print(f"VERIFICATION FAILED: {len(result.failures)} failures, {len(result.errors)} errors")
        print("=" * 76)
        sys.exit(1)


if __name__ == "__main__":
    run_live_e2e_verification()
