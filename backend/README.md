# RelayCX Backend Service

## 1. What This Does
The RelayCX Backend is a typed, high-throughput REST API built with FastAPI and SQLAlchemy 2.0 to power customer support operations. It manages support ticket creation with deterministic `TKT-XXXXXX` identifiers, provides real-time multi-field search and lifecycle status filtering, maintains an audit trail of internal agent notes with automatic lifecycle state transitions (`Open` → `In Progress` → `Closed`), and serves interactive OpenAPI documentation at `/docs`.

## 2. Prerequisites
- **Python:** 3.11+ (Tested on Python 3.12.3)
- **Pip:** 24.0+
- **Virtualenv / venv**

## 3. Setup Steps
Run the following commands from the repository root:

```bash
# 1. Create a Python virtual environment
python3 -m venv .venv

# 2. Activate the virtual environment
source .venv/bin/activate

# 3. Upgrade pip and install pinned dependencies
pip install --upgrade pip
pip install -r backend/requirements.txt

# 4. (Optional) Create local .env file
cp backend/.env.example backend/.env
```

## 4. Environment Variables

| Variable | Type | Default | Description |
|---|---|---|---|
| `DATABASE_URL` | String | `sqlite:///./relaycx.db` | SQLAlchemy connection URL for the local SQLite database. |
| `TURSO_DATABASE_URL` | String | *Empty* | Production libSQL database URL from Turso (used in Phase 5). |
| `TURSO_AUTH_TOKEN` | String | *Empty* | Production authentication token for Turso libSQL database. |

## 5. How to Run Locally

From the `backend/` directory:

```bash
uvicorn app.main:app --reload --port 8000
```

Once running:
- **API Base URL:** `http://localhost:8000`
- **Interactive Swagger Docs:** `http://localhost:8000/docs`
- **Alternative ReDoc Docs:** `http://localhost:8000/redoc`
