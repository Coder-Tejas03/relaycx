"""
Service layer containing all RelayCX core business logic.
Handles ticket ID generation, lifecycle state transitions, and auto-advance rules.
"""

import re
import secrets
import time
from typing import Optional
from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError, OperationalError
from sqlalchemy.orm import Session
from app import repository
from app.models import Ticket
from app.schemas import (
    CustomerHistorySummary,
    TicketCreateRequest,
    TicketCreatedResponse,
    TicketSummary,
    TicketDetailResponse,
    TicketUpdateRequest,
    TicketUpdatedResponse,
    NoteResponse,
)

# Canonical 3-character client codes for known brands
CLIENT_CODE_MAP: dict[str, str] = {
    "UrbanFit": "URB",
    "Nova Audio": "NOV",
    "Aura D2C": "AUR",
    "ThreadCo": "THR",
    "Zen Botanics": "ZEN",
    "Blaze": "BLA",
    "CasaNest": "CAS",
    "GlowTheory": "GLO",
}

# Domain-specific issue taxonomy with per-keyword weights
ISSUE_TAXONOMY: dict[str, list[tuple[str, int]]] = {
    "ANA": [
        ("csv", 3), ("export", 2), ("analytics", 3), ("reporting", 2),
        ("lambda timeout", 3), ("dashboard data", 2), ("empty file", 2),
        ("date range", 1), ("report", 1),
    ],
    "INT": [
        ("webhook", 3), ("http 429", 3), ("http 500", 2), ("http 4", 2),
        ("rate limit", 3), ("api", 2), ("endpoint", 2), ("integration", 2),
        ("429", 3), ("schema mismatch", 2), ("payload", 1),
    ],
    "ACC": [
        ("2fa", 3), ("lockout", 3), ("login", 2), ("otp", 3),
        ("password", 2), ("authentication", 2), ("account access", 3),
        ("verification code", 2), ("locked", 2),
    ],
    "PAY": [
        ("refund", 2), ("payment", 2), ("charge", 2), ("billing", 2),
        ("invoice", 2), ("stripe", 2), ("gateway", 1), ("transaction", 1),
    ],
    "ORD": [
        ("order", 2), ("delivery", 2), ("shipment", 2), ("shipping", 2),
        ("package", 2), ("tracking", 2), ("missing item", 2),
    ],
    "TEC": [
        ("crash", 2), ("bug", 2), ("error", 1), ("malfunction", 2),
        ("not working", 2), ("broken", 2), ("issue", 1),
    ],
    "PRD": [
        ("sizing", 3), ("size guide", 3), ("product information", 2),
        ("catalog", 2), ("specifications", 2), ("fit", 1),
    ],
}

VALID_ISSUE_TYPES: set[str] = {"ORD", "PAY", "ACC", "TEC", "INT", "ANA", "PRD", "GEN"}
TIE_BREAK_ORDER: list[str] = ["ANA", "INT", "ACC", "PAY", "ORD", "TEC", "PRD", "GEN"]
MINIMUM_SCORE: int = 2
MAX_SEQUENCE_RETRIES: int = 5


def classify_issue(subject: str, description: str) -> str:
    """
    Classify support ticket into an issue taxonomy family using weighted scoring
    and explicit tie-break priority. Matches in subject count 2x; matches in
    description count 1x. Returns 'GEN' if no category reaches MINIMUM_SCORE.
    """
    text_subject = (subject or "").lower()
    text_desc = (description or "").lower()
    scores: dict[str, int] = {}

    for code, keywords in ISSUE_TAXONOMY.items():
        score = 0
        for keyword, weight in keywords:
            if keyword in text_subject:
                score += weight * 2
            if keyword in text_desc:
                score += weight * 1
        if score > 0:
            scores[code] = score

    if not scores or max(scores.values()) < MINIMUM_SCORE:
        return "GEN"

    max_score = max(scores.values())
    candidates = [c for c, s in scores.items() if s == max_score]

    for code in TIE_BREAK_ORDER:
        if code in candidates:
            return code

    return "GEN"


def get_client_code(db: Session, client_brand: str) -> str:
    """
    Resolve or derive a stable 3-character uppercase client code for the brand.
    1. Static map lookup for known brands (case-insensitive).
    2. DB lookup for existing structured ticket IDs for this brand.
    3. Deterministic candidate generation from brand name with collision check and digit fallback.
    """
    brand = (client_brand or "").strip()
    if not brand:
        brand = "UrbanFit"

    # Step A: Static map lookup (case-insensitive)
    for known_brand, code in CLIENT_CODE_MAP.items():
        if known_brand.lower() == brand.lower():
            return code

    # Step B: Check existing tickets for this brand in database
    db_code = repository.get_client_code_from_db(db, brand)
    if db_code:
        return db_code

    # Step C: Dynamic generation for new unknown brand
    cleaned = re.sub(r"[^A-Za-z0-9]", "", brand).upper()
    letters_only = re.sub(r"[^A-Z]", "", cleaned)
    base_chars = letters_only if len(letters_only) >= 3 else cleaned

    if len(base_chars) < 3:
        candidate_base = (base_chars + "XXX")[:3]
    else:
        candidate_base = base_chars[:3]

    if not repository.is_client_code_taken(db, candidate_base, brand):
        return candidate_base

    prefix = candidate_base[:2]
    for digit in range(1, 10):
        alt_code = f"{prefix}{digit}"
        if not repository.is_client_code_taken(db, alt_code, brand):
            return alt_code

    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail=f"Unable to generate a unique 3-character client code for brand '{brand}'. Please register it in CLIENT_CODE_MAP."
    )


def generate_structured_ticket_id(db: Session, client_brand: str, issue_type: str) -> tuple[str, int]:
    """
    Generate a deterministic business ticket identifier in format 'TKT-{CLIENT}-{ISSUE}-{SEQ:04d}'.
    Returns the ticket_id string and the sequence integer.
    """
    client_code = get_client_code(db, client_brand)
    normalized_issue = (issue_type or "GEN").strip().upper()
    sequence = repository.get_next_sequence(db, client_brand, normalized_issue)
    ticket_id = f"TKT-{client_code}-{normalized_issue}-{sequence:04d}"
    return ticket_id, sequence


def generate_ticket_id(db: Optional[Session] = None) -> str:
    """
    Legacy ticket ID generator in format 'TKT-XXXXXX'. Retained for backward compatibility.
    """
    for _ in range(10):
        candidate = f"TKT-{secrets.token_hex(3).upper()}"
        if db is None:
            return candidate
        if repository.get_ticket_by_id(db, candidate) is None:
            return candidate
    return f"TKT-{secrets.token_hex(4).upper()[:6]}"


def create_new_ticket(db: Session, request_data: TicketCreateRequest) -> TicketCreatedResponse:
    """
    Classify incoming issue, generate structured ticket ID (TKT-{CLIENT}-{ISSUE}-{SEQ:04d}),
    and persist new ticket record in 'Open' state. Implements retry loop catching IntegrityError
    for safe concurrency.
    """
    brand = getattr(request_data, "client_brand", None) or "UrbanFit"
    issue_type = classify_issue(request_data.subject, request_data.description)
    intake_issue_type = issue_type

    for attempt in range(MAX_SEQUENCE_RETRIES):
        ticket_id, sequence = generate_structured_ticket_id(db, brand, issue_type)
        try:
            ticket = repository.create_ticket(
                db=db,
                ticket_id=ticket_id,
                data=request_data,
                intake_issue_type=intake_issue_type,
                issue_type=issue_type,
                ticket_sequence=sequence,
            )
            return TicketCreatedResponse.model_validate(ticket)
        except (IntegrityError, OperationalError, ValueError) as exc:
            exc_str = str(exc).lower()
            if isinstance(exc, (ValueError, OperationalError)):
                retryable = ("constraint", "unique", "sqlite_busy", "busy", "stream", "locked")
                if not any(k in exc_str for k in retryable):
                    raise
            try:
                db.rollback()
            except Exception:
                pass
            if attempt == MAX_SEQUENCE_RETRIES - 1:
                raise HTTPException(
                    status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                    detail="Ticket creation temporarily unavailable due to concurrent conflicts. Please retry."
                )
            time.sleep(0.05 * (attempt + 1))


def correct_issue_type(db: Session, ticket_id: str, new_issue_type: str) -> Ticket:
    """
    Correct the current classification issue_type of an existing ticket.
    Leaves ticket_id and intake_issue_type strictly unchanged (reference immutability).
    Validates new_issue_type against VALID_ISSUE_TYPES.
    Raises 404 if ticket not found.
    Raises 400 if new_issue_type is not a valid taxonomy code.
    """
    normalized_issue = (new_issue_type or "").strip().upper()
    if normalized_issue not in VALID_ISSUE_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid issue_type '{new_issue_type}'. Must be one of {sorted(list(VALID_ISSUE_TYPES))}"
        )
    ticket = repository.get_ticket_by_id(db, ticket_id)
    if not ticket:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Ticket '{ticket_id}' not found"
        )
    return repository.update_issue_type(db, ticket, normalized_issue)


def get_customer_history(
    db: Session,
    client_brand: str,
    customer_email: str,
    exclude_ticket_id: Optional[str] = None,
) -> list[TicketSummary]:
    """
    Retrieve prior tickets for a given customer under a specific client brand,
    enforcing brand isolation.
    """
    tickets = repository.get_tickets_by_customer(
        db=db,
        client_brand=client_brand,
        customer_email=customer_email,
        exclude_ticket_id=exclude_ticket_id,
    )
    return [TicketSummary.model_validate(t) for t in tickets]


def get_ticket_list(
    db: Session,
    status_filter: Optional[str] = None,
    search_query: Optional[str] = None,
    client_brand: Optional[str] = None,
    customer_email: Optional[str] = None,
    limit: Optional[int] = None,
    offset: Optional[int] = None,
) -> list[TicketSummary]:
    """
    Retrieve list of tickets matching optional status filter, search query, client_brand, customer_email,
    and optional limit/offset pagination.
    """
    tickets = repository.get_all_tickets(
        db,
        status_filter=status_filter,
        search_query=search_query,
        client_brand=client_brand,
        customer_email=customer_email,
        limit=limit,
        offset=offset,
    )
    return [TicketSummary.model_validate(t) for t in tickets]


def get_ticket_detail(db: Session, ticket_id: str) -> TicketDetailResponse:
    """
    Fetch complete ticket details with all associated notes.
    Raises HTTP 404 if ticket does not exist.
    """
    ticket = repository.get_ticket_by_id(db, ticket_id)
    if not ticket:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Ticket '{ticket_id}' not found"
        )
    return TicketDetailResponse.model_validate(ticket)


def update_ticket_data(
    db: Session,
    ticket_id: str,
    update_request: TicketUpdateRequest
) -> TicketUpdatedResponse:
    """
    Update ticket status and/or append an internal note.
    Applies the operational state machine and auto-advance rules:
    - If status is explicitly passed (ToggleGroup or 'Add Note & Resolve'): use explicit status.
    - If status is omitted and a note is added:
        - If current status is 'Open', auto-advance to 'In Progress'.
        - If current status is 'In Progress' or 'Closed', keep current status.
    - If neither status nor note provided: raise HTTP 400 Bad Request.
    """
    ticket = repository.get_ticket_by_id(db, ticket_id)
    if not ticket:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Ticket '{ticket_id}' not found"
        )

    has_status = update_request.status is not None
    has_note = bool(update_request.note_text and update_request.note_text.strip())

    if not has_status and not has_note:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="At least one of 'status' or 'note_text' must be provided"
        )

    old_status = ticket.status

    # Determine target status according to state machine rules
    if has_status:
        # Explicit status selection (ToggleGroup or Add Note & Resolve)
        target_status = update_request.status
    elif has_note:
        # Auto-advance rule: adding note on 'Open' transitions to 'In Progress'
        if ticket.status == "Open":
            target_status = "In Progress"
        else:
            target_status = ticket.status
    else:
        target_status = ticket.status

    status_changed = (target_status != old_status)
    status_change_text = f"{old_status} → {target_status}" if status_changed else None

    updated_ticket, created_note = repository.update_ticket(
        db=db,
        ticket=ticket,
        new_status=target_status,
        note_text=update_request.note_text,
        event_type="NOTE_ADDED",
        status_change_note_text=status_change_text,
    )

    note_resp = NoteResponse.model_validate(created_note) if created_note else None

    return TicketUpdatedResponse(
        ticket_id=updated_ticket.ticket_id,
        status=updated_ticket.status,
        updated_at=updated_ticket.updated_at,
        note=note_resp
    )
