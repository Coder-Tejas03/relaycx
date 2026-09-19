import { useState, useEffect, useCallback, useRef } from "react";
import { ticketApi } from "@/services/api";
import { useTicketsContext } from "@/context/TicketContext";
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

  const ticketsContext = useTicketsContext();

  const ticketRef = useRef(ticket);
  ticketRef.current = ticket;

  const isSubmittingRef = useRef(isSubmitting);
  isSubmittingRef.current = isSubmitting;

  const noteTextRef = useRef(noteText);
  noteTextRef.current = noteText;

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
    const currentTicket = ticketRef.current;
    if (!newStatus || newStatus === currentTicket?.status || isSubmittingRef.current) return;

    const previousTicket = currentTicket;
    const oldStatus = currentTicket?.status;
    const nowIso = new Date().toISOString();

    setActionError(null);

    // 1. Optimistically update local ticket state and global context
    const optimisticStatusNote = {
      id: `temp-status-${Date.now()}`,
      ticket_id: ticketId,
      note_text: `${oldStatus} → ${newStatus}`,
      event_type: "STATUS_CHANGE",
      created_at: nowIso,
      _pending: true,
    };

    setTicket((prev) => ({
      ...prev,
      status: newStatus,
      updated_at: nowIso,
      notes: [...(prev?.notes || []), optimisticStatusNote],
    }));

    ticketsContext?.updateTicketInState(ticketId, {
      status: newStatus,
      updated_at: nowIso,
    });

    setIsSubmitting(true);

    // 2. Fire network request
    try {
      const result = await ticketApi.update(ticketId, { status: newStatus });

      // Update timestamps & sync with backend and global context
      setTicket((prev) => {
        if (!prev) return prev;
        return {
          ...prev,
          status: result.status,
          updated_at: result.updated_at,
        };
      });

      ticketsContext?.updateTicketInState(ticketId, {
        status: result.status,
        updated_at: result.updated_at,
      });
      ticketsContext?.refresh(true);

      // Background silent sync to fetch canonical database records
      await fetchTicket(true);
    } catch (err) {
      // 3. Rollback on failure
      setTicket(previousTicket);
      ticketsContext?.updateTicketInState(ticketId, {
        status: previousTicket?.status,
        updated_at: previousTicket?.updated_at,
      });

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
  const handleAddNote = async (textOverride) => {
    const rawText = typeof textOverride === "string" ? textOverride : noteTextRef.current;
    const trimmed = rawText.trim();
    const currentTicket = ticketRef.current;
    if (!trimmed || isSubmittingRef.current || !currentTicket) return;

    const previousTicket = currentTicket;
    const previousText = rawText;
    const oldStatus = currentTicket.status;
    const willAutoAdvance = oldStatus === "Open";
    const targetStatus = willAutoAdvance ? "In Progress" : oldStatus;
    const nowIso = new Date().toISOString();

    setActionError(null);

    // 1. Build optimistic notes
    const optimisticNotes = [];
    if (willAutoAdvance) {
      optimisticNotes.push({
        id: `temp-status-${Date.now()}`,
        ticket_id: ticketId,
        note_text: "Open → In Progress",
        event_type: "STATUS_CHANGE",
        created_at: nowIso,
        _pending: true,
      });
    }

    optimisticNotes.push({
      id: `temp-note-${Date.now() + 1}`,
      ticket_id: ticketId,
      note_text: trimmed,
      event_type: "NOTE_ADDED",
      created_at: nowIso,
      _pending: true,
    });

    // Immediately mutate UI state and clear composer
    setTicket((prev) => ({
      ...prev,
      status: targetStatus,
      updated_at: nowIso,
      notes: [...(prev?.notes || []), ...optimisticNotes],
    }));
    setNoteText("");

    ticketsContext?.updateTicketInState(ticketId, {
      status: targetStatus,
      updated_at: nowIso,
    });

    setIsSubmitting(true);

    // 2. Fire network request
    try {
      await ticketApi.update(ticketId, { note_text: trimmed });

      ticketsContext?.refresh(true);

      // Canonical silent sync
      await fetchTicket(true);
    } catch (err) {
      // 3. Rollback on failure
      setTicket(previousTicket);
      setNoteText(previousText);
      ticketsContext?.updateTicketInState(ticketId, {
        status: previousTicket?.status,
        updated_at: previousTicket?.updated_at,
      });

      setActionError({
        type: "note",
        message: "Couldn't save note. Please try again.",
        retry: () => handleAddNote(previousText),
      });
      toast.error(err.message || "Failed to add internal note");
    } finally {
      setIsSubmitting(false);
    }
  };

  /**
   * Optimistically append a note and explicitly transition status to "Closed".
   */
  const handleAddNoteAndResolve = async (textOverride) => {
    const rawText = typeof textOverride === "string" ? textOverride : noteTextRef.current;
    const trimmed = rawText.trim();
    const currentTicket = ticketRef.current;
    if (!trimmed || isSubmittingRef.current || !currentTicket) return;

    const previousTicket = currentTicket;
    const previousText = rawText;
    const oldStatus = currentTicket.status;
    const nowIso = new Date().toISOString();

    setActionError(null);

    // 1. Build optimistic notes
    const optimisticNotes = [];
    if (oldStatus !== "Closed") {
      optimisticNotes.push({
        id: `temp-status-${Date.now()}`,
        ticket_id: ticketId,
        note_text: `${oldStatus} → Closed`,
        event_type: "STATUS_CHANGE",
        created_at: nowIso,
        _pending: true,
      });
    }

    optimisticNotes.push({
      id: `temp-note-${Date.now() + 1}`,
      ticket_id: ticketId,
      note_text: trimmed,
      event_type: "NOTE_ADDED",
      created_at: nowIso,
      _pending: true,
    });

    setTicket((prev) => ({
      ...prev,
      status: "Closed",
      updated_at: nowIso,
      notes: [...(prev?.notes || []), ...optimisticNotes],
    }));
    setNoteText("");

    ticketsContext?.updateTicketInState(ticketId, {
      status: "Closed",
      updated_at: nowIso,
    });

    setIsSubmitting(true);

    // 2. Fire network request
    try {
      await ticketApi.update(ticketId, {
        note_text: trimmed,
        status: "Closed",
      });

      ticketsContext?.refresh(true);

      // Canonical silent sync
      await fetchTicket(true);
    } catch (err) {
      // 3. Rollback on failure
      setTicket(previousTicket);
      setNoteText(previousText);
      ticketsContext?.updateTicketInState(ticketId, {
        status: previousTicket?.status,
        updated_at: previousTicket?.updated_at,
      });

      setActionError({
        type: "note",
        message: "Couldn't resolve ticket. Please try again.",
        retry: () => handleAddNoteAndResolve(previousText),
      });
      toast.error(err.message || "Failed to resolve ticket");
    } finally {
      setIsSubmitting(false);
    }
  };

  /**
   * Correct ticket classification issue type.
   * Optimistically updates ticket in state and global context, rolls back on error.
   * @param {string} newIssueType - e.g. "ORD", "PAY", "ACC", etc.
   */
  const handleIssueTypeChange = async (newIssueType) => {
    const currentTicket = ticketRef.current;
    if (!newIssueType || newIssueType === currentTicket?.issue_type || isSubmittingRef.current) return;

    const previousTicket = currentTicket;
    const nowIso = new Date().toISOString();

    setActionError(null);

    // 1. Optimistically update local ticket state and global context
    setTicket((prev) => ({
      ...prev,
      issue_type: newIssueType,
      updated_at: nowIso,
    }));

    ticketsContext?.updateTicketInState(ticketId, {
      issue_type: newIssueType,
      updated_at: nowIso,
    });

    setIsSubmitting(true);

    // 2. Fire network request
    try {
      const result = await ticketApi.updateIssueType(ticketId, newIssueType);

      setTicket((prev) => {
        if (!prev) return prev;
        return {
          ...prev,
          issue_type: result.issue_type,
          updated_at: result.updated_at,
        };
      });

      ticketsContext?.updateTicketInState(ticketId, {
        issue_type: result.issue_type,
        updated_at: result.updated_at,
      });
      ticketsContext?.refresh(true);
      toast.success(`Classification corrected to ${newIssueType}`);
    } catch (err) {
      // 3. Rollback on failure
      setTicket(previousTicket);
      ticketsContext?.updateTicketInState(ticketId, {
        issue_type: previousTicket?.issue_type,
        updated_at: previousTicket?.updated_at,
      });
      toast.error(err.message || "Failed to update classification");
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
    handleIssueTypeChange,
  };
}

export default useTicketDetail;
