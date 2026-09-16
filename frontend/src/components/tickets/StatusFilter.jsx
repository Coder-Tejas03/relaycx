import React from "react";
import { TICKET_STATUSES } from "@/constants";
import { cn } from "@/lib/utils";

const FILTER_OPTIONS = ["All", ...TICKET_STATUSES];

/**
 * Filter pill group for toggling ticket queue status.
 * @param {object} props
 * @param {string} props.activeFilter - "All" | "Open" | "In Progress" | "Closed"
 * @param {function(string): void} props.onChange - Callback when filter is clicked
 * @param {string} [props.className] - Optional container class
 */
export default function StatusFilter({
  activeFilter = "All",
  onChange,
  className,
}) {
  return (
    <div className={cn("inline-flex items-center gap-1.5 p-1 bg-zinc-900/60 rounded-xl border border-zinc-800/80", className)}>
      {FILTER_OPTIONS.map((filter) => {
        const isActive = activeFilter === filter;
        return (
          <button
            key={filter}
            type="button"
            onClick={() => onChange(filter)}
            className={cn(
              "px-3.5 py-1.5 rounded-lg text-xs font-medium transition-all duration-150 cursor-pointer select-none",
              isActive
                ? "bg-indigo-600 text-white shadow-sm shadow-indigo-600/30"
                : "text-zinc-400 hover:text-zinc-200 hover:bg-zinc-800/60"
            )}
          >
            {filter}
          </button>
        );
      })}
    </div>
  );
}
