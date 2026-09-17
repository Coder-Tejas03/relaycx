import React from "react";
import { ZapIcon } from "@animateicons/react/lucide";
import { Lock, RotateCcw } from "lucide-react";
import { Textarea } from "@/components/ui/textarea";

/**
 * Console for writing internal notes with dual action buttons (Add Note / Add Note & Resolve)
 * and explicit closed state UX (Reopen / Add Audit Note).
 * High-contrast Vercel monochrome action buttons.
 * @param {object} props
 * @param {string} props.noteText - Controlled text content
 * @param {function(string): void} props.onNoteChange - Text change callback
 * @param {function(): void} props.onAddNote - Submit standard note callback
 * @param {function(): void} props.onAddNoteAndResolve - Submit note and resolve ticket callback
 * @param {function(): void} props.onReopen - Reopen ticket callback for closed tickets
 * @param {boolean} props.isSubmitting - Loading/saving state
 * @param {"Open" | "In Progress" | "Closed"} props.currentStatus - Current ticket status
 */
export default function NoteConsole({
  noteText = "",
  onNoteChange,
  onAddNote,
  onAddNoteAndResolve,
  onReopen,
  isSubmitting = false,
  currentStatus = "Open",
}) {
  const isTextEmpty = !noteText || noteText.trim().length === 0;
  const isDisabled = isSubmitting || isTextEmpty;
  const isClosed = currentStatus === "Closed";

  const handleSubmit = (e) => {
    e?.preventDefault?.();
    if (!isDisabled) {
      onAddNote();
    }
  };

  const handleKeyDown = (e) => {
    if ((e.metaKey || e.ctrlKey) && e.key === "Enter") {
      e.preventDefault();
      if (!isDisabled) {
        handleSubmit(e);
      }
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-3">
      {/* Explicit closed ticket notice */}
      {isClosed && (
        <div className="flex items-start gap-2.5 p-3 rounded-lg bg-zinc-950/80 border border-zinc-800 text-xs text-zinc-300 animate-in fade-in duration-200">
          <Lock size={14} className="text-zinc-400 shrink-0 mt-0.5" />
          <div className="space-y-0.5">
            <p className="font-medium text-zinc-200">
              Ticket closed. Customer-facing activity is disabled.
            </p>
            <p className="text-zinc-400 text-[11px]">
              You can still add an audit note.
            </p>
          </div>
        </div>
      )}

      <div className="space-y-1.5">
        <label
          htmlFor="internal-note-input"
          className="text-xs font-medium text-zinc-300"
        >
          {isClosed ? "Audit Note" : "Internal Note"}
        </label>
        <Textarea
          id="internal-note-input"
          value={noteText}
          onChange={(e) => onNoteChange(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder={
            isClosed
              ? "Add an audit note for the record..."
              : "Write an internal note..."
          }
          disabled={isSubmitting}
          rows={3}
          className="w-full resize-y min-h-[85px] rounded-lg bg-zinc-950 border-zinc-800 text-zinc-100 placeholder:text-zinc-600 focus-visible:ring-zinc-600/40 text-xs sm:text-sm"
        />
      </div>

      <div className="flex flex-wrap items-center justify-between gap-3 pt-1">
        {!isClosed && (
          <span className="text-[11px] font-mono text-zinc-500">
            {currentStatus === "Open"
              ? "💡 Note submission auto-advances status to 'In Progress'"
              : "Status remains 'In Progress'"}
          </span>
        )}

        <div className="flex items-center gap-2.5 ml-auto">
          {isClosed ? (
            <>
              {/* Reopen Ticket Action for Closed Ticket */}
              {onReopen && (
                <button
                  type="button"
                  onClick={onReopen}
                  disabled={isSubmitting}
                  className="inline-flex items-center gap-1.5 h-8 px-3 rounded-md bg-zinc-900 border border-zinc-700 hover:border-amber-500/40 text-zinc-200 hover:text-amber-300 hover:bg-zinc-800 text-xs font-medium transition-colors cursor-pointer disabled:opacity-40 disabled:cursor-not-allowed select-none"
                >
                  <RotateCcw size={13} className="text-amber-400" />
                  <span>{isSubmitting ? "Reopening..." : "Reopen Ticket"}</span>
                </button>
              )}

              {/* Add Audit Note Action */}
              <button
                type="submit"
                disabled={isDisabled}
                title="Submit audit note (⌘↵)"
                className="inline-flex items-center justify-center gap-1.5 h-8 px-3.5 rounded-md bg-white hover:bg-zinc-200 text-black text-xs font-medium transition-colors cursor-pointer disabled:opacity-40 disabled:cursor-not-allowed select-none shadow-sm"
              >
                <span>{isSubmitting ? "Saving..." : "Add Audit Note"}</span>
                <kbd className="hidden sm:inline-block font-mono text-[10px] text-zinc-600 bg-zinc-200 px-1 py-0.5 rounded border border-zinc-300 select-none">
                  ⌘↵
                </kbd>
              </button>
            </>
          ) : (
            <>
              {/* Resolve & Close Quick Action */}
              <button
                type="button"
                onClick={onAddNoteAndResolve}
                disabled={isDisabled}
                className="inline-flex items-center gap-1.5 h-8 px-3 rounded-md bg-zinc-900 border border-zinc-800 hover:border-emerald-500/40 text-emerald-400 hover:text-emerald-300 hover:bg-zinc-850 text-xs font-medium transition-colors cursor-pointer disabled:opacity-40 disabled:cursor-not-allowed select-none"
              >
                <ZapIcon size={13} className="text-emerald-400" />
                <span>{isSubmitting ? "Resolving..." : "Add & Resolve"}</span>
              </button>

              {/* Primary Crisp White Button */}
              <button
                type="submit"
                disabled={isDisabled}
                title="Submit note (⌘↵)"
                className="inline-flex items-center justify-center gap-1.5 h-8 px-3.5 rounded-md bg-white hover:bg-zinc-200 text-black text-xs font-medium transition-colors cursor-pointer disabled:opacity-40 disabled:cursor-not-allowed select-none shadow-sm"
              >
                <span>{isSubmitting ? "Saving..." : "Add Note"}</span>
                <kbd className="hidden sm:inline-block font-mono text-[10px] text-zinc-600 bg-zinc-200 px-1 py-0.5 rounded border border-zinc-300 select-none">
                  ⌘↵
                </kbd>
              </button>
            </>
          )}
        </div>
      </div>
    </form>
  );
}


