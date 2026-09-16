"""
FastAPI application entry point for RelayCX.
Configures CORS, table initialization on startup, and registers API routers.
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import engine, Base
from app import routes


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan context manager.
    Ensures database tables are created on startup.
    """
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(
    title="RelayCX Support CRM API",
    description="High-velocity Customer Support Ticketing API with real-time triage and persistent audit trail.",
    version="1.0.0",
    lifespan=lifespan
)

# CORS configuration for local development and client consumption
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register API routes
app.include_router(routes.router)


@app.get("/", tags=["Health Check"], summary="Root Health Check")
def health_check():
    """Health check endpoint confirming API availability."""
    return {
        "status": "healthy",
        "service": "RelayCX API",
        "version": "1.0.0"
    }
