"""
Pydantic v2 schemas for request validation and response serialization.
Ensures strict type-safety, automatic 422 errors on invalid data, and ORM mapping.
"""

from datetime import datetime, timezone
from typing import Annotated, Literal, Optional
from pydantic import BaseModel, ConfigDict, EmailStr, Field, PlainSerializer


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


class TicketCreatedResponse(BaseModel):
    """Response returned upon successful ticket creation (HTTP 201)."""
    ticket_id: str
    status: str
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
    created_at: UtcDateTime
    updated_at: UtcDateTime

    model_config = ConfigDict(from_attributes=True)


class NoteResponse(BaseModel):
    """Representation of an internal note."""
    id: int
    ticket_id: str
    note_text: str
    created_at: UtcDateTime

    model_config = ConfigDict(from_attributes=True)


class TicketDetailResponse(BaseModel):
    """Comprehensive ticket detail including full description and nested notes."""
    id: int
    ticket_id: str
    customer_name: str
    customer_email: str
    subject: str
    description: str
    status: str
    created_at: UtcDateTime
    updated_at: UtcDateTime
    notes: list[NoteResponse] = []

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
