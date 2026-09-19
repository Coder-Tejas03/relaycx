"""
Unit tests for Phase 4: Commerce Provider Layer in app.integrations.commerce_provider.
Tests client-brand scoping, cross-client isolation, issue-family relevance filtering,
empty state triggers, and backward compatibility with get_order_context.
"""

import unittest
from app.integrations.commerce_provider import (
    SEEDED_CUSTOMER_CONTEXTS,
    ISSUE_RELEVANCE_RULES,
    get_relevant_context,
    get_order_context,
    _lookup_context,
)


class TestPhase4CommerceProvider(unittest.TestCase):
    # -------------------------------------------------------------------------
    # 1. Structure & Rules Configuration
    # -------------------------------------------------------------------------

    def test_issue_relevance_rules_completeness(self):
        """Ensure all 8 taxonomy families are defined with correct domain sets."""
        expected_families = {"ORD", "PAY", "ACC", "TEC", "INT", "ANA", "PRD", "GEN"}
        self.assertEqual(set(ISSUE_RELEVANCE_RULES.keys()), expected_families)

        # GEN must always be an empty set (never show context)
        self.assertEqual(ISSUE_RELEVANCE_RULES["GEN"], set())

        # ANA must only allow analytics
        self.assertEqual(ISSUE_RELEVANCE_RULES["ANA"], {"analytics"})

        # INT must allow developer and integration
        self.assertIn("developer", ISSUE_RELEVANCE_RULES["INT"])
        self.assertIn("integration", ISSUE_RELEVANCE_RULES["INT"])

        # ORD, PAY, PRD must include ecommerce
        self.assertIn("ecommerce", ISSUE_RELEVANCE_RULES["ORD"])
        self.assertIn("ecommerce", ISSUE_RELEVANCE_RULES["PAY"])
        self.assertIn("ecommerce", ISSUE_RELEVANCE_RULES["PRD"])

    def test_seeded_contexts_keys_are_tuples(self):
        """Verify all keys in SEEDED_CUSTOMER_CONTEXTS are (brand, email) tuples."""
        for key in SEEDED_CUSTOMER_CONTEXTS.keys():
            self.assertIsInstance(key, tuple)
            self.assertEqual(len(key), 2)
            brand, email = key
            self.assertIsInstance(brand, str)
            self.assertIsInstance(email, str)
            self.assertGreater(len(brand), 0)
            self.assertIn("@", email)

    # -------------------------------------------------------------------------
    # 2. Acceptance Criteria: Priya Nair / Aura D2C (ANA vs ORD)
    # -------------------------------------------------------------------------

    def test_priya_ana_ticket_excludes_cream_order(self):
        """
        Acceptance criterion: Priya's ANA ticket must NOT show the ecommerce
        cream order as active context; returns None for a clean empty state.
        """
        ctx = get_relevant_context(
            client_brand="Aura D2C",
            customer_email="priya.nair@datalens.ai",
            issue_type="ANA",
        )
        self.assertIsNone(ctx, "Priya's ANA ticket must not return ecommerce cream order context")

    def test_priya_ord_ticket_returns_cream_order(self):
        """
        When the issue family is ORD, Priya's ecommerce cream order IS relevant
        and must be returned.
        """
        ctx = get_relevant_context(
            client_brand="Aura D2C",
            customer_email="priya.nair@datalens.ai",
            issue_type="ORD",
        )
        self.assertIsNotNone(ctx)
        self.assertEqual(ctx["order_id"], "ORD-3918")
        self.assertIn("Aura Luxury Botanical Restorative Cream", ctx["item_name"])
        self.assertEqual(ctx["account_type"], "ecommerce")

    # -------------------------------------------------------------------------
    # 3. Acceptance Criteria: Dev Malhotra / Nova Audio (INT vs ORD)
    # -------------------------------------------------------------------------

    def test_dev_int_ticket_returns_developer_details(self):
        """
        Acceptance criterion: Dev's INT ticket on Nova Audio must return the
        developer account and telemetry API rate limit context.
        """
        ctx = get_relevant_context(
            client_brand="Nova Audio",
            customer_email="dev.malhotra@hypergrid.net",
            issue_type="INT",
        )
        self.assertIsNotNone(ctx)
        self.assertEqual(ctx["account_type"], "developer")
        self.assertEqual(ctx["order_id"], "SUB-DEV-902")
        self.assertIn("technical_details", ctx)
        self.assertEqual(ctx["technical_details"]["endpoint"], "/v1/telemetry")

    def test_dev_ord_ticket_excludes_developer_context(self):
        """
        Dev's developer account is NOT an ecommerce order, so an ORD ticket
        must return None.
        """
        ctx = get_relevant_context(
            client_brand="Nova Audio",
            customer_email="dev.malhotra@hypergrid.net",
            issue_type="ORD",
        )
        self.assertIsNone(ctx)

    # -------------------------------------------------------------------------
    # 4. Cross-Client Isolation (Same Customer Email Across Different Brands)
    # -------------------------------------------------------------------------

    def test_cross_client_isolation_rohan_kapoor(self):
        """
        Acceptance criterion: Cross-client isolation.
        Rohan has an account under UrbanFit (Joggers) and Nova Audio (Speakers).
        Retrieval must strictly isolate records by client_brand.
        """
        email = "rohan.kapoor@novabanking.com"

        # 1. Under UrbanFit, returns Joggers
        urbanfit_ctx = get_relevant_context(
            client_brand="UrbanFit",
            customer_email=email,
            issue_type="ORD",
        )
        self.assertIsNotNone(urbanfit_ctx)
        self.assertEqual(urbanfit_ctx["order_id"], "ORD-6104")
        self.assertIn("UrbanFit AeroDry Training Joggers", urbanfit_ctx["item_name"])

        # 2. Under Nova Audio, returns Speakers
        nova_ctx = get_relevant_context(
            client_brand="Nova Audio",
            customer_email=email,
            issue_type="ORD",
        )
        self.assertIsNotNone(nova_ctx)
        self.assertEqual(nova_ctx["order_id"], "ORD-5520")
        self.assertIn("Nova Studio Monitor Speakers", nova_ctx["item_name"])

        # 3. Under Aura D2C, returns None (no account exists)
        aura_ctx = get_relevant_context(
            client_brand="Aura D2C",
            customer_email=email,
            issue_type="ORD",
        )
        self.assertIsNone(aura_ctx)

    def test_rohan_acc_ticket_excludes_joggers_shipment(self):
        """
        Brief scenario: Rohan's 2FA lockout (ACC) under UrbanFit must NOT
        display his joggers shipping order as active context.
        """
        ctx = get_relevant_context(
            client_brand="UrbanFit",
            customer_email="rohan.kapoor@novabanking.com",
            issue_type="ACC",
        )
        self.assertIsNone(ctx)

    # -------------------------------------------------------------------------
    # 5. Meera Iyer / Aura D2C (PAY)
    # -------------------------------------------------------------------------

    def test_meera_pay_ticket_returns_checkout_hold(self):
        """Meera's checkout payment delay (PAY) must return her pending payment hold context."""
        ctx = get_relevant_context(
            client_brand="Aura D2C",
            customer_email="meera.iyer@cloudcart.dev",
            issue_type="PAY",
        )
        self.assertIsNotNone(ctx)
        self.assertEqual(ctx["order_id"], "ORD-4821")
        self.assertIn("Payment Pending", ctx["shipping_status"])

    # -------------------------------------------------------------------------
    # 6. GEN and Fallback Scenarios
    # -------------------------------------------------------------------------

    def test_gen_issue_family_always_returns_none(self):
        """GEN issue family must always return None regardless of customer data."""
        self.assertIsNone(
            get_relevant_context("UrbanFit", "zara.patel@finscale.io", "GEN")
        )
        self.assertIsNone(
            get_relevant_context("Nova Audio", "dev.malhotra@hypergrid.net", "GEN")
        )
        self.assertIsNone(
            get_relevant_context("Aura D2C", "meera.iyer@cloudcart.dev", "GEN")
        )

    def test_none_or_empty_issue_defaults_to_gen_and_returns_none(self):
        """If issue_type is None or empty string, it behaves as GEN and returns None."""
        self.assertIsNone(
            get_relevant_context("UrbanFit", "zara.patel@finscale.io", None)
        )
        self.assertIsNone(
            get_relevant_context("UrbanFit", "zara.patel@finscale.io", "")
        )

    # -------------------------------------------------------------------------
    # 7. Normalization & Edge Cases
    # -------------------------------------------------------------------------

    def test_case_insensitivity_and_whitespace_trimming(self):
        """Brand, email, and issue_type must be normalized."""
        ctx = get_relevant_context(
            client_brand="  urbanfit  ",
            customer_email="  Zara.Patel@Finscale.IO  ",
            issue_type="  ord  ",
        )
        self.assertIsNotNone(ctx)
        self.assertEqual(ctx["order_id"], "ORD-8921")

    def test_nonexistent_brand_or_email_returns_none(self):
        """Missing or unknown parameters return None gracefully."""
        self.assertIsNone(get_relevant_context("UnknownBrand", "zara.patel@finscale.io", "ORD"))
        self.assertIsNone(get_relevant_context("UrbanFit", "nonexistent@example.com", "ORD"))
        self.assertIsNone(get_relevant_context("", "zara.patel@finscale.io", "ORD"))
        self.assertIsNone(get_relevant_context("UrbanFit", "", "ORD"))

    # -------------------------------------------------------------------------
    # 8. Backward Compatibility: get_order_context(customer_email)
    # -------------------------------------------------------------------------

    def test_legacy_get_order_context(self):
        """Ensure get_order_context(email) works for existing callers."""
        zara_ctx = get_order_context("zara.patel@finscale.io")
        self.assertIsNotNone(zara_ctx)
        self.assertEqual(zara_ctx["order_id"], "ORD-8921")

        dev_ctx = get_order_context("dev.malhotra@hypergrid.net")
        self.assertIsNotNone(dev_ctx)
        self.assertEqual(dev_ctx["order_id"], "SUB-DEV-902")

        # Case-insensitive
        dev_ctx_case = get_order_context(" DEV.MALHOTRA@HYPERGRID.NET ")
        self.assertIsNotNone(dev_ctx_case)
        self.assertEqual(dev_ctx_case["order_id"], "SUB-DEV-902")

        # Unknown email
        self.assertIsNone(get_order_context("unknown@example.com"))
        self.assertIsNone(get_order_context(""))
        self.assertIsNone(get_order_context(None))


if __name__ == "__main__":
    unittest.main()
