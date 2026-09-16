import React from "react";
import AnimatedList from "@/components/magicui/AnimatedList";
import { formatRelativeTime } from "@/lib/utils";

/**
 * Chronological timeline of internal support notes on a ticket.
 * @param {object} props
 * @param {Array<{id: number, note_text: string, created_at: string}>} props.notes - List of internal note records
 */
export default function NoteTimeline({ notes = [] }) {
  if (!notes || notes.length === 0) {
    return (
      <div className="rounded-xl border border-dashed border-zinc-800/80 bg-zinc-900/20 py-8 px-4 text-center">
        <p className="text-xs text-zinc-500 font-medium">
          No internal notes yet. Use the console below to log an update.
        </p>
      </div>
    );
  }

  return (
    <div className="space-y-3">
      <div className="flex items-center justify-between text-xs text-zinc-400 font-medium px-1">
        <span>Internal Activity Log ({notes.length})</span>
        <span className="text-[11px] text-zinc-500">Chronological</span>
      </div>

      <AnimatedList className="space-y-2.5">
        {notes.map((note, index) => (
          <div
            key={note.id || `note-${index}`}
            className="rounded-xl border border-zinc-800/80 bg-zinc-900/70 p-4 shadow-sm backdrop-blur-sm transition-all hover:border-zinc-700/80"
          >
            <div className="flex items-center justify-between gap-2 mb-2">
              <div className="flex items-center gap-2">
                <span className="flex size-5 items-center justify-center rounded-full bg-indigo-500/10 text-indigo-400 text-[10px] font-bold">
                  #
                </span>
                <span className="text-xs font-semibold text-zinc-300">
                  Internal Note
                </span>
              </div>
              <span className="text-xs font-mono-id text-zinc-500">
                {formatRelativeTime(note.created_at)}
              </span>
            </div>

            <p className="whitespace-pre-wrap text-sm text-zinc-200 leading-relaxed break-words">
              {note.note_text}
            </p>
          </div>
        ))}
      </AnimatedList>
    </div>
  );
}
