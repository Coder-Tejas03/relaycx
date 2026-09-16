"""
Database engine configuration, session management, and Base declarative model.
Provides the get_db dependency for request session lifecycle.
"""

from collections.abc import Generator
from sqlalchemy import create_engine, text
from sqlalchemy.orm import declarative_base, sessionmaker, Session
from app.config import settings

# Determine database connection URL and connection arguments:
# Use Turso if configured, otherwise fallback to local SQLite.
connect_args = {"check_same_thread": False}

if settings.TURSO_DATABASE_URL and settings.TURSO_AUTH_TOKEN:
    db_url = f"sqlite+{settings.TURSO_DATABASE_URL}/?secure=true"
    connect_args["auth_token"] = settings.TURSO_AUTH_TOKEN
else:
    db_url = settings.DATABASE_URL

engine = create_engine(db_url, connect_args=connect_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def ensure_schema():
    """Ensure newly added columns exist in existing SQLite databases."""
    try:
        with engine.connect() as conn:
            result = conn.execute(text("PRAGMA table_info(notes)")).fetchall()
            cols = [r[1] for r in result]
            if cols and "event_type" not in cols:
                conn.execute(text("ALTER TABLE notes ADD COLUMN event_type VARCHAR(50) DEFAULT 'NOTE_ADDED'"))
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
