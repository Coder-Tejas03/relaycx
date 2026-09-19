"""
Commerce and customer operations context endpoints.
Exposes real-time e-commerce orders and technical subscription context for the agent workbench.
"""

from typing import Optional, Union
from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.orm import Session
from app.database import get_db
from app import service
from app.schemas import CommerceContextResponse, CustomerHistorySummary
from app.integrations.commerce_provider import get_order_context, get_relevant_context

router = APIRouter(prefix="/api/customers", tags=["Commerce Context"])


@router.get(
    "/{customer_email}/order-context",
    response_model=Union[CommerceContextResponse, None],
    responses={
        200: {
            "description": "Customer commerce or technical account context retrieved successfully.",
            "model": CommerceContextResponse,
        },
        204: {
            "description": "No active orders or subscription records found for this customer email.",
        },
    },
    summary="Get customer commerce and operational context",
)
def get_customer_order_context(customer_email: str):
    """
    Fetch active order context, fulfillment details, and account tier for a customer email.
    Returns HTTP 200 with structured context if found.
    Returns HTTP 204 No Content if no orders or active subscriptions are on file.
    """
    context = get_order_context(customer_email)
    if not context:
        return Response(status_code=status.HTTP_204_NO_CONTENT)
    return context


@router.get(
    "/{client_brand}/{customer_email}/context",
    response_model=Union[CommerceContextResponse, None],
    responses={
        200: {
            "description": "Customer commerce or technical account context retrieved successfully.",
            "model": CommerceContextResponse,
        },
        204: {
            "description": "No relevant orders or subscription records found for this customer and issue family.",
        },
    },
    summary="Get client-scoped and issue-relevant customer context",
    description="Fetches operational context strictly scoped to (client_brand, customer_email) and filtered by issue family relevance rules. Returns HTTP 204 if no relevant context exists."
)
def get_client_customer_context(
    client_brand: str,
    customer_email: str,
    issue_type: Optional[str] = None,
):
    """
    Fetch relevant operational context scoped strictly to (client_brand, customer_email)
    and filtered by issue family relevance rules.
    Returns HTTP 200 with structured context if found and relevant.
    Returns HTTP 204 No Content if not found or irrelevant to the issue family.
    """
    context = get_relevant_context(client_brand, customer_email, issue_type)
    if not context:
        return Response(status_code=status.HTTP_204_NO_CONTENT)
    return context


@router.get(
    "/{client_brand}/{customer_email}/history",
    response_model=list[CustomerHistorySummary],
    summary="Get customer ticket history under client brand",
    description="Returns prior tickets for a given customer under a specific client brand, enforcing brand isolation."
)
def get_client_customer_history(
    client_brand: str,
    customer_email: str,
    exclude_ticket_id: Optional[str] = None,
    db: Session = Depends(get_db),
) -> list[CustomerHistorySummary]:
    """Retrieve customer ticket history under a specific client brand."""
    return service.get_customer_history(
        db=db,
        client_brand=client_brand,
        customer_email=customer_email,
        exclude_ticket_id=exclude_ticket_id,
    )
