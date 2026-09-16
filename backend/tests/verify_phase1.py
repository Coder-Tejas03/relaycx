"""
Automated Verification Suite for Phase 1 Backend Foundation.
Tests all 9 criteria defined in MASTER_BUILD_GUIDE.md.
"""

import sys
from fastapi.testclient import TestClient
from app.main import app
from app.database import Base, engine


def run_verification():
    print("=" * 70)
    print("STARTING PHASE 1 BACKEND VERIFICATION SUITE")
    print("=" * 70)

    # Initialize clean tables for verification
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    client = TestClient(app)

    # 1. Health check & Swagger docs
    print("\n[TEST 1] Testing Health Check & Swagger UI Docs...")
    health_resp = client.get("/")
    assert health_resp.status_code == 200, f"Expected 200, got {health_resp.status_code}"
    docs_resp = client.get("/docs")
    assert docs_resp.status_code == 200, f"Expected 200 for /docs, got {docs_resp.status_code}"
    print("PASS: Health check and /docs accessible.")

    # 2. POST /api/tickets with valid body
    print("\n[TEST 2] Testing POST /api/tickets (Valid creation)...")
    create_payload = {
        "customer_name": "Aarav Sharma",
        "customer_email": "aarav.sharma@example.com",
        "subject": "Cannot access billing dashboard",
        "description": "Whenever I click on billing settings, the page hangs on a spinner."
    }
    create_resp = client.post("/api/tickets", json=create_payload)
    assert create_resp.status_code == 201, f"Expected 201, got {create_resp.status_code}: {create_resp.text}"
    created_data = create_resp.json()
    ticket_id = created_data["ticket_id"]
    assert ticket_id.startswith("TKT-"), f"ticket_id format invalid: {ticket_id}"
    assert len(ticket_id) == 10, f"ticket_id length invalid: {ticket_id} (expected 10 chars, e.g. TKT-C74B9E)"
    assert created_data["status"] == "Open", f"Expected initial status 'Open', got {created_data['status']}"
    print(f"PASS: Created ticket {ticket_id} with status 'Open'.")

    # Create a second ticket for search/filter testing
    create_payload_2 = {
        "customer_name": "Zara Patel",
        "customer_email": "zara.patel@testcorp.io",
        "subject": "Webhook failure on refund event",
        "description": "Refund webhook returns 500 error from our payment gateway integration."
    }
    client.post("/api/tickets", json=create_payload_2)

    # 3. GET /api/tickets (List)
    print("\n[TEST 3] Testing GET /api/tickets (List retrieval)...")
    list_resp = client.get("/api/tickets")
    assert list_resp.status_code == 200, f"Expected 200, got {list_resp.status_code}"
    tickets = list_resp.json()
    assert isinstance(tickets, list), "Expected list response"
    assert len(tickets) >= 2, f"Expected at least 2 tickets, got {len(tickets)}"
    print(f"PASS: Returned {len(tickets)} tickets in list view.")

    # 4. GET /api/tickets?search=name (Search & Filter)
    print("\n[TEST 4] Testing GET /api/tickets?search=aarav (Case-insensitive multi-field search)...")
    search_resp = client.get("/api/tickets?search=aarav")
    assert search_resp.status_code == 200
    search_results = search_resp.json()
    assert len(search_results) == 1, f"Expected 1 matching ticket, got {len(search_results)}"
    assert search_results[0]["ticket_id"] == ticket_id
    assert "Aarav" in search_results[0]["customer_name"]

    # Test status filter
    status_filter_resp = client.get("/api/tickets?status=Open")
    assert status_filter_resp.status_code == 200
    for t in status_filter_resp.json():
        assert t["status"] == "Open"
    print("PASS: Search and status filter working properly.")

    # 5. GET /api/tickets/{ticket_id} (Detail)
    print(f"\n[TEST 5] Testing GET /api/tickets/{ticket_id} (Detail view)...")
    detail_resp = client.get(f"/api/tickets/{ticket_id}")
    assert detail_resp.status_code == 200
    detail_data = detail_resp.json()
    assert detail_data["ticket_id"] == ticket_id
    assert detail_data["customer_name"] == "Aarav Sharma"
    assert detail_data["notes"] == []
    print("PASS: Detail view returned complete ticket data.")

    # 6. Auto-advance test: PUT with only note on Open ticket -> In Progress
    print("\n[TEST 6 & 7] Testing Auto-Advance State Machine (Note on Open ticket -> In Progress)...")
    note_payload = {
        "note_text": "Investigated billing gateway logs, escalating to payments engineering team."
    }
    update_resp = client.put(f"/api/tickets/{ticket_id}", json=note_payload)
    assert update_resp.status_code == 200, f"Expected 200, got {update_resp.status_code}: {update_resp.text}"
    update_data = update_resp.json()
    assert update_data["status"] == "In Progress", f"Auto-advance failed: expected 'In Progress', got '{update_data['status']}'"
    assert update_data["note"] is not None
    assert "Investigated billing gateway" in update_data["note"]["note_text"]

    # Verify detail shows the new notes (status change + user note) and status In Progress
    detail_check = client.get(f"/api/tickets/{ticket_id}").json()
    assert detail_check["status"] == "In Progress"
    assert len(detail_check["notes"]) == 2, f"Expected 2 notes (status change + user note), got {len(detail_check['notes'])}"
    assert detail_check["notes"][0]["event_type"] == "STATUS_CHANGE"
    assert "Open → In Progress" in detail_check["notes"][0]["note_text"]
    assert detail_check["notes"][1]["event_type"] == "NOTE_ADDED"
    assert "Investigated billing gateway" in detail_check["notes"][1]["note_text"]
    print("PASS: Auto-advance successfully transitioned Open -> In Progress and saved note.")

    # 7b. Second note on In Progress ticket: Status should remain In Progress (not reset or change)
    print("\n[TEST 7b] Testing Note on In Progress ticket (status remains In Progress)...")
    note_payload_2 = {
        "note_text": "Engineering identified faulty gateway credentials. Patch deployed."
    }
    update_resp_2 = client.put(f"/api/tickets/{ticket_id}", json=note_payload_2)
    assert update_resp_2.status_code == 200
    assert update_resp_2.json()["status"] == "In Progress"
    print("PASS: Second note preserved 'In Progress' status.")

    # 7c. Explicit Resolve / Close: PUT with status="Closed"
    print("\n[TEST 7c] Testing 'Add Note & Resolve' (Explicit status Closed)...")
    resolve_payload = {
        "status": "Closed",
        "note_text": "Customer confirmed dashboard access is restored. Resolving ticket."
    }
    resolve_resp = client.put(f"/api/tickets/{ticket_id}", json=resolve_payload)
    assert resolve_resp.status_code == 200
    assert resolve_resp.json()["status"] == "Closed"

    # Verify notes in detail view (2 status changes + 3 user notes = 5 notes)
    final_detail = client.get(f"/api/tickets/{ticket_id}").json()
    assert final_detail["status"] == "Closed"
    assert len(final_detail["notes"]) == 5, f"Expected 5 notes, got {len(final_detail['notes'])}"
    print("PASS: Ticket resolved and closed with full 5-note timeline.")

    # 8. GET /api/tickets/{nonexistent} -> 404
    print("\n[TEST 8] Testing GET /api/tickets/{nonexistent} -> 404 Not Found...")
    not_found_resp = client.get("/api/tickets/TKT-000000")
    assert not_found_resp.status_code == 404, f"Expected 404, got {not_found_resp.status_code}"
    print(f"PASS: Nonexistent ticket correctly returned 404: {not_found_resp.json()}")

    # 9. POST /api/tickets with invalid email -> 422
    print("\n[TEST 9] Testing POST /api/tickets with invalid email -> 422 Unprocessable Entity...")
    invalid_email_payload = {
        "customer_name": "Test User",
        "customer_email": "not-an-email",
        "subject": "Testing email validation",
        "description": "Should fail with 422"
    }
    invalid_resp = client.post("/api/tickets", json=invalid_email_payload)
    assert invalid_resp.status_code == 422, f"Expected 422, got {invalid_resp.status_code}"
    print(f"PASS: Invalid email rejected with 422: {invalid_resp.json()['detail'][0]['msg']}")

    print("\n" + "=" * 70)
    print("ALL 9 PHASE 1 TEST CRITERIA PASSED CLEANLY!")
    print("=" * 70)


if __name__ == "__main__":
    run_verification()
