import React from "react";
import { ZapIcon } from "@animateicons/react/lucide";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";

/**
 * Console for writing internal notes with dual action buttons (Add Note / Add Note & Resolve).
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
          className="text-xs font-semibold text-zinc-300"
        >
          Add Internal Note
        </label>
        <Textarea
          id="internal-note-input"
          value={noteText}
          onChange={(e) => onNoteChange(e.target.value)}
          placeholder="Document investigation progress, customer communication, or resolution details..."
          disabled={isSubmitting}
          rows={3}
          className="w-full resize-y min-h-[90px] rounded-xl bg-zinc-900/80 border-zinc-800 text-zinc-100 placeholder:text-zinc-500 focus-visible:ring-indigo-500/40 text-sm"
        />
      </div>

      <div className="flex flex-wrap items-center justify-between gap-3 pt-1">
        <span className="text-[11px] text-zinc-500">
          {currentStatus === "Open"
            ? "💡 Adding a note auto-advances status to 'In Progress'"
            : currentStatus === "Closed"
            ? "🔒 Ticket is closed — Notes logged here are preserved for audit without reopening"
            : "Status remains 'In Progress'"}
        </span>

        <div className="flex items-center gap-2.5 ml-auto">
          {/* Add Note Button */}
          <Button
            type="submit"
            disabled={isDisabled}
            variant="outline"
            size="sm"
            className="border-zinc-700 bg-zinc-800/80 hover:bg-zinc-800 hover:text-white text-zinc-200 text-xs font-medium cursor-pointer"
          >
            {isSubmitting
              ? "Saving..."
              : currentStatus === "Closed"
              ? "Add Audit Note"
              : "Add Note"}
          </Button>

          {/* Add Note & Resolve Button */}
          <Button
            type="button"
            onClick={onAddNoteAndResolve}
            disabled={isDisabled || currentStatus === "Closed"}
            size="sm"
            className="bg-emerald-600 hover:bg-emerald-500 text-white text-xs font-semibold gap-1.5 shadow-sm shadow-emerald-600/30 cursor-pointer disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <ZapIcon size={14} className="text-emerald-100" />
            {isSubmitting ? "Resolving..." : "Add Note & Resolve"}
          </Button>
        </div>
      </div>
    </form>
  );
}
