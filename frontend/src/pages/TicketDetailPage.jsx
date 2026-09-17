import React from "react";
import { Link, useParams, useNavigate } from "react-router-dom";
import BlurFade from "@/components/magicui/BlurFade";
import StatusBadge from "@/components/tickets/StatusBadge";
import NoteTimeline from "@/components/tickets/NoteTimeline";
import NoteConsole from "@/components/tickets/NoteConsole";
import { useTicketDetail } from "@/hooks/useTicketDetail";
import { formatRelativeTime, formatDateTime, formatDuration, cn } from "@/lib/utils";
import { TICKET_STATUSES } from "@/constants";
import { toast } from "sonner";
import {
  ArrowLeft,
  Copy,
  Check,
  AlertCircle,
  X,
  Play,
  CheckCircle2,
  RotateCcw,
  Loader2,
} from "lucide-react";


/**
 * Inline error recovery banner with retry capability and auto-dismiss.
 * Displayed directly below the failed action context.
 */
function ActionErrorBanner({ error, onDismiss }) {
  React.useEffect(() => {
    if (!error) return;
    const timer = setTimeout(() => {
      onDismiss?.();
    }, 8000);
    return () => clearTimeout(timer);
  }, [error, onDismiss]);

  if (!error) return null;

  return (
    <div
      role="alert"
      className="flex items-center justify-between gap-3 p-2.5 rounded-lg bg-red-950/40 border border-red-900/60 text-xs text-red-200 animate-in fade-in duration-ui"
    >
      <div className="flex items-center gap-2 flex-1 min-w-0">
        <AlertCircle size={14} className="text-red-400 shrink-0" />
        <span className="truncate">{error.message}</span>
      </div>
      <div className="flex items-center gap-2 shrink-0">
        {error.retry && (
          <button
            type="button"
            onClick={error.retry}
            className="px-2.5 py-1 min-h-[36px] rounded bg-red-900/60 hover:bg-red-900 text-red-100 font-medium transition-all duration-micro cursor-pointer text-[11px] border border-red-800/80 active:scale-95 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-red-400"
          >
            Retry
          </button>
        )}
        <button
          type="button"
          onClick={onDismiss}
          className="p-1.5 min-h-[36px] min-w-[36px] flex items-center justify-center rounded text-red-400 hover:text-red-200 hover:bg-red-900/40 transition-all duration-micro cursor-pointer active:scale-95 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-red-400"
          title="Dismiss error"
          aria-label="Dismiss error"
        >
          <X size={14} />
        </button>
      </div>
    </div>
  );
}

/**
 * Detail and operations workbench for a single support ticket.
 * High-density two-column layout with segmented status controller, customer context,
 * issue description, and collaboration notes timeline.
 */
export default function TicketDetailPage() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [copiedEmail, setCopiedEmail] = React.useState(false);
  const [copiedId, setCopiedId] = React.useState(false);
  const [showUnsavedModal, setShowUnsavedModal] = React.useState(false);
  const [pendingNavigation, setPendingNavigation] = React.useState(null);

  const {
    ticket,
    isLoading,
    isSubmitting,
    noteText,
    setNoteText,
    error,
    actionError,
    clearActionError,
    handleStatusChange,
    handleAddNote,
    handleAddNoteAndResolve,
  } = useTicketDetail(id);

  const hasUnsavedNotes = Boolean(noteText && noteText.trim().length > 0);

  const handleCopyEmail = () => {
    if (ticket?.customer_email) {
      navigator.clipboard.writeText(ticket.customer_email);
      setCopiedEmail(true);
      toast.success("Customer email copied to clipboard");
      setTimeout(() => setCopiedEmail(false), 2000);
    }
  };

  const handleCopyTicketId = () => {
    if (ticket?.ticket_id) {
      navigator.clipboard.writeText(ticket.ticket_id);
      setCopiedId(true);
      setTimeout(() => setCopiedId(false), 2000);
    }
  };

  const handleBreadcrumbClick = React.useCallback((e) => {
    e?.preventDefault?.();
    if (hasUnsavedNotes) {
      setPendingNavigation(() => () => {
        setNoteText("");
        navigate("/");
      });
      setShowUnsavedModal(true);
    } else {
      navigate("/");
    }
  }, [hasUnsavedNotes, navigate, setNoteText]);

  // Intercept beforeunload and in-app navigation when unsaved notes exist
  React.useEffect(() => {
    if (!hasUnsavedNotes) return;

    const handleBeforeUnload = (e) => {
      e.preventDefault();
      e.returnValue = "";
    };

    const handleDocumentClickCapture = (e) => {
      if (e.target.closest("#unsaved-note-modal")) return;

      const anchor = e.target.closest("a[href]");
      if (anchor) {
        const href = anchor.getAttribute("href");
        if (href && (href.startsWith("/") || href.startsWith("#")) && href !== window.location.pathname) {
          e.preventDefault();
          e.stopPropagation();
          setPendingNavigation(() => () => {
            setNoteText("");
            navigate(href);
          });
          setShowUnsavedModal(true);
          return;
        }
      }

      const asideButton = e.target.closest("aside button");
      if (asideButton) {
        e.preventDefault();
        e.stopPropagation();
        setPendingNavigation(() => () => {
          setNoteText("");
          asideButton.click();
        });
        setShowUnsavedModal(true);
      }
    };

    window.addEventListener("beforeunload", handleBeforeUnload);
    document.addEventListener("click", handleDocumentClickCapture, true);

    return () => {
      window.removeEventListener("beforeunload", handleBeforeUnload);
      document.removeEventListener("click", handleDocumentClickCapture, true);
    };
  }, [hasUnsavedNotes, navigate, setNoteText]);

  // Listen for status change events dispatched from Command Palette
  React.useEffect(() => {
    const handleStatusEvent = (e) => {
      const newStatus = e.detail?.status;
      if (newStatus && ticket) {
        handleStatusChange(newStatus);
      }
    };

    window.addEventListener("relaycx:ticket-status-change", handleStatusEvent);
    return () => {
      window.removeEventListener("relaycx:ticket-status-change", handleStatusEvent);
    };
  }, [ticket, handleStatusChange]);

  // Listen for Escape back navigation from useKeyboardShortcuts
  React.useEffect(() => {
    const handleBackEvent = (e) => {
      e.preventDefault();
      handleBreadcrumbClick(e);
    };

    window.addEventListener("relaycx:navigate-back", handleBackEvent);
    return () => {
      window.removeEventListener("relaycx:navigate-back", handleBackEvent);
    };
  }, [handleBreadcrumbClick]);

  return (
    <div className="p-4 sm:p-6 lg:p-8 space-y-6 max-w-7xl mx-auto">
      {/* Crisp Breadcrumb Navigation */}
      <BlurFade delay={0.06}>
        <nav aria-label="Breadcrumb" className="flex items-center gap-2 text-xs">
          <Link
            to="/"
            onClick={handleBreadcrumbClick}
            className="inline-flex items-center gap-1.5 text-zinc-400 hover:text-white transition-all duration-micro cursor-pointer focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-zinc-400 rounded-sm p-0.5"
          >
            <ArrowLeft size={13} />
            <span>Tickets</span>
          </Link>
          <span className="text-zinc-600 select-none">/</span>
          <span className="font-mono-id text-zinc-200 font-medium">
            {ticket?.ticket_id || id}
          </span>
        </nav>
      </BlurFade>

      {isLoading ? (
        // High-density loading skeletons
        <div className="grid grid-cols-1 gap-6 lg:grid-cols-3">
          <div className="space-y-6 lg:col-span-2 animate-pulse">
            <div className="h-60 rounded-xl bg-zinc-900/60 border border-zinc-800" />
            <div className="h-72 rounded-xl bg-zinc-900/60 border border-zinc-800" />
          </div>
          <div className="space-y-6 animate-pulse">
            <div className="h-40 rounded-xl bg-zinc-900/60 border border-zinc-800" />
            <div className="h-56 rounded-xl bg-zinc-900/60 border border-zinc-800" />
          </div>
        </div>
      ) : !ticket ? (
        // Clean Not Found State
        <BlurFade delay={0.12}>
          <div className="border border-zinc-800 bg-[#0A0A0A] rounded-xl text-center py-16 px-4">
            <div className="max-w-sm mx-auto space-y-3">
              <div className="size-10 rounded-full bg-zinc-900 border border-zinc-800 flex items-center justify-center text-zinc-500 mx-auto">
                ✕
              </div>
              <h2 className="text-base font-semibold text-white">
                Ticket Not Found
              </h2>
              <p className="text-xs text-zinc-400">
                {error || `The requested ticket "${id}" does not exist or could not be loaded.`}
              </p>
              <div className="pt-2">
                <Link
                  to="/"
                  className="inline-flex items-center justify-center min-h-[44px] sm:min-h-0 h-10 sm:h-8 px-4 rounded-md bg-white hover:bg-zinc-200 text-black text-xs font-medium transition-all duration-micro active:scale-[0.98] focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-zinc-400 focus-visible:ring-offset-2 focus-visible:ring-offset-black"
                >
                  Return to Queue
                </Link>
              </div>
            </div>
          </div>
        </BlurFade>
      ) : (
        // Full Two-Column Operations Layout (3:1 Ratio)
        <div className="grid grid-cols-1 gap-6 lg:grid-cols-3 items-start">
          {/* Left Column (70% width): Primary Ticket Card, Notes, Note Console */}
          <div className="space-y-6 lg:col-span-2">
            {/* Primary Ticket Narrative Card (No BorderBeam, sleek Vercel gradient highlight) */}
            <BlurFade delay={0.12}>
              <div className="relative overflow-hidden rounded-xl border border-white/[0.09] bg-[#212124] p-5 sm:p-6 shadow-xl">
                {/* Subtle top edge specular highlight */}
                <div className="absolute top-0 left-0 right-0 h-[1px] bg-gradient-to-r from-transparent via-zinc-600/40 to-transparent" />

                <div className="flex flex-wrap items-start justify-between gap-4">
                  <div>
                    <button
                      type="button"
                      onClick={handleCopyTicketId}
                      title="Click to copy Ticket ID"
                      className="group inline-flex items-center gap-1.5 font-mono-id tracking-wider text-xs text-zinc-400 hover:text-zinc-200 font-semibold cursor-pointer transition-all duration-micro active:scale-95 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-zinc-400 rounded-sm p-0.5"
                    >
                      <span>{ticket.ticket_id}</span>
                      {copiedId ? (
                        <Check size={13} className="text-emerald-400" />
                      ) : (
                        <Copy size={13} className="text-zinc-500 group-hover:text-zinc-300 transition-colors duration-micro" />
                      )}
                    </button>
                    <h1 className="mt-1 text-xl sm:text-2xl font-semibold tracking-tight text-white">
                      {ticket.subject}
                    </h1>
                  </div>

                  <StatusBadge status={ticket.status} />
                </div>

                {/* Customer Information with Quick Email Copy */}
                <div className="mt-4 flex flex-wrap items-center gap-3 text-xs">
                  <span className="font-medium text-zinc-300">
                    {ticket.customer_name}
                  </span>
                  <span className="text-zinc-600 select-none">•</span>
                  <button
                    type="button"
                    onClick={handleCopyEmail}
                    title="Click to copy email"
                    className="group inline-flex items-center gap-1.5 font-mono-id text-zinc-400 hover:text-white transition-all duration-micro cursor-pointer active:scale-95 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-zinc-400 rounded-sm p-0.5"
                  >
                    <span>{ticket.customer_email}</span>
                    {copiedEmail ? (
                      <Check size={13} className="text-emerald-400" />
                    ) : (
                      <Copy size={13} className="text-zinc-500 group-hover:text-zinc-300 transition-colors duration-micro" />
                    )}
                  </button>
                </div>

                {/* Issue Description Container */}
                <div className="mt-5 border-t border-white/[0.08] pt-4">
                  <h3 className="text-[11px] font-mono font-medium uppercase tracking-wider text-zinc-500 mb-2">
                    Issue Description
                  </h3>
                  <div className="whitespace-pre-wrap text-sm text-zinc-200 leading-relaxed break-words bg-[#17171A] p-4 rounded-lg border border-white/[0.08]">
                    {ticket.description}
                  </div>
                </div>
              </div>
            </BlurFade>

            {/* Internal Notes Timeline & Note Console */}
            <BlurFade delay={0.16}>
              <div className="rounded-xl border border-white/[0.09] bg-[#212124] p-5 sm:p-6 shadow-xl space-y-5">
                <div className="border-b border-white/[0.08] pb-3.5">
                  <h2 className="text-sm font-semibold text-white tracking-tight">
                    Internal Notes & Resolution Timeline
                  </h2>
                  <p className="text-xs text-zinc-400 mt-0.5">
                    Agent-only triage log and status transitions.
                  </p>
                </div>

                <NoteTimeline notes={ticket.notes} />

                <div className="border-t border-zinc-800/80 pt-4 space-y-3">
                  <NoteConsole
                    noteText={noteText}
                    onNoteChange={setNoteText}
                    onAddNote={handleAddNote}
                    onAddNoteAndResolve={handleAddNoteAndResolve}
                    onReopen={() => handleStatusChange("Open")}
                    isSubmitting={isSubmitting}
                    currentStatus={ticket.status}
                  />
                  {actionError?.type === "note" && (
                    <ActionErrorBanner
                      error={actionError}
                      onDismiss={clearActionError}
                    />
                  )}
                </div>
              </div>
            </BlurFade>
          </div>

          {/* Right Column (30% width): Primary CTA, Workflow Status & Audit Info */}
          <div className="space-y-6">
            {/* Primary Action CTA (Next Action Card) */}
            <BlurFade delay={0.13}>
              <div className="rounded-xl border border-white/[0.09] bg-[#212124] p-5 shadow-xl space-y-3.5">
                <div className="flex items-center justify-between">
                  <h3 className="text-xs font-mono font-medium uppercase tracking-wider text-zinc-400">
                    Next Action
                  </h3>
                  <span className="text-[10px] font-mono uppercase tracking-wider px-2 py-0.5 rounded bg-zinc-900 text-zinc-400 border border-zinc-800">
                    Primary CTA
                  </span>
                </div>

                {/* Open Ticket -> Start Investigation */}
                {ticket.status === "Open" && (
                  <button
                    type="button"
                    disabled={isSubmitting}
                    onClick={() => handleStatusChange("In Progress")}
                    className="w-full h-11 px-4 rounded-lg bg-white hover:bg-zinc-200 text-black font-semibold text-sm transition-all duration-micro flex items-center justify-center gap-2 cursor-pointer disabled:opacity-40 disabled:cursor-not-allowed shadow-md select-none active:scale-[0.98] focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-zinc-400 focus-visible:ring-offset-2 focus-visible:ring-offset-black"
                  >
                    {isSubmitting ? (
                      <>
                        <Loader2 size={16} className="animate-spin text-zinc-900" />
                        <span>Starting Investigation...</span>
                      </>
                    ) : (
                      <>
                        <Play size={15} className="fill-current text-black" />
                        <span>Start Investigation</span>
                      </>
                    )}
                  </button>
                )}

                {/* In Progress Ticket -> Resolve Ticket */}
                {ticket.status === "In Progress" && (
                  <button
                    type="button"
                    disabled={isSubmitting}
                    onClick={() => handleStatusChange("Closed")}
                    className="w-full h-11 px-4 rounded-lg bg-white hover:bg-zinc-200 text-black font-semibold text-sm transition-all duration-micro flex items-center justify-center gap-2 cursor-pointer disabled:opacity-40 disabled:cursor-not-allowed shadow-md select-none active:scale-[0.98] focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-zinc-400 focus-visible:ring-offset-2 focus-visible:ring-offset-black"
                  >
                    {isSubmitting ? (
                      <>
                        <Loader2 size={16} className="animate-spin text-zinc-900" />
                        <span>Resolving Ticket...</span>
                      </>
                    ) : (
                      <>
                        <CheckCircle2 size={16} className="text-emerald-600 stroke-[2.5]" />
                        <span>Resolve Ticket</span>
                      </>
                    )}
                  </button>
                )}

                {/* Closed Ticket -> Reopen Ticket */}
                {ticket.status === "Closed" && (
                  <button
                    type="button"
                    disabled={isSubmitting}
                    onClick={() => handleStatusChange("Open")}
                    className="w-full h-11 px-4 rounded-lg bg-zinc-900 border border-zinc-700 hover:bg-zinc-800 hover:border-amber-500/50 hover:text-amber-300 text-zinc-100 font-semibold text-sm transition-all duration-micro flex items-center justify-center gap-2 cursor-pointer disabled:opacity-40 disabled:cursor-not-allowed shadow-sm select-none active:scale-[0.98] focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-zinc-400"
                  >
                    {isSubmitting ? (
                      <>
                        <Loader2 size={16} className="animate-spin text-amber-400" />
                        <span>Reopening Ticket...</span>
                      </>
                    ) : (
                      <>
                        <RotateCcw size={15} className="text-amber-400" />
                        <span>Reopen Ticket</span>
                      </>
                    )}
                  </button>
                )}

                <p className="text-[11px] text-zinc-400 leading-relaxed">
                  {ticket.status === "Open"
                    ? "Advance ticket into active investigation queue."
                    : ticket.status === "In Progress"
                    ? "Confirm customer resolution and close ticket."
                    : "Reopen ticket to Open queue for follow-up inquiry."}
                </p>
              </div>
            </BlurFade>

            {/* Vercel Segmented Status Switcher */}
            <BlurFade delay={0.15}>
              <div className="rounded-xl border border-white/[0.09] bg-[#212124] p-5 shadow-xl space-y-3.5">
                <div className="flex items-center justify-between">
                  <h3 className="text-xs font-mono font-medium uppercase tracking-wider text-zinc-400">
                    WORKFLOW STATUS
                  </h3>
                </div>

                {/* Horizontal Segmented Button Group */}
                <div className="inline-flex p-1 bg-[#17171A] border border-white/[0.08] rounded-lg w-full">
                  {TICKET_STATUSES.map((statusOption) => {
                    const isCurrent = ticket.status === statusOption;
                    return (
                      <button
                        key={statusOption}
                        type="button"
                        disabled={isSubmitting}
                        onClick={() => handleStatusChange(statusOption)}
                        className={cn(
                          "flex-1 py-2 sm:py-1.5 min-h-[38px] sm:min-h-0 text-xs font-medium rounded-md transition-all duration-micro cursor-pointer text-center select-none focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-zinc-400 active:scale-[0.98] disabled:opacity-40 disabled:cursor-not-allowed",
                          isCurrent
                            ? "bg-zinc-800 text-white shadow-sm border border-zinc-700/60 font-semibold"
                            : "text-zinc-400 hover:text-zinc-200 hover:bg-zinc-900/50 active:bg-zinc-850"
                        )}
                      >
                        {statusOption}
                      </button>
                    );
                  })}
                </div>

                {/* Status context description */}
                <div className="flex items-center gap-2 pt-0.5">
                  <span
                    className={cn(
                      "size-1.5 rounded-full shrink-0",
                      ticket.status === "Open"
                        ? "bg-blue-400"
                        : ticket.status === "In Progress"
                        ? "bg-amber-400"
                        : "bg-zinc-500"
                    )}
                  />
                  <span className="text-[11px] text-zinc-400 font-medium">
                    {ticket.status === "Open"
                      ? "Awaiting investigation"
                      : ticket.status === "In Progress"
                      ? "Under active investigation"
                      : "Issue resolved"}
                  </span>
                </div>

                {actionError?.type === "status" && (
                  <ActionErrorBanner
                    error={actionError}
                    onDismiss={clearActionError}
                  />
                )}

                <p className="text-[11px] text-zinc-500">
                  Switching status immediately persists to Turso DB and updates queue visibility.
                </p>
              </div>
            </BlurFade>

            {/* Audit & Ticket Metadata Card */}
            <BlurFade delay={0.18}>
              <div className="rounded-xl border border-white/[0.09] bg-[#212124] p-5 shadow-xl space-y-3 text-xs">
                <div className="border-b border-white/[0.08] pb-2.5">
                  <h3 className="text-xs font-mono font-medium uppercase tracking-wider text-zinc-400">
                    Audit Information
                  </h3>
                </div>

                <div className="flex items-center justify-between py-1.5 border-b border-zinc-800/60">
                  <span className="text-zinc-500">Ticket ID</span>
                  <button
                    type="button"
                    onClick={handleCopyTicketId}
                    title="Click to copy Ticket ID"
                    className="group inline-flex items-center gap-1.5 font-mono-id text-zinc-200 hover:text-white cursor-pointer transition-all duration-micro active:scale-95 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-zinc-400 rounded-sm p-0.5"
                  >
                    <span>{ticket.ticket_id}</span>
                    {copiedId ? (
                      <Check size={12} className="text-emerald-400" />
                    ) : (
                      <Copy size={12} className="text-zinc-500 group-hover:text-zinc-300 transition-colors duration-micro" />
                    )}
                  </button>
                </div>

                <div className="flex items-center justify-between py-1.5 border-b border-zinc-800/60">
                  <span className="text-zinc-500">Customer</span>
                  <span className="text-zinc-200 font-medium truncate max-w-[150px]">
                    {ticket.customer_name}
                  </span>
                </div>

                <div className="flex items-center justify-between py-1.5 border-b border-zinc-800/60">
                  <span className="text-zinc-500">Activity</span>
                  <span className="font-mono-id text-zinc-200">
                    {ticket.notes?.length || 0} events
                  </span>
                </div>

                {ticket.status === "Closed" && (
                  <div className="flex items-center justify-between py-1.5 border-b border-zinc-800/60">
                    <span className="text-zinc-500">Resolution Time</span>
                    <span className="font-mono-id text-emerald-400 font-medium">
                      {formatDuration(ticket.created_at, ticket.updated_at)}
                    </span>
                  </div>
                )}

                <div className="flex flex-col py-1.5 border-b border-zinc-800/60 gap-0.5">
                  <div className="flex items-center justify-between">
                    <span className="text-zinc-500">Created</span>
                    <span className="text-zinc-400 font-mono-id text-[11px]">
                      {formatRelativeTime(ticket.created_at)}
                    </span>
                  </div>
                  <span className="font-mono-id text-[11px] text-zinc-500 text-right">
                    {formatDateTime(ticket.created_at)}
                  </span>
                </div>

                <div className="flex flex-col py-1 gap-0.5">
                  <div className="flex items-center justify-between">
                    <span className="text-zinc-500">Last Updated</span>
                    <span className="text-zinc-400 font-mono-id text-[11px]">
                      {formatRelativeTime(ticket.updated_at)}
                    </span>
                  </div>
                  <span className="font-mono-id text-[11px] text-zinc-500 text-right">
                    {formatDateTime(ticket.updated_at)}
                  </span>
                </div>
              </div>
            </BlurFade>
          </div>
        </div>
      )}

      {/* Unsaved Note Confirmation Dialog */}
      {showUnsavedModal && (
        <div
          id="unsaved-note-modal"
          role="dialog"
          aria-modal="true"
          aria-labelledby="unsaved-modal-title"
          className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-sm animate-in fade-in duration-ui"
        >
          <div className="relative w-full max-w-md rounded-xl border border-white/[0.12] bg-[#212124] p-5 sm:p-6 shadow-2xl space-y-4">
            <div className="flex items-start gap-3">
              <div className="size-9 rounded-full bg-amber-500/10 border border-amber-500/20 flex items-center justify-center text-amber-400 shrink-0 mt-0.5">
                <AlertCircle size={18} />
              </div>
              <div className="space-y-1 flex-1 min-w-0">
                <h2 id="unsaved-modal-title" className="text-sm font-semibold text-white">
                  Leave without saving?
                </h2>
                <p className="text-xs text-zinc-400 leading-relaxed">
                  You have an unsaved internal note in progress. If you leave now, your changes will be discarded.
                </p>
              </div>
            </div>

            <div className="flex items-center justify-end gap-2.5 pt-2 border-t border-white/[0.08]">
              <button
                type="button"
                onClick={() => {
                  setShowUnsavedModal(false);
                  setPendingNavigation(null);
                }}
                className="inline-flex items-center justify-center min-h-[44px] sm:min-h-0 h-10 sm:h-8 px-4 rounded-md border border-zinc-700/80 bg-zinc-900 text-zinc-300 hover:bg-zinc-800 hover:text-white active:scale-[0.98] text-xs font-medium transition-all duration-micro focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-zinc-400 cursor-pointer shadow-sm"
              >
                Stay
              </button>
              <button
                type="button"
                onClick={() => {
                  setShowUnsavedModal(false);
                  const performNav = pendingNavigation;
                  setPendingNavigation(null);
                  if (performNav) {
                    performNav();
                  } else {
                    setNoteText("");
                    navigate("/");
                  }
                }}
                className="inline-flex items-center justify-center min-h-[44px] sm:min-h-0 h-10 sm:h-8 px-4 rounded-md bg-red-950 border border-red-800 text-red-300 hover:bg-red-900/80 active:scale-[0.98] text-xs font-medium transition-all duration-micro focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-red-400 cursor-pointer shadow-sm"
              >
                Discard
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
