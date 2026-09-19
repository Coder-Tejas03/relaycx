"""
Standalone seed script for RelayCX demo dataset.
Clears existing tickets and notes, then seeds the manually-engineered dataset.

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

        # 2. Define relative timestamps
        now = datetime.now(timezone.utc)

        # ---------------------------------------------------------------------------
        # TICKET DATA
        # Add manually-engineered tickets here, one at a time.
        # Each entry must follow the structure:
        #
        # {
        #     "ticket": Ticket(
        #         ticket_id="TKT-{CLIENT3}-{ISSUE3}-{SEQ4}",
        #         customer_name="...",
        #         customer_email="...",
        #         subject="...",
        #         description="...",
        #         status="Open" | "In Progress" | "Closed",
        #         client_brand="...",
        #         channel="Email" | "WhatsApp" | "Web Portal" | "Instagram",
        #         intake_issue_type="...",   # 3-char code at ticket creation
        #         issue_type="...",          # 3-char code (may be updated post-triage)
        #         ticket_sequence=N,         # Per-brand per-issue sequence number
        #         created_at=<datetime>,
        #         updated_at=<datetime>,
        #     ),
        #     "notes": [
        #         Note(ticket_id="TKT-...", note_text="...", event_type="TICKET_CREATED", created_at=<datetime>),
        #         Note(ticket_id="TKT-...", note_text="Open → In Progress", event_type="STATUS_CHANGE", created_at=<datetime>),
        #         Note(ticket_id="TKT-...", note_text="...", event_type="NOTE_ADDED", created_at=<datetime>),
        #         Note(ticket_id="TKT-...", note_text="In Progress → Closed", event_type="STATUS_CHANGE", created_at=<datetime>),
        #     ],
        # }
        # ---------------------------------------------------------------------------
        tickets_data = [
            # =======================================================================
            # TICKET 01 — Aditya Joshi | Damaged Delivery | Zen Botanics
            # =======================================================================
            {
                "ticket": Ticket(
                    ticket_id="TKT-ZEN-ORD-0001",
                    customer_name="Aditya Joshi",
                    customer_email="aditya.joshi@gmail.com",
                    subject="Organic facial serum bottle arrived leaking",
                    description=(
                        "My order was delivered today, but the Organic Facial Serum bottle "
                        "was leaking inside the package. The dropper seal looks broken and "
                        "some of the serum has spilled into the box. I would like to know "
                        "if I can get a replacement or a refund."
                    ),
                    status="In Progress",
                    client_brand="Zen Botanics",
                    channel="WhatsApp",
                    intake_issue_type="ORD",
                    issue_type="ORD",
                    ticket_sequence=1,
                    created_at=now - timedelta(minutes=45),
                    updated_at=now - timedelta(minutes=15),
                ),
                "notes": [
                    Note(
                        ticket_id="TKT-ZEN-ORD-0001",
                        note_text="Ticket intake created via WhatsApp.",
                        event_type="TICKET_CREATED",
                        created_at=now - timedelta(minutes=45),
                    ),
                    Note(
                        ticket_id="TKT-ZEN-ORD-0001",
                        note_text="Open → In Progress",
                        event_type="STATUS_CHANGE",
                        created_at=now - timedelta(minutes=25),
                    ),
                    Note(
                        ticket_id="TKT-ZEN-ORD-0001",
                        note_text="Customer reported leakage immediately after delivery and requested a replacement or refund.",
                        event_type="NOTE_ADDED",
                        created_at=now - timedelta(minutes=15),
                    ),
                ],
            },

            # -----------------------------------------------------------------------
            # FOLLOW-UP TICKET: Aditya Joshi | Expedited Replacement | Zen Botanics
            # -----------------------------------------------------------------------
            {
                "ticket": Ticket(
                    ticket_id="TKT-ZEN-ORD-0002",
                    customer_name="Aditya Joshi",
                    customer_email="aditya.joshi@gmail.com",
                    subject="Expedited courier dispatch for replacement serum",
                    description=(
                        "Following up on ticket TKT-ZEN-ORD-0001 regarding the leaking bottle; "
                        "could you please dispatch the replacement bottle via priority air express? "
                        "I have an upcoming travel schedule next week and need the replacement delivered promptly."
                    ),
                    status="Open",
                    client_brand="Zen Botanics",
                    channel="WhatsApp",
                    intake_issue_type="ORD",
                    issue_type="ORD",
                    ticket_sequence=2,
                    created_at=now - timedelta(minutes=20),
                    updated_at=now - timedelta(minutes=20),
                ),
                "notes": [
                    Note(
                        ticket_id="TKT-ZEN-ORD-0002",
                        note_text="Ticket intake created via WhatsApp.",
                        event_type="TICKET_CREATED",
                        created_at=now - timedelta(minutes=20),
                    ),
                    Note(
                        ticket_id="TKT-ZEN-ORD-0002",
                        note_text="Customer requested priority courier dispatch for the approved replacement.",
                        event_type="NOTE_ADDED",
                        created_at=now - timedelta(minutes=10),
                    ),
                ],
            },

            # -----------------------------------------------------------------------
            # PRIOR HISTORY TICKET 1: Aditya Joshi (4 months ago, Closed)
            # -----------------------------------------------------------------------
            {
                "ticket": Ticket(
                    ticket_id="TKT-ZEN-PRD-0001",
                    customer_name="Aditya Joshi",
                    customer_email="aditya.joshi@gmail.com",
                    subject="Product availability question",
                    description="Inquiring whether Organic Facial Serum 50ml will be restocked this quarter.",
                    status="Closed",
                    client_brand="Zen Botanics",
                    channel="Email",
                    intake_issue_type="PRD",
                    issue_type="PRD",
                    ticket_sequence=1,
                    created_at=now - timedelta(days=120),
                    updated_at=now - timedelta(days=119),
                ),
                "notes": [
                    Note(
                        ticket_id="TKT-ZEN-PRD-0001",
                        note_text="Ticket intake created via email support.",
                        event_type="TICKET_CREATED",
                        created_at=now - timedelta(days=120),
                    ),
                    Note(
                        ticket_id="TKT-ZEN-PRD-0001",
                        note_text="Confirmed restock timeline with inventory team. Customer notified.",
                        event_type="NOTE_ADDED",
                        created_at=now - timedelta(days=119, hours=20),
                    ),
                    Note(
                        ticket_id="TKT-ZEN-PRD-0001",
                        note_text="In Progress → Closed",
                        event_type="STATUS_CHANGE",
                        created_at=now - timedelta(days=119),
                    ),
                ],
            },

            # -----------------------------------------------------------------------
            # PRIOR HISTORY TICKET 2: Aditya Joshi (7 months ago, Closed)
            # -----------------------------------------------------------------------
            {
                "ticket": Ticket(
                    ticket_id="TKT-ZEN-ACC-0001",
                    customer_name="Aditya Joshi",
                    customer_email="aditya.joshi@gmail.com",
                    subject="Address update request",
                    description="Requested changing default delivery address prior to next renewal.",
                    status="Closed",
                    client_brand="Zen Botanics",
                    channel="Web Portal",
                    intake_issue_type="ACC",
                    issue_type="ACC",
                    ticket_sequence=1,
                    created_at=now - timedelta(days=210),
                    updated_at=now - timedelta(days=209),
                ),
                "notes": [
                    Note(
                        ticket_id="TKT-ZEN-ACC-0001",
                        note_text="Ticket intake created via web portal.",
                        event_type="TICKET_CREATED",
                        created_at=now - timedelta(days=210),
                    ),
                    Note(
                        ticket_id="TKT-ZEN-ACC-0001",
                        note_text="Shipping profile updated successfully in Zen Botanics customer database.",
                        event_type="NOTE_ADDED",
                        created_at=now - timedelta(days=209, hours=22),
                    ),
                    Note(
                        ticket_id="TKT-ZEN-ACC-0001",
                        note_text="In Progress → Closed",
                        event_type="STATUS_CHANGE",
                        created_at=now - timedelta(days=209),
                    ),
                ],
            },

            # =======================================================================
            # TICKET 02 — Meera Iyer | Payment Deducted, Order Not Confirmed | Aura D2C
            # =======================================================================
            {
                "ticket": Ticket(
                    ticket_id="TKT-AUR-PAY-0001",
                    customer_name="Meera Iyer",
                    customer_email="meera.iyer@gmail.com",
                    subject="Payment deducted but order is still not confirmed",
                    description=(
                        "I placed an order for the Rose Glow Hydration Kit this morning. "
                        "The ₹1,899 payment was deducted from my UPI account, but I never "
                        "received an order confirmation. The checkout page showed an error "
                        "after the payment was completed. Please confirm whether my order "
                        "went through or if I will receive a refund."
                    ),
                    status="In Progress",
                    client_brand="Aura D2C",
                    channel="WhatsApp",
                    intake_issue_type="PAY",
                    issue_type="PAY",
                    ticket_sequence=1,
                    created_at=now - timedelta(hours=1, minutes=10),
                    updated_at=now - timedelta(minutes=20),
                ),
                "notes": [
                    Note(
                        ticket_id="TKT-AUR-PAY-0001",
                        note_text="Ticket intake created via WhatsApp.",
                        event_type="TICKET_CREATED",
                        created_at=now - timedelta(hours=1, minutes=10),
                    ),
                    Note(
                        ticket_id="TKT-AUR-PAY-0001",
                        note_text="Open → In Progress",
                        event_type="STATUS_CHANGE",
                        created_at=now - timedelta(minutes=50),
                    ),
                    Note(
                        ticket_id="TKT-AUR-PAY-0001",
                        note_text="Customer confirmed that the UPI amount was deducted successfully.",
                        event_type="NOTE_ADDED",
                        created_at=now - timedelta(minutes=40),
                    ),
                    Note(
                        ticket_id="TKT-AUR-PAY-0001",
                        note_text="Payment transaction found, but order confirmation was not completed.",
                        event_type="NOTE_ADDED",
                        created_at=now - timedelta(minutes=20),
                    ),
                ],
            },

            # -----------------------------------------------------------------------
            # FOLLOW-UP TICKET: Meera Iyer | Duplicate UPI Charge | Aura D2C
            # -----------------------------------------------------------------------
            {
                "ticket": Ticket(
                    ticket_id="TKT-AUR-PAY-0002",
                    customer_name="Meera Iyer",
                    customer_email="meera.iyer@gmail.com",
                    subject="UPI double charge during checkout retry",
                    description=(
                        "While attempting to place an order for the Rose Glow Hydration Kit after "
                        "a checkout timeout error, a second UPI deduction of ₹1,899 occurred under "
                        "transaction UPI-984210. Both debits reflect on my bank statement. Please "
                        "verify the double capture and process an immediate refund for the duplicate charge."
                    ),
                    status="In Progress",
                    client_brand="Aura D2C",
                    channel="WhatsApp",
                    intake_issue_type="PAY",
                    issue_type="PAY",
                    ticket_sequence=2,
                    created_at=now - timedelta(minutes=50),
                    updated_at=now - timedelta(minutes=25),
                ),
                "notes": [
                    Note(
                        ticket_id="TKT-AUR-PAY-0002",
                        note_text="Ticket intake created via WhatsApp.",
                        event_type="TICKET_CREATED",
                        created_at=now - timedelta(minutes=50),
                    ),
                    Note(
                        ticket_id="TKT-AUR-PAY-0002",
                        note_text="Open → In Progress",
                        event_type="STATUS_CHANGE",
                        created_at=now - timedelta(minutes=35),
                    ),
                    Note(
                        ticket_id="TKT-AUR-PAY-0002",
                        note_text="Duplicate UPI transaction ID confirmed with merchant payment gateway.",
                        event_type="NOTE_ADDED",
                        created_at=now - timedelta(minutes=25),
                    ),
                ],
            },

            # -----------------------------------------------------------------------
            # PRIOR HISTORY TICKET 1: Meera Iyer (2 months ago, Closed)
            # -----------------------------------------------------------------------
            {
                "ticket": Ticket(
                    ticket_id="TKT-AUR-ORD-0001",
                    customer_name="Meera Iyer",
                    customer_email="meera.iyer@gmail.com",
                    subject="Order delivery delay",
                    description="Customer inquiring about transit status for shipment delayed by local courier hub backlog.",
                    status="Closed",
                    client_brand="Aura D2C",
                    channel="Email",
                    intake_issue_type="ORD",
                    issue_type="ORD",
                    ticket_sequence=1,
                    created_at=now - timedelta(days=60),
                    updated_at=now - timedelta(days=58),
                ),
                "notes": [
                    Note(
                        ticket_id="TKT-AUR-ORD-0001",
                        note_text="Ticket intake created via email support.",
                        event_type="TICKET_CREATED",
                        created_at=now - timedelta(days=60),
                    ),
                    Note(
                        ticket_id="TKT-AUR-ORD-0001",
                        note_text="Open → In Progress",
                        event_type="STATUS_CHANGE",
                        created_at=now - timedelta(days=59, hours=18),
                    ),
                    Note(
                        ticket_id="TKT-AUR-ORD-0001",
                        note_text="Escalated to logistics partner; delivery completed.",
                        event_type="NOTE_ADDED",
                        created_at=now - timedelta(days=58, hours=4),
                    ),
                    Note(
                        ticket_id="TKT-AUR-ORD-0001",
                        note_text="In Progress → Closed",
                        event_type="STATUS_CHANGE",
                        created_at=now - timedelta(days=58),
                    ),
                ],
            },

            # -----------------------------------------------------------------------
            # PRIOR HISTORY TICKET 2: Meera Iyer (5 months ago, Closed)
            # -----------------------------------------------------------------------
            {
                "ticket": Ticket(
                    ticket_id="TKT-AUR-PRD-0001",
                    customer_name="Meera Iyer",
                    customer_email="meera.iyer@gmail.com",
                    subject="Product availability question",
                    description="Customer asking for ingredient formulation details and availability of 30ml travel size.",
                    status="Closed",
                    client_brand="Aura D2C",
                    channel="Web Portal",
                    intake_issue_type="PRD",
                    issue_type="PRD",
                    ticket_sequence=1,
                    created_at=now - timedelta(days=150),
                    updated_at=now - timedelta(days=149),
                ),
                "notes": [
                    Note(
                        ticket_id="TKT-AUR-PRD-0001",
                        note_text="Ticket intake created via web portal.",
                        event_type="TICKET_CREATED",
                        created_at=now - timedelta(days=150),
                    ),
                    Note(
                        ticket_id="TKT-AUR-PRD-0001",
                        note_text="Product specialist provided botanical ingredient sheet.",
                        event_type="NOTE_ADDED",
                        created_at=now - timedelta(days=149, hours=20),
                    ),
                    Note(
                        ticket_id="TKT-AUR-PRD-0001",
                        note_text="In Progress → Closed",
                        event_type="STATUS_CHANGE",
                        created_at=now - timedelta(days=149),
                    ),
                ],
            },

            # =======================================================================
            # TICKET 03 — Rohan Kapoor | Wrong Item Delivered | UrbanFit
            # =======================================================================
            {
                "ticket": Ticket(
                    ticket_id="TKT-URB-ORD-0001",
                    customer_name="Rohan Kapoor",
                    customer_email="rohan.kapoor@gmail.com",
                    subject="Received the wrong product in my UrbanFit order",
                    description=(
                        "My order was delivered today, but I received a pair of UrbanFit "
                        "Core Training Shorts instead of the AeroDry Joggers that I ordered. "
                        "The package label has my name and order number, but the product "
                        "inside is completely different. Please arrange a replacement with "
                        "the correct item."
                    ),
                    status="Open",
                    client_brand="UrbanFit",
                    channel="Email",
                    intake_issue_type="ORD",
                    issue_type="ORD",
                    ticket_sequence=1,
                    created_at=now - timedelta(hours=2),
                    updated_at=now - timedelta(minutes=40),
                ),
                "notes": [
                    Note(
                        ticket_id="TKT-URB-ORD-0001",
                        note_text="Ticket intake created via email support channel.",
                        event_type="TICKET_CREATED",
                        created_at=now - timedelta(hours=2),
                    ),
                    Note(
                        ticket_id="TKT-URB-ORD-0001",
                        note_text="Customer reported incorrect item immediately after delivery.",
                        event_type="NOTE_ADDED",
                        created_at=now - timedelta(hours=1, minutes=45),
                    ),
                    Note(
                        ticket_id="TKT-URB-ORD-0001",
                        note_text="Order and shipment details matched the customer's account.",
                        event_type="NOTE_ADDED",
                        created_at=now - timedelta(hours=1, minutes=15),
                    ),
                    Note(
                        ticket_id="TKT-URB-ORD-0001",
                        note_text="Fulfillment discrepancy identified; replacement requested.",
                        event_type="NOTE_ADDED",
                        created_at=now - timedelta(minutes=40),
                    ),
                ],
            },

            # -----------------------------------------------------------------------
            # FOLLOW-UP TICKET: Rohan Kapoor | Replacement Shipment Tracking | UrbanFit
            # -----------------------------------------------------------------------
            {
                "ticket": Ticket(
                    ticket_id="TKT-URB-ORD-0002",
                    customer_name="Rohan Kapoor",
                    customer_email="rohan.kapoor@gmail.com",
                    subject="Replacement joggers delivery rescheduled by courier",
                    description=(
                        "Following up on ticket TKT-URB-ORD-0001 regarding the incorrect item delivered. "
                        "I received an automated SMS from the courier saying the replacement shipment "
                        "was rescheduled due to address verification. Please confirm that the delivery "
                        "address matches my profile and dispatch without further delay."
                    ),
                    status="Open",
                    client_brand="UrbanFit",
                    channel="Email",
                    intake_issue_type="ORD",
                    issue_type="ORD",
                    ticket_sequence=2,
                    created_at=now - timedelta(minutes=35),
                    updated_at=now - timedelta(minutes=35),
                ),
                "notes": [
                    Note(
                        ticket_id="TKT-URB-ORD-0002",
                        note_text="Ticket intake created via email support channel.",
                        event_type="TICKET_CREATED",
                        created_at=now - timedelta(minutes=35),
                    ),
                    Note(
                        ticket_id="TKT-URB-ORD-0002",
                        note_text="Delivery address re-verified with customer shipping profile.",
                        event_type="NOTE_ADDED",
                        created_at=now - timedelta(minutes=20),
                    ),
                ],
            },

            # -----------------------------------------------------------------------
            # PRIOR HISTORY TICKET 1: Rohan Kapoor (6 weeks ago, Closed)
            # -----------------------------------------------------------------------
            {
                "ticket": Ticket(
                    ticket_id="TKT-URB-PRD-0001",
                    customer_name="Rohan Kapoor",
                    customer_email="rohan.kapoor@gmail.com",
                    subject="Size exchange for previous order",
                    description="Customer requested exchanging size M joggers for size L from prior seasonal drop.",
                    status="Closed",
                    client_brand="UrbanFit",
                    channel="Email",
                    intake_issue_type="PRD",
                    issue_type="PRD",
                    ticket_sequence=1,
                    created_at=now - timedelta(days=42),
                    updated_at=now - timedelta(days=40),
                ),
                "notes": [
                    Note(
                        ticket_id="TKT-URB-PRD-0001",
                        note_text="Ticket intake created via email support.",
                        event_type="TICKET_CREATED",
                        created_at=now - timedelta(days=42),
                    ),
                    Note(
                        ticket_id="TKT-URB-PRD-0001",
                        note_text="Open → In Progress",
                        event_type="STATUS_CHANGE",
                        created_at=now - timedelta(days=41, hours=18),
                    ),
                    Note(
                        ticket_id="TKT-URB-PRD-0001",
                        note_text="Reverse pickup completed; replacement dispatched.",
                        event_type="NOTE_ADDED",
                        created_at=now - timedelta(days=40, hours=6),
                    ),
                    Note(
                        ticket_id="TKT-URB-PRD-0001",
                        note_text="In Progress → Closed",
                        event_type="STATUS_CHANGE",
                        created_at=now - timedelta(days=40),
                    ),
                ],
            },

            # -----------------------------------------------------------------------
            # PRIOR HISTORY TICKET 2: Rohan Kapoor (4 months ago, Closed)
            # -----------------------------------------------------------------------
            {
                "ticket": Ticket(
                    ticket_id="TKT-URB-GEN-0001",
                    customer_name="Rohan Kapoor",
                    customer_email="rohan.kapoor@gmail.com",
                    subject="Delivery status enquiry",
                    description="Customer inquiring about courier transit timeline during monsoon weather advisory.",
                    status="Closed",
                    client_brand="UrbanFit",
                    channel="WhatsApp",
                    intake_issue_type="GEN",
                    issue_type="GEN",
                    ticket_sequence=1,
                    created_at=now - timedelta(days=120),
                    updated_at=now - timedelta(days=119),
                ),
                "notes": [
                    Note(
                        ticket_id="TKT-URB-GEN-0001",
                        note_text="Ticket intake created via WhatsApp.",
                        event_type="TICKET_CREATED",
                        created_at=now - timedelta(days=120),
                    ),
                    Note(
                        ticket_id="TKT-URB-GEN-0001",
                        note_text="Delivered confirmed by Delhivery hub. Resolved.",
                        event_type="NOTE_ADDED",
                        created_at=now - timedelta(days=119, hours=22),
                    ),
                    Note(
                        ticket_id="TKT-URB-GEN-0001",
                        note_text="Open → Closed",
                        event_type="STATUS_CHANGE",
                        created_at=now - timedelta(days=119),
                    ),
                ],
            },

            # -----------------------------------------------------------------------
            # PRIOR HISTORY TICKET 3: Rohan Kapoor (8 months ago, Closed)
            # -----------------------------------------------------------------------
            {
                "ticket": Ticket(
                    ticket_id="TKT-URB-PRD-0002",
                    customer_name="Rohan Kapoor",
                    customer_email="rohan.kapoor@gmail.com",
                    subject="Product availability question",
                    description="Customer inquiring about restock date for heavyweight hoodie drop.",
                    status="Closed",
                    client_brand="UrbanFit",
                    channel="Email",
                    intake_issue_type="PRD",
                    issue_type="PRD",
                    ticket_sequence=2,
                    created_at=now - timedelta(days=240),
                    updated_at=now - timedelta(days=239),
                ),
                "notes": [
                    Note(
                        ticket_id="TKT-URB-PRD-0002",
                        note_text="Ticket intake created via email.",
                        event_type="TICKET_CREATED",
                        created_at=now - timedelta(days=240),
                    ),
                    Note(
                        ticket_id="TKT-URB-PRD-0002",
                        note_text="Catalog restock schedule shared with customer.",
                        event_type="NOTE_ADDED",
                        created_at=now - timedelta(days=239, hours=12),
                    ),
                    Note(
                        ticket_id="TKT-URB-PRD-0002",
                        note_text="Open → Closed",
                        event_type="STATUS_CHANGE",
                        created_at=now - timedelta(days=239),
                    ),
                ],
            },

            # =======================================================================
            # TICKET 05 — Arjun Mehta | Delayed Delivery | CasaNest
            # =======================================================================
            {
                "ticket": Ticket(
                    ticket_id="TKT-CAS-ORD-0001",
                    customer_name="Arjun Mehta",
                    customer_email="arjun.mehta@gmail.com",
                    subject="My order is delayed and the delivery date has already passed",
                    description=(
                        "I ordered the CasaNest Ceramic Cookware Set last week and the "
                        "estimated delivery date was yesterday. The tracking page has not "
                        "updated since the package was picked up, and the order still hasn't "
                        "arrived. Please check where the shipment is and let me know when I "
                        "can expect delivery."
                    ),
                    status="Open",
                    client_brand="CasaNest",
                    channel="Web Portal",
                    intake_issue_type="ORD",
                    issue_type="ORD",
                    ticket_sequence=1,
                    created_at=now - timedelta(hours=3),
                    updated_at=now - timedelta(minutes=50),
                ),
                "notes": [
                    Note(
                        ticket_id="TKT-CAS-ORD-0001",
                        note_text="Ticket intake created via web portal.",
                        event_type="TICKET_CREATED",
                        created_at=now - timedelta(hours=3),
                    ),
                    Note(
                        ticket_id="TKT-CAS-ORD-0001",
                        note_text="Customer reported that the estimated delivery date has passed.",
                        event_type="NOTE_ADDED",
                        created_at=now - timedelta(hours=2, minutes=30),
                    ),
                    Note(
                        ticket_id="TKT-CAS-ORD-0001",
                        note_text="Shipment tracking has not updated since pickup.",
                        event_type="NOTE_ADDED",
                        created_at=now - timedelta(hours=1, minutes=45),
                    ),
                    Note(
                        ticket_id="TKT-CAS-ORD-0001",
                        note_text="Customer requested an updated delivery estimate.",
                        event_type="NOTE_ADDED",
                        created_at=now - timedelta(minutes=50),
                    ),
                ],
            },

            # -----------------------------------------------------------------------
            # FOLLOW-UP TICKET: Arjun Mehta | Warranty Lid Replacement | CasaNest
            # -----------------------------------------------------------------------
            {
                "ticket": Ticket(
                    ticket_id="TKT-CAS-ORD-0002",
                    customer_name="Arjun Mehta",
                    customer_email="arjun.mehta@gmail.com",
                    subject="Cookware lid replacement request for previous order",
                    description=(
                        "The glass lid for the ceramic sauté pan from my previous CasaNest "
                        "cookware set arrived with a small hairline crack near the rim. Could "
                        "you send a replacement lid under the manufacturer warranty?"
                    ),
                    status="Open",
                    client_brand="CasaNest",
                    channel="Web Portal",
                    intake_issue_type="ORD",
                    issue_type="ORD",
                    ticket_sequence=2,
                    created_at=now - timedelta(hours=1, minutes=15),
                    updated_at=now - timedelta(minutes=45),
                ),
                "notes": [
                    Note(
                        ticket_id="TKT-CAS-ORD-0002",
                        note_text="Ticket intake created via web portal.",
                        event_type="TICKET_CREATED",
                        created_at=now - timedelta(hours=1, minutes=15),
                    ),
                    Note(
                        ticket_id="TKT-CAS-ORD-0002",
                        note_text="Customer uploaded warranty invoice and photo of cracked lid.",
                        event_type="NOTE_ADDED",
                        created_at=now - timedelta(minutes=45),
                    ),
                ],
            },

            # =======================================================================
            # TICKET 06 — Sneha Kulkarni | Refund Not Received | GlowTheory
            # =======================================================================
            {
                "ticket": Ticket(
                    ticket_id="TKT-GLO-PAY-0001",
                    customer_name="Sneha Kulkarni",
                    customer_email="sneha.kulkarni@gmail.com",
                    subject="My refund has not been credited yet",
                    description=(
                        "I returned the GlowTheory Vitamin C Brightening Serum because I "
                        "received the wrong variant. The return was picked up a few days ago, "
                        "and I was told that the refund had been initiated, but I still "
                        "haven't received the money in my bank account. Please check the "
                        "refund status and let me know when I should expect the amount."
                    ),
                    status="In Progress",
                    client_brand="GlowTheory",
                    channel="Email",
                    intake_issue_type="PAY",
                    issue_type="PAY",
                    ticket_sequence=1,
                    created_at=now - timedelta(hours=2, minutes=30),
                    updated_at=now - timedelta(minutes=20),
                ),
                "notes": [
                    Note(
                        ticket_id="TKT-GLO-PAY-0001",
                        note_text="Ticket intake created via email support channel.",
                        event_type="TICKET_CREATED",
                        created_at=now - timedelta(hours=2, minutes=30),
                    ),
                    Note(
                        ticket_id="TKT-GLO-PAY-0001",
                        note_text="Open → In Progress",
                        event_type="STATUS_CHANGE",
                        created_at=now - timedelta(hours=1, minutes=45),
                    ),
                    Note(
                        ticket_id="TKT-GLO-PAY-0001",
                        note_text="Customer confirmed that the return shipment was already picked up.",
                        event_type="NOTE_ADDED",
                        created_at=now - timedelta(hours=1, minutes=30),
                    ),
                    Note(
                        ticket_id="TKT-GLO-PAY-0001",
                        note_text="Refund was initiated after return verification.",
                        event_type="NOTE_ADDED",
                        created_at=now - timedelta(minutes=50),
                    ),
                    Note(
                        ticket_id="TKT-GLO-PAY-0001",
                        note_text="Customer reported that the refund has not yet appeared in the original payment account.",
                        event_type="NOTE_ADDED",
                        created_at=now - timedelta(minutes=20),
                    ),
                ],
            },
        ]

        # 3. Insert all tickets and notes into database
        ticket_count = len(tickets_data)
        print(f"[2/3] Inserting {ticket_count} ticket(s) and activity timelines...")

        if ticket_count == 0:
            print("INFO: No tickets defined yet. Database is clean and ready.")
        else:
            for item in tickets_data:
                ticket = item["ticket"]
                notes = item["notes"]
                db.add(ticket)
                db.flush()  # Ensure ticket is persisted before attaching notes

                for note in notes:
                    db.add(note)

            db.commit()
            print(f"PASS: Inserted {ticket_count} ticket(s) and all associated activity notes.")

        # 4. Verification & Summary Output
        print("\n[3/3] Verifying dataset:")
        all_tickets = db.query(Ticket).all()
        all_notes = db.query(Note).all()

        open_tickets = [t for t in all_tickets if t.status == "Open"]
        ip_tickets = [t for t in all_tickets if t.status == "In Progress"]
        closed_tickets = [t for t in all_tickets if t.status == "Closed"]

        print(f"  • Total tickets in DB: {len(all_tickets)}")
        print(f"  • Total notes in DB:   {len(all_notes)}")
        print(f"  • Open ({len(open_tickets)}): {[t.ticket_id for t in open_tickets]}")
        print(f"  • In Progress ({len(ip_tickets)}): {[t.ticket_id for t in ip_tickets]}")
        print(f"  • Closed ({len(closed_tickets)}): {[t.ticket_id for t in closed_tickets]}")

        # Validate structured ID format for any tickets that do exist
        for t in all_tickets:
            parts = t.ticket_id.split("-")
            assert len(parts) == 4, f"Invalid ticket_id format: {t.ticket_id}"
            assert parts[0] == "TKT", f"Prefix must be TKT: {t.ticket_id}"
            assert len(parts[1]) == 3 and parts[1].isupper(), f"Client code must be 3 uppercase chars: {t.ticket_id}"
            assert len(parts[2]) == 3 and parts[2].isupper(), f"Issue code must be 3 uppercase chars: {t.ticket_id}"
            assert len(parts[3]) == 4 and parts[3].isdigit(), f"Sequence must be 4 digits: {t.ticket_id}"
            assert t.issue_type is not None and len(t.issue_type) >= 3, f"Missing issue_type: {t.ticket_id}"
            assert t.intake_issue_type is not None and len(t.intake_issue_type) >= 3, f"Missing intake_issue_type: {t.ticket_id}"
            assert t.ticket_sequence is not None and t.ticket_sequence >= 1, f"Missing ticket_sequence: {t.ticket_id}"

        # Verify all notes reference valid tickets
        valid_ticket_ids = {t.ticket_id for t in all_tickets}
        for n in all_notes:
            assert n.ticket_id in valid_ticket_ids, f"Orphaned note: {n.ticket_id}"

        print("\n" + "=" * 70)
        print("SUCCESS: RelayCX database is clean. Ready for new dataset.")
        print("=" * 70)

    except Exception as e:
        db.rollback()
        print(f"ERROR: Failed to seed database: {e}", file=sys.stderr)
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed_database()
