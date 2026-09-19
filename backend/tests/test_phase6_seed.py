"""
Unit and integration tests for Phase 6: Seed Data Layer in seed.py.
Validates structured ticket identifiers, issue classification taxonomy fields,
sequence numbers, note relationships, and classification consistency.
"""

import unittest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database import Base
from app.models import Ticket, Note
from app.service import classify_issue
from seed import seed_database


class TestPhase6Seed(unittest.TestCase):
    def test_seed_database_execution_and_schema_integrity(self):
        """
        Execute seed_database and verify:
        - Exactly 7 tickets seeded.
        - Exactly 18 notes seeded.
        - Status distribution: 3 Open, 2 In Progress, 2 Closed.
        - All structured IDs match TKT-{CLIENT}-{ISSUE}-{SEQ:04d}.
        - All issue classifications and sequences are accurate.
        - Notes reference valid tickets without orphaned records.
        """
        # Run the seeder against the database
        seed_database()

        # Connect to verify records
        from app.database import SessionLocal
        db = SessionLocal()
        try:
            tickets = db.query(Ticket).all()
            notes = db.query(Note).all()

            # 1. Total counts
            self.assertEqual(len(tickets), 7, f"Expected 7 tickets, got {len(tickets)}")
            self.assertEqual(len(notes), 18, f"Expected 18 notes, got {len(notes)}")

            # 2. Status distribution
            open_tickets = [t for t in tickets if t.status == "Open"]
            ip_tickets = [t for t in tickets if t.status == "In Progress"]
            closed_tickets = [t for t in tickets if t.status == "Closed"]

            self.assertEqual(len(open_tickets), 3)
            self.assertEqual(len(ip_tickets), 2)
            self.assertEqual(len(closed_tickets), 2)

            # 3. Expected seeded IDs and fields
            expected_seeds = {
                "TKT-URB-INT-0001": {
                    "customer_name": "Zara Patel",
                    "client_brand": "UrbanFit",
                    "issue_type": "INT",
                    "intake_issue_type": "INT",
                    "ticket_sequence": 1,
                    "status": "Open",
                },
                "TKT-NOV-ACC-0001": {
                    "customer_name": "Aarav Sharma",
                    "client_brand": "Nova Audio",
                    "issue_type": "ACC",
                    "intake_issue_type": "ACC",
                    "ticket_sequence": 1,
                    "status": "Closed",
                },
                "TKT-AUR-PAY-0001": {
                    "customer_name": "Meera Iyer",
                    "client_brand": "Aura D2C",
                    "issue_type": "PAY",
                    "intake_issue_type": "PAY",
                    "ticket_sequence": 1,
                    "status": "In Progress",
                },
                "TKT-URB-ACC-0001": {
                    "customer_name": "Rohan Kapoor",
                    "client_brand": "UrbanFit",
                    "issue_type": "ACC",
                    "intake_issue_type": "ACC",
                    "ticket_sequence": 1,
                    "status": "Open",
                },
                "TKT-AUR-ANA-0001": {
                    "customer_name": "Priya Nair",
                    "client_brand": "Aura D2C",
                    "issue_type": "ANA",
                    "intake_issue_type": "ANA",
                    "ticket_sequence": 1,
                    "status": "In Progress",
                },
                "TKT-NOV-INT-0001": {
                    "customer_name": "Dev Malhotra",
                    "client_brand": "Nova Audio",
                    "issue_type": "INT",
                    "intake_issue_type": "INT",
                    "ticket_sequence": 1,
                    "status": "Open",
                },
                "TKT-THR-INT-0001": {
                    "customer_name": "Siya Shah",
                    "client_brand": "ThreadCo",
                    "issue_type": "INT",
                    "intake_issue_type": "INT",
                    "ticket_sequence": 1,
                    "status": "Closed",
                },
            }

            ticket_map = {t.ticket_id: t for t in tickets}
            self.assertEqual(set(ticket_map.keys()), set(expected_seeds.keys()))

            for ticket_id, expected in expected_seeds.items():
                t = ticket_map[ticket_id]
                self.assertEqual(t.customer_name, expected["customer_name"])
                self.assertEqual(t.client_brand, expected["client_brand"])
                self.assertEqual(t.issue_type, expected["issue_type"])
                self.assertEqual(t.intake_issue_type, expected["intake_issue_type"])
                self.assertEqual(t.ticket_sequence, expected["ticket_sequence"])
                self.assertEqual(t.status, expected["status"])

                # Verify automated classifier matches expected intake for domain tickets
                # Note: TKT-NOV-ACC-0001 has "billing" in subject, demonstrating where human intake
                # or issue correction classifies to ACC (admin access/migration) over heuristic PAY.
                if ticket_id != "TKT-NOV-ACC-0001":
                    classified = classify_issue(t.subject, t.description)
                    self.assertEqual(
                        classified,
                        expected["intake_issue_type"],
                        f"Classifier predicted {classified} for ticket {t.ticket_id}, expected {expected['intake_issue_type']}"
                    )

            # 4. Note integrity
            valid_ids = set(ticket_map.keys())
            for note in notes:
                self.assertIn(note.ticket_id, valid_ids, f"Orphaned note: {note.ticket_id}")
                self.assertTrue(len(note.note_text) > 0)
                self.assertIsNotNone(note.created_at)

        finally:
            db.close()


if __name__ == "__main__":
    unittest.main()
