"""
Regression test for existing routes and service layer calls with updated repository.py.
Uses in-memory SQLite database to ensure no remote database impact.
"""

import os
import unittest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

# Override database before importing app
from app.database import Base, get_db
from app.main import app

engine = create_engine(
    "sqlite:///:memory:",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


class TestExistingRoutesRegression(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        Base.metadata.create_all(bind=engine)
        app.dependency_overrides[get_db] = override_get_db
        cls.client = TestClient(app)

    @classmethod
    def tearDownClass(cls):
        app.dependency_overrides.pop(get_db, None)
        Base.metadata.drop_all(bind=engine)

    def test_health_and_docs(self):
        r1 = self.client.get("/")
        self.assertEqual(r1.status_code, 200)
        r2 = self.client.get("/docs")
        self.assertEqual(r2.status_code, 200)

    def test_ticket_crud_and_note_flow(self):
        # 1. Create ticket
        payload = {
            "customer_name": "Zara Patel",
            "customer_email": "zara.patel@testcorp.io",
            "subject": "Webhook failure on refund event",
            "description": "Refund webhook returns 500 error",
            "client_brand": "UrbanFit",
            "channel": "Email"
        }
        res_create = self.client.post("/api/tickets", json=payload)
        self.assertEqual(res_create.status_code, 201)
        data = res_create.json()
        ticket_id = data["ticket_id"]
        self.assertEqual(data["status"], "Open")

        # 2. List tickets
        res_list = self.client.get("/api/tickets")
        self.assertEqual(res_list.status_code, 200)
        self.assertGreaterEqual(len(res_list.json()), 1)

        # 3. Get ticket detail
        res_detail = self.client.get(f"/api/tickets/{ticket_id}")
        self.assertEqual(res_detail.status_code, 200)
        self.assertEqual(res_detail.json()["customer_name"], "Zara Patel")

        # 4. Update ticket note (auto-advance Open -> In Progress)
        res_update = self.client.put(f"/api/tickets/{ticket_id}", json={
            "note_text": "Investigating logs."
        })
        self.assertEqual(res_update.status_code, 200)
        self.assertEqual(res_update.json()["status"], "In Progress")

        # 5. Resolve ticket
        res_resolve = self.client.put(f"/api/tickets/{ticket_id}", json={
            "status": "Closed",
            "note_text": "Resolved problem."
        })
        self.assertEqual(res_resolve.status_code, 200)
        self.assertEqual(res_resolve.json()["status"], "Closed")


if __name__ == "__main__":
    unittest.main()
