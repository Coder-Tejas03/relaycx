"""
Repository layer for raw database CRUD operations.
Encapsulates all direct SQLAlchemy session operations.
"""

from typing import Optional
from sqlalchemy import or_
from sqlalchemy.orm import Session
from app.models import Ticket, Note, utc_now
from app.schemas import TicketCreateRequest


def create_ticket(db: Session, ticket_id: str, data: TicketCreateRequest) -> Ticket:
    """
    Persist a new ticket record to the database with status 'Open'.
    """
    ticket = Ticket(
        ticket_id=ticket_id,
        customer_name=data.customer_name.strip(),
        customer_email=data.customer_email.strip().lower(),
        subject=data.subject.strip(),
        description=data.description.strip(),
        status="Open",
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
    search_query: Optional[str] = None
) -> list[Ticket]:
    """
    Retrieve tickets ordered by created_at DESC with optional status and search filters.
    Performs case-insensitive substring search across ticket_id, customer_name,
    customer_email, subject, and description.
    """
    query = db.query(Ticket)

    # Apply status filter if supplied and not 'All'
    if status_filter and status_filter.lower() != "all":
        query = query.filter(Ticket.status == status_filter)

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
        return query.order_by(Ticket.created_at.asc()).all()

    return query.order_by(Ticket.created_at.desc()).all()


def get_ticket_by_id(db: Session, ticket_id: str) -> Optional[Ticket]:
    """
    Fetch a single ticket by its human-readable business ID (e.g., TKT-C74B9E).
    Returns None if no matching ticket exists.
    """
    return db.query(Ticket).filter(Ticket.ticket_id == ticket_id).first()


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
