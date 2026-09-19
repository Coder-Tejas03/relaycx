"""
Simulated D2C Commerce & SaaS Account Provider.
Implements the pluggable commerce context contract for RelayCX.
Provides deterministic, domain-coherent customer operational context
without requiring live third-party API credentials during staging/demo.

Features:
1. Client-Brand Scoping: All customer records are strictly keyed on (client_brand, customer_email)
   tuples to prevent cross-client data leakage.
2. Issue-Domain Relevance: Filters context by primary issue family so irrelevant data
   (e.g. consumer ecommerce face cream orders during an analytics Lambda timeout) is never shown.
3. Backward Compatibility: Preserves get_order_context(email) for existing callers.
"""

from typing import Optional


# Maps 3-character issue families to allowed context domain / account_type categories
ISSUE_RELEVANCE_RULES: dict[str, set[str]] = {
    "ANA": {"analytics"},
    "INT": {"developer", "integration"},
    "ACC": {"account", "auth"},
    "PAY": {"payment", "refund", "ecommerce"},
    "ORD": {"order", "shipment", "ecommerce"},
    "TEC": {"developer", "ecommerce"},
    "PRD": {"ecommerce"},
    "GEN": set(),  # General issues never display context — clean empty state
}


# Deterministic customer context database keyed by (client_brand, normalized_customer_email).
# Entries are added here manually, one per ticket, as tickets are engineered.
# Each key is a (client_brand, customer_email) tuple; value is the structured context dict.
#
# Supported fields (all optional beyond account_type):
#   account_type          : "ecommerce" | "developer" | "account" | "auth" | "analytics"
#   order_id              : str  — e.g. "ORD-1234" or "SUB-DEV-001"
#   order_date            : str  — human-readable, e.g. "3 days ago"
#   item_name             : str  — product or plan name
#   total_amount          : str  — e.g. "₹2,499" or "₹48,000 / year"
#   payment_method        : str  — e.g. "UPI (Razorpay)" or "Corporate Invoicing (Net 30)"
#   carrier               : str  — e.g. "Blue Dart Express"
#   tracking_number       : str  — e.g. "BLR-89210-RT"
#   shipping_status       : str  — e.g. "In Transit" | "Delivered" | "Payment Pending"
#   estimated_delivery    : str  — e.g. "Tomorrow by 6:00 PM" | "Delivered 2 days ago"
#   customer_lifetime_value: str — e.g. "₹18,400 (4 orders)"
#   customer_tier         : str  — e.g. "Repeat Customer" | "Gold VIP"
#   return_window_active  : bool
#   dispute_reason        : str  — optional, only when there's an active dispute
#   notes                 : str  — internal ops note for the agent workbench
#   technical_details     : dict — for developer/SaaS accounts (endpoint, quota, etc.)
SEEDED_CUSTOMER_CONTEXTS: dict[tuple[str, str], dict] = {
    ("Zen Botanics", "aditya.joshi@zenbotanics.com"): {
        "account_type": "ecommerce",
        "order_id": "ORD-ZB-10482",
        "order_date": "17 Sep 2026",
        "item_name": "Organic Facial Serum 30ml",
        "total_amount": "₹1,299",
        "payment_method": "Prepaid · UPI (Razorpay)",
        "carrier": "Blue Dart Express",
        "tracking_number": "BDE-728491-ZB",
        "shipping_status": "Delivered",
        "estimated_delivery": "Delivered today at 11:18 AM",
        "customer_lifetime_value": "₹6,847 (5 orders)",
        "customer_tier": "Gold Member",
        "return_window_active": True,
        "dispute_reason": (
            "Package was delivered today and customer reported a leaking bottle "
            "immediately after delivery. Replacement is available for the same SKU. "
            "Refund is also eligible for the order amount."
        ),
        "notes": (
            "Delivery scan completed at 11:18 AM. Customer complaint was received "
            "approximately 35 minutes after delivery. Order is fully paid and has "
            "no previous refund or replacement recorded."
        ),
    },
    ("Aura D2C", "meera.iyer@aurad2c.com"): {
        "account_type": "ecommerce",
        "order_id": "ORD-AU-5837",
        "order_date": "19 Sep 2026",
        "item_name": "Rose Glow Hydration Kit (30ml)",
        "total_amount": "₹1,899",
        "payment_method": "Prepaid · UPI (Razorpay)",
        "carrier": "Not assigned",
        "tracking_number": None,
        "shipping_status": "Payment Pending",
        "estimated_delivery": "Awaiting payment confirmation",
        "customer_lifetime_value": "₹8,497 (6 orders)",
        "customer_tier": "Gold Member",
        "return_window_active": False,
        "dispute_reason": (
            "UPI payment of ₹1,899 was successfully received by the payment gateway, "
            "but the order confirmation callback did not complete. Order is currently "
            "on payment hold and has not entered fulfillment. Payment reconciliation "
            "is required before dispatch."
        ),
        "notes": (
            "Gateway transaction ID: RZP-AU-918274. Payment captured at 10:42 AM. "
            "Order creation callback failed after payment capture. "
            "No courier or fulfillment record has been created yet."
        ),
    },
    ("UrbanFit", "rohan.kapoor@urbanfit.in"): {
        "account_type": "ecommerce",
        "order_id": "ORD-UF-7316",
        "order_date": "16 Sep 2026",
        "item_name": "UrbanFit AeroDry Joggers (Charcoal / M)",
        "total_amount": "₹2,499",
        "payment_method": "Prepaid · Credit Card (Visa)",
        "carrier": "Delhivery Air",
        "tracking_number": "DLV-73160-UF",
        "shipping_status": "Delivered",
        "estimated_delivery": "Delivered today at 12:36 PM",
        "customer_lifetime_value": "₹14,296 (7 orders)",
        "customer_tier": "Gold Member",
        "return_window_active": True,
        "dispute_reason": (
            "Shipment was delivered successfully, but the fulfillment record "
            "indicates a SKU mismatch. Customer received Core Training Shorts "
            "instead of the ordered AeroDry Joggers. Replacement for the ordered "
            "SKU is available."
        ),
        "notes": (
            "Ordered SKU: UF-ADJ-CHR-M. Packed SKU: UF-CTS-BLK-M. "
            "Fulfillment scan confirms the packed SKU does not match the order. "
            "Customer has requested replacement with the originally ordered item."
        ),
    },
    ("CasaNest", "arjun.mehta@gmail.com"): {
        "account_type": "ecommerce",
        "order_id": "ORD-CN-2841",
        "order_date": "14 Sep 2026",
        "item_name": "CasaNest Ceramic Cookware Set (5-Piece)",
        "total_amount": "₹3,299",
        "payment_method": "Prepaid · UPI (Razorpay)",
        "carrier": "Delhivery",
        "tracking_number": "DLV-CN-2841",
        "shipping_status": "In Transit",
        "estimated_delivery": "18 Sep 2026",
        "customer_lifetime_value": "₹3,299 (1 order)",
        "customer_tier": "New Customer",
        "return_window_active": False,
        "dispute_reason": (
            "The estimated delivery date has passed and the shipment has not reached the customer. "
            "The latest carrier scan was recorded at a Delhivery sorting facility on 17 Sep 2026 at 8:42 PM. "
            "Delivery is currently delayed and a revised delivery estimate is required."
        ),
        "notes": (
            "Last tracking event: Mumbai Sorting Facility — 17 Sep 2026, 8:42 PM. "
            "No delivery attempt has been recorded. Order is fully paid and has not been cancelled or refunded. "
            "Customer is eligible for a delivery-delay escalation if the shipment remains undelivered after the next carrier update."
        ),
    },
    ("GlowTheory", "sneha.kulkarni@gmail.com"): {
        "account_type": "ecommerce",
        "order_id": "ORD-GT-6194",
        "order_date": "12 Sep 2026",
        "item_name": "GlowTheory Vitamin C Brightening Serum 30ml",
        "total_amount": "₹1,499",
        "payment_method": "Prepaid · Credit Card (Visa)",
        "carrier": "Blue Dart Express",
        "tracking_number": "BDE-GT-6194-R",
        "shipping_status": "Delivered",
        "estimated_delivery": "Delivered on 15 Sep 2026",
        "customer_lifetime_value": "₹1,499 (1 order)",
        "customer_tier": "New Customer",
        "return_window_active": False,
        "dispute_reason": (
            "Return was received and verified on 17 Sep 2026. A refund of ₹1,499 "
            "was initiated to the original payment method on 17 Sep 2026. "
            "The refund is currently pending with the payment processor and has "
            "not yet been confirmed as credited to the customer."
        ),
        "notes": (
            "Refund reference: RFD-GT-6194-1729. Refund initiated: 17 Sep 2026 at 3:26 PM. "
            "Original payment method: Visa ending in 4821. No partial refund or replacement has been issued."
        ),
    },
}


def _lookup_context(client_brand: str, customer_email: str) -> Optional[dict]:
    """
    Look up customer context by (client_brand, customer_email) tuple with
    case-insensitive matching and whitespace stripping.
    """
    if not client_brand or not customer_email:
        return None

    target_brand = client_brand.strip().lower()
    target_email = customer_email.strip().lower()

    for (brand, email), context in SEEDED_CUSTOMER_CONTEXTS.items():
        if brand.strip().lower() == target_brand and email.strip().lower() == target_email:
            return context

    return None


def get_relevant_context(
    client_brand: str,
    customer_email: str,
    issue_type: Optional[str] = None
) -> Optional[dict]:
    """
    Retrieve operational customer context scoped strictly to (client_brand, customer_email)
    and filtered by issue-family relevance.

    Returns:
        - dict: Structured context if found AND relevant to issue_type.
        - None: If not found, or if context is irrelevant to the issue_type (e.g. consumer
                ecommerce face cream order for an analytics export ticket), prompting
                the frontend to render a clean empty state.
    """
    if not client_brand or not customer_email:
        return None

    context = _lookup_context(client_brand, customer_email)
    if not context:
        return None

    normalized_issue = issue_type.strip().upper() if issue_type else "GEN"
    allowed_domains = ISSUE_RELEVANCE_RULES.get(normalized_issue, set())
    if not allowed_domains:
        return None

    # Determine context domains (supports account_type, domain, and domains list)
    context_domains = set()
    acc_type = context.get("account_type")
    if acc_type:
        context_domains.add(acc_type.strip().lower())
    domain = context.get("domain")
    if domain:
        context_domains.add(domain.strip().lower())
    for d in context.get("domains", []):
        if d:
            context_domains.add(str(d).strip().lower())

    if context_domains.intersection(allowed_domains):
        return context

    return None


def get_order_context(customer_email: str) -> Optional[dict]:
    """
    Retrieve operational customer context by email address across all client brands.
    Maintains backward-compatibility for legacy endpoints.
    """
    if not customer_email:
        return None

    normalized_email = customer_email.strip().lower()
    for (brand, email), context in SEEDED_CUSTOMER_CONTEXTS.items():
        if email.strip().lower() == normalized_email:
            return context

    return None
