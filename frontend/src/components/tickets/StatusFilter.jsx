import React from "react";
import { TICKET_STATUSES } from "@/constants";
import { cn } from "@/lib/utils";

const FILTER_OPTIONS = ["All", ...TICKET_STATUSES];

/**
 * Filter pill group for toggling ticket queue status.
 * Styled as a sleek monochrome segmented control.
 * @param {object} props
 * @param {string} props.activeFilter - "All" | "Open" | "In Progress" | "Closed"
 * @param {function(string): void} props.onChange - Callback when filter is clicked
 * @param {string} [props.className] - Optional container class
 */
export default function StatusFilter({
  activeFilter = "All",
  onChange,
  counts,
  className,
}) {
  const getCount = (filter) => {
    if (!counts) return undefined;
    if (counts[filter] !== undefined) return counts[filter];
    if (filter === "All") return counts.total;
    if (filter === "Open") return counts.open;
    if (filter === "In Progress") return counts.inProgress;
    if (filter === "Closed") return counts.closed;
    return undefined;
  };

  return (
    <div className={cn("inline-flex items-center gap-1 p-1 bg-[#17171A] rounded-lg border border-white/[0.09] max-w-full overflow-x-auto", className)}>
      {FILTER_OPTIONS.map((filter) => {
        const isActive = activeFilter === filter;
        const count = getCount(filter);
        return (
          <button
            key={filter}
            type="button"
            onClick={() => onChange(filter)}
            className={cn(
              "px-3 py-2 sm:py-1 min-h-[38px] sm:min-h-0 rounded-md text-xs font-medium transition-all duration-micro cursor-pointer select-none inline-flex items-center gap-1.5 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-zinc-400 active:scale-[0.98]",
              isActive
                ? "bg-zinc-800 text-white shadow-sm border border-zinc-700/60"
                : "text-zinc-400 hover:text-zinc-200 hover:bg-zinc-900/60 active:bg-zinc-900"
            )}
          >
            <span>{filter}</span>
            {count !== undefined && (
              <span
                className={cn(
                  "font-mono text-[11px] transition-colors duration-micro",
                  isActive ? "text-zinc-300" : "text-zinc-500"
                )}
              >
                ({count})
              </span>
            )}
          </button>
        );
      })}
    </div>
  );
}

