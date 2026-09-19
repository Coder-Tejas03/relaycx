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
    IssueTypeUpdateRequest,
    IssueTypeCorrectedResponse,
    CustomerHistorySummary,
)

router = APIRouter(prefix="/api/tickets", tags=["Tickets"])


@router.post(
    "",
    response_model=TicketCreatedResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new support ticket",
    description="Captures customer inquiry, auto-generates deterministic structured ID, and sets status to Open."
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
    description="Returns tickets sorted by created_at DESC with optional status filtering, search, client brand, and customer email."
)
@router.get(
    "/",
    response_model=list[TicketSummary],
    include_in_schema=False
)
def list_tickets(
    status: Optional[str] = None,
    search: Optional[str] = None,
    client_brand: Optional[str] = None,
    customer_email: Optional[str] = None,
    limit: Optional[int] = None,
    offset: Optional[int] = None,
    db: Session = Depends(get_db)
) -> list[TicketSummary]:
    """Retrieve filtered and searched tickets with optional pagination."""
    return service.get_ticket_list(
        db,
        status_filter=status,
        search_query=search,
        client_brand=client_brand,
        customer_email=customer_email,
        limit=limit,
        offset=offset,
    )


@router.get(
    "/customer-history",
    response_model=list[CustomerHistorySummary],
    summary="Get customer ticket history",
    description="Returns prior tickets for a given customer under a specific client brand, enforcing brand isolation."
)
def get_customer_tickets_history(
    client_brand: str,
    customer_email: str,
    exclude_ticket_id: Optional[str] = None,
    db: Session = Depends(get_db)
) -> list[CustomerHistorySummary]:
    """Retrieve customer ticket history under a specific client brand."""
    return service.get_customer_history(
        db,
        client_brand=client_brand,
        customer_email=customer_email,
        exclude_ticket_id=exclude_ticket_id,
    )


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


@router.patch(
    "/{ticket_id}/issue-type",
    response_model=IssueTypeCorrectedResponse,
    summary="Correct ticket classification issue type",
    description="Corrects the current classification issue_type of a ticket. Note that ticket_id and intake_issue_type remain strictly immutable."
)
def patch_ticket_issue_type(
    ticket_id: str,
    body: IssueTypeUpdateRequest,
    db: Session = Depends(get_db)
) -> IssueTypeCorrectedResponse:
    """Correct current issue_type classification."""
    updated_ticket = service.correct_issue_type(db, ticket_id, body.issue_type)
    return IssueTypeCorrectedResponse.model_validate(updated_ticket)


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
