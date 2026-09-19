// Application-wide constants. Import from here, never hardcode.

export const TICKET_STATUSES = ["Open", "In Progress", "Closed"];

export const STATUS_STYLES = {
  "Open": {
    bg: "var(--status-open-bg)",
    text: "var(--status-open-text)",
    border: "var(--status-open-border)",
    dot: "var(--status-open-dot)",
  },
  "In Progress": {
    bg: "var(--status-inprogress-bg)",
    text: "var(--status-inprogress-text)",
    border: "var(--status-inprogress-border)",
    dot: "var(--status-inprogress-dot)",
  },
  "Closed": {
    bg: "var(--status-closed-bg)",
    text: "var(--status-closed-text)",
    border: "var(--status-closed-border)",
    dot: "var(--status-closed-dot)",
  },
};

// Read from .env at build time (Vite exposes VITE_ prefixed vars)
export const API_BASE_URL = (import.meta.env.VITE_API_BASE_URL || "http://localhost:8000").replace(/\/+$/, "");

// 8 Canonical Issue Families for classification and issue correction
export const ISSUE_TAXONOMY = [
  { value: "ORD", label: "ORD — Orders & Shipping" },
  { value: "PAY", label: "PAY — Billing & Payments" },
  { value: "ACC", label: "ACC — Account & Access" },
  { value: "TEC", label: "TEC — Technical & Bugs" },
  { value: "INT", label: "INT — Integrations & APIs" },
  { value: "ANA", label: "ANA — Analytics & Data" },
  { value: "PRD", label: "PRD — Product & Features" },
  { value: "GEN", label: "GEN — General Inquiry" },
];
