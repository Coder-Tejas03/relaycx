"""
Concurrency Stress Test for RelayCX Structured Ticket ID Generation.
Simulates 10 simultaneous requests attempting to create tickets under the exact same
(client_brand, issue_type) partition, verifying that:
1. No duplicate ticket IDs are generated.
2. No duplicate (client_brand, issue_type, ticket_sequence) tuples exist.
3. Concurrency retry loop catches IntegrityError cleanly without unhandled crashes.
4. All requests either succeed (HTTP 201) or cleanly return service unavailable (HTTP 503).
"""

import os
import tempfile
import unittest
from concurrent.futures import ThreadPoolExecutor, as_completed
from fastapi import HTTPException
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.database import Base
from app.models import Ticket, Note
from app import service
from app.schemas import TicketCreateRequest


class TestConcurrentCreation(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp_db = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
        cls.temp_db.close()
        cls.test_engine = create_engine(
            f"sqlite:///{cls.temp_db.name}",
            connect_args={"check_same_thread": False, "timeout": 30},
        )
        cls.TestSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=cls.test_engine)
        Base.metadata.create_all(bind=cls.test_engine)
        cls.client = TestClient(app)

    @classmethod
    def tearDownClass(cls):
        cls.test_engine.dispose()
        if os.path.exists(cls.temp_db.name):
            try:
                os.unlink(cls.temp_db.name)
            except OSError:
                pass

    def test_01_simultaneous_ticket_creation_uniqueness(self):
        """
        Fire 10 concurrent ticket creation requests for UrbanFit + ORD.
        Validate zero duplicate IDs, zero duplicate sequences, and clean error handling.
        """
        num_concurrent = 10
        brand = "UrbanFit"
        created_results = []
        status_codes = []

        def create_ticket_worker(worker_id):
            db = self.TestSessionLocal()
            worker_payload = TicketCreateRequest(
                customer_name=f"Concurrent Test #{worker_id}",
                customer_email=f"concurrent.test.{worker_id}@example.com",
                client_brand=brand,
                channel="Email",
                subject=f"Order delivery transit concurrency test #{worker_id}",
                description="High volume concurrency test checking simultaneous order sequence allocation.",
            )
            try:
                ticket_resp = service.create_new_ticket(db, worker_payload)
                return 201, {
                    "ticket_id": ticket_resp.ticket_id,
                    "ticket_sequence": ticket_resp.ticket_sequence,
                }
            except HTTPException as e:
                return e.status_code, e.detail
            except Exception as e:
                return 500, str(e)
            finally:
                db.close()

        with ThreadPoolExecutor(max_workers=num_concurrent) as executor:
            futures = [executor.submit(create_ticket_worker, i) for i in range(num_concurrent)]
            for f in as_completed(futures):
                code, body = f.result()
                status_codes.append(code)
                if code == 201:
                    created_results.append(body)

        # Print concurrency test summary
        print(f"\n[Concurrency Test] Fired {num_concurrent} requests: {status_codes.count(201)} succeeded (201), {status_codes.count(503)} retries exhausted (503).")

        # Invariant 1: No server 500 errors or unhandled database crashes
        for code in status_codes:
            self.assertIn(
                code,
                [201, 503],
                f"Unexpected status code {code}. Expected 201 Created or 503 Clean Retry Exhaustion."
            )

        # Invariant 2: At least some requests succeeded
        self.assertGreater(len(created_results), 0, "Expected at least one ticket created successfully")

        # Invariant 3: All generated ticket IDs are strictly unique
        created_ids = [t["ticket_id"] for t in created_results]
        self.assertEqual(
            len(created_ids),
            len(set(created_ids)),
            f"Duplicate ticket IDs generated during concurrent execution: {created_ids}"
        )

        # Invariant 4: All generated sequences are strictly unique
        created_seqs = [t["ticket_sequence"] for t in created_results]
        self.assertEqual(
            len(created_seqs),
            len(set(created_seqs)),
            f"Duplicate sequences generated during concurrent execution: {created_seqs}"
        )

        # Invariant 5: Verify records in DB match
        db = self.TestSessionLocal()
        try:
            for t_data in created_results:
                t_id = t_data["ticket_id"]
                db_record = db.query(Ticket).filter(Ticket.ticket_id == t_id).first()
                self.assertIsNotNone(db_record, f"Ticket {t_id} missing in database")
                self.assertEqual(db_record.client_brand, brand)
                self.assertEqual(db_record.ticket_sequence, t_data["ticket_sequence"])
        finally:
            db.close()


if __name__ == "__main__":
    unittest.main()
