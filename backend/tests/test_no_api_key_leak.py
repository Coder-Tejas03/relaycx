"""
Security & Data Sanitization Test: Prevention of API Key Leakage.
Verifies that developer account operational contexts never expose live API keys,
secret tokens, or credential strings in both the integration layer and HTTP responses.
"""

import unittest
import json
from urllib.parse import quote
from fastapi.testclient import TestClient
from app.main import app
from app.integrations.commerce_provider import (
    SEEDED_CUSTOMER_CONTEXTS,
    get_relevant_context,
)


class TestNoApiKeyLeak(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client = TestClient(app)

    def test_dev_malhotra_context_does_not_contain_api_key(self):
        """
        Verify Dev Malhotra's developer context does not contain any 'key_live'
        or credential-like strings in any field.
        """
        ctx = get_relevant_context("Nova Audio", "dev.malhotra@hypergrid.net", "INT")
        self.assertIsNotNone(ctx)

        # Operational fields must still be present
        self.assertEqual(ctx.get("account_type"), "developer")
        self.assertEqual(ctx.get("order_id"), "SUB-DEV-902")
        self.assertIn("Rate Limit Throttled", ctx.get("shipping_status", ""))

        # No credential leak in tracking_number or any other field
        tracking = ctx.get("tracking_number")
        self.assertFalse(
            tracking and "key_live" in str(tracking).lower(),
            f"tracking_number leaked an API key: {tracking}"
        )

        # Deep scan all values in the dictionary
        def scan_for_keys(obj):
            if isinstance(obj, dict):
                for k, v in obj.items():
                    self.assertNotIn("api_key", k.lower())
                    scan_for_keys(v)
            elif isinstance(obj, (list, tuple)):
                for item in obj:
                    scan_for_keys(item)
            elif isinstance(obj, str):
                self.assertNotIn("key_live", obj.lower(), f"Leaked live key string in value: {obj}")

        scan_for_keys(ctx)

    def test_all_seeded_contexts_free_of_live_keys(self):
        """
        Exhaustively verify that NO customer entry across all brands contains
        live API keys or secret tokens.
        """
        for (brand, email), data in SEEDED_CUSTOMER_CONTEXTS.items():
            serialized = json.dumps(data)
            self.assertNotIn(
                "key_live",
                serialized.lower(),
                f"Customer context for ({brand}, {email}) contains 'key_live'"
            )

    def test_http_endpoint_does_not_expose_api_key(self):
        """
        Verify the HTTP context endpoint response payload for developer accounts
        contains zero API key credentials or 'Live API Key' markers.
        """
        url = f"/api/customers/{quote('Nova Audio')}/{quote('dev.malhotra@hypergrid.net')}/context?issue_type=INT"
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        raw_text = response.text
        self.assertNotIn("key_live", raw_text.lower())
        self.assertNotIn("live api key", raw_text.lower())

        data = response.json()
        self.assertEqual(data["order_id"], "SUB-DEV-902")
        self.assertEqual(data["account_type"], "developer")
        self.assertNotIn("key_live", str(data).lower())


if __name__ == "__main__":
    unittest.main()
