// Application-wide constants. Import from here, never hardcode.

export const TICKET_STATUSES = ["Open", "In Progress", "Closed"];

export const STATUS_STYLES = {
  "Open": {
    bg: "var(--status-open-bg)",
    text: "var(--status-open-text)",
    border: "var(--status-open-border)",
  },
  "In Progress": {
    bg: "var(--status-inprogress-bg)",
    text: "var(--status-inprogress-text)",
    border: "var(--status-inprogress-border)",
  },
  "Closed": {
    bg: "var(--status-closed-bg)",
    text: "var(--status-closed-text)",
    border: "var(--status-closed-border)",
  },
};

// Read from .env at build time (Vite exposes VITE_ prefixed vars)
export const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";
