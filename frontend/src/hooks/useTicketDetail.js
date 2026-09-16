import { useState, useEffect, useCallback } from "react";
import { ticketApi } from "@/services/api";
import { toast } from "sonner";

/**
 * Custom hook managing single ticket state, note timeline, status transitions,
 * and auto-advance business logic interactions.
 * @param {string} ticketId - Identifier e.g. "TKT-C74B9E"
 * @returns {object} Ticket detail state and action handlers
 */
export function useTicketDetail(ticketId) {
  const [ticket, setTicket] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [noteText, setNoteText] = useState("");
  const [error, setError] = useState(null);

  const fetchTicket = useCallback(async () => {
    if (!ticketId) return;

    setIsLoading(true);
    setError(null);

    try {
      const data = await ticketApi.getById(ticketId);
      setTicket(data);
    } catch (err) {
      const message = err.message || `Failed to fetch ticket ${ticketId}`;
      setError(message);
      toast.error(message);
    } finally {
      setIsLoading(false);
    }
  }, [ticketId]);

  useEffect(() => {
    fetchTicket();
  }, [fetchTicket]);

  /**
   * Directly change ticket status via ToggleGroup.
   * @param {"Open" | "In Progress" | "Closed"} newStatus
   */
  const handleStatusChange = async (newStatus) => {
    if (!newStatus || newStatus === ticket?.status || isSubmitting) return;

    setIsSubmitting(true);
    try {
      await ticketApi.update(ticketId, { status: newStatus });
      toast.success(`Ticket status updated to "${newStatus}"`);
      await fetchTicket();
    } catch (err) {
      toast.error(err.message || "Failed to update ticket status");
    } finally {
      setIsSubmitting(false);
    }
  };

  /**
   * Append a note with automatic status advancement (Open -> In Progress on backend).
   */
  const handleAddNote = async () => {
    const trimmed = noteText.trim();
    if (!trimmed || isSubmitting) return;

    setIsSubmitting(true);
    try {
      await ticketApi.update(ticketId, { note_text: trimmed });
      setNoteText("");
      toast.success("Internal note added successfully");
      await fetchTicket();
    } catch (err) {
      toast.error(err.message || "Failed to add internal note");
    } finally {
      setIsSubmitting(false);
    }
  };

  /**
   * Append a note and explicitly transition status to "Closed".
   */
  const handleAddNoteAndResolve = async () => {
    const trimmed = noteText.trim();
    if (!trimmed || isSubmitting) return;

    setIsSubmitting(true);
    try {
      await ticketApi.update(ticketId, {
        note_text: trimmed,
        status: "Closed",
      });
      setNoteText("");
      toast.success("Ticket resolved and note logged!");
      await fetchTicket();
    } catch (err) {
      toast.error(err.message || "Failed to resolve ticket");
    } finally {
      setIsSubmitting(false);
    }
  };

  return {
    ticket,
    isLoading,
    isSubmitting,
    noteText,
    setNoteText,
    error,
    refresh: fetchTicket,
    handleStatusChange,
    handleAddNote,
    handleAddNoteAndResolve,
  };
}

export default useTicketDetail;
