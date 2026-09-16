import React from "react";
import { ZapIcon } from "@animateicons/react/lucide";
import { Textarea } from "@/components/ui/textarea";

/**
 * Console for writing internal notes with dual action buttons (Add Note / Add Note & Resolve).
 * High-contrast Vercel monochrome action buttons.
 * @param {object} props
 * @param {string} props.noteText - Controlled text content
 * @param {function(string): void} props.onNoteChange - Text change callback
 * @param {function(): void} props.onAddNote - Submit standard note callback
 * @param {function(): void} props.onAddNoteAndResolve - Submit note and resolve ticket callback
 * @param {boolean} props.isSubmitting - Loading/saving state
 * @param {"Open" | "In Progress" | "Closed"} props.currentStatus - Current ticket status
 */
export default function NoteConsole({
  noteText = "",
  onNoteChange,
  onAddNote,
  onAddNoteAndResolve,
  isSubmitting = false,
  currentStatus = "Open",
}) {
  const isTextEmpty = !noteText || noteText.trim().length === 0;
  const isDisabled = isSubmitting || isTextEmpty;

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!isDisabled) {
      onAddNote();
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-3">
      <div className="space-y-1.5">
        <label
          htmlFor="internal-note-input"
          className="text-xs font-medium text-zinc-300"
        >
          Add Internal Note
        </label>
        <Textarea
          id="internal-note-input"
          value={noteText}
          onChange={(e) => onNoteChange(e.target.value)}
          placeholder="Document investigation progress, customer communication, or resolution steps..."
          disabled={isSubmitting}
          rows={3}
          className="w-full resize-y min-h-[85px] rounded-lg bg-zinc-950 border-zinc-800 text-zinc-100 placeholder:text-zinc-600 focus-visible:ring-zinc-600/40 text-xs sm:text-sm"
        />
      </div>

      <div className="flex flex-wrap items-center justify-between gap-3 pt-1">
        <span className="text-[11px] font-mono text-zinc-500">
          {currentStatus === "Open"
            ? "💡 Note submission auto-advances status to 'In Progress'"
            : currentStatus === "Closed"
            ? "🔒 Ticket is closed — Note recorded for audit log"
            : "Status remains 'In Progress'"}
        </span>

        <div className="flex items-center gap-2.5 ml-auto">
          {/* Resolve & Close Quick Action */}
          {currentStatus !== "Closed" && (
            <button
              type="button"
              onClick={onAddNoteAndResolve}
              disabled={isDisabled}
              className="inline-flex items-center gap-1.5 h-8 px-3 rounded-md bg-zinc-900 border border-zinc-800 hover:border-emerald-500/40 text-emerald-400 hover:text-emerald-300 hover:bg-zinc-850 text-xs font-medium transition-colors cursor-pointer disabled:opacity-40 disabled:cursor-not-allowed select-none"
            >
              <ZapIcon size={13} className="text-emerald-400" />
              <span>{isSubmitting ? "Resolving..." : "Add & Resolve"}</span>
            </button>
          )}

          {/* Primary Crisp White Button */}
          <button
            type="submit"
            disabled={isDisabled}
            className="inline-flex items-center justify-center h-8 px-3.5 rounded-md bg-white hover:bg-zinc-200 text-black text-xs font-medium transition-colors cursor-pointer disabled:opacity-40 disabled:cursor-not-allowed select-none shadow-sm"
          >
            {isSubmitting
              ? "Saving..."
              : currentStatus === "Closed"
              ? "Add Audit Note"
              : "Add Note"}
          </button>
        </div>
      </div>
    </form>
  );
}
