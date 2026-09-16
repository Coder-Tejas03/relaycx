import React from "react";
import { Link } from "react-router-dom";
import ShimmerButton from "@/components/magicui/ShimmerButton";

/**
 * Top navigation bar rendered across pages.
 * Displays logo, status indicator, and primary action button.
 */
export function AppHeader({ ticketCount = null }) {
  return (
    <header className="sticky top-0 z-40 w-full border-b border-[#27272A] bg-[#09090B]/80 backdrop-blur-md">
      <div className="mx-auto flex h-16 max-w-7xl items-center justify-between px-4 sm:px-6 lg:px-8">
        <div className="flex items-center gap-3">
          <Link to="/" className="flex items-center gap-2 text-xl font-bold tracking-tight text-white hover:opacity-90">
            <span className="flex size-8 items-center justify-center rounded-lg bg-indigo-600 text-white shadow-md shadow-indigo-500/30">
              R
            </span>
            <span>Relay<span className="text-indigo-400">CX</span></span>
          </Link>
          <span className="rounded-full border border-zinc-700 bg-zinc-800/60 px-2 py-0.5 text-xs text-zinc-400">
            v1.0 MVP
          </span>
          {ticketCount !== null && (
            <span className="rounded-full border border-indigo-500/20 bg-indigo-500/10 px-2.5 py-0.5 text-xs font-medium text-indigo-300">
              {ticketCount} tickets
            </span>
          )}
        </div>

        <div className="flex items-center gap-3">
          <Link to="/tickets/new">
            <ShimmerButton className="h-9 px-4 text-xs font-semibold">
              + Create Ticket
            </ShimmerButton>
          </Link>
        </div>
      </div>
    </header>
  );
}

export default AppHeader;
