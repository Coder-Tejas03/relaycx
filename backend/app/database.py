"""
Database engine configuration, session management, and Base declarative model.
Provides the get_db dependency for request session lifecycle.
"""

from collections.abc import Generator
from sqlalchemy import create_engine, text
from sqlalchemy.orm import declarative_base, sessionmaker, Session
from sqlalchemy.pool import NullPool
from app.config import settings

# Determine database connection URL and connection arguments:
# Use Turso if configured, otherwise fallback to local SQLite.
connect_args = {"check_same_thread": False}

if settings.TURSO_DATABASE_URL and settings.TURSO_AUTH_TOKEN:
    db_url = f"sqlite+{settings.TURSO_DATABASE_URL}/?secure=true"
    connect_args["auth_token"] = settings.TURSO_AUTH_TOKEN
    engine = create_engine(db_url, connect_args=connect_args, poolclass=NullPool)
else:
    db_url = settings.DATABASE_URL
    engine = create_engine(db_url, connect_args=connect_args)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def ensure_schema():
    """Ensure newly added columns exist in existing SQLite databases."""
    try:
        with engine.connect() as conn:
            # Check notes table
            result = conn.execute(text("PRAGMA table_info(notes)")).fetchall()
            cols = [r[1] for r in result]
            if cols and "event_type" not in cols:
                conn.execute(text("ALTER TABLE notes ADD COLUMN event_type VARCHAR(50) DEFAULT 'NOTE_ADDED'"))
                conn.commit()

            # Check tickets table for client_brand, channel, intake_issue_type, issue_type, ticket_sequence
            result_t = conn.execute(text("PRAGMA table_info(tickets)")).fetchall()
            t_cols = [r[1] for r in result_t]
            if t_cols and "client_brand" not in t_cols:
                conn.execute(text("ALTER TABLE tickets ADD COLUMN client_brand VARCHAR(100)"))
                conn.commit()
            if t_cols and "channel" not in t_cols:
                conn.execute(text("ALTER TABLE tickets ADD COLUMN channel VARCHAR(50)"))
                conn.commit()
            if t_cols and "intake_issue_type" not in t_cols:
                conn.execute(text("ALTER TABLE tickets ADD COLUMN intake_issue_type VARCHAR(10)"))
                conn.commit()
            if t_cols and "issue_type" not in t_cols:
                conn.execute(text("ALTER TABLE tickets ADD COLUMN issue_type VARCHAR(10)"))
                conn.commit()
            if t_cols and "ticket_sequence" not in t_cols:
                conn.execute(text("ALTER TABLE tickets ADD COLUMN ticket_sequence INTEGER"))
                conn.commit()
    except Exception:
        pass


def get_db() -> Generator[Session, None, None]:
    """
    FastAPI dependency yielding a database session per request,
    guaranteeing session closure when the request completes.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
