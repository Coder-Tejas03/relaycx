"""
Standalone seed script for RelayCX demo dataset.
Clears existing tickets and notes, then seeds exactly 7 realistic customer tickets
exercising all workflow states, rich timelines, and search capabilities.

Usage:
    cd backend && ../.venv/bin/python seed.py
"""

import sys
from datetime import datetime, timedelta, timezone
from sqlalchemy import text
from app.database import Base, engine, SessionLocal, ensure_schema
from app.models import Ticket, Note


def seed_database():
    print("=" * 70)
    print("RELAYCX DEMO DATA SEEDING")
    print("=" * 70)

    # Ensure tables exist and migrations are applied
    Base.metadata.create_all(bind=engine)
    ensure_schema()

    db = SessionLocal()
    try:
        # 1. Safely clear existing database records
        print("[1/3] Clearing existing notes and tickets...")
        db.execute(text("DELETE FROM notes"))
        db.execute(text("DELETE FROM tickets"))
        db.commit()
        print("PASS: Database cleared successfully.")

        # 2. Define realistic timestamps relative to now (UTC)
        now = datetime.now(timezone.utc)

        # Ticket A timestamps (5.5 days old, neglected)
        t_a_created = now - timedelta(days=5, hours=12)

        # Ticket B timestamps (3 days old, resolved 2 days 2 hours ago)
        t_b_created = now - timedelta(days=3)
        t_b_open_to_ip = now - timedelta(days=2, hours=20)
        t_b_note1 = now - timedelta(days=2, hours=18)
        t_b_note2 = now - timedelta(days=2, hours=8)
        t_b_ip_to_closed = now - timedelta(days=2, hours=2)
        t_b_resolved = now - timedelta(days=2, hours=2)

        # Ticket C timestamps (2 days old, active triage)
        t_c_created = now - timedelta(days=2)
        t_c_open_to_ip = now - timedelta(days=1, hours=18)
        t_c_note1 = now - timedelta(days=1, hours=16)
        t_c_note2 = now - timedelta(hours=14)

        # Ticket D timestamps (recent intake today, ~1 hour ago)
        t_d_created = now - timedelta(hours=1, minutes=15)

        # Ticket E timestamps (1 day old, active)
        t_e_created = now - timedelta(days=1)
        t_e_open_to_ip = now - timedelta(hours=18)
        t_e_note1 = now - timedelta(hours=16)

        # Ticket F timestamps (4.5 days old, high urgency open)
        t_f_created = now - timedelta(days=4, hours=14)

        # Ticket G timestamps (2.5 days old, webhook search keyword, resolved 1 day ago)
        t_g_created = now - timedelta(days=2, hours=12)
        t_g_open_to_ip = now - timedelta(days=2, hours=2)
        t_g_note1 = now - timedelta(days=1, hours=18)
        t_g_ip_to_closed = now - timedelta(days=1, hours=2)
        t_g_resolved = now - timedelta(days=1, hours=2)

        # 3. Construct the 7 realistic demo tickets
        tickets_data = [
            # A: Zara Patel | Open | 5.5 days old | 0 notes (neglected inquiry)
            {
                "ticket": Ticket(
                    ticket_id="TKT-A82F10",
                    customer_name="Zara Patel",
                    customer_email="zara.patel@finscale.io",
                    subject="Webhook failure on refund event",
                    description=(
                        "Refund webhook events are failing intermittently with HTTP 500 internal server "
                        "error on our secondary merchant endpoint. Refunds are processed in Stripe, but "
                        "the corresponding customer ledger state does not synchronize in our internal dashboard."
                    ),
                    status="Open",
                    created_at=t_a_created,
                    updated_at=t_a_created,
                ),
                "notes": [],
            },
            # B: Aarav Sharma | Closed | 3 days ago | 3 agent notes + 2 status changes + 1 intake
            {
                "ticket": Ticket(
                    ticket_id="TKT-B41E93",
                    customer_name="Aarav Sharma",
                    customer_email="aarav.sharma@payflow.tech",
                    subject="Cannot access billing dashboard",
                    description=(
                        "When attempting to navigate to Settings > Billing, the screen hangs indefinitely "
                        "on a loading spinner. Multiple organization admins are experiencing the exact same issue "
                        "since yesterday morning after our team domain migration."
                    ),
                    status="Closed",
                    created_at=t_b_created,
                    updated_at=t_b_resolved,
                ),
                "notes": [
                    Note(
                        ticket_id="TKT-B41E93",
                        note_text="Ticket intake created via customer support portal.",
                        event_type="TICKET_CREATED",
                        created_at=t_b_created,
                    ),
                    Note(
                        ticket_id="TKT-B41E93",
                        note_text="Open → In Progress",
                        event_type="STATUS_CHANGE",
                        created_at=t_b_open_to_ip,
                    ),
                    Note(
                        ticket_id="TKT-B41E93",
                        note_text=(
                            "Investigated billing gateway logs. Identified stale session authorization tokens "
                            "failing validation against the payment provider API. Working with core auth team "
                            "on session cache invalidation."
                        ),
                        event_type="NOTE_ADDED",
                        created_at=t_b_note1,
                    ),
                    Note(
                        ticket_id="TKT-B41E93",
                        note_text=(
                            "Session cache cluster purged and backend token refresh logic patched. Verified dashboard "
                            "loads across test accounts in staging."
                        ),
                        event_type="NOTE_ADDED",
                        created_at=t_b_note2,
                    ),
                    Note(
                        ticket_id="TKT-B41E93",
                        note_text="In Progress → Closed",
                        event_type="STATUS_CHANGE",
                        created_at=t_b_ip_to_closed,
                    ),
                    Note(
                        ticket_id="TKT-B41E93",
                        note_text=(
                            "Customer confirmed full dashboard access has been restored on all admin accounts. "
                            "Verified zero lingering 401/500 errors in Datadog. Resolving ticket."
                        ),
                        event_type="NOTE_ADDED",
                        created_at=t_b_resolved,
                    ),
                ],
            },
            # C: Meera Iyer | In Progress | 2 days ago | 2 notes + 1 status change + 1 intake
            {
                "ticket": Ticket(
                    ticket_id="TKT-C73D5A",
                    customer_name="Meera Iyer",
                    customer_email="meera.iyer@cloudcart.dev",
                    subject="Payment processing delay on checkout",
                    description=(
                        "Customers reporting checkout confirmation taking upwards of 45 seconds on Stripe credit "
                        "card transactions. 3 high-value customers abandoned checkout sessions today."
                    ),
                    status="In Progress",
                    created_at=t_c_created,
                    updated_at=t_c_note2,
                ),
                "notes": [
                    Note(
                        ticket_id="TKT-C73D5A",
                        note_text="Ticket intake created via priority merchant support queue.",
                        event_type="TICKET_CREATED",
                        created_at=t_c_created,
                    ),
                    Note(
                        ticket_id="TKT-C73D5A",
                        note_text="Open → In Progress",
                        event_type="STATUS_CHANGE",
                        created_at=t_c_open_to_ip,
                    ),
                    Note(
                        ticket_id="TKT-C73D5A",
                        note_text=(
                            "Reviewed egress latency to Stripe webhook ingestion endpoints. Observing p99 network "
                            "spikes between us-east-1 and payment gateway. Escrow transaction queues backing up."
                        ),
                        event_type="NOTE_ADDED",
                        created_at=t_c_note1,
                    ),
                    Note(
                        ticket_id="TKT-C73D5A",
                        note_text=(
                            "Engaged network reliability team. Routing checkout payloads through alternate edge proxy. "
                            "Latency dropped to 420ms; monitoring queue drain."
                        ),
                        event_type="NOTE_ADDED",
                        created_at=t_c_note2,
                    ),
                ],
            },
            # D: Rohan Kapoor | Open | ~1 hour ago (today) | 0 notes (new intake)
            {
                "ticket": Ticket(
                    ticket_id="TKT-D19C48",
                    customer_name="Rohan Kapoor",
                    customer_email="rohan.kapoor@novabanking.com",
                    subject="Account locked after failed 2FA attempts",
                    description=(
                        "User entered incorrect SMS verification codes 5 times after changing mobile devices. "
                        "Account is currently in hard lockout. Customer has provided photo verification of corporate identity."
                    ),
                    status="Open",
                    created_at=t_d_created,
                    updated_at=t_d_created,
                ),
                "notes": [],
            },
            # E: Priya Nair | In Progress | 1 day ago | 1 note + 1 status change + 1 intake
            {
                "ticket": Ticket(
                    ticket_id="TKT-E62B07",
                    customer_name="Priya Nair",
                    customer_email="priya.nair@datalens.ai",
                    subject="CSV export returns empty file for date range filter",
                    description=(
                        "When exporting analytics reports for custom date ranges spanning more than 30 days, "
                        "the generated CSV file downloads with 0 bytes. Narrow date ranges (1-7 days) export properly."
                    ),
                    status="In Progress",
                    created_at=t_e_created,
                    updated_at=t_e_note1,
                ),
                "notes": [
                    Note(
                        ticket_id="TKT-E62B07",
                        note_text="Ticket intake created via standard email support channel.",
                        event_type="TICKET_CREATED",
                        created_at=t_e_created,
                    ),
                    Note(
                        ticket_id="TKT-E62B07",
                        note_text="Open → In Progress",
                        event_type="STATUS_CHANGE",
                        created_at=t_e_open_to_ip,
                    ),
                    Note(
                        ticket_id="TKT-E62B07",
                        note_text=(
                            "Replicated export query on staging replica. Queries exceeding 30-day window hit Lambda "
                            "execution timeout of 15 seconds. Need to offload large batch CSV exports to async background worker."
                        ),
                        event_type="NOTE_ADDED",
                        created_at=t_e_note1,
                    ),
                ],
            },
            # F: Dev Malhotra | Open | 4.5 days ago | 0 notes (high urgency sitting idle)
            {
                "ticket": Ticket(
                    ticket_id="TKT-F95A31",
                    customer_name="Dev Malhotra",
                    customer_email="dev.malhotra@hypergrid.net",
                    subject="API rate limit errors causing production outage",
                    description=(
                        "Experiencing continuous HTTP 429 Too Many Requests on the /v1/telemetry endpoint during "
                        "peak production traffic hours. Ingestion backlog currently exceeds 120,000 telemetry events."
                    ),
                    status="Open",
                    created_at=t_f_created,
                    updated_at=t_f_created,
                ),
                "notes": [],
            },
            # G: Siya Shah | Closed | 2.5 days ago | Webhook search keyword, complete journey, resolved 1 day ago
            {
                "ticket": Ticket(
                    ticket_id="TKT-G38D64",
                    customer_name="Siya Shah",
                    customer_email="siya.shah@eventmesh.org",
                    subject="Webhook endpoint returning 400 on payment.completed event",
                    description=(
                        "Our production webhook receiver is failing with HTTP 400 Bad Request whenever payment.completed "
                        "event payloads are delivered. Suspect payload schema discrepancy with latest API release."
                    ),
                    status="Closed",
                    created_at=t_g_created,
                    updated_at=t_g_resolved,
                ),
                "notes": [
                    Note(
                        ticket_id="TKT-G38D64",
                        note_text="Ticket intake created via developer API integrations channel.",
                        event_type="TICKET_CREATED",
                        created_at=t_g_created,
                    ),
                    Note(
                        ticket_id="TKT-G38D64",
                        note_text="Open → In Progress",
                        event_type="STATUS_CHANGE",
                        created_at=t_g_open_to_ip,
                    ),
                    Note(
                        ticket_id="TKT-G38D64",
                        note_text=(
                            "Investigated webhook delivery logs. The payment.completed event payload schema introduced "
                            "an object array for line_items instead of string IDs in v2.4. Customer webhook parser expected v2.3 schema."
                        ),
                        event_type="NOTE_ADDED",
                        created_at=t_g_note1,
                    ),
                    Note(
                        ticket_id="TKT-G38D64",
                        note_text="In Progress → Closed",
                        event_type="STATUS_CHANGE",
                        created_at=t_g_ip_to_closed,
                    ),
                    Note(
                        ticket_id="TKT-G38D64",
                        note_text=(
                            "Customer updated their parser to support v2.4 webhook schema. Resent 14 failed webhook deliveries; "
                            "all returned HTTP 200 OK. Resolving ticket."
                        ),
                        event_type="NOTE_ADDED",
                        created_at=t_g_resolved,
                    ),
                ],
            },
        ]

        # 4. Insert all tickets and notes into database
        print("[2/3] Inserting 7 realistic tickets and activity timelines...")
        for item in tickets_data:
            ticket = item["ticket"]
            notes = item["notes"]
            db.add(ticket)
            db.flush()  # Ensure ticket is persisted before attaching notes

            for note in notes:
                db.add(note)

        db.commit()
        print("PASS: Inserted 7 tickets and all associated activity notes.")

        # 5. Verification & Summary Output
        print("\n[3/3] Verifying seeded dataset:")
        all_tickets = db.query(Ticket).all()
        all_notes = db.query(Note).all()

        open_tickets = [t for t in all_tickets if t.status == "Open"]
        ip_tickets = [t for t in all_tickets if t.status == "In Progress"]
        closed_tickets = [t for t in all_tickets if t.status == "Closed"]

        print(f"  • Total tickets in DB: {len(all_tickets)} (Expected: 7)")
        print(f"  • Total notes in DB: {len(all_notes)}")
        print(f"  • Open tickets ({len(open_tickets)}): {[t.ticket_id for t in open_tickets]}")
        print(f"  • In Progress tickets ({len(ip_tickets)}): {[t.ticket_id for t in ip_tickets]}")
        print(f"  • Closed tickets ({len(closed_tickets)}): {[t.ticket_id for t in closed_tickets]}")

        assert len(all_tickets) == 7, f"Expected exactly 7 tickets, found {len(all_tickets)}"
        assert len(open_tickets) == 3, f"Expected 3 Open tickets, found {len(open_tickets)}"
        assert len(ip_tickets) == 2, f"Expected 2 In Progress tickets, found {len(ip_tickets)}"
        assert len(closed_tickets) == 2, f"Expected 2 Closed tickets, found {len(closed_tickets)}"

        print("\n" + "=" * 70)
        print("SUCCESS: RelayCX demo dataset seeded cleanly! Ready for showcase.")
        print("=" * 70)

    except Exception as e:
        db.rollback()
        print(f"ERROR: Failed to seed database: {e}", file=sys.stderr)
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed_database()
