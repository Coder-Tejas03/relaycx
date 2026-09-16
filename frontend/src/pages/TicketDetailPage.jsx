import React from "react";
import { Link, useParams } from "react-router-dom";
import AppHeader from "@/components/layout/AppHeader";
import BlurFade from "@/components/magicui/BlurFade";
import BorderBeam from "@/components/magicui/BorderBeam";
import StatusBadge from "@/components/tickets/StatusBadge";
import NoteTimeline from "@/components/tickets/NoteTimeline";
import NoteConsole from "@/components/tickets/NoteConsole";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { useTicketDetail } from "@/hooks/useTicketDetail";
import { formatRelativeTime, formatDateTime, cn } from "@/lib/utils";
import { TICKET_STATUSES } from "@/constants";
import { toast } from "sonner";

/**
 * Detail and operations page for a single support ticket.
 * Displays customer inquiry, notes timeline, note console with auto-advance,
 * direct status controls, and audit metadata.
 */
export default function TicketDetailPage() {
  const { id } = useParams();

  const {
    ticket,
    isLoading,
    isSubmitting,
    noteText,
    setNoteText,
    error,
    handleStatusChange,
    handleAddNote,
    handleAddNoteAndResolve,
  } = useTicketDetail(id);

  const handleCopyEmail = () => {
    if (ticket?.customer_email) {
      navigator.clipboard.writeText(ticket.customer_email);
      toast.success("Email copied!");
    }
  };

  return (
    <div className="min-h-screen bg-[var(--bg-base)] text-zinc-100 antialiased selection:bg-indigo-500/30 selection:text-indigo-200">
      <AppHeader />

      <main className="mx-auto max-w-7xl px-4 py-8 sm:px-6 lg:px-8 space-y-6">
        {/* Navigation Breadcrumb */}
        <BlurFade delay={0.08}>
          <div>
            <Link
              to="/"
              className="inline-flex items-center gap-1.5 text-xs font-medium text-zinc-400 transition-colors hover:text-white group"
            >
              <span className="transition-transform group-hover:-translate-x-0.5">←</span>
              Back to Tickets Queue
            </Link>
          </div>
        </BlurFade>

        {isLoading ? (
          // Loading Skeleton
          <div className="grid grid-cols-1 gap-6 lg:grid-cols-3">
            <div className="space-y-6 lg:col-span-2 animate-pulse">
              <div className="h-64 rounded-xl bg-zinc-900/60 border border-zinc-800" />
              <div className="h-72 rounded-xl bg-zinc-900/60 border border-zinc-800" />
            </div>
            <div className="space-y-6 animate-pulse">
              <div className="h-40 rounded-xl bg-zinc-900/60 border border-zinc-800" />
              <div className="h-56 rounded-xl bg-zinc-900/60 border border-zinc-800" />
            </div>
          </div>
        ) : !ticket ? (
          // Not Found State
          <BlurFade delay={0.16}>
            <Card className="border-zinc-800 bg-zinc-900/40 text-center py-16 px-4">
              <div className="max-w-sm mx-auto space-y-3">
                <div className="w-12 h-12 rounded-full bg-zinc-800 flex items-center justify-center text-zinc-400 mx-auto">
                  ✕
                </div>
                <h2 className="text-lg font-semibold text-white">
                  Ticket Not Found
                </h2>
                <p className="text-xs text-zinc-400">
                  {error || `The requested ticket "${id}" does not exist or could not be loaded.`}
                </p>
                <div className="pt-2">
                  <Link to="/">
                    <Button
                      size="sm"
                      className="bg-indigo-600 hover:bg-indigo-500 text-white text-xs"
                    >
                      Return to Queue
                    </Button>
                  </Link>
                </div>
              </div>
            </Card>
          </BlurFade>
        ) : (
          // Full Two-Column Operations Layout
          <div className="grid grid-cols-1 gap-6 lg:grid-cols-3">
            {/* Left Column: Ticket Detail, Notes, Console */}
            <div className="space-y-6 lg:col-span-2">
              {/* Primary Ticket Card with BorderBeam */}
              <BlurFade delay={0.14}>
                <div className="relative overflow-hidden rounded-xl border border-zinc-800/80 bg-zinc-900/70 p-6 shadow-2xl backdrop-blur-sm">
                  <BorderBeam
                    size={260}
                    duration={14}
                    colorFrom="#6366F1"
                    colorTo="#A855F7"
                  />

                  <div className="flex flex-wrap items-start justify-between gap-4">
                    <div>
                      <span className="font-mono-id tracking-wider text-xs text-indigo-400 font-semibold">
                        {ticket.ticket_id}
                      </span>
                      <h1 className="mt-1.5 text-xl sm:text-2xl font-bold tracking-tight text-white">
                        {ticket.subject}
                      </h1>
                    </div>

                    <StatusBadge status={ticket.status} />
                  </div>

                  {/* Customer Information with One-Click Email Copy */}
                  <div className="mt-4 flex flex-wrap items-center gap-3 text-xs">
                    <span className="font-medium text-zinc-300">
                      {ticket.customer_name}
                    </span>
                    <span className="text-zinc-600">•</span>
                    <button
                      type="button"
                      onClick={handleCopyEmail}
                      title="Click to copy email"
                      className="group inline-flex items-center gap-1.5 font-mono-id text-zinc-400 hover:text-indigo-300 transition-colors cursor-pointer break-all"
                    >
                      <span>{ticket.customer_email}</span>
                      <svg
                        className="w-3.5 h-3.5 text-zinc-500 group-hover:text-indigo-400 transition-colors"
                        fill="none"
                        viewBox="0 0 24 24"
                        stroke="currentColor"
                        strokeWidth={2}
                      >
                        <path
                          strokeLinecap="round"
                          strokeLinejoin="round"
                          d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z"
                        />
                      </svg>
                    </button>
                  </div>

                  {/* Issue Description */}
                  <div className="mt-5 border-t border-zinc-800/80 pt-4">
                    <h3 className="text-xs font-semibold uppercase tracking-wider text-zinc-400 mb-2">
                      Issue Description
                    </h3>
                    <p className="whitespace-pre-wrap text-sm text-zinc-200 leading-relaxed break-words bg-zinc-950/40 p-4 rounded-lg border border-zinc-800/50">
                      {ticket.description}
                    </p>
                  </div>
                </div>
              </BlurFade>

              {/* Internal Notes Timeline & Note Console */}
              <BlurFade delay={0.2}>
                <Card className="border-zinc-800/80 bg-zinc-900/60 shadow-xl backdrop-blur-sm">
                  <CardHeader className="border-b border-zinc-800/80 pb-4">
                    <CardTitle className="text-base font-semibold text-white">
                      Internal Notes & Collaboration
                    </CardTitle>
                  </CardHeader>
                  <CardContent className="pt-5 space-y-6">
                    <NoteTimeline notes={ticket.notes} />

                    <div className="border-t border-zinc-800/80 pt-5">
                      <NoteConsole
                        noteText={noteText}
                        onNoteChange={setNoteText}
                        onAddNote={handleAddNote}
                        onAddNoteAndResolve={handleAddNoteAndResolve}
                        isSubmitting={isSubmitting}
                        currentStatus={ticket.status}
                      />
                    </div>
                  </CardContent>
                </Card>
              </BlurFade>
            </div>

            {/* Right Column: Status Controls & Audit Information */}
            <div className="space-y-6">
              {/* Status Controls Card */}
              <BlurFade delay={0.16}>
                <Card className="border-zinc-800/80 bg-zinc-900/60 shadow-xl backdrop-blur-sm">
                  <CardHeader className="pb-3 border-b border-zinc-800/80">
                    <CardTitle className="text-sm font-semibold text-white">
                      Ticket Status
                    </CardTitle>
                  </CardHeader>
                  <CardContent className="pt-4 space-y-2">
                    <p className="text-xs text-zinc-400 mb-3">
                      Select status to manually transition ticket workflow:
                    </p>

                    <div className="grid grid-cols-1 gap-2">
                      {TICKET_STATUSES.map((statusOption) => {
                        const isCurrent = ticket.status === statusOption;
                        return (
                          <button
                            key={statusOption}
                            type="button"
                            disabled={isSubmitting}
                            onClick={() => handleStatusChange(statusOption)}
                            className={cn(
                              "w-full flex items-center justify-between px-3.5 py-2 rounded-lg text-xs font-medium transition-all duration-150 border cursor-pointer select-none",
                              isCurrent
                                ? "bg-indigo-600/20 border-indigo-500/50 text-indigo-200 font-semibold"
                                : "bg-zinc-950/40 border-zinc-800 text-zinc-400 hover:text-zinc-200 hover:bg-zinc-800/60"
                            )}
                          >
                            <span className="flex items-center gap-2">
                              <span
                                className={cn(
                                  "w-2 h-2 rounded-full",
                                  isCurrent ? "bg-indigo-400" : "bg-zinc-600"
                                )}
                              />
                              {statusOption}
                            </span>
                            {isCurrent && (
                              <span className="text-[10px] text-indigo-400 font-bold uppercase tracking-wider">
                                Current
                              </span>
                            )}
                          </button>
                        );
                      })}
                    </div>
                  </CardContent>
                </Card>
              </BlurFade>

              {/* Audit Information Card */}
              <BlurFade delay={0.22}>
                <Card className="border-zinc-800/80 bg-zinc-900/60 shadow-xl backdrop-blur-sm">
                  <CardHeader className="pb-3 border-b border-zinc-800/80">
                    <CardTitle className="text-sm font-semibold text-white">
                      Audit Information
                    </CardTitle>
                  </CardHeader>
                  <CardContent className="pt-4 space-y-3 text-xs">
                    <div className="flex items-center justify-between py-1 border-b border-zinc-800/60">
                      <span className="text-zinc-400">Ticket ID</span>
                      <span className="font-mono-id text-zinc-300">
                        {ticket.ticket_id}
                      </span>
                    </div>

                    <div className="flex items-center justify-between py-1 border-b border-zinc-800/60">
                      <span className="text-zinc-400">Customer</span>
                      <span className="text-zinc-300 font-medium truncate max-w-[150px]">
                        {ticket.customer_name}
                      </span>
                    </div>

                    <div className="flex items-center justify-between py-1 border-b border-zinc-800/60">
                      <span className="text-zinc-400">Internal Notes</span>
                      <span className="text-zinc-300 font-semibold">
                        {ticket.notes?.length || 0}
                      </span>
                    </div>

                    <div className="flex flex-col py-1 border-b border-zinc-800/60 gap-1">
                      <div className="flex items-center justify-between">
                        <span className="text-zinc-400">Created</span>
                        <span className="text-zinc-400 font-mono-id text-[11px]">
                          {formatRelativeTime(ticket.created_at)}
                        </span>
                      </div>
                      <span className="font-mono-id text-[11px] text-zinc-500 text-right">
                        {formatDateTime(ticket.created_at)}
                      </span>
                    </div>

                    <div className="flex flex-col py-1 gap-1">
                      <div className="flex items-center justify-between">
                        <span className="text-zinc-400">Last Updated</span>
                        <span className="text-zinc-400 font-mono-id text-[11px]">
                          {formatRelativeTime(ticket.updated_at)}
                        </span>
                      </div>
                      <span className="font-mono-id text-[11px] text-zinc-500 text-right">
                        {formatDateTime(ticket.updated_at)}
                      </span>
                    </div>
                  </CardContent>
                </Card>
              </BlurFade>
            </div>
          </div>
        )}
      </main>
    </div>
  );
}
