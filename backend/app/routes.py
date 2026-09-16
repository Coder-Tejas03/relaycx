"""
FastAPI route handlers for RelayCX tickets API.
All 4 core endpoints: Create, List/Filter, Detail, and Update.
"""

from typing import Optional
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.database import get_db
from app import service
from app.schemas import (
    TicketCreateRequest,
    TicketCreatedResponse,
    TicketSummary,
    TicketDetailResponse,
    TicketUpdateRequest,
    TicketUpdatedResponse,
)

router = APIRouter(prefix="/api/tickets", tags=["Tickets"])


@router.post(
    "",
    response_model=TicketCreatedResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new support ticket",
    description="Captures customer inquiry, auto-generates deterministic TKT-XXXXXX ID, and sets status to Open."
)
@router.post(
    "/",
    response_model=TicketCreatedResponse,
    status_code=status.HTTP_201_CREATED,
    include_in_schema=False
)
def create_ticket(
    body: TicketCreateRequest,
    db: Session = Depends(get_db)
) -> TicketCreatedResponse:
    """Create a ticket and persist to database."""
    return service.create_new_ticket(db, body)


@router.get(
    "",
    response_model=list[TicketSummary],
    summary="List all tickets",
    description="Returns tickets sorted by created_at DESC with optional status filtering and case-insensitive search."
)
@router.get(
    "/",
    response_model=list[TicketSummary],
    include_in_schema=False
)
def list_tickets(
    status: Optional[str] = None,
    search: Optional[str] = None,
    db: Session = Depends(get_db)
) -> list[TicketSummary]:
    """Retrieve filtered and searched tickets."""
    return service.get_ticket_list(db, status_filter=status, search_query=search)


@router.get(
    "/{ticket_id}",
    response_model=TicketDetailResponse,
    summary="Get ticket detail",
    description="Returns complete ticket details including the chronological list of internal operational notes."
)
def get_ticket(
    ticket_id: str,
    db: Session = Depends(get_db)
) -> TicketDetailResponse:
    """Retrieve ticket detail by business ID."""
    return service.get_ticket_detail(db, ticket_id)


@router.put(
    "/{ticket_id}",
    response_model=TicketUpdatedResponse,
    summary="Update ticket status and/or append internal note",
    description="Updates ticket status, appends internal notes, and executes auto-advance state machine logic."
)
def update_ticket(
    ticket_id: str,
    body: TicketUpdateRequest,
    db: Session = Depends(get_db)
) -> TicketUpdatedResponse:
    """Update ticket status and/or append note."""
    return service.update_ticket_data(db, ticket_id, body)
