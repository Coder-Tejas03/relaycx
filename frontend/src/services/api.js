import { API_BASE_URL } from "@/constants";

const BASE = `${API_BASE_URL}/api/tickets`;
const DEFAULT_TIMEOUT_MS = 5000;

/**
 * Fetch wrapper with timeout and offline detection to prevent indefinite hangs.
 */
async function fetchWithTimeout(url, options = {}, timeoutMs = DEFAULT_TIMEOUT_MS) {
  if (typeof navigator !== "undefined" && navigator.onLine === false) {
    throw new Error("Network connection offline. Unable to reach server.");
  }

  const controller = new AbortController();
  const timeoutId = setTimeout(() => {
    controller.abort();
  }, timeoutMs);

  try {
    const response = await fetch(url, {
      ...options,
      signal: options.signal || controller.signal,
    });
    return response;
  } catch (err) {
    if (err.name === "AbortError") {
      throw new Error("Request timed out. Please check your network connection.");
    }
    throw err;
  } finally {
    clearTimeout(timeoutId);
  }
}

/**
 * Helper to extract clean error message from FastAPI response.
 * Handles both JSON detail objects and plain text errors.
 */
async function parseApiError(response, defaultMsg) {
  try {
    const errorJson = await response.json();
    if (errorJson && errorJson.detail) {
      if (typeof errorJson.detail === "string") {
        return errorJson.detail;
      }
      if (Array.isArray(errorJson.detail)) {
        return errorJson.detail.map((err) => err.msg || JSON.stringify(err)).join("; ");
      }
      return JSON.stringify(errorJson.detail);
    }
  } catch {
    try {
      const errorText = await response.text();
      if (errorText) return errorText;
    } catch {
      // Fall through to default message
    }
  }
  return defaultMsg;
}

/**
 * Service encapsulating all communication with the RelayCX backend API.
 * Components and hooks import from here, never calling fetch() directly.
 */
export const ticketApi = {
  /**
   * Fetch all tickets with optional filtering by status and search keyword.
   * @param {string|null} status - "Open", "In Progress", "Closed", or null/"All" for all
   * @param {string} search - Substring to search across ticket fields
   * @returns {Promise<Array<object>>} List of tickets
   */
  getAll: async (status = null, search = "") => {
    const params = new URLSearchParams();
    if (status && status !== "All") {
      params.append("status", status);
    }
    if (search && search.trim() !== "") {
      params.append("search", search.trim());
    }

    const query = params.toString() ? `?${params.toString()}` : "";
    const response = await fetchWithTimeout(`${BASE}${query}`, {
      headers: { Accept: "application/json" },
    });

    if (!response.ok) {
      const errorMsg = await parseApiError(
        response,
        `Failed to fetch tickets (${response.status})`
      );
      throw new Error(errorMsg);
    }

    return response.json();
  },

  /**
   * Fetch complete details for a single ticket including chronological internal notes.
   * @param {string} ticketId - e.g. "TKT-C74B9E"
   * @returns {Promise<object>} Detailed ticket object
   */
  getById: async (ticketId) => {
    const response = await fetchWithTimeout(`${BASE}/${encodeURIComponent(ticketId)}`, {
      headers: { Accept: "application/json" },
    });

    if (!response.ok) {
      const errorMsg = await parseApiError(
        response,
        `Failed to fetch ticket ${ticketId} (${response.status})`
      );
      throw new Error(errorMsg);
    }

    return response.json();
  },

  /**
   * Create a new ticket.
   * @param {object} data - { customer_name, customer_email, subject, description }
   * @returns {Promise<object>} Created ticket response { ticket_id, created_at }
   */
  create: async (data) => {
    const response = await fetchWithTimeout(`${BASE}/`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Accept: "application/json",
      },
      body: JSON.stringify(data),
    });

    if (!response.ok) {
      const errorMsg = await parseApiError(
        response,
        `Failed to create ticket (${response.status})`
      );
      throw new Error(errorMsg);
    }

    return response.json();
  },

  /**
   * Update ticket status and/or append an internal note.
   * @param {string} ticketId - e.g. "TKT-C74B9E"
   * @param {object} data - { status?, note_text? }
   * @returns {Promise<object>} Updated ticket response { updated_at }
   */
  update: async (ticketId, data) => {
    const response = await fetchWithTimeout(`${BASE}/${encodeURIComponent(ticketId)}`, {
      method: "PUT",
      headers: {
        "Content-Type": "application/json",
        Accept: "application/json",
      },
      body: JSON.stringify(data),
    });

    if (!response.ok) {
      const errorMsg = await parseApiError(
        response,
        `Failed to update ticket ${ticketId} (${response.status})`
      );
      throw new Error(errorMsg);
    }

    return response.json();
  },
};
