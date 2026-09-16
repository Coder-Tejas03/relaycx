# RelayCX — High-Velocity Customer Support CRM

RelayCX is an opinionated, full-stack customer support ticketing workspace engineered for rapid triage, tracking, and operational resolution. It bridges inbound customer inquiries with internal agent workflows through deterministic ticket IDs, a responsive search-and-filter queue, and an append-only timeline of operational notes with ergonomic auto-advancing statuses. The platform is architected as a decoupled system featuring a typed Python FastAPI backend and a modern React Vite Single Page Application. Data persistence is powered by SQLite with seamless compatibility for distributed libSQL via Turso in production. Built with precision craft and sub-second interaction speed, RelayCX eliminates ticket management friction for high-velocity teams.

## Architecture & Subsystems

- [Backend Service Documentation](backend/README.md) — FastAPI, SQLAlchemy 2.0, Pydantic v2 schemas, and REST endpoints.
- **Frontend SPA** (Phase 2 & 3) — React 18, Vite, Tailwind CSS v4, shadcn/ui, and Magic UI.
- **Hosted Persistence** (Phase 5) — Managed Turso libSQL cloud database.
