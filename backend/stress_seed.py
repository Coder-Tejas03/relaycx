"""
Repeatable Stress-Testing Dataset Generator for RelayCX.
Generates exactly 60 realistic stress tickets across diverse customers, issue families,
brands, and lifecycle states to stress-test data isolation, structured ID sequencing,
concurrency, search/filter performance, and customer history retrieval.

Does NOT modify or replace the 7 canonical demo tickets.

Usage:
    cd backend && ../.venv/bin/python stress_seed.py           # Seed 60 stress tickets
    cd backend && ../.venv/bin/python stress_seed.py --restore # Remove stress tickets, restore canonical
"""

import sys
import argparse
from datetime import datetime, timedelta, timezone
from sqlalchemy import text
from app.database import engine, SessionLocal, ensure_schema
from app.models import Ticket, Note
from app import repository, service
from app.service import classify_issue, generate_structured_ticket_id
from seed import seed_database as restore_canonical_seed

CANONICAL_TICKET_IDS = {
    "TKT-URB-INT-0001",
    "TKT-NOV-ACC-0001",
    "TKT-AUR-PAY-0001",
    "TKT-URB-ACC-0001",
    "TKT-AUR-ANA-0001",
    "TKT-NOV-INT-0001",
    "TKT-THR-INT-0001",
}


def get_stress_tickets_spec():
    """
    Returns the specification of exactly 60 realistic stress tickets.
    Covers all 6 required scenarios:
    1. Customer with 10 tickets under same client (Ishaan Kapoor / Aura D2C)
    2. Customer A: multiple issues (Karan Mehta / Aura D2C: ANA, PAY, ORD, INT)
    3. Customer B: multiple issues (Sonali Joshi / UrbanFit: ACC, ORD, PAY)
    4. Cross-client customer (Rohan Kapoor: UrbanFit ORD, Nova Audio ORD, Nova Audio INT)
    5. Cross-client multi-brand (Ananya Rao: Aura D2C PAY, ThreadCo ANA, Nova Audio INT)
    6. Sequence stress: 10 tickets under Aura D2C + INT (TKT-AUR-INT-0001..0010)
    7. Unique customers across diverse brands & issues
    8. GEN / ambiguous tickets
    """
    now = datetime.now(timezone.utc)

    # Helper for relative timestamps
    def hours_ago(h):
        return now - timedelta(hours=h)

    def days_ago(d, h=0):
        return now - timedelta(days=d, hours=h)

    specs = [
        # =====================================================================
        # GROUP 1: Ishaan Kapoor (10 tickets, Aura D2C) - High-Volume Customer (§7)
        # =====================================================================
        {
            "name": "Ishaan Kapoor",
            "email": "ishaan.kapoor@cloudcart.dev",
            "brand": "Aura D2C",
            "channel": "Email",
            "status": "In Progress",
            "subject": "CSV export lambda timeout on monthly order analytics",
            "description": "Exporting order analytics for October hits the 15s Lambda execution timeout, resulting in a zero byte file download.",
            "created_at": days_ago(6, 4),
            "updated_at": days_ago(5, 2),
            "notes": [
                ("Ticket intake created via automated system export monitor.", "TICKET_CREATED", days_ago(6, 4)),
                ("Open → In Progress", "STATUS_CHANGE", days_ago(5, 12)),
                ("Investigating Lambda concurrency and execution limits on reporting worker.", "NOTE_ADDED", days_ago(5, 2)),
            ],
        },
        {
            "name": "Ishaan Kapoor",
            "email": "ishaan.kapoor@cloudcart.dev",
            "brand": "Aura D2C",
            "channel": "WhatsApp",
            "status": "Open",
            "subject": "Payment charged twice on credit card at checkout",
            "description": "Double charge of ₹2,899 appeared on customer credit card statement after a momentary network interruption on checkout.",
            "created_at": hours_ago(5),
            "updated_at": hours_ago(5),
            "notes": [],
        },
        {
            "name": "Ishaan Kapoor",
            "email": "ishaan.kapoor@cloudcart.dev",
            "brand": "Aura D2C",
            "channel": "Web Portal",
            "status": "Closed",
            "subject": "Order shipment tracking number shows not found on Blue Dart",
            "description": "AWB tracking number BLD-88219 returned tracking details not found on Blue Dart portal for 48 hours after dispatch email.",
            "created_at": days_ago(8),
            "updated_at": days_ago(6),
            "notes": [
                ("Ticket intake created via support portal.", "TICKET_CREATED", days_ago(8)),
                ("Open → In Progress", "STATUS_CHANGE", days_ago(7, 18)),
                ("Courier manifest scanned at regional hub. Tracking updated.", "NOTE_ADDED", days_ago(7, 10)),
                ("In Progress → Closed", "STATUS_CHANGE", days_ago(6)),
                ("Customer confirmed delivery received in good condition.", "NOTE_ADDED", days_ago(6)),
            ],
        },
        {
            "name": "Ishaan Kapoor",
            "email": "ishaan.kapoor@cloudcart.dev",
            "brand": "Aura D2C",
            "channel": "Email",
            "status": "Open",
            "subject": "Webhook endpoint returning HTTP 500 on order.created payload",
            "description": "Our ingestion receiver is receiving HTTP 500 errors on order.created webhooks sent by the store integration.",
            "created_at": days_ago(2, 6),
            "updated_at": days_ago(2, 6),
            "notes": [],
        },
        {
            "name": "Ishaan Kapoor",
            "email": "ishaan.kapoor@cloudcart.dev",
            "brand": "Aura D2C",
            "channel": "Email",
            "status": "Closed",
            "subject": "Organization admin 2FA lockout after corporate domain migration",
            "description": "Admin cannot authenticate to settings dashboard due to 2FA verification failure following email domain switch.",
            "created_at": days_ago(12),
            "updated_at": days_ago(10),
            "notes": [
                ("Ticket intake created via emergency admin line.", "TICKET_CREATED", days_ago(12)),
                ("Open → In Progress", "STATUS_CHANGE", days_ago(11, 20)),
                ("Identity verified via secondary corporate auth channel. 2FA secret reset.", "NOTE_ADDED", days_ago(10, 4)),
                ("In Progress → Closed", "STATUS_CHANGE", days_ago(10)),
            ],
        },
        {
            "name": "Ishaan Kapoor",
            "email": "ishaan.kapoor@cloudcart.dev",
            "brand": "Aura D2C",
            "channel": "WhatsApp",
            "status": "Open",
            "subject": "Missing items from delivered package shipment",
            "description": "Received parcel ORD-9102 containing facial serum but the botanical mist duo was missing from the box.",
            "created_at": hours_ago(18),
            "updated_at": hours_ago(18),
            "notes": [],
        },
        {
            "name": "Ishaan Kapoor",
            "email": "ishaan.kapoor@cloudcart.dev",
            "brand": "Aura D2C",
            "channel": "Email",
            "status": "In Progress",
            "subject": "Refund billing adjustment missing promotional discount balance",
            "description": "The refunded transaction did not credit back the ₹450 promotional coupon balance to the digital wallet.",
            "created_at": days_ago(1, 10),
            "updated_at": hours_ago(14),
            "notes": [
                ("Ticket intake created via email support.", "TICKET_CREATED", days_ago(1, 10)),
                ("Open → In Progress", "STATUS_CHANGE", hours_ago(20)),
                ("Billing team calculating promotional credit adjustment.", "NOTE_ADDED", hours_ago(14)),
            ],
        },
        {
            "name": "Ishaan Kapoor",
            "email": "ishaan.kapoor@cloudcart.dev",
            "brand": "Aura D2C",
            "channel": "Web Portal",
            "status": "Open",
            "subject": "Reporting analytics dashboard showing empty charts for weekly retention",
            "description": "Weekly customer retention report renders empty graphs when grouped by cohort despite active customer activity.",
            "created_at": days_ago(3, 8),
            "updated_at": days_ago(3, 8),
            "notes": [],
        },
        {
            "name": "Ishaan Kapoor",
            "email": "ishaan.kapoor@cloudcart.dev",
            "brand": "Aura D2C",
            "channel": "Email",
            "status": "Open",
            "subject": "Mobile app crash when applying product category filter",
            "description": "Android app crashes with NullPointerException when filtering catalog products by organic certification tag.",
            "created_at": days_ago(4, 12),
            "updated_at": days_ago(4, 12),
            "notes": [],
        },
        {
            "name": "Ishaan Kapoor",
            "email": "ishaan.kapoor@cloudcart.dev",
            "brand": "Aura D2C",
            "channel": "Email",
            "status": "Closed",
            "subject": "Assistance needed with corporate gifting catalog options",
            "description": "Inquiring about bulk packaging and custom branding options for corporate holiday gift hampers.",
            "created_at": days_ago(15),
            "updated_at": days_ago(13),
            "notes": [
                ("Ticket intake created.", "TICKET_CREATED", days_ago(15)),
                ("Open → In Progress", "STATUS_CHANGE", days_ago(14, 10)),
                ("Shared corporate catalog and pricing sheet with customer.", "NOTE_ADDED", days_ago(13, 14)),
                ("In Progress → Closed", "STATUS_CHANGE", days_ago(13)),
            ],
        },

        # =====================================================================
        # GROUP 2: Karan Mehta (4 tickets, Aura D2C) - Customer A (§5)
        # =====================================================================
        {
            "name": "Karan Mehta",
            "email": "karan.mehta@finscale.io",
            "brand": "Aura D2C",
            "channel": "Email",
            "status": "Open",
            "subject": "Analytics report generation timeout on large date range",
            "description": "Generating customer segmentation CSV report for last 90 days fails with timeout.",
            "created_at": days_ago(1, 4),
            "updated_at": days_ago(1, 4),
            "notes": [],
        },
        {
            "name": "Karan Mehta",
            "email": "karan.mehta@finscale.io",
            "brand": "Aura D2C",
            "channel": "Email",
            "status": "Closed",
            "subject": "Stripe invoice billing link expired for enterprise tier",
            "description": "Invoice payment link sent for annual renewal expired before finance team could process payment.",
            "created_at": days_ago(5),
            "updated_at": days_ago(4),
            "notes": [
                ("Ticket intake created.", "TICKET_CREATED", days_ago(5)),
                ("Regenerated payment invoice link via Stripe billing portal.", "NOTE_ADDED", days_ago(4, 8)),
                ("In Progress → Closed", "STATUS_CHANGE", days_ago(4)),
            ],
        },
        {
            "name": "Karan Mehta",
            "email": "karan.mehta@finscale.io",
            "brand": "Aura D2C",
            "channel": "WhatsApp",
            "status": "In Progress",
            "subject": "Order package delivery delayed past promised estimated delivery date",
            "description": "Order for Luxury Botanical Trio promised delivery by yesterday has not arrived.",
            "created_at": hours_ago(30),
            "updated_at": hours_ago(8),
            "notes": [
                ("Ticket intake created via WhatsApp.", "TICKET_CREATED", hours_ago(30)),
                ("Open → In Progress", "STATUS_CHANGE", hours_ago(22)),
                ("Courier hub contacted. Out for delivery today.", "NOTE_ADDED", hours_ago(8)),
            ],
        },
        {
            "name": "Karan Mehta",
            "email": "karan.mehta@finscale.io",
            "brand": "Aura D2C",
            "channel": "Email",
            "status": "Open",
            "subject": "API rate limit 429 received on bulk catalog sync integration endpoint",
            "description": "Product catalog sync job received continuous HTTP 429 rate limit errors during nightly catalog update.",
            "created_at": hours_ago(12),
            "updated_at": hours_ago(12),
            "notes": [],
        },

        # =====================================================================
        # GROUP 3: Sonali Joshi (3 tickets, UrbanFit) - Customer B (§5)
        # =====================================================================
        {
            "name": "Sonali Joshi",
            "email": "sonali.joshi@urbanfit.co",
            "brand": "UrbanFit",
            "channel": "Email",
            "status": "Open",
            "subject": "Account login 2FA OTP verification code not arriving on SMS",
            "description": "Attempting to login to membership portal but SMS OTP code is never delivered.",
            "created_at": hours_ago(4),
            "updated_at": hours_ago(4),
            "notes": [],
        },
        {
            "name": "Sonali Joshi",
            "email": "sonali.joshi@urbanfit.co",
            "brand": "UrbanFit",
            "channel": "WhatsApp",
            "status": "In Progress",
            "subject": "Order exchange request for training joggers size medium to large",
            "description": "Customer needs to exchange delivered charcoal joggers from size M to L.",
            "created_at": days_ago(1, 16),
            "updated_at": hours_ago(6),
            "notes": [
                ("Ticket intake created.", "TICKET_CREATED", days_ago(1, 16)),
                ("Open → In Progress", "STATUS_CHANGE", days_ago(1)),
                ("Pickup scheduled via Delhivery courier for reverse pickup.", "NOTE_ADDED", hours_ago(6)),
            ],
        },
        {
            "name": "Sonali Joshi",
            "email": "sonali.joshi@urbanfit.co",
            "brand": "UrbanFit",
            "channel": "Email",
            "status": "Closed",
            "subject": "Payment transaction charged on card but order confirmation failed",
            "description": "Debit card charged ₹3,499 but cart checkout threw payment verification error.",
            "created_at": days_ago(7),
            "updated_at": days_ago(5),
            "notes": [
                ("Ticket intake created.", "TICKET_CREATED", days_ago(7)),
                ("Open → In Progress", "STATUS_CHANGE", days_ago(6, 12)),
                ("Payment reconciled with Razorpay gateway. Order manually generated and fulfilled.", "NOTE_ADDED", days_ago(5, 8)),
                ("In Progress → Closed", "STATUS_CHANGE", days_ago(5)),
            ],
        },

        # =====================================================================
        # GROUP 4: Rohan Kapoor (Cross-Client Isolation, UrbanFit + Nova Audio) (§5)
        # =====================================================================
        {
            "name": "Rohan Kapoor",
            "email": "rohan.kapoor@novabanking.com",
            "brand": "UrbanFit",
            "channel": "Email",
            "status": "In Progress",
            "subject": "Tracking shipment status inquiry for replacement training joggers",
            "description": "Replacement package tracking number DEL-89042-IN has had no scan updates for 36 hours.",
            "created_at": days_ago(2, 4),
            "updated_at": hours_ago(16),
            "notes": [
                ("Ticket intake created.", "TICKET_CREATED", days_ago(2, 4)),
                ("Open → In Progress", "STATUS_CHANGE", days_ago(1, 18)),
                ("Delhivery logistics hub confirms parcel transit to Gurgaon sorting facility.", "NOTE_ADDED", hours_ago(16)),
            ],
        },
        {
            "name": "Rohan Kapoor",
            "email": "rohan.kapoor@novabanking.com",
            "brand": "Nova Audio",
            "channel": "Email",
            "status": "Open",
            "subject": "Delivery address update for studio monitor speakers order",
            "description": "Need to update corporate delivery address for Nova Studio Monitors order ORD-5520 prior to dispatch.",
            "created_at": hours_ago(9),
            "updated_at": hours_ago(9),
            "notes": [],
        },
        {
            "name": "Rohan Kapoor",
            "email": "rohan.kapoor@novabanking.com",
            "brand": "Nova Audio",
            "channel": "Web Portal",
            "status": "Closed",
            "subject": "API webhook integration returning HTTP 400 bad request on telemetry stream",
            "description": "Telemetry audio stream webhook receiver rejected payload due to header authorization format mismatch.",
            "created_at": days_ago(9),
            "updated_at": days_ago(7),
            "notes": [
                ("Ticket intake created via developer portal.", "TICKET_CREATED", days_ago(9)),
                ("Open → In Progress", "STATUS_CHANGE", days_ago(8, 14)),
                ("Customer resolved header auth format to match Bearer token scheme. Deliveries 200 OK.", "NOTE_ADDED", days_ago(7, 4)),
                ("In Progress → Closed", "STATUS_CHANGE", days_ago(7)),
            ],
        },

        # =====================================================================
        # GROUP 5: Ananya Rao (Cross-Client across 3 brands: Aura, ThreadCo, Nova) (§5)
        # =====================================================================
        {
            "name": "Ananya Rao",
            "email": "ananya.rao@omnimail.tech",
            "brand": "Aura D2C",
            "channel": "Email",
            "status": "Open",
            "subject": "Subscription renewal payment failed on recurring credit card charge",
            "description": "Monthly botanical elixir auto-ship subscription failed with payment gateway declined error.",
            "created_at": hours_ago(8),
            "updated_at": hours_ago(8),
            "notes": [],
        },
        {
            "name": "Ananya Rao",
            "email": "ananya.rao@omnimail.tech",
            "brand": "ThreadCo",
            "channel": "Email",
            "status": "In Progress",
            "subject": "Monthly sales analytics reporting CSV export missing tax breakdown",
            "description": "The downloaded analytics report omits GST tax breakdown columns for B2B wholesale orders.",
            "created_at": days_ago(1, 8),
            "updated_at": hours_ago(11),
            "notes": [
                ("Ticket intake created.", "TICKET_CREATED", days_ago(1, 8)),
                ("Open → In Progress", "STATUS_CHANGE", hours_ago(24)),
                ("Engineering added GST column to export query template.", "NOTE_ADDED", hours_ago(11)),
            ],
        },
        {
            "name": "Ananya Rao",
            "email": "ananya.rao@omnimail.tech",
            "brand": "Nova Audio",
            "channel": "Web Portal",
            "status": "Closed",
            "subject": "API webhook authorization signature verification mismatch",
            "description": "HMAC-SHA256 signature header verification fails intermittently when payload contains unicode characters.",
            "created_at": days_ago(6),
            "updated_at": days_ago(4),
            "notes": [
                ("Ticket intake created.", "TICKET_CREATED", days_ago(6)),
                ("Open → In Progress", "STATUS_CHANGE", days_ago(5, 12)),
                ("Identified UTF-8 byte encoding normalization issue in verification middleware. Patched.", "NOTE_ADDED", days_ago(4, 6)),
                ("In Progress → Closed", "STATUS_CHANGE", days_ago(4)),
            ],
        },

        # =====================================================================
        # GROUP 6: Aura D2C + INT Sequence Stress (10 tickets: TKT-AUR-INT-0001..0010) (§8)
        # =====================================================================
        {
            "name": "Kabir Sen",
            "email": "kabir.sen@devscale.io",
            "brand": "Aura D2C",
            "channel": "Email",
            "status": "Open",
            "subject": "Webhook integration returning HTTP 500 internal server error",
            "description": "Webhook notification endpoint fails with HTTP 500 when dispatching inventory adjustment events.",
            "created_at": days_ago(4, 8),
            "updated_at": days_ago(4, 8),
            "notes": [],
        },
        {
            "name": "Neha Gupta",
            "email": "neha.gupta@cloudware.org",
            "brand": "Aura D2C",
            "channel": "Email",
            "status": "In Progress",
            "subject": "API rate limit 429 errors on bulk product inventory update endpoint",
            "description": "Continuous HTTP 429 Too Many Requests encountered during high frequency inventory sync.",
            "created_at": days_ago(3, 14),
            "updated_at": days_ago(2, 8),
            "notes": [
                ("Ticket intake created.", "TICKET_CREATED", days_ago(3, 14)),
                ("Open → In Progress", "STATUS_CHANGE", days_ago(2, 18)),
                ("Temporarily increased API rate limiter bucket capacity to 500 req/min.", "NOTE_ADDED", days_ago(2, 8)),
            ],
        },
        {
            "name": "Tariq Khan",
            "email": "tariq.khan@syncflow.net",
            "brand": "Aura D2C",
            "channel": "Web Portal",
            "status": "Closed",
            "subject": "Webhook duplicate delivery on order.fulfilled event",
            "description": "Duplicate webhook event deliveries caused double fulfillment records in secondary ERP.",
            "created_at": days_ago(5, 10),
            "updated_at": days_ago(3, 2),
            "notes": [
                ("Ticket intake created.", "TICKET_CREATED", days_ago(5, 10)),
                ("Open → In Progress", "STATUS_CHANGE", days_ago(4, 16)),
                ("Configured idempotency key deduplication cache on webhook dispatch worker.", "NOTE_ADDED", days_ago(3, 2)),
                ("In Progress → Closed", "STATUS_CHANGE", days_ago(3, 2)),
            ],
        },
        {
            "name": "Tanya Verma",
            "email": "tanya.verma@apexcloud.io",
            "brand": "Aura D2C",
            "channel": "Email",
            "status": "Open",
            "subject": "API integration endpoint returning schema mismatch on product payload",
            "description": "The v2 product API response schema contains an unexpected array instead of an object for variant attributes.",
            "created_at": days_ago(2, 10),
            "updated_at": days_ago(2, 10),
            "notes": [],
        },
        {
            "name": "Rahul Roy",
            "email": "rahul.roy@databridge.dev",
            "brand": "Aura D2C",
            "channel": "Email",
            "status": "Open",
            "subject": "API rate limit HTTP 429 throttling during store catalog migration",
            "description": "Bulk import pipeline hit rate limit cap resulting in 40,000 stalled catalog entities.",
            "created_at": days_ago(1, 14),
            "updated_at": days_ago(1, 14),
            "notes": [],
        },
        {
            "name": "Pooja Bose",
            "email": "pooja.bose@applink.co",
            "brand": "Aura D2C",
            "channel": "Email",
            "status": "In Progress",
            "subject": "Webhook secret rotation failure on production endpoint",
            "description": "Rotating webhook signing secret caused all subsequent HMAC validations to fail with 401 Unauthorized.",
            "created_at": hours_ago(28),
            "updated_at": hours_ago(10),
            "notes": [
                ("Ticket intake created.", "TICKET_CREATED", hours_ago(28)),
                ("Open → In Progress", "STATUS_CHANGE", hours_ago(20)),
                ("Synchronized dual secret verification window in webhook validator.", "NOTE_ADDED", hours_ago(10)),
            ],
        },
        {
            "name": "Amit Deshmukh",
            "email": "amit.deshmukh@enterprisegrid.com",
            "brand": "Aura D2C",
            "channel": "Email",
            "status": "Closed",
            "subject": "API gateway connection reset on POST to /v1/orders webhook",
            "description": "TCP connection reset by peer during TLS handshake on webhook listener endpoint.",
            "created_at": days_ago(7),
            "updated_at": days_ago(5),
            "notes": [
                ("Ticket intake created.", "TICKET_CREATED", days_ago(7)),
                ("Open → In Progress", "STATUS_CHANGE", days_ago(6, 10)),
                ("Renewed intermediate CA certificates on edge load balancer.", "NOTE_ADDED", days_ago(5, 4)),
                ("In Progress → Closed", "STATUS_CHANGE", days_ago(5)),
            ],
        },
        {
            "name": "Sanya Sethi",
            "email": "sanya.sethi@pipestream.io",
            "brand": "Aura D2C",
            "channel": "WhatsApp",
            "status": "Open",
            "subject": "Webhook retry backoff logic exceeding 24-hour SLA",
            "description": "Failed webhook delivery retries are scheduled with exponential backoff exceeding the standard SLA window.",
            "created_at": hours_ago(15),
            "updated_at": hours_ago(15),
            "notes": [],
        },
        {
            "name": "Farhan Ali",
            "email": "farhan.ali@cloudmatrix.org",
            "brand": "Aura D2C",
            "channel": "Email",
            "status": "In Progress",
            "subject": "API payload truncated on large event batch delivery",
            "description": "Webhooks containing more than 50 line items are truncated at the 64KB edge buffer limit.",
            "created_at": days_ago(1, 2),
            "updated_at": hours_ago(7),
            "notes": [
                ("Ticket intake created.", "TICKET_CREATED", days_ago(1, 2)),
                ("Open → In Progress", "STATUS_CHANGE", hours_ago(18)),
                ("Evaluating chunked payload streaming for oversized webhook events.", "NOTE_ADDED", hours_ago(7)),
            ],
        },
        {
            "name": "Divya Pillai",
            "email": "divya.pillai@securenet.in",
            "brand": "Aura D2C",
            "channel": "Email",
            "status": "Closed",
            "subject": "API authentication bearer token rejected with HTTP 401",
            "description": "Service account bearer token rejected due to clock skew between server and token issuer.",
            "created_at": days_ago(4, 18),
            "updated_at": days_ago(3, 8),
            "notes": [
                ("Ticket intake created.", "TICKET_CREATED", days_ago(4, 18)),
                ("Open → In Progress", "STATUS_CHANGE", days_ago(4, 2)),
                ("Configured 60s NTP clock drift tolerance in JWT authentication validator.", "NOTE_ADDED", days_ago(3, 8)),
                ("In Progress → Closed", "STATUS_CHANGE", days_ago(3, 8)),
            ],
        },

        # =====================================================================
        # GROUP 7: Diverse Unique Customers Across Brands & Taxonomy Families (23 tickets)
        # =====================================================================
        {
            "name": "Arjun Singhania",
            "email": "arjun.singhania@urbanfitwear.in",
            "brand": "UrbanFit",
            "channel": "Email",
            "status": "Open",
            "subject": "Product sizing chart discrepancy for compression tights fit",
            "description": "Size guide measurements for compression tights waist do not match physical garment received.",
            "created_at": hours_ago(6),
            "updated_at": hours_ago(6),
            "notes": [],
        },
        {
            "name": "Kavita Reddy",
            "email": "kavita.reddy@hyderabadtech.co",
            "brand": "UrbanFit",
            "channel": "WhatsApp",
            "status": "In Progress",
            "subject": "Order delivery tracking delayed on Blue Dart express shipment",
            "description": "Air shipment package ORD-7104 stuck at Mumbai airport transshipment facility for 3 days.",
            "created_at": days_ago(2, 6),
            "updated_at": hours_ago(14),
            "notes": [
                ("Ticket intake created.", "TICKET_CREATED", days_ago(2, 6)),
                ("Open → In Progress", "STATUS_CHANGE", days_ago(1, 16)),
                ("Escalated to Blue Dart priority resolution desk.", "NOTE_ADDED", hours_ago(14)),
            ],
        },
        {
            "name": "Manoj Bajpai",
            "email": "manoj.bajpai@fitnesspro.in",
            "brand": "UrbanFit",
            "channel": "Email",
            "status": "Closed",
            "subject": "Payment refund balance credited to wrong bank account",
            "description": "Refund for returned yoga mat credited to expired net banking account rather than original card.",
            "created_at": days_ago(6),
            "updated_at": days_ago(4),
            "notes": [
                ("Ticket intake created.", "TICKET_CREATED", days_ago(6)),
                ("Open → In Progress", "STATUS_CHANGE", days_ago(5, 12)),
                ("Razorpay payout re-routed to updated UPI handle. Verified credited.", "NOTE_ADDED", days_ago(4, 6)),
                ("In Progress → Closed", "STATUS_CHANGE", days_ago(4)),
            ],
        },
        {
            "name": "Nikhil Agarwal",
            "email": "nikhil.agarwal@novasound.io",
            "brand": "Nova Audio",
            "channel": "Email",
            "status": "Open",
            "subject": "Headphone driver distortion in left ear cup hardware",
            "description": "Left ear cup on Nova Studio Wireless headphones crackles at frequencies below 120Hz.",
            "created_at": hours_ago(16),
            "updated_at": hours_ago(16),
            "notes": [],
        },
        {
            "name": "Sneha Kulkarni",
            "email": "sneha.kulkarni@audiomix.org",
            "brand": "Nova Audio",
            "channel": "Web Portal",
            "status": "In Progress",
            "subject": "Cannot access billing invoice history on subscriber portal",
            "description": "Clicking Download Invoice on monthly subscription history page returns blank PDF page.",
            "created_at": days_ago(1, 18),
            "updated_at": hours_ago(12),
            "notes": [
                ("Ticket intake created.", "TICKET_CREATED", days_ago(1, 18)),
                ("Open → In Progress", "STATUS_CHANGE", hours_ago(22)),
                ("Billing service PDF generation template patched for font rendering.", "NOTE_ADDED", hours_ago(12)),
            ],
        },
        {
            "name": "Rajesh Nambiar",
            "email": "rajesh.nambiar@audiotech.in",
            "brand": "Nova Audio",
            "channel": "Email",
            "status": "Closed",
            "subject": "Order shipment package marked delivered but not received by concierge",
            "description": "Delhivery tracking indicates delivered yesterday 4 PM but building reception has no record of parcel.",
            "created_at": days_ago(5, 4),
            "updated_at": days_ago(3, 10),
            "notes": [
                ("Ticket intake created.", "TICKET_CREATED", days_ago(5, 4)),
                ("Open → In Progress", "STATUS_CHANGE", days_ago(4, 14)),
                ("Courier delivery executive re-visited and delivered to correct suite.", "NOTE_ADDED", days_ago(3, 10)),
                ("In Progress → Closed", "STATUS_CHANGE", days_ago(3, 10)),
            ],
        },
        {
            "name": "Ayesha Siddiqui",
            "email": "ayesha.siddiqui@threadco.com",
            "brand": "ThreadCo",
            "channel": "Email",
            "status": "Open",
            "subject": "Order package returned to sender by courier without delivery attempt",
            "description": "Tracking indicates package marked RTO - Address Incomplete despite correct pin code.",
            "created_at": hours_ago(7),
            "updated_at": hours_ago(7),
            "notes": [],
        },
        {
            "name": "Vikramaditya Rao",
            "email": "vikramaditya.rao@apparelhub.net",
            "brand": "ThreadCo",
            "channel": "Instagram",
            "status": "In Progress",
            "subject": "Product sizing specifications missing for bamboo crew socks pack",
            "description": "Catalog page does not specify shoe size chart range for size Large bamboo socks.",
            "created_at": days_ago(1, 12),
            "updated_at": hours_ago(9),
            "notes": [
                ("Ticket intake created via Instagram DM.", "TICKET_CREATED", days_ago(1, 12)),
                ("Open → In Progress", "STATUS_CHANGE", hours_ago(20)),
                ("Content team updating catalog page with UK/US shoe size conversion matrix.", "NOTE_ADDED", hours_ago(9)),
            ],
        },
        {
            "name": "Bhavna Patel",
            "email": "bhavna.patel@textilecraft.in",
            "brand": "ThreadCo",
            "channel": "Email",
            "status": "Closed",
            "subject": "Account locked after failed 2FA verification attempts on wholesale portal",
            "description": "B2B buyer entered incorrect OTP 5 times. Account placed in 24-hour security hold.",
            "created_at": days_ago(8),
            "updated_at": days_ago(6),
            "notes": [
                ("Ticket intake created.", "TICKET_CREATED", days_ago(8)),
                ("Open → In Progress", "STATUS_CHANGE", days_ago(7, 10)),
                ("Account unlocked after verifying registered tax identification certificate.", "NOTE_ADDED", days_ago(6, 4)),
                ("In Progress → Closed", "STATUS_CHANGE", days_ago(6)),
            ],
        },
        {
            "name": "Aditya Joshi",
            "email": "aditya.joshi@zenbotanics.com",
            "brand": "Zen Botanics",
            "channel": "Email",
            "status": "Open",
            "subject": "Organic facial serum bottle leaking during transit shipment",
            "description": "Received package containing facial oil with broken dropper seal and liquid leaked in carton.",
            "created_at": hours_ago(11),
            "updated_at": hours_ago(11),
            "notes": [],
        },
        {
            "name": "Pallavi Menon",
            "email": "pallavi.menon@naturalcare.dev",
            "brand": "Zen Botanics",
            "channel": "WhatsApp",
            "status": "In Progress",
            "subject": "Discount promo code not applying on checkout payment total",
            "description": "Seasonal discount code WELCOME20 displays 'Code Valid' but does not discount cart total.",
            "created_at": days_ago(1, 20),
            "updated_at": hours_ago(15),
            "notes": [
                ("Ticket intake created.", "TICKET_CREATED", days_ago(1, 20)),
                ("Open → In Progress", "STATUS_CHANGE", hours_ago(23)),
                ("Identified minimum cart value threshold misconfigured in coupon rule engine.", "NOTE_ADDED", hours_ago(15)),
            ],
        },
        {
            "name": "Girish Chawla",
            "email": "girish.chawla@botanicallife.org",
            "brand": "Zen Botanics",
            "channel": "Email",
            "status": "Closed",
            "subject": "Order package delivery delayed past promised delivery date",
            "description": "Herbal tea infusion sampler box ordered 8 days ago has not been delivered.",
            "created_at": days_ago(7, 12),
            "updated_at": days_ago(4, 18),
            "notes": [
                ("Ticket intake created.", "TICKET_CREATED", days_ago(7, 12)),
                ("Open → In Progress", "STATUS_CHANGE", days_ago(6, 14)),
                ("Replacement parcel dispatched via Blue Dart Air priority. Delivered.", "NOTE_ADDED", days_ago(4, 18)),
                ("In Progress → Closed", "STATUS_CHANGE", days_ago(4, 18)),
            ],
        },
        {
            "name": "Meenakshi Sundaram",
            "email": "meenakshi.s@zenbotanics.com",
            "brand": "Zen Botanics",
            "channel": "Email",
            "status": "Open",
            "subject": "CSV export analytics report returns empty file for monthly sales",
            "description": "Monthly revenue export under Reports > Financials generates a 0-byte CSV file.",
            "created_at": days_ago(2, 12),
            "updated_at": days_ago(2, 12),
            "notes": [],
        },
        {
            "name": "Ritu Sharma",
            "email": "ritu.sharma@urbanpulse.in",
            "brand": "UrbanFit",
            "channel": "Email",
            "status": "Open",
            "subject": "Account password reset email link not arriving in inbox",
            "description": "Requested password reset link multiple times over 2 hours but no email received.",
            "created_at": hours_ago(3),
            "updated_at": hours_ago(3),
            "notes": [],
        },
        {
            "name": "Harish Venkat",
            "email": "harish.venkat@audioforge.io",
            "brand": "Nova Audio",
            "channel": "Email",
            "status": "In Progress",
            "subject": "Webhook integration HTTP 500 error on payment.completed event",
            "description": "Ingestion bridge fails when payment completed event contains multi-currency values.",
            "created_at": days_ago(2, 1),
            "updated_at": hours_ago(19),
            "notes": [
                ("Ticket intake created.", "TICKET_CREATED", days_ago(2, 1)),
                ("Open → In Progress", "STATUS_CHANGE", days_ago(1, 10)),
                ("Adding currency code normalizer to payload intake pipeline.", "NOTE_ADDED", hours_ago(19)),
            ],
        },
        {
            "name": "Tanvi Bhatia",
            "email": "tanvi.bhatia@threadsociety.com",
            "brand": "ThreadCo",
            "channel": "Email",
            "status": "Open",
            "subject": "Payment refund processed in Stripe but bank ledger not updated",
            "description": "Stripe transaction status shows refunded 4 days ago but customer account shows pending.",
            "created_at": days_ago(1, 6),
            "updated_at": days_ago(1, 6),
            "notes": [],
        },
        {
            "name": "Varun Khanna",
            "email": "varun.khanna@urbanpulse.in",
            "brand": "UrbanFit",
            "channel": "WhatsApp",
            "status": "Closed",
            "subject": "Order package delivery missing workout gym bag",
            "description": "Gym bag was omitted from multi-item shipment ORD-4412.",
            "created_at": days_ago(9),
            "updated_at": days_ago(6),
            "notes": [
                ("Ticket intake created.", "TICKET_CREATED", days_ago(9)),
                ("Open → In Progress", "STATUS_CHANGE", days_ago(8, 4)),
                ("Second shipment dispatched containing missing gym bag.", "NOTE_ADDED", days_ago(6, 12)),
                ("In Progress → Closed", "STATUS_CHANGE", days_ago(6)),
            ],
        },
        {
            "name": "Shweta Tiwari",
            "email": "shweta.tiwari@purebotanics.in",
            "brand": "Zen Botanics",
            "channel": "Email",
            "status": "Open",
            "subject": "Account login lockout after multiple failed password attempts",
            "description": "Entered wrong password after returning from vacation. Account currently locked.",
            "created_at": hours_ago(5),
            "updated_at": hours_ago(5),
            "notes": [],
        },
        {
            "name": "Deepak Chopra",
            "email": "deepak.chopra@soundstage.dev",
            "brand": "Nova Audio",
            "channel": "Email",
            "status": "In Progress",
            "subject": "CSV export reporting analytics date range filter timeout",
            "description": "Exporting telemetry log metrics for greater than 14 days causes Lambda timeout.",
            "created_at": days_ago(2, 14),
            "updated_at": hours_ago(17),
            "notes": [
                ("Ticket intake created.", "TICKET_CREATED", days_ago(2, 14)),
                ("Open → In Progress", "STATUS_CHANGE", days_ago(1, 20)),
                ("Investigating S3 multipart export stream to prevent worker timeout.", "NOTE_ADDED", hours_ago(17)),
            ],
        },
        {
            "name": "Kritika Roy",
            "email": "kritika.roy@fashionweave.org",
            "brand": "ThreadCo",
            "channel": "Email",
            "status": "Open",
            "subject": "Product sizing specifications incorrect for merino wool sweater",
            "description": "Sleeve length on received sweater is 4 inches shorter than catalog specifications chart.",
            "created_at": days_ago(1, 1),
            "updated_at": days_ago(1, 1),
            "notes": [],
        },
        {
            "name": "Anil Kumble",
            "email": "anil.kumble@urbanfit.co",
            "brand": "UrbanFit",
            "channel": "Email",
            "status": "Closed",
            "subject": "API webhook delivery failing with HTTP 429 rate limit exceeded",
            "description": "Inventory webhook listener received continuous 429 status during midnight batch.",
            "created_at": days_ago(10),
            "updated_at": days_ago(8),
            "notes": [
                ("Ticket intake created.", "TICKET_CREATED", days_ago(10)),
                ("Open → In Progress", "STATUS_CHANGE", days_ago(9, 12)),
                ("Configured client-side retry exponential backoff with jitter. Deliveries healthy.", "NOTE_ADDED", days_ago(8, 6)),
                ("In Progress → Closed", "STATUS_CHANGE", days_ago(8)),
            ],
        },
        {
            "name": "Siddharth Sen",
            "email": "siddharth.sen@aurabeauty.in",
            "brand": "Aura D2C",
            "channel": "WhatsApp",
            "status": "Open",
            "subject": "Order package delivery shipment tracking status stuck in transit",
            "description": "Shipment has remained in transit status between Bangalore hub and Mumbai for 5 days.",
            "created_at": hours_ago(22),
            "updated_at": hours_ago(22),
            "notes": [],
        },
        {
            "name": "Sunita Rao",
            "email": "sunita.rao@zenbotanics.com",
            "brand": "Zen Botanics",
            "channel": "Email",
            "status": "In Progress",
            "subject": "Payment billing charge dispute on international transaction fee",
            "description": "Credit card billed unexpected 3.5% foreign currency markup on domestic order.",
            "created_at": days_ago(2, 4),
            "updated_at": hours_ago(13),
            "notes": [
                ("Ticket intake created.", "TICKET_CREATED", days_ago(2, 4)),
                ("Open → In Progress", "STATUS_CHANGE", days_ago(1, 14)),
                ("Verifying Stripe payment gateway settlement currency configuration.", "NOTE_ADDED", hours_ago(13)),
            ],
        },

        # =====================================================================
        # GROUP 8: GEN / Ambiguous Tickets (4 tickets) (§4)
        # =====================================================================
        {
            "name": "Rohit Varma",
            "email": "rohit.varma@retailpartners.in",
            "brand": "UrbanFit",
            "channel": "Email",
            "status": "Open",
            "subject": "Inquiry regarding retail partnership and regional distribution terms",
            "description": "Our distribution group operates 14 athletic outlets and would like to explore stocking UrbanFit merchandise.",
            "created_at": days_ago(3, 2),
            "updated_at": days_ago(3, 2),
            "notes": [],
        },
        {
            "name": "Nandita Bose",
            "email": "nandita.bose@soundpress.com",
            "brand": "Nova Audio",
            "channel": "Email",
            "status": "In Progress",
            "subject": "Press inquiry regarding upcoming product launch press kit",
            "description": "Technology editor requesting review sample and press embargo specifications for upcoming monitor series.",
            "created_at": days_ago(2, 8),
            "updated_at": hours_ago(18),
            "notes": [
                ("Ticket intake created.", "TICKET_CREATED", days_ago(2, 8)),
                ("Open → In Progress", "STATUS_CHANGE", days_ago(1, 16)),
                ("Forwarded to PR and communications director.", "NOTE_ADDED", hours_ago(18)),
            ],
        },
        {
            "name": "Akash Verma",
            "email": "akash.verma@greendesign.org",
            "brand": "Aura D2C",
            "channel": "Web Portal",
            "status": "Closed",
            "subject": "Feedback regarding eco-friendly packaging materials and recycling",
            "description": "Suggestions on replacing plastic wrap with biodegradable hemp fiber inserts in product shipping cartons.",
            "created_at": days_ago(11),
            "updated_at": days_ago(9),
            "notes": [
                ("Ticket intake created.", "TICKET_CREATED", days_ago(11)),
                ("Acknowledged and routed to product sustainability committee.", "NOTE_ADDED", days_ago(9, 6)),
                ("In Progress → Closed", "STATUS_CHANGE", days_ago(9)),
            ],
        },
        {
            "name": "Simran Kaur",
            "email": "simran.kaur@botanicalwellness.in",
            "brand": "Zen Botanics",
            "channel": "Email",
            "status": "Open",
            "subject": "General inquiry on wholesale catalog pricing and ingredient sourcing",
            "description": "Requesting detailed supplier origin verification certificates and wholesale pricing tiers.",
            "created_at": days_ago(1, 16),
            "updated_at": days_ago(1, 16),
            "notes": [],
        },
    ]

    return specs


def seed_stress_dataset():
    """
    Seed exactly 60 stress tickets on top of canonical demo data.
    Ensures sequential sequence IDs, data isolation, and rich activity notes.
    """
    print("=" * 70)
    print("RELAYCX STRESS DATASET SEEDING (60 TICKETS)")
    print("=" * 70)

    # Ensure schema exists
    ensure_schema()
    db = SessionLocal()

    try:
        # Step 1: Verify canonical tickets exist; if database is empty, seed canonical first
        existing_tickets = db.query(Ticket).all()
        canonical_present = [t for t in existing_tickets if t.ticket_id in CANONICAL_TICKET_IDS]
        if len(canonical_present) == 0:
            print("[1/4] Canonical demo data missing. Seeding canonical 7 tickets first...")
            db.close()
            restore_canonical_seed()
            db = SessionLocal()
        else:
            print(f"[1/4] Verified {len(canonical_present)} canonical tickets present.")

        # Step 2: Clear any existing non-canonical stress tickets (idempotency)
        print("[2/4] Clearing existing stress records (preserving canonical)...")
        formatted_ids = ", ".join(f"'{tid}'" for tid in CANONICAL_TICKET_IDS)
        db.execute(text(f"DELETE FROM notes WHERE ticket_id NOT IN ({formatted_ids})"))
        db.execute(text(f"DELETE FROM tickets WHERE ticket_id NOT IN ({formatted_ids})"))
        db.commit()
        print("PASS: Cleaned any non-canonical stress records.")

        # Step 3: Insert 60 stress tickets using deterministic classification and sequencing
        specs = get_stress_tickets_spec()
        print(f"[3/4] Inserting {len(specs)} realistic stress tickets...")
        assert len(specs) == 60, f"Expected exactly 60 specs, got {len(specs)}"

        inserted_count = 0
        notes_count = 0

        # Pre-compute next sequence per (brand, issue_type) partition
        seq_map: dict[tuple[str, str], int] = {}
        ticket_mappings = []
        note_mappings = []

        for item in specs:
            brand = item["brand"]
            subject = item["subject"]
            description = item["description"]

            # Classify issue family using existing weighted classifier
            issue_type = classify_issue(subject, description)
            intake_issue_type = issue_type

            # In-memory sequence counter to avoid 60 remote network roundtrips
            pair = (brand, issue_type)
            if pair not in seq_map:
                seq_map[pair] = repository.get_next_sequence(db, brand, issue_type)
            sequence = seq_map[pair]
            seq_map[pair] = sequence + 1

            client_code = service.get_client_code(db, brand)
            ticket_id = f"TKT-{client_code}-{issue_type}-{sequence:04d}"

            ticket_mappings.append({
                "ticket_id": ticket_id,
                "customer_name": item["name"],
                "customer_email": item["email"].strip().lower(),
                "subject": subject,
                "description": description,
                "status": item["status"],
                "client_brand": brand,
                "channel": item.get("channel", "Email"),
                "intake_issue_type": intake_issue_type,
                "issue_type": issue_type,
                "ticket_sequence": sequence,
                "created_at": item["created_at"],
                "updated_at": item["updated_at"],
            })

            # Insert notes
            for note_text, event_type, note_time in item.get("notes", []):
                note_mappings.append({
                    "ticket_id": ticket_id,
                    "note_text": note_text,
                    "event_type": event_type,
                    "created_at": note_time,
                })

        print(f"  Bulk inserting {len(ticket_mappings)} tickets and {len(note_mappings)} notes...", flush=True)
        db.bulk_insert_mappings(Ticket, ticket_mappings)
        db.bulk_insert_mappings(Note, note_mappings)
        db.commit()
        print(f"PASS: Inserted {len(ticket_mappings)} stress tickets with {len(note_mappings)} timeline notes.", flush=True)

        # Step 4: Verification & Breakdown
        print("\n[4/4] Verifying dataset statistics:")
        all_tickets = db.query(Ticket).all()
        all_notes = db.query(Note).all()

        canonical_tickets = [t for t in all_tickets if t.ticket_id in CANONICAL_TICKET_IDS]
        stress_tickets = [t for t in all_tickets if t.ticket_id not in CANONICAL_TICKET_IDS]

        open_tickets = [t for t in all_tickets if t.status == "Open"]
        ip_tickets = [t for t in all_tickets if t.status == "In Progress"]
        closed_tickets = [t for t in all_tickets if t.status == "Closed"]

        print(f"  • Total tickets in DB:    {len(all_tickets)} (Expected: 67 = 7 canonical + 60 stress)")
        print(f"  • Canonical tickets:      {len(canonical_tickets)}")
        print(f"  • Stress tickets:         {len(stress_tickets)}")
        print(f"  • Total timeline notes:   {len(all_notes)}")
        print(f"  • Open tickets:           {len(open_tickets)}")
        print(f"  • In Progress tickets:    {len(ip_tickets)}")
        print(f"  • Closed tickets:         {len(closed_tickets)}")

        # Print brand distribution
        brands = {}
        for t in all_tickets:
            brands[t.client_brand] = brands.get(t.client_brand, 0) + 1
        print("\n  Brand Distribution:")
        for b, count in sorted(brands.items()):
            print(f"    - {b:15s}: {count} tickets")

        # Invariant checks
        assert len(canonical_tickets) == 7, f"Canonical tickets altered! Expected 7, found {len(canonical_tickets)}"
        assert len(stress_tickets) == 60, f"Stress tickets incorrect! Expected 60, found {len(stress_tickets)}"
        assert len(all_tickets) == 67, f"Total tickets mismatch! Expected 67, found {len(all_tickets)}"

        # Check Aura D2C INT sequence
        aura_int_tickets = [t for t in all_tickets if t.client_brand == "Aura D2C" and t.intake_issue_type == "INT"]
        aura_int_seqs = sorted([t.ticket_sequence for t in aura_int_tickets])
        print(f"\n  Aura D2C INT Sequence count: {len(aura_int_seqs)} (Sequences: {aura_int_seqs})")
        assert len(aura_int_seqs) >= 10, f"Expected 10+ Aura INT tickets, got {len(aura_int_seqs)}"
        assert aura_int_seqs[:10] == list(range(1, 11)), f"Sequences not consecutive 1..10: {aura_int_seqs[:10]}"

        print("\n" + "=" * 70)
        print("SUCCESS: RelayCX stress dataset seeded cleanly! Ready for stress testing.")
        print("=" * 70)

    except Exception as e:
        db.rollback()
        print(f"ERROR: Failed to seed stress dataset: {e}", file=sys.stderr)
        raise
    finally:
        db.close()


def restore_canonical_dataset():
    """
    Cleans up all stress data and restores canonical 7-ticket demo dataset cleanly.
    """
    print("=" * 70)
    print("RESTORING CANONICAL RELAYCX DEMO DATASET (7 TICKETS)")
    print("=" * 70)
    restore_canonical_seed()
    print("PASS: Canonical dataset restored.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="RelayCX Stress Dataset Seeder")
    parser.add_argument(
        "--restore",
        action="store_true",
        help="Remove stress tickets and restore canonical 7-ticket demo dataset",
    )
    args = parser.parse_args()

    if args.restore:
        restore_canonical_dataset()
    else:
        seed_stress_dataset()
