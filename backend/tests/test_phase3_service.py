"""
Unit tests for Phase 3: Service Layer functions in app.service.
Tests issue classification, client code derivation, structured ID generation,
retry loop concurrency, issue type correction, and customer history retrieval.
Uses an in-memory SQLite database for complete isolation.
"""

import unittest
from unittest.mock import patch
from fastapi import HTTPException
from sqlalchemy import create_engine
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base
from app.models import Ticket
from app.schemas import TicketCreateRequest
from app import repository, service


class TestPhase3Service(unittest.TestCase):
    def setUp(self):
        """Create a fresh in-memory database and session for every test."""
        self.engine = create_engine(
            "sqlite:///:memory:",
            connect_args={"check_same_thread": False},
            poolclass=StaticPool,
        )
        Base.metadata.create_all(bind=self.engine)
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
        self.db = self.SessionLocal()

    def tearDown(self):
        """Clean up the session and drop tables."""
        self.db.close()
        Base.metadata.drop_all(bind=self.engine)

    # -------------------------------------------------------------------------
    # 1. Issue Classification & Weighted Scorer Tests
    # -------------------------------------------------------------------------

    def test_classify_issue_worked_examples(self):
        """Verify design doc worked examples match expected classifications."""
        # Example 1: Webhook + refund -> INT wins decisively over PAY
        int_res = service.classify_issue(
            subject="Refund webhook returns HTTP 500",
            description="webhook events failing"
        )
        self.assertEqual(int_res, "INT")

        # Example 2: Billing portal not loading -> PAY wins
        pay_res = service.classify_issue(
            subject="Billing portal not loading",
            description="screen hangs on spinner"
        )
        self.assertEqual(pay_res, "PAY")

        # Example 3: CSV export with lambda timeout -> ANA
        ana_res = service.classify_issue(
            subject="Lambda timeout on CSV export",
            description="Exporting Q3 report returns empty file"
        )
        self.assertEqual(ana_res, "ANA")

    def test_classify_issue_all_taxonomy_families(self):
        """Verify representative keywords for each of the 7 specific families."""
        cases = [
            ("CSV export failure", "Q3 analytics dashboard data empty", "ANA"),
            ("Webhook rate limit", "HTTP 429 from partner endpoint integration", "INT"),
            ("2FA lockout", "Cannot login with verification code, locked out", "ACC"),
            ("Charge dispute", "Stripe invoice payment transaction failed", "PAY"),
            ("Tracking number missing", "Order shipment delivery package lost", "ORD"),
            ("Application crash", "Fatal bug and error on startup, not working", "TEC"),
            ("Sizing guide inquiry", "Product information and catalog fit specifications", "PRD"),
        ]
        for subject, desc, expected in cases:
            with self.subTest(subject=subject, expected=expected):
                result = service.classify_issue(subject, desc)
                self.assertEqual(result, expected)

    def test_classify_issue_subject_double_weight(self):
        """Subject matches count 2x, so subject keyword can override conflicting description keyword."""
        # Subject has PRD ("sizing", wt 3 -> 6 pts)
        # Description has PAY ("refund", wt 2 -> 2 pts)
        result = service.classify_issue(
            subject="Sizing question for jacket",
            description="I might need a refund if it does not fit"
        )
        self.assertEqual(result, "PRD")

    def test_classify_issue_below_threshold_returns_gen(self):
        """Texts with no taxonomy keywords or score < MINIMUM_SCORE return GEN."""
        self.assertEqual(service.classify_issue("Hello", "Need some general help"), "GEN")
        self.assertEqual(service.classify_issue("", ""), "GEN")
        # Single weight-1 word in description only -> score = 1 < MINIMUM_SCORE (2) -> GEN
        self.assertEqual(service.classify_issue("Hi there", "Small issue"), "GEN")

    def test_classify_issue_tie_break_order(self):
        """When two categories tie with equal max score, TIE_BREAK_ORDER decides."""
        # ANA vs INT: ANA is 1st in tie-break order, INT is 2nd.
        # "export" (ANA, wt 2) in subject -> 4 pts
        # "endpoint" (INT, wt 2) in subject -> 4 pts
        result = service.classify_issue(
            subject="Export endpoint failure",
            description="something happened"
        )
        self.assertEqual(result, "ANA")

    # -------------------------------------------------------------------------
    # 2. Client Code Resolution Tests
    # -------------------------------------------------------------------------

    def test_get_client_code_static_map(self):
        """Static map resolves known brands case-insensitively."""
        self.assertEqual(service.get_client_code(self.db, "UrbanFit"), "URB")
        self.assertEqual(service.get_client_code(self.db, "urbanfit"), "URB")
        self.assertEqual(service.get_client_code(self.db, "Nova Audio"), "NOV")
        self.assertEqual(service.get_client_code(self.db, "Aura D2C"), "AUR")
        self.assertEqual(service.get_client_code(self.db, "ThreadCo"), "THR")
        self.assertEqual(service.get_client_code(self.db, "Zen Botanics"), "ZEN")
        self.assertEqual(service.get_client_code(self.db, "Blaze"), "BLA")

    def test_get_client_code_dynamic_generation_unknown_brand(self):
        """Unknown brand derives candidate code from name."""
        code = service.get_client_code(self.db, "Kite Commerce")
        self.assertEqual(code, "KIT")

    def test_get_client_code_collision_handling(self):
        """When candidate code is already taken by another brand, digit suffixes are tried."""
        # Brand A claims "KIT"
        payload_a = TicketCreateRequest(
            customer_name="User A", customer_email="a@test.com",
            subject="General question", description="Help", client_brand="KitchenWare"
        )
        repository.create_ticket(self.db, "TKT-KIT-GEN-0001", payload_a)

        # Brand B ("Kite Commerce") candidate "KIT" collides -> should fallback to "KI1"
        code_b = service.get_client_code(self.db, "Kite Commerce")
        self.assertEqual(code_b, "KI1")

    def test_get_client_code_persists_via_db(self):
        """Once a structured ticket exists for an unknown brand, DB lookup reuses the exact same code."""
        # First ticket for unknown brand "LuxeFashion" -> derives "LUX"
        code1 = service.get_client_code(self.db, "LuxeFashion")
        self.assertEqual(code1, "LUX")

        payload = TicketCreateRequest(
            customer_name="Luxe User", customer_email="luxe@test.com",
            subject="Help", description="Help desc", client_brand="LuxeFashion"
        )
        repository.create_ticket(self.db, f"TKT-{code1}-GEN-0001", payload)

        # Subsequent call uses DB lookup and gets "LUX"
        code2 = service.get_client_code(self.db, "LuxeFashion")
        self.assertEqual(code2, "LUX")

    # -------------------------------------------------------------------------
    # 3. Structured Ticket ID Generation Tests
    # -------------------------------------------------------------------------

    def test_generate_structured_ticket_id(self):
        """Verifies format TKT-{CLIENT}-{ISSUE}-{SEQ:04d} and per-brand/issue sequence."""
        # First ticket for UrbanFit INT
        t_id_1, seq_1 = service.generate_structured_ticket_id(self.db, "UrbanFit", "INT")
        self.assertEqual(t_id_1, "TKT-URB-INT-0001")
        self.assertEqual(seq_1, 1)

        # Persist a ticket with that ID and sequence
        payload = TicketCreateRequest(
            customer_name="Zara", customer_email="zara@test.com",
            subject="Webhook", description="Webhook", client_brand="UrbanFit"
        )
        repository.create_ticket(self.db, t_id_1, payload, "INT", "INT", seq_1)

        # Second ticket for UrbanFit INT should be 0002
        t_id_2, seq_2 = service.generate_structured_ticket_id(self.db, "UrbanFit", "INT")
        self.assertEqual(t_id_2, "TKT-URB-INT-0002")
        self.assertEqual(seq_2, 2)

        # Nova Audio INT should start at 0001
        t_id_nova, seq_nova = service.generate_structured_ticket_id(self.db, "Nova Audio", "INT")
        self.assertEqual(t_id_nova, "TKT-NOV-INT-0001")
        self.assertEqual(seq_nova, 1)

    # -------------------------------------------------------------------------
    # 4. create_new_ticket & Concurrency Retry Loop Tests
    # -------------------------------------------------------------------------

    def test_create_new_ticket_success(self):
        """create_new_ticket auto-classifies, generates structured ID, and returns response."""
        payload = TicketCreateRequest(
            customer_name="Priya Nair",
            customer_email="priya.nair@datalens.ai",
            subject="Lambda timeout on CSV export",
            description="Q3 reporting dashboard data is empty",
            client_brand="Aura D2C",
            channel="Email"
        )
        resp = service.create_new_ticket(self.db, payload)

        self.assertEqual(resp.ticket_id, "TKT-AUR-ANA-0001")
        self.assertEqual(resp.status, "Open")
        self.assertEqual(resp.client_brand, "Aura D2C")
        self.assertEqual(resp.issue_type, "ANA")
        self.assertEqual(resp.intake_issue_type, "ANA")
        self.assertEqual(resp.ticket_sequence, 1)

    def test_create_new_ticket_retry_loop_on_integrity_error(self):
        """Simulate concurrent collision on first attempt: retry loop succeeds on attempt 2."""
        payload = TicketCreateRequest(
            customer_name="Zara Patel",
            customer_email="zara@test.com",
            subject="Webhook failure",
            description="500 error",
            client_brand="UrbanFit"
        )

        real_create_ticket = repository.create_ticket
        attempt_count = 0

        def flaky_create_ticket(*args, **kwargs):
            nonlocal attempt_count
            attempt_count += 1
            if attempt_count == 1:
                # Simulate concurrent transaction claiming sequence 1
                raise IntegrityError("mock UNIQUE violation", params=None, orig=Exception())
            return real_create_ticket(*args, **kwargs)

        with patch("app.repository.create_ticket", side_effect=flaky_create_ticket):
            resp = service.create_new_ticket(self.db, payload)
            self.assertEqual(attempt_count, 2)
            self.assertEqual(resp.ticket_id, "TKT-URB-INT-0001")

    def test_create_new_ticket_retries_exhausted_raises_503(self):
        """When all MAX_SEQUENCE_RETRIES fail with IntegrityError, HTTP 503 is raised."""
        payload = TicketCreateRequest(
            customer_name="Zara Patel",
            customer_email="zara@test.com",
            subject="Webhook failure",
            description="500 error",
            client_brand="UrbanFit"
        )

        def always_fail(*args, **kwargs):
            raise IntegrityError("mock UNIQUE violation", params=None, orig=Exception())

        with patch("app.repository.create_ticket", side_effect=always_fail):
            with self.assertRaises(HTTPException) as ctx:
                service.create_new_ticket(self.db, payload)
            self.assertEqual(ctx.exception.status_code, 503)

    # -------------------------------------------------------------------------
    # 5. Issue Type Correction Tests
    # -------------------------------------------------------------------------

    def test_correct_issue_type_success(self):
        """Agent corrects issue_type; ticket_id and intake_issue_type remain immutable."""
        payload = TicketCreateRequest(
            customer_name="Meera Joshi",
            customer_email="meera@example.com",
            subject="Payment issue",
            description="Card charge declined",
            client_brand="Aura D2C"
        )
        created = service.create_new_ticket(self.db, payload)
        self.assertEqual(created.ticket_id, "TKT-AUR-PAY-0001")
        self.assertEqual(created.intake_issue_type, "PAY")
        self.assertEqual(created.issue_type, "PAY")

        # Correct issue type from PAY to INT
        updated_ticket = service.correct_issue_type(self.db, created.ticket_id, "INT")

        self.assertEqual(updated_ticket.ticket_id, "TKT-AUR-PAY-0001")  # IMMUTABLE
        self.assertEqual(updated_ticket.intake_issue_type, "PAY")         # IMMUTABLE
        self.assertEqual(updated_ticket.issue_type, "INT")                # MUTATED

    def test_correct_issue_type_invalid_code_raises_400(self):
        """Invalid issue taxonomy code raises HTTP 400 Bad Request."""
        payload = TicketCreateRequest(
            customer_name="Test", customer_email="test@example.com",
            subject="Test", description="Test", client_brand="UrbanFit"
        )
        created = service.create_new_ticket(self.db, payload)

        with self.assertRaises(HTTPException) as ctx:
            service.correct_issue_type(self.db, created.ticket_id, "INVALID_CODE")
        self.assertEqual(ctx.exception.status_code, 400)

    def test_correct_issue_type_nonexistent_ticket_raises_404(self):
        """Non-existent ticket ID raises HTTP 404 Not Found."""
        with self.assertRaises(HTTPException) as ctx:
            service.correct_issue_type(self.db, "TKT-NON-EXIST-0001", "INT")
        self.assertEqual(ctx.exception.status_code, 404)

    # -------------------------------------------------------------------------
    # 6. Customer History Retrieval Tests
    # -------------------------------------------------------------------------

    def test_get_customer_history(self):
        """Returns prior tickets under the client brand and excludes current ticket."""
        email = "priya@example.com"
        p1 = TicketCreateRequest(
            customer_name="Priya", customer_email=email,
            subject="Analytics export", description="CSV empty", client_brand="Aura D2C"
        )
        t1 = service.create_new_ticket(self.db, p1)

        p2 = TicketCreateRequest(
            customer_name="Priya", customer_email=email,
            subject="Payment failure", description="Declined card", client_brand="Aura D2C"
        )
        t2 = service.create_new_ticket(self.db, p2)

        # Cross-brand ticket for same customer under UrbanFit
        p3 = TicketCreateRequest(
            customer_name="Priya", customer_email=email,
            subject="Sizing question", description="Size M", client_brand="UrbanFit"
        )
        service.create_new_ticket(self.db, p3)

        # Query history for Priya under Aura D2C, excluding t2
        history = service.get_customer_history(
            self.db,
            client_brand="Aura D2C",
            customer_email=email,
            exclude_ticket_id=t2.ticket_id
        )

        self.assertEqual(len(history), 1)
        self.assertEqual(history[0].ticket_id, t1.ticket_id)
        self.assertEqual(history[0].intake_issue_type, "ANA")


if __name__ == "__main__":
    unittest.main()
