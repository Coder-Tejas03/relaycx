import React from "react";
import { Link } from "react-router-dom";
import { Plus, Menu, X } from "lucide-react";

/**
 * Top navigation bar rendered within AppShell.
 * Ultra-clean, distraction-free monochrome header with logo and primary CTA.
 * @param {object} props
 * @param {boolean} [props.mobileMenuOpen] - State of mobile sidebar
 * @param {function(): void} [props.onToggleMobileMenu] - Toggle handler for mobile sidebar
 */
export function AppHeader({ mobileMenuOpen = false, onToggleMobileMenu }) {
  return (
    <header className="sticky top-0 z-40 w-full h-14 border-b border-zinc-800/80 bg-black/90 backdrop-blur-md transition-colors">
      <div className="flex h-full w-full items-center justify-between px-4 sm:px-6">
        {/* Left: Mobile menu toggle + Clean Logo */}
        <div className="flex items-center gap-3">
          {onToggleMobileMenu && (
            <button
              type="button"
              onClick={onToggleMobileMenu}
              aria-label="Toggle navigation menu"
              className="flex md:hidden min-h-[44px] min-w-[44px] items-center justify-center rounded-md border border-zinc-800 bg-zinc-900/60 text-zinc-400 hover:text-white hover:bg-zinc-800 active:scale-95 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-zinc-400 transition-all duration-micro cursor-pointer"
            >
              {mobileMenuOpen ? <X size={18} /> : <Menu size={18} />}
            </button>
          )}

          <Link
            to="/"
            className="flex items-center gap-2.5 text-sm font-semibold tracking-tight text-white hover:opacity-90 active:scale-[0.99] focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-zinc-400 rounded-md p-0.5 transition-all duration-micro"
          >
            {/* Vercel-style monochrome [R] block */}
            <span className="flex size-6 items-center justify-center rounded-md bg-zinc-900 border border-zinc-800 text-xs font-mono font-bold text-zinc-100 shadow-sm">
              R
            </span>
            <span>RelayCX</span>
          </Link>
        </div>

        {/* Right: Focused Primary CTA */}
        <div className="flex items-center gap-3">
          <Link
            to="/tickets/new"
            className="inline-flex items-center justify-center gap-1.5 min-h-[44px] sm:min-h-0 h-10 sm:h-8 px-3.5 rounded-md bg-white hover:bg-zinc-200 text-black text-xs font-medium transition-all duration-micro select-none shadow-sm cursor-pointer shrink-0 active:scale-[0.98] focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-zinc-400 focus-visible:ring-offset-2 focus-visible:ring-offset-black"
          >
            <Plus size={14} strokeWidth={2.5} />
            <span>Create Ticket</span>
          </Link>
        </div>
      </div>
    </header>
  );
}

export default AppHeader;
