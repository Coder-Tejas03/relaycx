import React from "react";
import { useLocation, useNavigate } from "react-router-dom";
import { Inbox, Layers, ExternalLink, Terminal } from "lucide-react";
import { useTicketsContext } from "@/context/TicketContext";
import { API_BASE_URL } from "@/constants";
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

  const handleAllQueueClick = (e) => {
    e.preventDefault();
    setStatusFilter("All");
    if (!isHome) {
      navigate("/");
    }
    if (onNavigate) onNavigate();
  };

  const isInboxActive = isHome && statusFilter === "Open";
  const isAllQueueActive = isHome && statusFilter !== "Open";

  return (
    <aside className="w-60 shrink-0 h-full border-r border-zinc-800/80 bg-black flex flex-col justify-between py-4 px-3 select-none">
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
              className={cn(
                "w-full flex items-center justify-between px-2.5 py-2 rounded-lg text-xs font-medium transition-colors cursor-pointer",
                isInboxActive
                  ? "bg-zinc-900 text-white border border-zinc-800 shadow-sm"
                  : "text-zinc-400 hover:text-zinc-200 hover:bg-zinc-900/60"
              )}
            >
              <div className="flex items-center gap-2.5">
                <Inbox size={15} className={isInboxActive ? "text-white" : "text-zinc-400"} />
                <span>Inbox</span>
              </div>
              {stats.open > 0 && (
                <span className="font-mono text-[11px] px-1.5 py-0.2 rounded bg-zinc-800 text-zinc-300 border border-zinc-700/50">
                  {stats.open}
                </span>
              )}
            </button>

            {/* All Queue Nav Item */}
            <button
              type="button"
              onClick={handleAllQueueClick}
              className={cn(
                "w-full flex items-center justify-between px-2.5 py-2 rounded-lg text-xs font-medium transition-colors cursor-pointer",
                isAllQueueActive
                  ? "bg-zinc-900 text-white border border-zinc-800 shadow-sm"
                  : "text-zinc-400 hover:text-zinc-200 hover:bg-zinc-900/60"
              )}
            >
              <div className="flex items-center gap-2.5">
                <Layers size={15} className={isAllQueueActive ? "text-white" : "text-zinc-400"} />
                <span>All Queue</span>
              </div>
              <span className="font-mono text-[11px] px-1.5 py-0.2 rounded bg-zinc-900 text-zinc-500 border border-zinc-800">
                {stats.total}
              </span>
            </button>
          </nav>
        </div>
      </div>

      {/* Bottom Dev & System Section */}
      <div className="pt-4 border-t border-zinc-900 space-y-2">
        <div className="px-2.5 text-[10px] font-mono font-semibold tracking-wider text-zinc-500 uppercase">
          Developer & System
        </div>

        <a
          href={`${API_BASE_URL}/docs`}
          target="_blank"
          rel="noopener noreferrer"
          className="flex items-center justify-between px-2.5 py-1.5 rounded-lg text-xs font-medium text-zinc-400 hover:text-zinc-200 hover:bg-zinc-900/60 transition-colors"
        >
          <div className="flex items-center gap-2">
            <Terminal size={14} className="text-zinc-500" />
            <span>FastAPI Docs</span>
          </div>
          <ExternalLink size={12} className="text-zinc-600" />
        </a>

        <div className="px-2.5 py-2 rounded-lg bg-zinc-950 border border-zinc-900 text-[11px] font-mono text-zinc-500 space-y-1">
          <div className="flex items-center justify-between text-zinc-400">
            <span>Storage</span>
            <span className="text-zinc-300">Turso LibSQL</span>
          </div>
          <div className="flex items-center justify-between text-zinc-500">
            <span>Engine</span>
            <span>FastAPI v0.115</span>
          </div>
        </div>
      </div>
    </aside>
  );
}

export default Sidebar;
