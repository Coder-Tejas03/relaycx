"""
Unit tests for Phase 2: Repository Layer functions in app.repository.
Tests all functions in isolation using an in-memory SQLite database.
"""

import unittest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database import Base
from app.models import Ticket, Note
from app.schemas import TicketCreateRequest
from app import repository


class TestPhase2Repository(unittest.TestCase):
    def setUp(self):
        """Create a fresh in-memory database and session for every test."""
        self.engine = create_engine(
            "sqlite:///:memory:",
            connect_args={"check_same_thread": False}
        )
        Base.metadata.create_all(bind=self.engine)
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
        self.db = self.SessionLocal()

    def tearDown(self):
        """Clean up the session and drop tables."""
        self.db.close()
        Base.metadata.drop_all(bind=self.engine)

    def test_create_ticket_with_defaults(self):
        """Test create_ticket with default classification and sequence values."""
        payload = TicketCreateRequest(
            customer_name="Test Customer",
            customer_email="test@urbanfit.com",
            subject="Cannot checkout",
            description="Payment gateway timeout",
            client_brand="UrbanFit",
            channel="Email"
        )
        ticket = repository.create_ticket(
            db=self.db,
            ticket_id="TKT-URB-GEN-0001",
            data=payload
        )
        self.assertIsNotNone(ticket.id)
        self.assertEqual(ticket.ticket_id, "TKT-URB-GEN-0001")
        self.assertEqual(ticket.status, "Open")
        self.assertEqual(ticket.client_brand, "UrbanFit")
        self.assertEqual(ticket.channel, "Email")
        self.assertEqual(ticket.intake_issue_type, "GEN")
        self.assertEqual(ticket.issue_type, "GEN")
        self.assertIsNone(ticket.ticket_sequence)

    def test_create_ticket_with_explicit_fields(self):
        """Test create_ticket with explicit intake_issue_type, issue_type, and sequence."""
        payload = TicketCreateRequest(
            customer_name="Priya Nair",
            customer_email="priya.nair@datalens.ai",
            subject="CSV export empty",
            description="Exporting Q3 report returns empty file",
            client_brand="Aura D2C",
            channel="Portal"
        )
        ticket = repository.create_ticket(
            db=self.db,
            ticket_id="TKT-AUR-ANA-0001",
            data=payload,
            intake_issue_type="ANA",
            issue_type="ANA",
            ticket_sequence=1
        )
        self.assertEqual(ticket.intake_issue_type, "ANA")
        self.assertEqual(ticket.issue_type, "ANA")
        self.assertEqual(ticket.ticket_sequence, 1)

    def test_get_next_sequence_incrementing(self):
        """Test sequence starts at 1 and increments per (client_brand, issue_type)."""
        # Empty DB returns 1
        seq1 = repository.get_next_sequence(self.db, "UrbanFit", "INT")
        self.assertEqual(seq1, 1)

        # Insert a ticket with sequence 1
        payload = TicketCreateRequest(
            customer_name="Zara Patel",
            customer_email="zara@test.com",
            subject="Webhook failure",
            description="500 error",
            client_brand="UrbanFit"
        )
        repository.create_ticket(
            db=self.db,
            ticket_id="TKT-URB-INT-0001",
            data=payload,
            intake_issue_type="INT",
            issue_type="INT",
            ticket_sequence=1
        )

        # Next sequence should be 2
        seq2 = repository.get_next_sequence(self.db, "UrbanFit", "INT")
        self.assertEqual(seq2, 2)

        # Different brand should still be 1
        seq_aura = repository.get_next_sequence(self.db, "Aura D2C", "INT")
        self.assertEqual(seq_aura, 1)

        # Different issue family for same brand should still be 1
        seq_acc = repository.get_next_sequence(self.db, "UrbanFit", "ACC")
        self.assertEqual(seq_acc, 1)

    def test_get_next_sequence_preserves_intake_history(self):
        """Test that get_next_sequence accounts for intake_issue_type even if issue_type was updated."""
        payload = TicketCreateRequest(
            customer_name="Dev Singh",
            customer_email="dev@example.com",
            subject="API rate limit",
            description="HTTP 429",
            client_brand="Nova Audio"
        )
        ticket = repository.create_ticket(
            db=self.db,
            ticket_id="TKT-NOV-INT-0001",
            data=payload,
            intake_issue_type="INT",
            issue_type="INT",
            ticket_sequence=1
        )

        # Now update issue_type to PAY
        repository.update_issue_type(self.db, ticket, "PAY")

        # Next sequence for INT should still be 2 (because TKT-NOV-INT-0001 took sequence 1 at intake)
        seq_int = repository.get_next_sequence(self.db, "Nova Audio", "INT")
        self.assertEqual(seq_int, 2)

    def test_get_client_code_from_db(self):
        """Test extracting client code from existing tickets."""
        # No tickets -> None
        self.assertIsNone(repository.get_client_code_from_db(self.db, "UrbanFit"))

        # Legacy ticket format (TKT-A82F10) -> Should NOT return as client code
        legacy_ticket = Ticket(
            ticket_id="TKT-A82F10",
            customer_name="Legacy User",
            customer_email="legacy@example.com",
            subject="Old ticket",
            description="Old description",
            client_brand="UrbanFit"
        )
        self.db.add(legacy_ticket)
        self.db.commit()
        self.assertIsNone(repository.get_client_code_from_db(self.db, "UrbanFit"))

        # Add a structured ticket -> Returns "URB"
        structured_ticket = Ticket(
            ticket_id="TKT-URB-INT-0001",
            customer_name="New User",
            customer_email="new@example.com",
            subject="Structured ticket",
            description="Structured description",
            client_brand="UrbanFit"
        )
        self.db.add(structured_ticket)
        self.db.commit()
        self.assertEqual(repository.get_client_code_from_db(self.db, "UrbanFit"), "URB")

    def test_is_client_code_taken(self):
        """Test candidate code collision detection across brands."""
        # Code not used anywhere -> False
        self.assertFalse(repository.is_client_code_taken(self.db, "URB", "UrbanFit"))
        self.assertFalse(repository.is_client_code_taken(self.db, "URB", "OtherBrand"))

        # Add ticket for UrbanFit with code URB
        ticket = Ticket(
            ticket_id="TKT-URB-INT-0001",
            customer_name="User",
            customer_email="u@example.com",
            subject="Test",
            description="Test",
            client_brand="UrbanFit"
        )
        self.db.add(ticket)
        self.db.commit()

        # Code URB for UrbanFit itself -> False (it's their own code)
        self.assertFalse(repository.is_client_code_taken(self.db, "URB", "UrbanFit"))

        # Code URB for another brand -> True (collision!)
        self.assertTrue(repository.is_client_code_taken(self.db, "URB", "UrbanBoutique"))

    def test_update_issue_type(self):
        """Test updating issue_type preserves ticket_id and intake_issue_type."""
        payload = TicketCreateRequest(
            customer_name="Meera Joshi",
            customer_email="meera@example.com",
            subject="Refund webhook failed",
            description="Returns HTTP 500",
            client_brand="Aura D2C"
        )
        ticket = repository.create_ticket(
            db=self.db,
            ticket_id="TKT-AUR-ANA-0002",
            data=payload,
            intake_issue_type="ANA",
            issue_type="ANA",
            ticket_sequence=2
        )
        initial_updated_at = ticket.updated_at

        # Agent corrects classification to INT
        updated = repository.update_issue_type(self.db, ticket, "INT")

        self.assertEqual(updated.ticket_id, "TKT-AUR-ANA-0002")  # IMMUTABLE
        self.assertEqual(updated.intake_issue_type, "ANA")         # IMMUTABLE
        self.assertEqual(updated.issue_type, "INT")                # MUTATED
        self.assertEqual(updated.ticket_sequence, 2)              # IMMUTABLE
        self.assertGreaterEqual(updated.updated_at, initial_updated_at)

    def test_get_tickets_by_customer(self):
        """Test customer history query with brand isolation and ticket exclusion."""
        email = "rohan@example.com"

        # Create 2 tickets under UrbanFit
        p1 = TicketCreateRequest(
            customer_name="Rohan", customer_email=email,
            subject="2FA lockout", description="Cannot login", client_brand="UrbanFit"
        )
        t1 = repository.create_ticket(self.db, "TKT-URB-ACC-0001", p1, "ACC", "ACC", 1)

        p2 = TicketCreateRequest(
            customer_name="Rohan", customer_email=email,
            subject="Sizing question", description="Size M or L", client_brand="UrbanFit"
        )
        t2 = repository.create_ticket(self.db, "TKT-URB-PRD-0001", p2, "PRD", "PRD", 1)

        # Create 1 ticket under Aura D2C for the SAME email (cross-client test)
        p3 = TicketCreateRequest(
            customer_name="Rohan", customer_email=email,
            subject="Face cream shipment", description="Track delivery", client_brand="Aura D2C"
        )
        t3 = repository.create_ticket(self.db, "TKT-AUR-ORD-0001", p3, "ORD", "ORD", 1)

        # Query UrbanFit tickets for Rohan -> Should return 2 tickets, NOT t3
        uf_tickets = repository.get_tickets_by_customer(self.db, "UrbanFit", email)
        self.assertEqual(len(uf_tickets), 2)
        uf_ids = [t.ticket_id for t in uf_tickets]
        self.assertIn("TKT-URB-ACC-0001", uf_ids)
        self.assertIn("TKT-URB-PRD-0001", uf_ids)
        self.assertNotIn("TKT-AUR-ORD-0001", uf_ids)

        # Query with exclude_ticket_id = t1.ticket_id -> Should return only t2
        filtered = repository.get_tickets_by_customer(
            self.db, "UrbanFit", email, exclude_ticket_id=t1.ticket_id
        )
        self.assertEqual(len(filtered), 1)
        self.assertEqual(filtered[0].ticket_id, "TKT-URB-PRD-0001")

        # Query Aura D2C for Rohan -> Should return only t3
        aura_tickets = repository.get_tickets_by_customer(self.db, "Aura D2C", email)
        self.assertEqual(len(aura_tickets), 1)
        self.assertEqual(aura_tickets[0].ticket_id, "TKT-AUR-ORD-0001")

    def test_get_all_tickets_brand_and_email_filters(self):
        """Test get_all_tickets with client_brand and customer_email filtering."""
        p1 = TicketCreateRequest(
            customer_name="Alice", customer_email="alice@test.com",
            subject="Sub 1", description="Desc 1", client_brand="UrbanFit"
        )
        p2 = TicketCreateRequest(
            customer_name="Bob", customer_email="bob@test.com",
            subject="Sub 2", description="Desc 2", client_brand="Nova Audio"
        )
        p3 = TicketCreateRequest(
            customer_name="Alice", customer_email="alice@test.com",
            subject="Sub 3", description="Desc 3", client_brand="Nova Audio"
        )
        repository.create_ticket(self.db, "TKT-URB-GEN-0001", p1)
        repository.create_ticket(self.db, "TKT-NOV-GEN-0001", p2)
        repository.create_ticket(self.db, "TKT-NOV-GEN-0002", p3)

        # Filter by client_brand="UrbanFit"
        uf_all = repository.get_all_tickets(self.db, client_brand="UrbanFit")
        self.assertEqual(len(uf_all), 1)
        self.assertEqual(uf_all[0].client_brand, "UrbanFit")

        # Filter by customer_email="alice@test.com"
        alice_all = repository.get_all_tickets(self.db, customer_email="alice@test.com")
        self.assertEqual(len(alice_all), 2)

        # Combined filter: customer_email="alice@test.com" AND client_brand="Nova Audio"
        alice_nov = repository.get_all_tickets(
            self.db, client_brand="Nova Audio", customer_email="alice@test.com"
        )
        self.assertEqual(len(alice_nov), 1)
        self.assertEqual(alice_nov[0].ticket_id, "TKT-NOV-GEN-0002")


if __name__ == "__main__":
    unittest.main()
