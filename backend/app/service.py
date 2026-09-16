"""
Service layer containing all RelayCX core business logic.
Handles ticket ID generation, lifecycle state transitions, and auto-advance rules.
"""

import secrets
from typing import Optional
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from app import repository
from app.schemas import (
    TicketCreateRequest,
    TicketCreatedResponse,
    TicketSummary,
    TicketDetailResponse,
    TicketUpdateRequest,
    TicketUpdatedResponse,
    NoteResponse,
)


def generate_ticket_id(db: Optional[Session] = None) -> str:
    """
    Generate a deterministic business ticket identifier in format 'TKT-XXXXXX'
    where XXXXXX is 6 random uppercase hex characters.
    Optionally ensures uniqueness against the database.
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
    Generate a unique ticket ID and persist a new ticket record in 'Open' state.
    """
    ticket_id = generate_ticket_id(db)
    ticket = repository.create_ticket(db, ticket_id, request_data)
    return TicketCreatedResponse.model_validate(ticket)


def get_ticket_list(
    db: Session,
    status_filter: Optional[str] = None,
    search_query: Optional[str] = None
) -> list[TicketSummary]:
    """
    Retrieve list of tickets matching optional status filter and search query.
    """
    tickets = repository.get_all_tickets(db, status_filter=status_filter, search_query=search_query)
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

    updated_ticket, created_note = repository.update_ticket(
        db=db,
        ticket=ticket,
        new_status=target_status,
        note_text=update_request.note_text
    )

    note_resp = NoteResponse.model_validate(created_note) if created_note else None

    return TicketUpdatedResponse(
        ticket_id=updated_ticket.ticket_id,
        status=updated_ticket.status,
        updated_at=updated_ticket.updated_at,
        note=note_resp
    )
