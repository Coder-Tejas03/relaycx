import { clsx } from "clsx";
import { twMerge } from "tailwind-merge";

/**
 * Merge class names using clsx and tailwind-merge.
 * @param {...any} inputs - Class names, conditions, or arrays of classes.
 * @returns {string} Merged class string.
 */
export function cn(...inputs) {
  return twMerge(clsx(inputs));
}

/**
 * Safely parses an ISO date string or Date object.
 * Ensures ISO strings without an explicit timezone (e.g. from SQLite/FastAPI)
 * are treated as UTC rather than interpreted as local device time.
 * @param {string|Date} dateInput
 * @returns {Date|null}
 */
export function parseUtcDate(dateInput) {
  if (!dateInput) return null;
  if (dateInput instanceof Date) return isNaN(dateInput.getTime()) ? null : dateInput;

  let str = String(dateInput).trim();
  if (!str) return null;

  // If string has a space instead of T (e.g., SQLite raw output), normalize it
  if (str.includes(" ") && !str.includes("T")) {
    str = str.replace(" ", "T");
  }

  // If ISO string without Z or timezone offset (+HH:MM / -HH:MM), append Z
  if (!str.endsWith("Z") && !/[+-]\d{2}(:\d{2})?$/.test(str)) {
    str = str + "Z";
  }

  const date = new Date(str);
  return isNaN(date.getTime()) ? null : date;
}

/**
 * Formats an ISO date string or Date object into a human-friendly relative time.
 * e.g., "just now", "14m ago", "2h ago", "3d ago", or "Oct 14, 2026" if > 30 days.
 * @param {string|Date} dateInput
 * @returns {string} Formatted relative time.
 */
export function formatRelativeTime(dateInput) {
  const date = parseUtcDate(dateInput);
  if (!date) return "";

  const now = new Date();
  const diffInSeconds = Math.floor((now.getTime() - date.getTime()) / 1000);

  if (diffInSeconds < 0 || diffInSeconds < 60) return "just now";

  const diffInMinutes = Math.floor(diffInSeconds / 60);
  if (diffInMinutes < 60) return `${diffInMinutes}m ago`;

  const diffInHours = Math.floor(diffInMinutes / 60);
  if (diffInHours < 24) return `${diffInHours}h ago`;

  const diffInDays = Math.floor(diffInHours / 24);
  if (diffInDays < 30) return `${diffInDays}d ago`;

  return date.toLocaleDateString("en-US", {
    month: "short",
    day: "numeric",
    year: "numeric",
  });
}

/**
 * Formats an ISO date string into user-friendly localized date and time.
 * @param {string|Date} dateInput
 * @returns {string} Formatted date & time, e.g. "Sep 16, 2026, 11:14 AM"
 */
export function formatDateTime(dateInput) {
  const date = parseUtcDate(dateInput);
  if (!date) return "N/A";

  return date.toLocaleString("en-US", {
    month: "short",
    day: "numeric",
    year: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  });
}

/**
 * Formats an ISO date string into time only (e.g. "2:41 PM").
 * @param {string|Date} dateInput
 * @returns {string} Formatted time string
 */
export function formatTimeOnly(dateInput) {
  const date = parseUtcDate(dateInput);
  if (!date) return "";

  return date.toLocaleTimeString("en-US", {
    hour: "numeric",
    minute: "2-digit",
  });
}

/**
 * Formats duration between two dates into a human-readable string.
 * Examples: "14m", "2h 36m", "3d 4h", or "< 1m" if under 60 seconds.
 * @param {string|Date} startDateInput - Starting timestamp (e.g. created_at)
 * @param {string|Date} endDateInput - Ending timestamp (e.g. updated_at)
 * @returns {string} Human-readable duration
 */
export function formatDuration(startDateInput, endDateInput) {
  const start = parseUtcDate(startDateInput);
  const end = parseUtcDate(endDateInput);
  if (!start || !end) return "N/A";

  const diffInSeconds = Math.max(0, Math.floor((end.getTime() - start.getTime()) / 1000));
  if (diffInSeconds < 60) return "< 1m";

  const days = Math.floor(diffInSeconds / 86400);
  const hours = Math.floor((diffInSeconds % 86400) / 3600);
  const minutes = Math.floor((diffInSeconds % 3600) / 60);

  if (days > 0) {
    return hours > 0 ? `${days}d ${hours}h` : `${days}d`;
  }
  if (hours > 0) {
    return minutes > 0 ? `${hours}h ${minutes}m` : `${hours}h`;
  }
  return `${minutes}m`;
}

