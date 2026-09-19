import { API_BASE_URL } from "@/constants";

const BASE = `${API_BASE_URL}/api/tickets`;
const DEFAULT_TIMEOUT_MS = 15000;


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

  /**
   * Fetch prior tickets for a customer under a specific client brand.
   * @param {string} clientBrand - Client brand name e.g. "UrbanFit"
   * @param {string} customerEmail - Customer email address
   * @param {string|null} [excludeTicketId] - Optional current ticket ID to omit
   * @returns {Promise<Array<object>>} List of CustomerHistorySummary objects
   */
  getCustomerHistory: async (clientBrand, customerEmail, excludeTicketId = null) => {
    if (!clientBrand || !customerEmail) return [];
    const params = new URLSearchParams();
    params.append("client_brand", clientBrand);
    params.append("customer_email", customerEmail);
    if (excludeTicketId) {
      params.append("exclude_ticket_id", excludeTicketId);
    }

    const url = `${BASE}/customer-history?${params.toString()}`;
    const response = await fetchWithTimeout(url, {
      headers: { Accept: "application/json" },
    });

    if (!response.ok) {
      const errorMsg = await parseApiError(
        response,
        `Failed to fetch customer history (${response.status})`
      );
      throw new Error(errorMsg);
    }

    return response.json();
  },

  /**
   * Correct the current classification issue_type of a ticket.
   * Note: ticket_id and intake_issue_type remain strictly immutable.
   * @param {string} ticketId - Business ID e.g. "TKT-URB-INT-0001"
   * @param {string} issueType - Taxonomy family code e.g. "ORD", "PAY", "ACC", etc.
   * @returns {Promise<object>} IssueTypeCorrectedResponse { ticket_id, issue_type, intake_issue_type, updated_at }
   */
  updateIssueType: async (ticketId, issueType) => {
    const response = await fetchWithTimeout(`${BASE}/${encodeURIComponent(ticketId)}/issue-type`, {
      method: "PATCH",
      headers: {
        "Content-Type": "application/json",
        Accept: "application/json",
      },
      body: JSON.stringify({ issue_type: issueType }),
    });

    if (!response.ok) {
      const errorMsg = await parseApiError(
        response,
        `Failed to update ticket classification (${response.status})`
      );
      throw new Error(errorMsg);
    }

    return response.json();
  },
};

/**
 * Service encapsulating customer operations and e-commerce context APIs.
 */
export const customerApi = {
  /**
   * Fetch client-scoped and issue-relevant context for a customer.
   * @param {string} clientBrand - Client brand name
   * @param {string} customerEmail - Customer email address
   * @param {string|null} [issueType] - Current classification issue type (e.g. "ORD", "ANA")
   * @returns {Promise<object|null>} Context object or null if 204 No Content
   */
  getRelevantContext: async (clientBrand, customerEmail, issueType = null) => {
    if (!clientBrand || !customerEmail) return null;
    const params = new URLSearchParams();
    if (issueType) {
      params.append("issue_type", issueType);
    }
    const query = params.toString() ? `?${params.toString()}` : "";
    const url = `${API_BASE_URL}/api/customers/${encodeURIComponent(clientBrand)}/${encodeURIComponent(customerEmail)}/context${query}`;
    const response = await fetchWithTimeout(url, {
      headers: { Accept: "application/json" },
    });

    if (response.status === 204) {
      return null;
    }

    if (!response.ok) {
      const errorMsg = await parseApiError(
        response,
        `Failed to fetch relevant customer context (${response.status})`
      );
      throw new Error(errorMsg);
    }

    return response.json();
  },

  /**
   * Fetch active commerce or SaaS operational context for a customer email (legacy backward-compat).
   * @param {string} customerEmail - Customer email address
   * @returns {Promise<object|null>} Order context object, or null if no records found (HTTP 204)
   */
  getOrderContext: async (customerEmail) => {
    if (!customerEmail) return null;
    const url = `${API_BASE_URL}/api/customers/${encodeURIComponent(customerEmail)}/order-context`;
    const response = await fetchWithTimeout(url, {
      headers: { Accept: "application/json" },
    });

    if (response.status === 204) {
      return null;
    }

    if (!response.ok) {
      const errorMsg = await parseApiError(
        response,
        `Failed to fetch customer order context (${response.status})`
      );
      throw new Error(errorMsg);
    }

    return response.json();
  },
};
