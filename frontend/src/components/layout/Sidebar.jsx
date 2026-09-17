import React from "react";
import { useLocation, useNavigate } from "react-router-dom";
import { Inbox, Layers } from "lucide-react";
import { useTicketsContext } from "@/context/TicketContext";
import { cn } from "@/lib/utils";

/**
 * Persistent Vercel-grade navigation sidebar.
 * Anchors the viewport to eliminate empty void space.
 * @param {object} props
 * @param {function(): void} [props.onNavigate] - Optional callback to close mobile drawer on navigation
 */
export function Sidebar({ onNavigate }) {
  const location = useLocation();
  const navigate = useNavigate();
  const { stats, statusFilter, setStatusFilter } = useTicketsContext();

  const isHome = location.pathname === "/";

  const handleInboxClick = (e) => {
    e.preventDefault();
    setStatusFilter("Open");
    if (!isHome) {
      navigate("/");
    }
    if (onNavigate) onNavigate();
  };

  const handleAllTicketsClick = (e) => {
    e.preventDefault();
    setStatusFilter("All");
    if (!isHome) {
      navigate("/");
    }
    if (onNavigate) onNavigate();
  };

  const isInboxActive = isHome && statusFilter === "Open";
  const isAllTicketsActive = isHome && statusFilter !== "Open";

  return (
    <aside className="w-60 shrink-0 h-full border-r border-zinc-800/80 bg-black flex flex-col py-4 px-3 select-none">
      <div className="space-y-6">
        {/* Navigation Group */}
        <div>
          <div className="px-2.5 pb-2 text-[10px] font-mono font-semibold tracking-wider text-zinc-500 uppercase">
            Workspaces
          </div>
          <nav className="space-y-1">
            {/* Inbox Nav Item */}
            <button
              type="button"
              onClick={handleInboxClick}
              title="Open tickets requiring agent attention"
              className={cn(
                "w-full flex items-center justify-between px-2.5 py-2.5 sm:py-2 min-h-[44px] sm:min-h-0 rounded-lg text-xs font-medium transition-all duration-micro cursor-pointer focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-zinc-400 active:scale-[0.99]",
                isInboxActive
                  ? "bg-zinc-900 text-white border border-zinc-800 shadow-sm"
                  : "text-zinc-400 hover:text-zinc-200 hover:bg-zinc-900/60 active:bg-zinc-800"
              )}
            >
              <div className="flex items-center gap-2.5">
                <Inbox size={15} className={isInboxActive ? "text-white" : "text-zinc-400"} />
                <span>Inbox</span>
              </div>
              <span className="font-mono text-[11px] px-1.5 py-0.2 rounded bg-zinc-800 text-zinc-300 border border-zinc-700/50">
                {stats.open}
              </span>
            </button>

            {/* All Tickets Nav Item */}
            <button
              type="button"
              onClick={handleAllTicketsClick}
              title="All tickets in support queue"
              className={cn(
                "w-full flex items-center justify-between px-2.5 py-2.5 sm:py-2 min-h-[44px] sm:min-h-0 rounded-lg text-xs font-medium transition-all duration-micro cursor-pointer focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-zinc-400 active:scale-[0.99]",
                isAllTicketsActive
                  ? "bg-zinc-900 text-white border border-zinc-800 shadow-sm"
                  : "text-zinc-400 hover:text-zinc-200 hover:bg-zinc-900/60 active:bg-zinc-800"
              )}
            >
              <div className="flex items-center gap-2.5">
                <Layers size={15} className={isAllTicketsActive ? "text-white" : "text-zinc-400"} />
                <span>All Tickets</span>
              </div>
              <span className="font-mono text-[11px] px-1.5 py-0.2 rounded bg-zinc-900 text-zinc-400 border border-zinc-800">
                {stats.total}
              </span>
            </button>
          </nav>
        </div>
      </div>
    </aside>
  );
}

export default Sidebar;
