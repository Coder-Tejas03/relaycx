import React, { createContext, useContext, useState, useEffect, useCallback, useRef, useMemo } from "react";
import { ticketApi } from "@/services/api";
import { toast } from "sonner";

const TicketContext = createContext(null);

/**
 * Global Ticket Context Provider
 * Maintains central queue state, metrics, real-time debounced search,
 * and status filters shared across the AppShell Sidebar and Page views.
 */
export function TicketProvider({ children }) {
  const [allTickets, setAllTickets] = useState([]);
  const [tickets, setTickets] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);

  const [searchQuery, setSearchQuery] = useState(() => {
    try {
      return sessionStorage.getItem("relaycx_search_query") || "";
    } catch {
      return "";
    }
  });

  const [debouncedQuery, setDebouncedQuery] = useState(() => {
    try {
      return sessionStorage.getItem("relaycx_search_query") || "";
    } catch {
      return "";
    }
  });

  const [statusFilter, setStatusFilter] = useState(() => {
    try {
      return sessionStorage.getItem("relaycx_status_filter") || "All";
    } catch {
      return "All";
    }
  });

  const requestIdRef = useRef(0);

  // Persist filter and search to sessionStorage
  useEffect(() => {
    try {
      sessionStorage.setItem("relaycx_search_query", searchQuery);
    } catch {
      // Ignore storage errors
    }
  }, [searchQuery]);

  useEffect(() => {
    try {
      sessionStorage.setItem("relaycx_status_filter", statusFilter);
    } catch {
      // Ignore storage errors
    }
  }, [statusFilter]);

  // Debounce search query changes
  useEffect(() => {
    const timer = setTimeout(() => {
      setDebouncedQuery(searchQuery);
    }, 200);
    return () => clearTimeout(timer);
  }, [searchQuery]);

  // Fetch filtered tickets for the active table view and overview for stats
  const fetchFilteredTickets = useCallback(async () => {
    const currentRequestId = ++requestIdRef.current;
    setIsLoading(true);
    setError(null);

    try {
      const isDefaultQueue = statusFilter === "All" && (!debouncedQuery || debouncedQuery.trim() === "");
      let filteredData;
      let overviewData;

      if (isDefaultQueue) {
        overviewData = await ticketApi.getAll(null, "");
        filteredData = overviewData;
      } else {
        [filteredData, overviewData] = await Promise.all([
          ticketApi.getAll(statusFilter === "All" ? null : statusFilter, debouncedQuery),
          ticketApi.getAll(null, "")
        ]);
      }

      if (currentRequestId === requestIdRef.current) {
        setTickets(Array.isArray(filteredData) ? filteredData : []);
        if (Array.isArray(overviewData)) {
          setAllTickets(overviewData);
        }
        setIsLoading(false);
      }
    } catch (err) {
      if (currentRequestId === requestIdRef.current) {
        const message = err.message || "Failed to load tickets from server";
        setError(message);
        setIsLoading(false);
        toast.error(message);
      }
    }
  }, [statusFilter, debouncedQuery]);

  useEffect(() => {
    fetchFilteredTickets();
  }, [fetchFilteredTickets]);

  const resetFilters = useCallback(() => {
    setSearchQuery("");
    setDebouncedQuery("");
    setStatusFilter("All");
    try {
      sessionStorage.removeItem("relaycx_search_query");
      sessionStorage.removeItem("relaycx_status_filter");
    } catch {
      // Ignore storage errors
    }
  }, []);

  const refresh = useCallback(async () => {
    await fetchFilteredTickets();
  }, [fetchFilteredTickets]);

  // Computed metrics ribbon statistics from all tickets
  const stats = useMemo(() => {
    const total = allTickets.length;
    const open = allTickets.filter((t) => t.status === "Open").length;
    const inProgress = allTickets.filter((t) => t.status === "In Progress").length;
    const closed = allTickets.filter((t) => t.status === "Closed").length;
    const resolutionRate = total > 0 ? Math.round((closed / total) * 100) : 0;

    return {
      total,
      open,
      inProgress,
      closed,
      resolutionRate,
    };
  }, [allTickets]);

  const value = {
    allTickets,
    tickets,
    isLoading,
    error,
    searchQuery,
    setSearchQuery,
    statusFilter,
    setStatusFilter,
    resetFilters,
    refresh,
    stats,
  };

  return <TicketContext.Provider value={value}>{children}</TicketContext.Provider>;
}

export function useTicketsContext() {
  const context = useContext(TicketContext);
  if (!context) {
    throw new Error("useTicketsContext must be used within a TicketProvider");
  }
  return context;
}
