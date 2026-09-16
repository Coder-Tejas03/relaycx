import React from "react";
import { Link, useParams } from "react-router-dom";
import BlurFade from "@/components/magicui/BlurFade";
import StatusBadge from "@/components/tickets/StatusBadge";
import NoteTimeline from "@/components/tickets/NoteTimeline";
import NoteConsole from "@/components/tickets/NoteConsole";
import { useTicketDetail } from "@/hooks/useTicketDetail";
import { formatRelativeTime, formatDateTime, cn } from "@/lib/utils";
import { TICKET_STATUSES } from "@/constants";
import { toast } from "sonner";
import { ArrowLeft, Copy, Check, AlertCircle, X } from "lucide-react";

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
      className="flex items-center justify-between gap-3 p-2.5 rounded-lg bg-red-950/40 border border-red-900/60 text-xs text-red-200 animate-in fade-in duration-200"
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
            className="px-2.5 py-1 rounded bg-red-900/60 hover:bg-red-900 text-red-100 font-medium transition-colors cursor-pointer text-[11px] border border-red-800/80"
          >
            Retry
          </button>
        )}
        <button
          type="button"
          onClick={onDismiss}
          className="p-1 rounded text-red-400 hover:text-red-200 hover:bg-red-900/40 transition-colors cursor-pointer"
          title="Dismiss error"
          aria-label="Dismiss error"
        >
          <X size={13} />
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
  const [copied, setCopied] = React.useState(false);

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

  const handleCopyEmail = () => {
    if (ticket?.customer_email) {
      navigator.clipboard.writeText(ticket.customer_email);
      setCopied(true);
      toast.success("Customer email copied to clipboard");
      setTimeout(() => setCopied(false), 2000);
    }
  };

  return (
    <div className="p-4 sm:p-6 lg:p-8 space-y-6 max-w-7xl mx-auto">
      {/* Crisp Breadcrumb Navigation */}
      <BlurFade delay={0.06}>
        <nav aria-label="Breadcrumb" className="flex items-center gap-2 text-xs">
          <Link
            to="/"
            className="inline-flex items-center gap-1.5 text-zinc-400 hover:text-white transition-colors"
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
                  className="inline-flex items-center justify-center h-8 px-4 rounded-md bg-white hover:bg-zinc-200 text-black text-xs font-medium transition-colors"
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
                    <span className="font-mono-id tracking-wider text-xs text-zinc-400 font-semibold">
                      {ticket.ticket_id}
                    </span>
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
                    className="group inline-flex items-center gap-1.5 font-mono-id text-zinc-400 hover:text-white transition-colors cursor-pointer"
                  >
                    <span>{ticket.customer_email}</span>
                    {copied ? (
                      <Check size={13} className="text-emerald-400" />
                    ) : (
                      <Copy size={13} className="text-zinc-500 group-hover:text-zinc-300 transition-colors" />
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

          {/* Right Column (30% width): Status Control Switcher & Audit Info */}
          <div className="space-y-6">
            {/* Vercel Segmented Status Switcher */}
            <BlurFade delay={0.14}>
              <div className="rounded-xl border border-white/[0.09] bg-[#212124] p-5 shadow-xl space-y-3.5">
                <div className="flex items-center justify-between">
                  <h3 className="text-xs font-mono font-medium uppercase tracking-wider text-zinc-400">
                    Workflow Status
                  </h3>
                  <span className="text-[11px] font-mono text-zinc-500">Manual Override</span>
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
                          "flex-1 py-1.5 text-xs font-medium rounded-md transition-all cursor-pointer text-center select-none",
                          isCurrent
                            ? "bg-zinc-800 text-white shadow-sm border border-zinc-700/60 font-semibold"
                            : "text-zinc-400 hover:text-zinc-200 hover:bg-zinc-900/50"
                        )}
                      >
                        {statusOption}
                      </button>
                    );
                  })}
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
                  <span className="font-mono-id text-zinc-200">
                    {ticket.ticket_id}
                  </span>
                </div>

                <div className="flex items-center justify-between py-1.5 border-b border-zinc-800/60">
                  <span className="text-zinc-500">Customer</span>
                  <span className="text-zinc-200 font-medium truncate max-w-[150px]">
                    {ticket.customer_name}
                  </span>
                </div>

                <div className="flex items-center justify-between py-1.5 border-b border-zinc-800/60">
                  <span className="text-zinc-500">Internal Notes</span>
                  <span className="font-mono-id text-zinc-200">
                    {ticket.notes?.length || 0}
                  </span>
                </div>

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
    </div>
  );
}
