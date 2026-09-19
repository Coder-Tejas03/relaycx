"""
Unit and integration tests for Phase 5 API routes and schema contracts:
1. Client-scoped & issue-relevant context route (GET /api/customers/{client_brand}/{customer_email}/context)
2. Backward compatibility of legacy context route (GET /api/customers/{customer_email}/order-context)
3. Issue classification correction route (PATCH /api/tickets/{ticket_id}/issue-type)
4. List tickets query filters (client_brand, customer_email)
5. Customer ticket history endpoints (/api/tickets/customer-history and /api/customers/{client_brand}/{customer_email}/history)
"""

import unittest
from urllib.parse import quote
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

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


class TestPhase5Routes(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        Base.metadata.create_all(bind=engine)
        app.dependency_overrides[get_db] = override_get_db
        cls.client = TestClient(app)

    @classmethod
    def tearDownClass(cls):
        app.dependency_overrides.pop(get_db, None)
        Base.metadata.drop_all(bind=engine)

    def setUp(self):
        # Clean tickets and notes tables between test methods
        with engine.connect() as conn:
            conn.execute(Base.metadata.tables["notes"].delete())
            conn.execute(Base.metadata.tables["tickets"].delete())
            conn.commit()

    # -------------------------------------------------------------------------
    # 1. Client-Scoped & Issue-Relevant Context Endpoint
    # -------------------------------------------------------------------------

    def test_client_scoped_context_priya_ana_relevance(self):
        """Priya with ANA ticket gets HTTP 204, but with ORD ticket gets HTTP 200 with cream order."""
        email = "priya.nair@datalens.ai"
        brand = "Aura D2C"

        # ANA issue type -> Relevance rule excludes ecommerce cream order -> 204 No Content
        res_ana = self.client.get(f"/api/customers/{quote(brand)}/{quote(email)}/context?issue_type=ANA")
        self.assertEqual(res_ana.status_code, 204)

        # ORD issue type -> Relevant to ecommerce order -> 200 OK
        res_ord = self.client.get(f"/api/customers/{quote(brand)}/{quote(email)}/context?issue_type=ORD")
        self.assertEqual(res_ord.status_code, 200)
        data = res_ord.json()
        self.assertEqual(data["order_id"], "ORD-3918")
        self.assertIn("Cream Duo", data["item_name"])

    def test_client_scoped_context_dev_int_relevance(self):
        """Dev with INT ticket gets developer details; with ORD gets HTTP 204."""
        email = "dev.malhotra@hypergrid.net"
        brand = "Nova Audio"

        # INT issue type -> Relevant to developer account -> 200 OK
        res_int = self.client.get(f"/api/customers/{quote(brand)}/{quote(email)}/context?issue_type=INT")
        self.assertEqual(res_int.status_code, 200)
        data = res_int.json()
        self.assertEqual(data["account_type"], "developer")
        self.assertIsNotNone(data.get("technical_details"))
        self.assertEqual(data["technical_details"]["quota"], "5,000,000 req/mo")

        # ORD issue type -> Developer account irrelevant to retail shipment -> 204 No Content
        res_ord = self.client.get(f"/api/customers/{quote(brand)}/{quote(email)}/context?issue_type=ORD")
        self.assertEqual(res_ord.status_code, 204)

    def test_client_scoped_context_cross_brand_isolation_rohan(self):
        """Rohan's context is isolated between UrbanFit (joggers) and Nova Audio (speakers)."""
        email = "rohan.kapoor@novabanking.com"

        # UrbanFit + ORD -> Joggers ORD-6104
        res_urb = self.client.get(f"/api/customers/UrbanFit/{quote(email)}/context?issue_type=ORD")
        self.assertEqual(res_urb.status_code, 200)
        self.assertEqual(res_urb.json()["order_id"], "ORD-6104")

        # Nova Audio + ORD -> Studio Monitor Speakers ORD-5520
        res_nov = self.client.get(f"/api/customers/{quote('Nova Audio')}/{quote(email)}/context?issue_type=ORD")
        self.assertEqual(res_nov.status_code, 200)
        self.assertEqual(res_nov.json()["order_id"], "ORD-5520")

        # Aura D2C + ORD -> No account registered -> 204 No Content
        res_aur = self.client.get(f"/api/customers/{quote('Aura D2C')}/{quote(email)}/context?issue_type=ORD")
        self.assertEqual(res_aur.status_code, 204)

    def test_client_scoped_context_gen_or_missing_returns_204(self):
        """GEN issue family or missing issue type always returns HTTP 204 No Content."""
        email = "zara.patel@finscale.io"
        brand = "UrbanFit"

        res_gen = self.client.get(f"/api/customers/{quote(brand)}/{quote(email)}/context?issue_type=GEN")
        self.assertEqual(res_gen.status_code, 204)

        res_none = self.client.get(f"/api/customers/{quote(brand)}/{quote(email)}/context")
        self.assertEqual(res_none.status_code, 204)

    # -------------------------------------------------------------------------
    # 2. Legacy Order Context Route Backward Compatibility
    # -------------------------------------------------------------------------

    def test_legacy_customer_order_context_route(self):
        """Existing GET /api/customers/{email}/order-context continues to function."""
        # Known customer email -> 200 OK
        res_known = self.client.get("/api/customers/zara.patel@finscale.io/order-context")
        self.assertEqual(res_known.status_code, 200)
        self.assertEqual(res_known.json()["order_id"], "ORD-8921")

        # Unknown customer email -> 204 No Content
        res_unknown = self.client.get("/api/customers/unknown.user@domain.com/order-context")
        self.assertEqual(res_unknown.status_code, 204)

    # -------------------------------------------------------------------------
    # 3. PATCH /api/tickets/{ticket_id}/issue-type (Classification Correction)
    # -------------------------------------------------------------------------

    def test_patch_issue_type_success_and_immutability(self):
        """Correcting issue_type updates only issue_type; ticket_id and intake_issue_type remain immutable."""
        # 1. Create a ticket that classifies as ANA
        create_res = self.client.post("/api/tickets", json={
            "customer_name": "Priya Nair",
            "customer_email": "priya.nair@datalens.ai",
            "subject": "Lambda timeout during analytics export",
            "description": "Exporting CSV dashboard data causes timeout error",
            "client_brand": "Aura D2C",
        })
        self.assertEqual(create_res.status_code, 201)
        created_data = create_res.json()
        ticket_id = created_data["ticket_id"]

        self.assertEqual(created_data["issue_type"], "ANA")
        self.assertEqual(created_data["intake_issue_type"], "ANA")
        self.assertTrue(ticket_id.startswith("TKT-AUR-ANA-"))

        # 2. PATCH issue-type to INT
        patch_res = self.client.patch(f"/api/tickets/{ticket_id}/issue-type", json={
            "issue_type": "INT"
        })
        self.assertEqual(patch_res.status_code, 200)
        patch_data = patch_res.json()

        # Check immutability of ticket_id and intake_issue_type
        self.assertEqual(patch_data["ticket_id"], ticket_id)
        self.assertEqual(patch_data["intake_issue_type"], "ANA")
        self.assertEqual(patch_data["issue_type"], "INT")
        self.assertIn("updated_at", patch_data)

        # 3. Verify via GET /api/tickets/{ticket_id}
        detail_res = self.client.get(f"/api/tickets/{ticket_id}")
        self.assertEqual(detail_res.status_code, 200)
        detail_data = detail_res.json()
        self.assertEqual(detail_data["ticket_id"], ticket_id)
        self.assertEqual(detail_data["intake_issue_type"], "ANA")
        self.assertEqual(detail_data["issue_type"], "INT")

    def test_patch_issue_type_invalid_code_returns_422(self):
        """Invalid issue_type code fails Pydantic schema validation with HTTP 422."""
        create_res = self.client.post("/api/tickets", json={
            "customer_name": "Test User",
            "customer_email": "test@example.com",
            "subject": "General question",
            "description": "Need assistance",
            "client_brand": "UrbanFit",
        })
        ticket_id = create_res.json()["ticket_id"]

        patch_res = self.client.patch(f"/api/tickets/{ticket_id}/issue-type", json={
            "issue_type": "INVALID_CODE"
        })
        self.assertEqual(patch_res.status_code, 422)

    def test_patch_issue_type_nonexistent_ticket_returns_404(self):
        """Attempting to patch a non-existent ticket returns HTTP 404."""
        patch_res = self.client.patch("/api/tickets/TKT-NONEXISTENT/issue-type", json={
            "issue_type": "INT"
        })
        self.assertEqual(patch_res.status_code, 404)

    # -------------------------------------------------------------------------
    # 4. List Tickets Query Filters (client_brand, customer_email)
    # -------------------------------------------------------------------------

    def test_list_tickets_with_brand_and_email_filters(self):
        """Query parameters client_brand and customer_email correctly filter ticket list."""
        # Create 3 tickets
        self.client.post("/api/tickets", json={
            "customer_name": "Zara Patel",
            "customer_email": "zara@finscale.io",
            "subject": "Webhook 1",
            "description": "Webhook 500 error",
            "client_brand": "UrbanFit",
        })
        self.client.post("/api/tickets", json={
            "customer_name": "Bob Singh",
            "customer_email": "bob@finscale.io",
            "subject": "Sizing query",
            "description": "Need sizing guide",
            "client_brand": "UrbanFit",
        })
        self.client.post("/api/tickets", json={
            "customer_name": "Priya Nair",
            "customer_email": "priya@datalens.ai",
            "subject": "Export query",
            "description": "CSV export issue",
            "client_brand": "Aura D2C",
        })

        # Filter by client_brand
        res_urb = self.client.get("/api/tickets?client_brand=UrbanFit")
        self.assertEqual(res_urb.status_code, 200)
        self.assertEqual(len(res_urb.json()), 2)
        for t in res_urb.json():
            self.assertEqual(t["client_brand"], "UrbanFit")

        res_aur = self.client.get("/api/tickets?client_brand=Aura%20D2C")
        self.assertEqual(res_aur.status_code, 200)
        self.assertEqual(len(res_aur.json()), 1)
        self.assertEqual(res_aur.json()[0]["client_brand"], "Aura D2C")

        # Filter by customer_email
        res_email = self.client.get("/api/tickets?customer_email=zara@finscale.io")
        self.assertEqual(res_email.status_code, 200)
        self.assertEqual(len(res_email.json()), 1)
        self.assertEqual(res_email.json()[0]["customer_email"], "zara@finscale.io")

        # Combined filter
        res_comb = self.client.get("/api/tickets?client_brand=UrbanFit&customer_email=zara@finscale.io")
        self.assertEqual(res_comb.status_code, 200)
        self.assertEqual(len(res_comb.json()), 1)

        # Empty result on mismatched filter
        res_empty = self.client.get("/api/tickets?client_brand=Nova%20Audio")
        self.assertEqual(res_empty.status_code, 200)
        self.assertEqual(len(res_empty.json()), 0)

    # -------------------------------------------------------------------------
    # 5. Customer Ticket History Endpoints
    # -------------------------------------------------------------------------

    def test_customer_history_endpoints_and_isolation(self):
        """Customer history endpoints enforce brand isolation and support excluding current ticket."""
        email = "priya.nair@datalens.ai"

        # Ticket 1 (Aura D2C)
        t1 = self.client.post("/api/tickets", json={
            "customer_name": "Priya Nair", "customer_email": email,
            "subject": "Issue 1", "description": "Analytics error",
            "client_brand": "Aura D2C",
        }).json()

        # Ticket 2 (Aura D2C)
        t2 = self.client.post("/api/tickets", json={
            "customer_name": "Priya Nair", "customer_email": email,
            "subject": "Issue 2", "description": "Payment checkout issue",
            "client_brand": "Aura D2C",
        }).json()

        # Ticket 3 (UrbanFit - different brand for same customer)
        self.client.post("/api/tickets", json={
            "customer_name": "Priya Nair", "customer_email": email,
            "subject": "Issue 3", "description": "Tee sizing question",
            "client_brand": "UrbanFit",
        })

        # Test GET /api/tickets/customer-history
        url_1 = f"/api/tickets/customer-history?client_brand=Aura%20D2C&customer_email={quote(email)}&exclude_ticket_id={t2['ticket_id']}"
        res_hist_1 = self.client.get(url_1)
        self.assertEqual(res_hist_1.status_code, 200)
        items_1 = res_hist_1.json()
        self.assertEqual(len(items_1), 1)
        self.assertEqual(items_1[0]["ticket_id"], t1["ticket_id"])
        self.assertEqual(items_1[0]["client_brand"], "Aura D2C")

        # Test GET /api/customers/{client_brand}/{customer_email}/history
        url_2 = f"/api/customers/Aura%20D2C/{quote(email)}/history?exclude_ticket_id={t2['ticket_id']}"
        res_hist_2 = self.client.get(url_2)
        self.assertEqual(res_hist_2.status_code, 200)
        items_2 = res_hist_2.json()
        self.assertEqual(len(items_2), 1)
        self.assertEqual(items_2[0]["ticket_id"], t1["ticket_id"])


if __name__ == "__main__":
    unittest.main()
