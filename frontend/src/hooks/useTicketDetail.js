import { useState, useEffect, useCallback } from "react";
import { ticketApi } from "@/services/api";
import { toast } from "sonner";

/**
 * Custom hook managing single ticket state, note timeline, status transitions,
 * optimistic UI updates, error rollback, and auto-advance business logic.
 * @param {string} ticketId - Identifier e.g. "TKT-C74B9E"
 * @returns {object} Ticket detail state, action errors, and optimistic action handlers
 */
export function useTicketDetail(ticketId) {
  const [ticket, setTicket] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [noteText, setNoteText] = useState("");
  const [error, setError] = useState(null);
  const [actionError, setActionError] = useState(null);

  const fetchTicket = useCallback(async (silent = false) => {
    if (!ticketId) return;

    if (!silent) {
      setIsLoading(true);
      setError(null);
    }

    try {
      const data = await ticketApi.getById(ticketId);
      setTicket(data);
    } catch (err) {
      const message = err.message || `Failed to fetch ticket ${ticketId}`;
      if (!silent) {
        setError(message);
        toast.error(message);
      }
    } finally {
      if (!silent) {
        setIsLoading(false);
      }
    }
  }, [ticketId]);

  useEffect(() => {
    fetchTicket();
  }, [fetchTicket]);

  const clearActionError = useCallback(() => {
    setActionError(null);
  }, []);

  /**
   * Optimistically change ticket status via ToggleGroup.
   * Immediately reflects in UI, rolls back on error with Retry capability.
   * @param {"Open" | "In Progress" | "Closed"} newStatus
   */
  const handleStatusChange = async (newStatus) => {
    if (!newStatus || newStatus === ticket?.status || isSubmitting) return;

    const previousTicket = ticket;
    const oldStatus = ticket?.status;

    setActionError(null);

    // 1. Optimistically update local ticket state
    const optimisticStatusNote = {
      id: `temp-status-${Date.now()}`,
      ticket_id: ticketId,
      note_text: `${oldStatus} → ${newStatus}`,
      event_type: "STATUS_CHANGE",
      created_at: new Date().toISOString(),
      _pending: true,
    };

    setTicket((prev) => ({
      ...prev,
      status: newStatus,
      updated_at: new Date().toISOString(),
      notes: [...(prev?.notes || []), optimisticStatusNote],
    }));

    setIsSubmitting(true);

    // 2. Fire network request
    try {
      const result = await ticketApi.update(ticketId, { status: newStatus });
      toast.success(`Ticket status updated to "${newStatus}"`);

      // Update timestamps & sync with backend
      setTicket((prev) => {
        if (!prev) return prev;
        return {
          ...prev,
          status: result.status,
          updated_at: result.updated_at,
        };
      });

      // Background silent sync to fetch canonical database records
      await fetchTicket(true);
    } catch (err) {
      // 3. Rollback on failure
      setTicket(previousTicket);
      setActionError({
        type: "status",
        message: `Couldn't update status. Ticket remains ${previousTicket?.status || "unchanged"}.`,
        retry: () => handleStatusChange(newStatus),
      });
      toast.error(err.message || "Failed to update ticket status");
    } finally {
      setIsSubmitting(false);
    }
  };

  /**
   * Optimistically append note with auto-advance (Open -> In Progress).
   * Note appears immediately in timeline, input clears immediately.
   * On failure, note is removed from timeline, input text is restored, and error is shown.
   */
  const handleAddNote = async () => {
    const trimmed = noteText.trim();
    if (!trimmed || isSubmitting || !ticket) return;

    const previousTicket = ticket;
    const previousText = noteText;
    const oldStatus = ticket.status;
    const willAutoAdvance = oldStatus === "Open";
    const targetStatus = willAutoAdvance ? "In Progress" : oldStatus;

    setActionError(null);

    // 1. Build optimistic notes
    const optimisticNotes = [];
    if (willAutoAdvance) {
      optimisticNotes.push({
        id: `temp-status-${Date.now()}`,
        ticket_id: ticketId,
        note_text: "Open → In Progress",
        event_type: "STATUS_CHANGE",
        created_at: new Date().toISOString(),
        _pending: true,
      });
    }

    optimisticNotes.push({
      id: `temp-note-${Date.now() + 1}`,
      ticket_id: ticketId,
      note_text: trimmed,
      event_type: "NOTE_ADDED",
      created_at: new Date().toISOString(),
      _pending: true,
    });

    // Immediately mutate UI state and clear composer
    setTicket((prev) => ({
      ...prev,
      status: targetStatus,
      updated_at: new Date().toISOString(),
      notes: [...(prev?.notes || []), ...optimisticNotes],
    }));
    setNoteText("");
    setIsSubmitting(true);

    // 2. Fire network request
    try {
      await ticketApi.update(ticketId, { note_text: trimmed });
      toast.success("Internal note added successfully");

      // Canonical silent sync
      await fetchTicket(true);
    } catch (err) {
      // 3. Rollback on failure
      setTicket(previousTicket);
      setNoteText(previousText);
      setActionError({
        type: "note",
        message: "Couldn't save note. Please try again.",
        retry: () => handleAddNote(),
      });
      toast.error(err.message || "Failed to add internal note");
    } finally {
      setIsSubmitting(false);
    }
  };

  /**
   * Optimistically append a note and explicitly transition status to "Closed".
   */
  const handleAddNoteAndResolve = async () => {
    const trimmed = noteText.trim();
    if (!trimmed || isSubmitting || !ticket) return;

    const previousTicket = ticket;
    const previousText = noteText;
    const oldStatus = ticket.status;

    setActionError(null);

    // 1. Build optimistic notes
    const optimisticNotes = [];
    if (oldStatus !== "Closed") {
      optimisticNotes.push({
        id: `temp-status-${Date.now()}`,
        ticket_id: ticketId,
        note_text: `${oldStatus} → Closed`,
        event_type: "STATUS_CHANGE",
        created_at: new Date().toISOString(),
        _pending: true,
      });
    }

    optimisticNotes.push({
      id: `temp-note-${Date.now() + 1}`,
      ticket_id: ticketId,
      note_text: trimmed,
      event_type: "NOTE_ADDED",
      created_at: new Date().toISOString(),
      _pending: true,
    });

    setTicket((prev) => ({
      ...prev,
      status: "Closed",
      updated_at: new Date().toISOString(),
      notes: [...(prev?.notes || []), ...optimisticNotes],
    }));
    setNoteText("");
    setIsSubmitting(true);

    // 2. Fire network request
    try {
      await ticketApi.update(ticketId, {
        note_text: trimmed,
        status: "Closed",
      });
      toast.success("Ticket resolved and note logged!");

      // Canonical silent sync
      await fetchTicket(true);
    } catch (err) {
      // 3. Rollback on failure
      setTicket(previousTicket);
      setNoteText(previousText);
      setActionError({
        type: "note",
        message: "Couldn't resolve ticket. Please try again.",
        retry: () => handleAddNoteAndResolve(),
      });
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
    actionError,
    clearActionError,
    refresh: fetchTicket,
    handleStatusChange,
    handleAddNote,
    handleAddNoteAndResolve,
  };
}

export default useTicketDetail;
