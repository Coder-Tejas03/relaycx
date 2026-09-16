"""
Database engine configuration, session management, and Base declarative model.
Provides the get_db dependency for request session lifecycle.
"""

from collections.abc import Generator
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker, Session
from app.config import settings

# Determine database connection URL:
# Use Turso if configured, otherwise fallback to local SQLite.
if settings.TURSO_DATABASE_URL and settings.TURSO_AUTH_TOKEN:
    db_url = f"sqlite+{settings.TURSO_DATABASE_URL}/?authToken={settings.TURSO_AUTH_TOKEN}&secure=true"
else:
    db_url = settings.DATABASE_URL

connect_args = {}
if db_url.startswith("sqlite"):
    connect_args["check_same_thread"] = False

engine = create_engine(db_url, connect_args=connect_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


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
