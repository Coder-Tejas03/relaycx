# RelayCX Frontend

The RelayCX frontend is a modern, responsive Single Page Application (SPA) built with React 18, Vite, and Tailwind CSS v4. It delivers a fast, dark-themed customer support management experience equipped with shadcn/ui primitives, Magic UI micro-animations, animated Lucide icons via `@animateicons/react`, and Sonner toast notifications. Support agents can view live queues, filter by status, search tickets with debounced queries, create tickets, and manage ticket lifecycle operations with internal notes.

---

## Prerequisites

- **Node.js**: v18.0.0 or higher (Tested on Node v24.13.1)
- **npm**: v9.0.0 or higher (Tested on npm 11.8.0)
- **Backend Service**: RelayCX FastAPI backend running locally on `http://localhost:8000`

---

## Setup Steps

1. Navigate to the `frontend/` directory:
   ```bash
   cd frontend
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Configure your local environment file:
   ```bash
   cp .env.example .env
   ```

---

## Environment Variables

| Variable | Description | Default / Example |
|---|---|---|
| `VITE_API_BASE_URL` | Base URL pointing to the FastAPI backend API | `http://localhost:8000` |

---

## How to Run Locally

Start the Vite development server:
```bash
npm run dev
```

The application will be available at `http://localhost:5173`.

To build the production bundle:
```bash
npm run build
```
The output will be placed in the `dist/` directory.
