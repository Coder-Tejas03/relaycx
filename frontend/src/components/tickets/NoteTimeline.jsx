import React from "react";
import AnimatedList from "@/components/magicui/AnimatedList";
import { formatRelativeTime, formatDateTime, cn } from "@/lib/utils";
import {
  ArrowRightLeft,
  MessageSquare,
  Sparkles,
  CheckCircle2,
  RefreshCw,
} from "lucide-react";

const EVENT_CONFIG = {
  STATUS_CHANGE: {
    label: "STATUS CHANGE",
    badgeClass: "bg-amber-500/10 text-amber-400 border-amber-500/20",
    iconClass: "text-amber-400",
    icon: ArrowRightLeft,
  },
  NOTE_ADDED: {
    label: "NOTE ADDED",
    badgeClass: "bg-zinc-800/80 text-zinc-300 border-zinc-700/60",
    iconClass: "text-zinc-400",
    icon: MessageSquare,
  },
  TICKET_CREATED: {
    label: "CREATED",
    badgeClass: "bg-blue-500/10 text-blue-400 border-blue-500/20",
    iconClass: "text-blue-400",
    icon: Sparkles,
  },
  TICKET_RESOLVED: {
    label: "RESOLVED",
    badgeClass: "bg-emerald-500/10 text-emerald-400 border-emerald-500/20",
    iconClass: "text-emerald-400",
    icon: CheckCircle2,
  },
  TICKET_REOPENED: {
    label: "REOPENED",
    badgeClass: "bg-amber-500/10 text-amber-400 border-amber-500/20",
    iconClass: "text-amber-400",
    icon: RefreshCw,
  },
};

/**
 * Chronological timeline of internal support notes and status transitions.
 * Features semantic event tags, vertical connecting spine, and hover timestamps.
 * @param {object} props
 * @param {Array<{id: number|string, note_text: string, event_type?: string, created_at: string, _pending?: boolean}>} props.notes
 */
export default function NoteTimeline({ notes = [] }) {
  if (!notes || notes.length === 0) {
    return (
      <div className="rounded-lg border border-dashed border-zinc-800/80 bg-zinc-950/40 py-8 px-4 text-center">
        <p className="text-xs text-zinc-500 font-medium">
          No internal notes logged yet. Use the console below to record investigation activity.
        </p>
      </div>
    );
  }

  return (
    <div className="space-y-3">
      <div className="flex items-center justify-between text-xs text-zinc-400 font-medium px-1">
        <span>Activity Log ({notes.length})</span>
        <span className="text-[11px] font-mono text-zinc-500">Chronological</span>
      </div>

      <div className="relative">
        {/* Continuous vertical spine connecting timeline events */}
        {notes.length > 1 && (
          <div
            className="absolute left-[13px] top-4 bottom-4 w-[1px] bg-zinc-800 pointer-events-none"
            aria-hidden="true"
          />
        )}

        <AnimatedList className="space-y-3">
          {notes.map((note, index) => {
            const rawType = (note.event_type || "NOTE_ADDED").toUpperCase();
            const config = EVENT_CONFIG[rawType] || EVENT_CONFIG.NOTE_ADDED;
            const Icon = config.icon;
            const isPending = Boolean(note._pending);
            const isStatusChange = rawType === "STATUS_CHANGE";

            return (
              <div
                key={note.id || `note-${index}`}
                className={cn(
                  "relative flex items-start gap-3 transition-opacity",
                  isPending && "opacity-75"
                )}
              >
                {/* Timeline node icon on the spine */}
                <div
                  className="relative z-10 flex size-7 shrink-0 items-center justify-center rounded-full bg-[#18181B] border border-zinc-800 shadow-sm mt-1"
                  aria-hidden="true"
                >
                  <Icon size={12} className={config.iconClass} />
                </div>

                {/* Event content card */}
                <div className="flex-1 rounded-lg border border-zinc-800/80 bg-zinc-950/60 p-3.5 space-y-2 hover:border-zinc-700/80 transition-all shadow-sm">
                  <div className="flex items-center justify-between gap-2">
                    <div className="flex items-center gap-2">
                      <span
                        className={cn(
                          "text-[10px] font-mono px-2 py-0.5 rounded border tracking-wider font-semibold uppercase",
                          config.badgeClass
                        )}
                      >
                        {config.label}
                      </span>
                      {isPending && (
                        <span className="text-[10px] font-mono text-zinc-500 italic">
                          Saving...
                        </span>
                      )}
                    </div>

                    {/* Exact time on hover, relative time displayed */}
                    <time
                      dateTime={note.created_at}
                      title={formatDateTime(note.created_at)}
                      className="text-xs font-mono-id text-zinc-500 hover:text-zinc-300 transition-colors cursor-default"
                    >
                      {formatRelativeTime(note.created_at)}
                    </time>
                  </div>

                  {isStatusChange ? (
                    <div className="inline-flex items-center gap-2 py-0.5 text-xs sm:text-sm font-medium text-amber-200/90 font-mono">
                      <span>{note.note_text}</span>
                    </div>
                  ) : (
                    <p className="whitespace-pre-wrap text-xs sm:text-sm text-zinc-200 leading-relaxed break-words">
                      {note.note_text}
                    </p>
                  )}
                </div>
              </div>
            );
          })}
        </AnimatedList>
      </div>
    </div>
  );
}
