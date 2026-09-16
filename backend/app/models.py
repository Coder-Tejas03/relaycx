"""
SQLAlchemy ORM models for Tickets and Notes.
Implements the relational schema with cascading delete and indexing.
"""

from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base


def utc_now() -> datetime:
    """Return the current timezone-aware UTC datetime."""
    return datetime.now(timezone.utc)


class Ticket(Base):
    """
    Ticket table representing customer inquiries and support cases.
    """
    __tablename__ = "tickets"

    id = Column(Integer, primary_key=True, autoincrement=True)
    ticket_id = Column(String(32), unique=True, index=True, nullable=False)
    customer_name = Column(String(255), nullable=False)
    customer_email = Column(String(255), index=True, nullable=False)
    subject = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    status = Column(String(50), index=True, nullable=False, default="Open")
    created_at = Column(DateTime, nullable=False, default=utc_now)
    updated_at = Column(DateTime, nullable=False, default=utc_now, onupdate=utc_now)

    # Relationship to notes: cascading delete-orphan ensures cleanup when tickets are deleted
    notes = relationship(
        "Note",
        back_populates="ticket",
        cascade="all, delete-orphan",
        order_by="[Note.created_at.asc(), Note.id.asc()]"
    )


class Note(Base):
    """
    Note table representing internal agent operational notes appended to a ticket.
    """
    __tablename__ = "notes"

    id = Column(Integer, primary_key=True, autoincrement=True)
    ticket_id = Column(String(32), ForeignKey("tickets.ticket_id", ondelete="CASCADE"), nullable=False, index=True)
    note_text = Column(Text, nullable=False)
    event_type = Column(String(50), nullable=True, default="NOTE_ADDED")
    created_at = Column(DateTime, nullable=False, default=utc_now)

    # Back reference to the parent ticket
    ticket = relationship("Ticket", back_populates="notes")
