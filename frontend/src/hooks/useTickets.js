import { useState, useEffect, useCallback, useRef } from "react";
import { ticketApi } from "@/services/api";
import { toast } from "sonner";

/**
 * Custom hook for managing the ticket queue list, real-time debounced search,
 * status filtering, loading skeletons, and error notifications.
 * @returns {object} Queue state and mutators
 */
export function useTickets() {
  const [tickets, setTickets] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);
  const [searchQuery, setSearchQuery] = useState("");
  const [debouncedQuery, setDebouncedQuery] = useState("");
  const [statusFilter, setStatusFilter] = useState("All");

  // Keep track of active request sequence to avoid race conditions
  const requestIdRef = useRef(0);

  // Debounce search query changes by 200ms
  useEffect(() => {
    const timer = setTimeout(() => {
      setDebouncedQuery(searchQuery);
    }, 200);

    return () => clearTimeout(timer);
  }, [searchQuery]);

  const fetchTickets = useCallback(async () => {
    const currentRequestId = ++requestIdRef.current;
    setIsLoading(true);
    setError(null);

    try {
      const data = await ticketApi.getAll(
        statusFilter === "All" ? null : statusFilter,
        debouncedQuery
      );

      // Only update state if this is still the most recent request
      if (currentRequestId === requestIdRef.current) {
        setTickets(Array.isArray(data) ? data : []);
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
    fetchTickets();
  }, [fetchTickets]);

  const resetFilters = useCallback(() => {
    setSearchQuery("");
    setDebouncedQuery("");
    setStatusFilter("All");
  }, []);

  return {
    tickets,
    isLoading,
    error,
    searchQuery,
    setSearchQuery,
    statusFilter,
    setStatusFilter,
    refresh: fetchTickets,
    resetFilters,
  };
}

export default useTickets;
