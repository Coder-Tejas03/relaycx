"""
Pydantic v2 schemas for request validation and response serialization.
Ensures strict type-safety, automatic 422 errors on invalid data, and ORM mapping.
"""

from datetime import datetime, timezone
from typing import Annotated, Literal, Optional
from pydantic import BaseModel, ConfigDict, EmailStr, Field, PlainSerializer, field_validator


def serialize_utc_datetime(dt: datetime) -> str:
    """Ensure datetime has UTC timezone before serializing to ISO 8601 string."""
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.isoformat()


# Timezone-aware datetime type for JSON serialization
UtcDateTime = Annotated[datetime, PlainSerializer(serialize_utc_datetime, return_type=str)]

# Allowed lifecycle status values
TicketStatus = Literal["Open", "In Progress", "Closed"]


class TicketCreateRequest(BaseModel):
    """Payload for creating a new support ticket."""
    customer_name: str = Field(..., min_length=1, max_length=255, description="Full customer name")
    customer_email: EmailStr = Field(..., description="Valid customer email address")
    subject: str = Field(..., min_length=1, max_length=255, description="Summary of the issue")
    description: str = Field(..., min_length=1, description="Detailed problem narrative")
    client_brand: Optional[str] = Field("UrbanFit", description="D2C brand or client name")
    channel: Optional[str] = Field("Email", description="Inbound communication channel")


class TicketCreatedResponse(BaseModel):
    """Response returned upon successful ticket creation (HTTP 201)."""
    ticket_id: str
    status: str
    client_brand: Optional[str] = None
    channel: Optional[str] = None
    issue_type: Optional[str] = "GEN"
    intake_issue_type: Optional[str] = "GEN"
    ticket_sequence: Optional[int] = None
    created_at: UtcDateTime

    model_config = ConfigDict(from_attributes=True)


class TicketSummary(BaseModel):
    """Lightweight ticket representation for the queue list view."""
    id: int
    ticket_id: str
    customer_name: str
    customer_email: str
    subject: str
    status: str
    client_brand: Optional[str] = None
    channel: Optional[str] = None
    issue_type: Optional[str] = "GEN"
    intake_issue_type: Optional[str] = "GEN"
    ticket_sequence: Optional[int] = None
    created_at: UtcDateTime
    updated_at: UtcDateTime

    model_config = ConfigDict(from_attributes=True)


class NoteResponse(BaseModel):
    """Representation of an internal note."""
    id: int
    ticket_id: str
    note_text: str
    event_type: str = "NOTE_ADDED"
    created_at: UtcDateTime

    model_config = ConfigDict(from_attributes=True)

    @field_validator("event_type", mode="before")
    @classmethod
    def default_event_type(cls, v):
        return v or "NOTE_ADDED"


class TicketDetailResponse(BaseModel):
    """Comprehensive ticket detail including full description and nested notes."""
    id: int
    ticket_id: str
    customer_name: str
    customer_email: str
    subject: str
    description: str
    status: str
    client_brand: Optional[str] = None
    channel: Optional[str] = None
    issue_type: Optional[str] = "GEN"
    intake_issue_type: Optional[str] = "GEN"
    ticket_sequence: Optional[int] = None
    created_at: UtcDateTime
    updated_at: UtcDateTime
    notes: list[NoteResponse] = []

    model_config = ConfigDict(from_attributes=True)


IssueType = Literal["ORD", "PAY", "ACC", "TEC", "INT", "ANA", "PRD", "GEN"]


class IssueTypeUpdateRequest(BaseModel):
    """Payload for correcting the current classification issue_type of a ticket."""
    issue_type: IssueType = Field(..., description="Target issue family code")


class IssueTypeCorrectedResponse(BaseModel):
    """Response returned upon successfully correcting a ticket's classification."""
    ticket_id: str
    issue_type: str
    intake_issue_type: Optional[str] = "GEN"
    updated_at: UtcDateTime

    model_config = ConfigDict(from_attributes=True)


class CustomerHistorySummary(BaseModel):
    """Lightweight summary of prior tickets for customer history audit view."""
    id: int
    ticket_id: str
    subject: str
    status: str
    client_brand: Optional[str] = None
    issue_type: Optional[str] = "GEN"
    intake_issue_type: Optional[str] = "GEN"
    created_at: UtcDateTime

    model_config = ConfigDict(from_attributes=True)


class TicketUpdateRequest(BaseModel):
    """Payload for updating ticket status and/or appending an internal note."""
    status: Optional[TicketStatus] = Field(None, description="Optional target status")
    note_text: Optional[str] = Field(None, description="Optional note text to append")


class TicketUpdatedResponse(BaseModel):
    """Response returned upon updating ticket status or adding a note."""
    ticket_id: str
    status: str
    updated_at: UtcDateTime
    note: Optional[NoteResponse] = None

    model_config = ConfigDict(from_attributes=True)


class TechnicalAccountDetails(BaseModel):
    """Deep contextual details for SaaS / API developer accounts."""
    endpoint: Optional[str] = None
    quota: Optional[str] = None
    current_usage: Optional[str] = None
    active_keys: Optional[int] = None
    rate_limit_policy: Optional[str] = None


class CommerceContextResponse(BaseModel):
    """Contextual customer order or SaaS account data for the agent workbench."""
    account_type: str = "ecommerce"  # "ecommerce" | "developer"
    order_id: str
    order_date: str
    item_name: str
    total_amount: str
    payment_method: str
    carrier: Optional[str] = None
    tracking_number: Optional[str] = None
    shipping_status: str
    estimated_delivery: Optional[str] = None
    customer_lifetime_value: Optional[str] = None
    customer_tier: Optional[str] = None
    return_window_active: Optional[bool] = None
    dispute_reason: Optional[str] = None
    notes: Optional[str] = None
    technical_details: Optional[TechnicalAccountDetails] = None
