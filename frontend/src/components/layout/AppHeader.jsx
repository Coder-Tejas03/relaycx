import React, { useState, useEffect } from "react";
import { Link } from "react-router-dom";
import { SunIcon, MoonIcon } from "@animateicons/react/lucide";
import ShimmerButton from "@/components/magicui/ShimmerButton";

/**
 * Top navigation bar rendered across pages.
 * Displays logo, status indicator, ticket count, theme toggle, and CTA button.
 * @param {object} props
 * @param {number|null} [props.ticketCount] - Optional total count of tickets to display in header
 */
export function AppHeader({ ticketCount = null }) {
  const [theme, setTheme] = useState("dark");

  useEffect(() => {
    const currentTheme = document.documentElement.getAttribute("data-theme") || "dark";
    setTheme(currentTheme);
  }, []);

  const toggleTheme = () => {
    const nextTheme = theme === "dark" ? "light" : "dark";
    setTheme(nextTheme);
    document.documentElement.setAttribute("data-theme", nextTheme);
  };

  return (
    <header className="sticky top-0 z-40 w-full border-b border-zinc-800 bg-zinc-950/80 backdrop-blur-md transition-colors">
      <div className="mx-auto flex h-16 max-w-7xl items-center justify-between px-4 sm:px-6 lg:px-8">
        {/* Left: Logo & Live Ticket Count */}
        <div className="flex items-center gap-3">
          <Link
            to="/"
            className="flex items-center gap-2.5 text-lg font-bold tracking-tight text-white hover:opacity-90 transition-opacity"
          >
            <span className="flex size-8 items-center justify-center rounded-lg bg-indigo-600 text-white font-bold shadow-md shadow-indigo-500/30">
              R
            </span>
            <span>
              Relay<span className="text-indigo-400">CX</span>
            </span>
          </Link>

          <span className="hidden sm:inline-flex rounded-full border border-zinc-700/60 bg-zinc-800/60 px-2 py-0.5 text-xs text-zinc-400">
            v1.0 MVP
          </span>

          {ticketCount !== null && ticketCount !== undefined && (
            <span className="rounded-full border border-indigo-500/30 bg-indigo-500/10 px-2.5 py-0.5 text-xs font-medium text-indigo-300 animate-in fade-in duration-200">
              {ticketCount} {ticketCount === 1 ? "ticket" : "tickets"}
            </span>
          )}
        </div>

        {/* Right: Theme Toggle & Create Ticket CTA */}
        <div className="flex items-center gap-3">
          <button
            type="button"
            onClick={toggleTheme}
            aria-label="Toggle theme"
            className="flex size-9 items-center justify-center rounded-lg border border-zinc-800 bg-zinc-900/80 text-zinc-400 hover:text-zinc-100 hover:bg-zinc-800 transition-all duration-200 cursor-pointer"
          >
            {theme === "dark" ? (
              <SunIcon size={18} className="transition-transform duration-300 hover:rotate-45" />
            ) : (
              <MoonIcon size={18} className="transition-transform duration-300 hover:-rotate-12" />
            )}
          </button>

          <Link to="/tickets/new">
            <ShimmerButton className="h-9 px-3.5 text-xs font-semibold shadow-indigo-500/20">
              + Create Ticket
            </ShimmerButton>
          </Link>
        </div>
      </div>
    </header>
  );
}

export default AppHeader;
