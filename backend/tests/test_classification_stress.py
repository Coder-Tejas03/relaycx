"""
Stress and Robustness Tests for RelayCX Issue Taxonomy Classifier.
Exhaustively validates weighted scoring, multi-signal resolution, tie-breaking priority,
case-insensitivity, whitespace tolerance, and deterministic behavior across 30+ realistic inputs.
"""

import unittest
from app.service import classify_issue, ISSUE_TAXONOMY, VALID_ISSUE_TYPES, TIE_BREAK_ORDER


class TestClassificationStress(unittest.TestCase):
    def test_01_all_families_reachable(self):
        """Verify that every single valid taxonomy family can be produced by the classifier."""
        family_test_inputs = {
            "ORD": ("Order shipment package tracking", "Where is my delivered package?"),
            "PAY": ("Stripe refund payment dispute", "Charge on credit card was billed twice"),
            "ACC": ("Account 2FA lockout", "User password login verification code failed"),
            "TEC": ("App crash on launch", "Software malfunction bug not working"),
            "INT": ("Webhook endpoint returning HTTP 500", "API rate limit 429 payload integration"),
            "ANA": ("CSV export analytics lambda timeout", "Reporting dashboard empty file for date range"),
            "PRD": ("Product sizing guide catalog", "Size guide measurements fit specifications"),
            "GEN": ("General feedback", "Thanks for your help with the team"),
        }
        for expected_family, (subject, desc) in family_test_inputs.items():
            result = classify_issue(subject, desc)
            self.assertEqual(
                result,
                expected_family,
                f"Expected {expected_family} for '{subject}', got {result}"
            )

    def test_02_realistic_multi_signal_scenarios(self):
        """
        Test realistic scenarios containing keywords from multiple categories.
        Verifies weighted scoring and tie-breaking resolve deterministically.
        """
        cases = [
            # INT vs PAY: 'webhook' (3*2=6) + 'http 500' (2*2=4) = 10 vs 'refund' (2*2=4). INT wins.
            ("Refund webhook returns HTTP 500", "Stripe payment sync failed", "INT"),
            # ACC vs PAY: '2fa' (3*2=6) + 'lockout' (3*2=6) = 12 vs 'billing' (2*2=4). ACC wins.
            ("Customer 2FA lockout on billing portal", "Cannot access credit card settings", "ACC"),
            # ANA vs ORD: 'csv' (3*2=6) + 'export' (2*2=4) + 'analytics' (3*2=6) = 16 vs 'order' (2*2=4). ANA wins.
            ("CSV export lambda timeout on order analytics", "Empty file downloaded for date range", "ANA"),
            # INT vs PAY: 'api' (2*2=4) + '429' (3*2=6) = 10 vs 'payment' (2*2=4) + 'gateway' (1*2=2). INT wins.
            ("Payment gateway API returning 429", "Rate limit throttled on checkout requests", "INT"),
            # ORD vs PRD: 'order' (2*2=4) + 'shipment' (2*2=4) + 'tracking' (2*2=4) = 12 vs 'product' (2*1=2). ORD wins.
            ("Order shipment tracking unavailable", "Package tracking number not found", "ORD"),
            # PRD: 'sizing' (3*2=6) + 'size guide' (3*2=6) + 'fit' (1*2=2) = 14
            ("Product sizing information incorrect", "Size guide does not match received garment fit", "PRD"),
            # ANA: 'dashboard data' (2*2=4) + 'report' (1*2=2) + 'export' (2*2=4) = 10
            ("Dashboard report export failing", "Monthly analytics export returns 0 bytes", "ANA"),
        ]

        for subject, desc, expected in cases:
            actual = classify_issue(subject, desc)
            self.assertEqual(
                actual,
                expected,
                f"Failed for subject='{subject}': expected {expected}, got {actual}"
            )

    def test_03_tie_break_hierarchy(self):
        """
        Verify that exact equal scores break according to TIE_BREAK_ORDER:
        ['ANA', 'INT', 'ACC', 'PAY', 'ORD', 'TEC', 'PRD', 'GEN']
        """
        # ANA vs INT tie: 'export' (2*2=4) vs 'api' (2*2=4) -> ANA wins tie-break
        self.assertEqual(classify_issue("export api", ""), "ANA")

        # INT vs PAY tie: 'api' (2*2=4) vs 'refund' (2*2=4) -> INT wins tie-break
        self.assertEqual(classify_issue("api refund", ""), "INT")

        # ACC vs PAY tie: 'login' (2*2=4) vs 'refund' (2*2=4) -> ACC wins tie-break
        self.assertEqual(classify_issue("login refund", ""), "ACC")

        # PAY vs ORD tie: 'refund' (2*2=4) vs 'order' (2*2=4) -> PAY wins tie-break
        self.assertEqual(classify_issue("refund order", ""), "PAY")

        # ORD vs TEC tie: 'order' (2*2=4) vs 'malfunction' (2*2=4) -> ORD wins tie-break
        self.assertEqual(classify_issue("order malfunction", ""), "ORD")

    def test_04_subject_2x_weight_dominates_description(self):
        """
        Verify that keywords in the subject count 2x relative to description.
        Subject 'refund' (2*2=4) should beat description 'sizing' (3*1=3).
        """
        result = classify_issue(
            subject="Refund requested for purchase",
            description="The product sizing was slightly off"
        )
        self.assertEqual(result, "PAY")

    def test_05_ambiguous_and_generic_fallback_to_gen(self):
        """
        Inquiries without sufficient domain keywords must fall back cleanly to GEN.
        """
        generic_inputs = [
            ("Hello", "I have a general question about your services"),
            ("Assistance required", "Could someone from customer support please call me back?"),
            ("Partnership proposal", "We would like to discuss stocking your products in our retail outlets"),
            ("Feedback on packaging", "The new box design looks great"),
            ("", ""),
            ("   ", "   "),
            ("Random inquiry", "Nothing specific, just checking in"),
        ]
        for subj, desc in generic_inputs:
            res = classify_issue(subj, desc)
            self.assertEqual(res, "GEN", f"Expected GEN for '{subj}', got '{res}'")

    def test_06_case_insensitivity_and_whitespace_tolerance(self):
        """
        Test that uppercase, mixed case, and leading/trailing whitespace
        do not alter classification outcomes.
        """
        variations = [
            "WEBHOOK FAILURE HTTP 500",
            "webhook failure http 500",
            "  Webhook Failure HTTP 500  \n",
            "\t\tWEBHOOK failure Http 500\r\n",
        ]
        for var in variations:
            self.assertEqual(classify_issue(var, "Internal server error"), "INT")

    def test_07_http_status_codes(self):
        """Verify HTTP status codes match appropriate families."""
        self.assertEqual(classify_issue("HTTP 429 Too Many Requests", "Throttled"), "INT")
        self.assertEqual(classify_issue("HTTP 500 Internal Server Error", "API gateway error"), "INT")

    def test_08_strictly_deterministic_across_iterations(self):
        """Verify that repeated calls for the exact same input yield identical results."""
        subj = "Webhook delivery failure on Stripe payment charge with 2FA lockout"
        desc = "Rate limit 429 on CSV export"

        first_run = classify_issue(subj, desc)
        for _ in range(50):
            self.assertEqual(classify_issue(subj, desc), first_run)


if __name__ == "__main__":
    unittest.main()
