"""
Repository layer for raw database CRUD operations.
Encapsulates all direct SQLAlchemy session operations.
"""

from typing import Optional
from sqlalchemy import func, or_
from sqlalchemy.orm import Session
from app.models import Ticket, Note, utc_now
from app.schemas import TicketCreateRequest


def create_ticket(
    db: Session,
    ticket_id: str,
    data: TicketCreateRequest,
    intake_issue_type: str = "GEN",
    issue_type: str = "GEN",
    ticket_sequence: Optional[int] = None,
) -> Ticket:
    """
    Persist a new ticket record to the database with status 'Open'.
    Accepts intake_issue_type, issue_type, and ticket_sequence with safe defaults.
    """
    client_brand = getattr(data, "client_brand", None) or "UrbanFit"
    channel = getattr(data, "channel", None) or "Email"

    ticket = Ticket(
        ticket_id=ticket_id,
        customer_name=data.customer_name.strip(),
        customer_email=data.customer_email.strip().lower(),
        subject=data.subject.strip(),
        description=data.description.strip(),
        status="Open",
        client_brand=client_brand.strip(),
        channel=channel.strip(),
        intake_issue_type=intake_issue_type.strip().upper() if intake_issue_type else "GEN",
        issue_type=issue_type.strip().upper() if issue_type else "GEN",
        ticket_sequence=ticket_sequence,
        created_at=utc_now(),
        updated_at=utc_now(),
    )
    db.add(ticket)
    db.commit()
    db.refresh(ticket)
    return ticket


def get_all_tickets(
    db: Session,
    status_filter: Optional[str] = None,
    search_query: Optional[str] = None,
    client_brand: Optional[str] = None,
    customer_email: Optional[str] = None,
    limit: Optional[int] = None,
    offset: Optional[int] = None,
) -> list[Ticket]:
    """
    Retrieve tickets ordered by created_at DESC with optional status, search, client_brand, customer_email,
    and optional limit/offset pagination.
    Performs case-insensitive substring search across ticket_id, customer_name,
    customer_email, subject, and description.
    """
    query = db.query(Ticket)

    # Apply status filter if supplied and not 'All'
    if status_filter and status_filter.lower() != "all":
        query = query.filter(Ticket.status == status_filter)

    # Apply client_brand filter if supplied and not 'All'
    if client_brand and client_brand.strip() and client_brand.strip().lower() != "all":
        query = query.filter(Ticket.client_brand == client_brand.strip())

    # Apply customer_email filter if supplied
    if customer_email and customer_email.strip():
        query = query.filter(Ticket.customer_email == customer_email.strip().lower())

    # Apply case-insensitive multi-field search query
    if search_query and search_query.strip():
        term = f"%{search_query.strip()}%"
        query = query.filter(
            or_(
                Ticket.ticket_id.ilike(term),
                Ticket.customer_name.ilike(term),
                Ticket.customer_email.ilike(term),
                Ticket.subject.ilike(term),
                Ticket.description.ilike(term),
            )
        )

    # When viewing Open queue (Inbox / Needs Attention), prioritize oldest neglected tickets first (FIFO)
    if status_filter and status_filter.lower() == "open":
        query = query.order_by(Ticket.created_at.asc())
    else:
        query = query.order_by(Ticket.created_at.desc())

    if offset is not None and offset > 0:
        query = query.offset(offset)
    if limit is not None and limit > 0:
        query = query.limit(limit)

    return query.all()


def get_ticket_by_id(db: Session, ticket_id: str) -> Optional[Ticket]:
    """
    Fetch a single ticket by its human-readable business ID (e.g., TKT-C74B9E or TKT-URB-INT-0001).
    Returns None if no matching ticket exists.
    """
    return db.query(Ticket).filter(Ticket.ticket_id == ticket_id).first()


def get_next_sequence(db: Session, client_brand: str, issue_type: str) -> int:
    """
    Compute the next safe sequence integer for (client_brand, issue_type).
    Uses MAX(ticket_sequence) + 1. Checks both issue_type and intake_issue_type
    to ensure uniqueness even if an earlier ticket's issue_type was updated.
    """
    brand = client_brand.strip()
    issue = issue_type.strip().upper()
    result = (
        db.query(func.max(Ticket.ticket_sequence))
        .filter(
            Ticket.client_brand == brand,
            or_(
                Ticket.issue_type == issue,
                Ticket.intake_issue_type == issue,
            )
        )
        .scalar()
    )
    return (result or 0) + 1


def get_client_code_from_db(db: Session, client_brand: str) -> Optional[str]:
    """
    Extract client code from an existing ticket's ticket_id for the specified client_brand.
    Looks for tickets with structured ticket_id format 'TKT-{CLIENT}-{ISSUE}-{SEQ}'.
    Returns the 3-character uppercase client code if found, else None.
    """
    brand = client_brand.strip()
    tickets = (
        db.query(Ticket.ticket_id)
        .filter(Ticket.client_brand == brand)
        .order_by(Ticket.id.desc())
        .all()
    )
    for (t_id,) in tickets:
        if t_id:
            parts = t_id.split("-")
            # Structured ticket IDs have 4 parts: TKT - {CLIENT} - {ISSUE} - {SEQ}
            if len(parts) >= 3 and len(parts[1]) == 3 and parts[1].isupper():
                return parts[1]
    return None


def is_client_code_taken(db: Session, candidate_code: str, client_brand: str) -> bool:
    """
    Check if a candidate 3-letter client code is already claimed by a different brand.
    Returns True if taken by another brand, False otherwise.
    """
    code = candidate_code.strip().upper()
    brand = client_brand.strip()
    existing = (
        db.query(Ticket.id)
        .filter(
            Ticket.ticket_id.like(f"TKT-{code}-%"),
            Ticket.client_brand != brand,
        )
        .first()
    )
    return existing is not None


def update_issue_type(db: Session, ticket: Ticket, new_issue_type: str) -> Ticket:
    """
    Update the current classification issue_type of a ticket.
    Leaves ticket_id and intake_issue_type strictly unchanged.
    Updates updated_at timestamp.
    """
    ticket.issue_type = new_issue_type.strip().upper()
    ticket.updated_at = utc_now()
    db.commit()
    db.refresh(ticket)
    return ticket


def get_tickets_by_customer(
    db: Session,
    client_brand: str,
    customer_email: str,
    exclude_ticket_id: Optional[str] = None,
) -> list[Ticket]:
    """
    Fetch all tickets for a specific customer under a specific client brand,
    ordered by created_at DESC (newest first).
    Optionally excludes a specific ticket_id (e.g. the currently viewed ticket).
    """
    query = db.query(Ticket).filter(
        Ticket.client_brand == client_brand.strip(),
        Ticket.customer_email == customer_email.strip().lower(),
    )
    if exclude_ticket_id and exclude_ticket_id.strip():
        query = query.filter(Ticket.ticket_id != exclude_ticket_id.strip())

    return query.order_by(Ticket.created_at.desc()).all()


def update_ticket(
    db: Session,
    ticket: Ticket,
    new_status: Optional[str] = None,
    note_text: Optional[str] = None,
    event_type: str = "NOTE_ADDED",
    status_change_note_text: Optional[str] = None,
) -> tuple[Ticket, Optional[Note]]:
    """
    Update ticket status and/or append internal notes, updating updated_at timestamp.
    - If status_change_note_text is provided, persists a synthetic STATUS_CHANGE note.
    - If note_text is provided, persists a note with event_type (default NOTE_ADDED).
    - Returns updated ticket and the primary created note (user note if present, else status note).
    """
    created_note: Optional[Note] = None
    status_note: Optional[Note] = None

    if new_status:
        ticket.status = new_status

    if status_change_note_text:
        status_note = Note(
            ticket_id=ticket.ticket_id,
            note_text=status_change_note_text,
            event_type="STATUS_CHANGE",
            created_at=utc_now(),
        )
        db.add(status_note)

    if note_text and note_text.strip():
        created_note = Note(
            ticket_id=ticket.ticket_id,
            note_text=note_text.strip(),
            event_type=event_type,
            created_at=utc_now(),
        )
        db.add(created_note)

    ticket.updated_at = utc_now()
    db.commit()
    db.refresh(ticket)
    if status_note:
        db.refresh(status_note)
    if created_note:
        db.refresh(created_note)

    primary_note = created_note if created_note else status_note
    return ticket, primary_note
