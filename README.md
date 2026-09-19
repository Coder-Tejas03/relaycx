# RelayCX — High-Velocity Customer Support CRM & Commerce Intelligence Platform

[![Live Demo](https://img.shields.io/badge/Live_Demo-relaycx--eight.vercel.app-22c55e?style=for-the-badge&logo=vercel)](https://relaycx-eight.vercel.app/)
[![FastAPI](https://img.shields.io/badge/Backend-FastAPI_0.115+-009688?style=for-the-badge&logo=fastapi)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/Frontend-React_19_Vite-61DAFB?style=for-the-badge&logo=react)](https://react.dev)
[![TailwindCSS](https://img.shields.io/badge/Styling-Tailwind_CSS_v4-38B2AC?style=for-the-badge&logo=tailwind-css)](https://tailwindcss.com)

RelayCX is an enterprise-grade customer support CRM engineered for high-volume modern e-commerce, D2C, and multi-tenant support operations. It bridges inbound customer inquiries with high-velocity agent workflows by unifying core ticket lifecycle management with **multi-client brand isolation**, **omnichannel intake attribution**, **smooth-animated queue pagination**, and **real-time customer commerce intelligence**—giving support agents instant operational clarity without external tab context-switching.

---

## 🌐 Deployments & Quick Access

* **Live Application:** [https://relaycx-eight.vercel.app/](https://relaycx-eight.vercel.app/)
* **Interactive OpenAPI / Swagger Documentation:** Available locally at `http://localhost:8000/docs` or on the deployed backend URL at `/docs`.
* **Demo Video Walkthrough:** `[Insert Demo Video Link Here]`

---

## 📋 Operational Capabilities Matrix

| Operational Domain | Capability Details | RelayCX Architecture & Implementation |
| :--- | :--- | :--- |
| **Ticket Lifecycle & Sequencing** | Inbound intake, deterministic sequence IDs, metadata tracking | Strict Pydantic v2 schemas, collision-resistant IDs (`TKT-URB-ORD-0001`), client brand & channel tagging, and automated weighted keyword taxonomy (`ORD`, `PAY`, `ACC`, `TEC`, `PRD`, `GEN`). |
| **High-Density Queue & Pagination** | Fast list view, page shifting, performance scaling | Restricts active DOM view to 10 records per page with smooth `motion/react` page animations, responsive counter (`Showing 1–10 of 12`), safe clamping, and filter-reset safety. |
| **Multi-Field Instant Search** | Quick lookup across names, IDs, emails, and subjects | Real-time, 200ms debounced case-insensitive multi-field search across five core fields in both SQLite and client cache. |
| **Status Distribution & Triage** | Filtering by `Open`, `In Progress`, `Closed` | Dynamic status tabs with live count pills synchronized to real-time database state and clickable KPI cards (`Total Volume`, `Needs Attention`, `Active Triage`, `Resolution Rate`). |
| **Workbench & Audit Timeline** | Detailed triage workspace, status updates, internal notes | Full ticket workbench with chronological audit timeline, auto-advancing state machine (`Open` $\rightarrow$ `In Progress`), and structured event tagging (`TICKET_CREATED`, `STATUS_CHANGE`, `NOTE_ADDED`). |

---

## 🚀 Advanced Architecture & Enterprise Capabilities

RelayCX was designed from the ground up to solve the real-world friction of support teams handling hundreds of inquiries daily across diverse channels and multiple brand portfolios:

1. **Multi-Client Brand Scoping & Isolation (`client_brand`):**
   Real support agencies and multi-brand conglomerates manage multiple client brands simultaneously (e.g., *UrbanFit*, *Zen Botanics*, *Aura D2C*, *CasaNest*, *GlowTheory*). RelayCX enforces brand-isolated customer ticket histories and brand-partitioned sequence counters.
2. **Omnichannel Intake Attribution (`channel`):**
   Tracks whether inbound customer inquiries originated via **Email**, **WhatsApp**, **Web Portal**, or **Instagram**, rendering dedicated channel badges and filtering hooks.
3. **Real-Time Commerce Intelligence (`CommerceProvider`):**
   Support agents spend up to 40% of their triage time alt-tabbing into Shopify, Stripe, or shipping portals. RelayCX automatically injects live order details, carrier tracking links, return window status, dispute reasons, and customer lifetime value (LTV) right next to the ticket.
4. **Queue Table Pagination (10 Records / Page):**
   Restricts the active DOM view to 10 records per page with smooth `motion/react` page transition animations, smart windowing, safe clamping, and filter-reset safety, eliminating table lag as queues scale to hundreds of records.
5. **High-Velocity Keyboard Ergonomics (`Cmd + K` Command Palette):**
   A global modal engine allowing agents to search tickets, switch views, toggle status filters, and trigger quick actions without touching their mouse.

---

## ⚡ Key Architecture & Features

* **Deterministic Collision-Resistant Ticket IDs:** Formatted as `TKT-{CLIENT3}-{ISSUE3}-{SEQ4}` (e.g., `TKT-URB-ORD-0001`) with automated weighted keyword classification (`ORD`, `PAY`, `ACC`, `TEC`, `PRD`, `GEN`) and database-enforced unique constraints.
* **Auto-Advancing State Machine:** Appending an operational note to an `Open` ticket automatically transitions its lifecycle status to `In Progress`, eliminating repetitive manual clicks.
* **Customer Audit History:** Cross-ticket brand-scoped audit drawer displaying prior inquiries from the customer under that specific client brand.
* **Smooth Motion System:** Fluid transitions, shimmer loading skeletons, and subtle micro-interactions built with `motion/react` and Tailwind CSS v4 design tokens.
* **Resilient Networking:** Custom fetch wrapper with timeout abort controllers (`AbortController`) and browser offline state detection (`navigator.onLine`).

---

## 🏛️ System Architecture

RelayCX follows a strict **Layered Clean Architecture** separating routing protocols, domain business rules, data access logic, and relational persistence.

```text
┌─────────────────────────────────────────────────────────────────────────┐
│                 Client Layer (React 19 + Vite 8 + Tailwind v4)          │
│  - Support Operations Queue (Paginated) - Dynamic Status & KPI Ribbons │
│  - Cmd + K Quick Command Palette        - Smooth Motion Transitions    │
│  - Commerce Context & History Drawers   - Resilient Web Fetch Wrapper   │
└────────────────────────────────────┬────────────────────────────────────┘
                                     │ JSON / REST via Web Fetch
                                     ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                    FastAPI Gateway & Route Controllers                  │
│             /api/tickets/*            │        /api/customers/*         │
└──────────────────┬─────────────────────┴────────────────┬───────────────┘
                   │                                      │
                   ▼                                      ▼
┌──────────────────────────────────────┐ ┌────────────────────────────────┐
│         Ticket Core Service          │ │   Commerce Integration Provider │
│  - Concurrency-safe sequence counter │ │   - Customer profile aggregation│
│  - Deterministic state machine       │ │   - Order & carrier tracking   │
│  - Automated taxonomy classification │ │   - Extensible provider adapter │
└──────────────────┬───────────────────┘ └────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                           Repository Layer                              │
│         - Atomic session transactions    - Parameterized filters        │
│         - Limit & offset pagination      - Efficient record mapping     │
└────────────────────────────────────┬────────────────────────────────────┘
                                     │ SQLAlchemy ORM 2.0
                                     ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                  Persistence Engine (SQLite WAL / Turso libSQL)         │
│  - Composite unique constraints      - Indexed lookups (email, ID)      │
│  - Cascading delete-orphan notes     - Distributed cloud compatibility  │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## 🗄️ Database Schema & Relational Design

The relational database uses a normalized schema with composite integrity constraints, cascading relationships, and optimized indexing.

```text
                  ┌─────────────────────────────────────────────────────┐
                  │                       TICKETS                       │
                  ├─────────────────────────────────────────────────────┤
                  │ id                : INTEGER (PK, Auto)              │
                  │ ticket_id         : VARCHAR(32) [UNIQUE, INDEX]     │
                  │ customer_name     : VARCHAR(255)                    │
                  │ customer_email    : VARCHAR(255) [INDEX]            │
                  │ subject           : VARCHAR(255)                    │
                  │ description       : TEXT                            │
                  │ status            : VARCHAR(50) [INDEX]             │
                  │ client_brand      : VARCHAR(100)                    │
                  │ channel           : VARCHAR(50)                     │
                  │ intake_issue_type : VARCHAR(10)                     │
                  │ issue_type        : VARCHAR(10)                     │
                  │ ticket_sequence   : INTEGER                         │
                  │ created_at        : DATETIME (UTC)                  │
                  │ updated_at        : DATETIME (UTC)                  │
                  ├─────────────────────────────────────────────────────┤
                  │ CONSTRAINT: uq_client_intake_sequence               │
                  │ UNIQUE(client_brand, intake_issue_type, sequence)   │
                  └──────────────────────────┬──────────────────────────┘
                                             │ 1
                                             │
                                             │ 1:N Relationship (CASCADE)
                                             │
                                             │ N
                  ┌──────────────────────────┴──────────────────────────┐
                  │                        NOTES                        │
                  ├─────────────────────────────────────────────────────┤
                  │ id                : INTEGER (PK, Auto)              │
                  │ ticket_id         : VARCHAR(32) [FK -> tickets, IX] │
                  │ note_text         : TEXT                            │
                  │ event_type        : VARCHAR(50)                     │
                  │ created_at        : DATETIME (UTC)                  │
                  └─────────────────────────────────────────────────────┘
```

---

## 🔌 REST API Specification

### 1. Create a Ticket
* **Endpoint:** `POST /api/tickets`
* **Status:** `201 Created`
* **Request Body:**
  ```json
  {
    "customer_name": "Rohan Kapoor",
    "customer_email": "rohan.kapoor@urbanfit.com",
    "subject": "Received the wrong product in my UrbanFit order",
    "description": "I ordered the Performance Joggers in Size M but received a basic gym towel instead.",
    "client_brand": "UrbanFit",
    "channel": "WhatsApp"
  }
  ```
* **Response:**
  ```json
  {
    "ticket_id": "TKT-URB-ORD-0001",
    "status": "Open",
    "client_brand": "UrbanFit",
    "channel": "WhatsApp",
    "issue_type": "ORD",
    "intake_issue_type": "ORD",
    "ticket_sequence": 1,
    "created_at": "2026-09-19T06:40:00Z"
  }
  ```

### 2. List, Search, and Paginate Tickets
* **Endpoint:** `GET /api/tickets`
* **Status:** `200 OK`
* **Query Parameters:**
  * `status` *(optional)*: Filter by `Open`, `In Progress`, `Closed`, or `All`.
  * `search` *(optional)*: Case-insensitive substring match across ticket ID, customer name, email, subject, or description.
  * `client_brand` *(optional)*: Filter tickets by specific D2C client brand.
  * `customer_email` *(optional)*: Filter tickets by customer email.
  * `limit` *(optional)*: Number of records to return for pagination (default: all).
  * `offset` *(optional)*: Number of records to skip for pagination (default: 0).
* **Response:** Array of `TicketSummary` items.

### 3. Retrieve Ticket Detail & Audit Timeline
* **Endpoint:** `GET /api/tickets/{ticket_id}`
* **Status:** `200 OK`
* **Response:**
  ```json
  {
    "ticket_id": "TKT-URB-ORD-0001",
    "customer_name": "Rohan Kapoor",
    "customer_email": "rohan.kapoor@urbanfit.com",
    "subject": "Received the wrong product in my UrbanFit order",
    "description": "I ordered the Performance Joggers in Size M but received a basic gym towel instead.",
    "status": "Open",
    "client_brand": "UrbanFit",
    "channel": "WhatsApp",
    "issue_type": "ORD",
    "intake_issue_type": "ORD",
    "ticket_sequence": 1,
    "created_at": "2026-09-19T06:40:00Z",
    "updated_at": "2026-09-19T06:40:00Z",
    "notes": [
      {
        "id": 1,
        "ticket_id": "TKT-URB-ORD-0001",
        "note_text": "Ticket opened via WhatsApp inbound webhook.",
        "event_type": "TICKET_CREATED",
        "created_at": "2026-09-19T06:40:00Z"
      }
    ]
  }
  ```

### 4. Update Status & Append Internal Note
* **Endpoint:** `PUT /api/tickets/{ticket_id}`
* **Status:** `200 OK`
* **Request Body (Accepts either `note_text` or `notes`):**
  ```json
  {
    "status": "In Progress",
    "notes": "Warehouse dispatch logs verified; replacement parcel dispatched via Blue Dart."
  }
  ```
* **Response:**
  ```json
  {
    "ticket_id": "TKT-URB-ORD-0001",
    "status": "In Progress",
    "updated_at": "2026-09-19T06:55:00Z",
    "note": {
      "id": 2,
      "ticket_id": "TKT-URB-ORD-0001",
      "note_text": "Warehouse dispatch logs verified; replacement parcel dispatched via Blue Dart.",
      "event_type": "NOTE_ADDED",
      "created_at": "2026-09-19T06:55:00Z"
    },
    "success": true
  }
  ```

### 5. Correct Ticket Classification Issue Type
* **Endpoint:** `PATCH /api/tickets/{ticket_id}/issue-type`
* **Status:** `200 OK`
* **Request Body:** `{"issue_type": "ORD"}`
* **Behavior:** Safely updates the operational triage issue family while strictly preserving ticket ID and intake issue immutability.

### 6. Retrieve Brand-Scoped Customer History
* **Endpoint:** `GET /api/tickets/customer-history?client_brand=UrbanFit&customer_email=rohan.kapoor@urbanfit.com`
* **Status:** `200 OK`
* **Behavior:** Returns all prior tickets for that customer scoped strictly to that brand, enforcing brand privacy isolation.

### 7. Fetch Commerce Customer Context
* **Endpoint:** `GET /api/customers/{client_brand}/{customer_email}/context?issue_type=ORD`
* **Status:** `200 OK` (or `204 No Content` if no record exists)
* **Response:** Returns aggregated order ID, purchase date, item summary, order total, carrier tracking number, shipping status, dispute reason, and customer lifetime value.

---

## 🛠️ Local Installation & Setup

### Prerequisites
* **Python 3.12+**
* **Node.js 18+** and npm
* **Git**

```bash
git clone https://github.com/coder-tejas03/relaycx.git
cd relaycx
```

### 1. Backend Service (FastAPI)

```bash
cd backend

# Create and activate virtual environment
python3 -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment variables
cp .env.example .env

# Populate database with canonical multi-brand seed records
python seed.py

# Launch development server
uvicorn app.main:app --reload --port 8000
```
*The API gateway runs at `http://localhost:8000` with interactive Swagger documentation at `http://localhost:8000/docs`.*

### 2. Frontend Client (React 19 + Vite 8)

```bash
cd ../frontend

# Install dependencies
npm install

# Configure environment
cp .env.example .env
# Verify VITE_API_BASE_URL is set to http://localhost:8000

# Start Vite development server
npm run dev
```
*The client application runs at `http://localhost:5173`.*

---

## 🧪 Testing & Verification Suite

RelayCX includes automated test suites covering unit regressions, state machine auto-advances, concurrency, security, and end-to-end user journeys.

Run from the `backend/` directory:

```bash
# 1. Run unit regression tests
python -m unittest tests/test_existing_routes_regression.py

# 2. Run Phase 1 & Phase 2 verification suites
python tests/verify_phase1.py
python tests/verify_phase2.py

# 3. Run full test matrix with pytest (if pytest is installed)
pytest tests/ -v

# 4. Run full live end-to-end verification against running server
python ../verify_e2e.py
```

Frontend verification (from `frontend/` directory):
```bash
npm run lint   # Fast Oxlint static checks
npm run build  # Production Vite bundle compilation
```

---

## 📐 Architectural Decisions & Trade-Offs

| Decision | Chosen Solution | Considered Alternative | Justification & Trade-Off |
| :--- | :--- | :--- | :--- |
| **Persistence Engine** | SQLite (WAL mode) + Turso libSQL | Hosted Cloud PostgreSQL | Zero-config instant local bootstrapping with zero Docker overhead. Abstracted through SQLAlchemy 2.0 ORM to enable seamless PostgreSQL switching via `DATABASE_URL`. |
| **Queue Pagination** | Client-Side Slicing + Backend Query Params | Pure Server-Side Pagination Only | Preserves 100% accurate global KPI ribbon counts (Total Volume, Resolution Rate) and tab pill badges without extra network roundtrips, while cutting DOM render load to 10 rows. Backend supports optional `limit`/`offset` for future scalability. |
| **Commerce Context** | Decoupled Provider Adapter (`commerce_provider.py`) | Direct Shopify/ERP Webhooks | Prevents external third-party API rate limits and network latency from degrading support triage speed. |
| **UI State Sync** | Optimistic Updates + Micro-animations | WebSockets / Heavy Polling | WebSockets introduce stateful infrastructure overhead; optimistic updates provide instant agent feedback with zero network latency. |
| **Styling Architecture** | Tailwind CSS v4 + Geist Font + shadcn/ui | Heavy UI Frameworks (MUI / AntD) | Keeps bundle sizes lean (529ms build), allows bespoke OpenAI/Vercel charcoal aesthetic, and enables precision keyboard workflows. |

---

## 📁 Repository Structure

```text
relaycx/
├── backend/
│   ├── app/
│   │   ├── integrations/
│   │   │   └── commerce_provider.py    # Commerce context provider & mock order datasets
│   │   ├── config.py                   # Pydantic BaseSettings environment loader
│   │   ├── database.py                 # SQLAlchemy engine, session factory, schema migration
│   │   ├── main.py                     # FastAPI app factory, CORS, and routers
│   │   ├── models.py                   # SQLAlchemy schema models (Ticket, Note)
│   │   ├── repository.py               # Data access layer, pagination, & queries
│   │   ├── routes.py                   # Ticket REST API routes (/api/tickets/*)
│   │   ├── routes_commerce.py          # Commerce context routes (/api/customers/*)
│   │   ├── schemas.py                  # Pydantic v2 request/response models & validation
│   │   └── service.py                  # State machine logic, taxonomy scoring, auto-advance
│   ├── tests/                          # Regression, concurrency, security, & verification tests
│   ├── seed.py                         # Canonical 12-ticket multi-brand seed script
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── tickets/
│   │   │   │   ├── TicketTable.jsx     # High-density queue table with motion transitions
│   │   │   │   ├── Pagination.jsx      # 10 records/page pagination bar
│   │   │   │   ├── TicketRow.jsx        # Row component with customer avatars & badges
│   │   │   │   ├── StatusFilter.jsx     # Status filtering tabs with live count pills
│   │   │   │   ├── SearchBar.jsx        # 200ms debounced search input
│   │   │   │   ├── MetricsRibbon.jsx    # Top KPI cards with clickable status filters
│   │   │   │   ├── NoteConsole.jsx      # Internal notes composer & auto-advance buttons
│   │   │   │   ├── NoteTimeline.jsx     # Chronological audit timeline
│   │   │   │   ├── CommerceContextCard.jsx # Embedded customer order & tracking card
│   │   │   │   └── CustomerHistoryPanel.jsx # Brand-scoped customer ticket history
│   │   │   ├── layout/                 # AppShell, AppHeader, Sidebar
│   │   │   ├── magicui/                # BlurFade, BorderBeam, ShimmerButton
│   │   │   └── CommandPalette.jsx      # Cmd+K Quick action navigation engine
│   │   ├── pages/                      # HomePage, TicketDetailPage, CreateTicketPage
│   │   ├── context/TicketContext.jsx   # Global queue state & optimistic updates
│   │   ├── services/api.js             # Native fetch wrapper with timeouts & offline detection
│   │   └── index.css                   # Tailwind v4 theme, depth tokens, & motion durations
│   ├── package.json
│   └── vite.config.js
├── docs/                               # Architecture & system documentation
├── verify_e2e.py                       # Root-level live E2E verification runner
└── render.yaml                         # Deployment configuration
```

---

## 👤 Author & Maintainer

* **Developer:** Tejas Gosavi
* **GitHub:** [@Coder-Tejas03](https://github.com/Coder-Tejas03)
* **Live Demo:** [https://relaycx-eight.vercel.app/](https://relaycx-eight.vercel.app/)
* **Repository:** [https://github.com/Coder-Tejas03/relaycx](https://github.com/Coder-Tejas03/relaycx)