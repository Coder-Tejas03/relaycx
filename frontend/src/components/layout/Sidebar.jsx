import React from "react";
import { useLocation, useNavigate } from "react-router-dom";
import { Inbox, Layers, PanelLeftClose, PanelLeftOpen } from "lucide-react";
import { useTicketsContext } from "@/context/TicketContext";
import { cn } from "@/lib/utils";

/**
 * Persistent Vercel-grade navigation sidebar.
 * Supports desktop collapsible state (240px expanded <-> 48px collapsed icon-only)
 * with native title tooltips and smooth transitions under 200ms.
 *
 * @param {object} props
 * @param {function(): void} [props.onNavigate] - Optional callback to close mobile drawer on navigation
 * @param {boolean} [props.isCollapsed=false] - Whether desktop sidebar is collapsed to 48px
 * @param {function(): void} [props.onToggleCollapse] - Toggle handler for desktop collapsible state
 */
export function Sidebar({
  onNavigate,
  isCollapsed = false,
  onToggleCollapse,
}) {
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
    <aside
      className={cn(
        "shrink-0 h-full border-r border-zinc-800/80 bg-black flex flex-col justify-between select-none transition-[width,padding] duration-ui ease-in-out overflow-x-hidden",
        isCollapsed ? "w-12 py-4 px-1.5" : "w-60 py-4 px-3"
      )}
    >
      <div className="space-y-6">
        {/* Navigation Group */}
        <div>
          {!isCollapsed && (
            <div className="px-2.5 pb-2 text-[10px] font-mono font-semibold tracking-wider text-zinc-500 uppercase truncate">
              Workspaces
            </div>
          )}

          <nav className="space-y-1">
            {/* Inbox Nav Item */}
            <button
              type="button"
              onClick={handleInboxClick}
              title={isCollapsed ? `Inbox (${stats.open})` : "Open tickets requiring agent attention"}
              aria-label={`Inbox (${stats.open})`}
              className={cn(
                "w-full flex items-center min-h-[44px] sm:min-h-0 rounded-lg text-xs font-medium transition-all duration-micro cursor-pointer focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-zinc-400 active:scale-[0.99]",
                isCollapsed
                  ? "justify-center p-2.5"
                  : "justify-between px-2.5 py-2.5 sm:py-2",
                isInboxActive
                  ? "bg-zinc-900 text-white border border-zinc-800 shadow-sm"
                  : "text-zinc-400 hover:text-zinc-200 hover:bg-zinc-900/60 active:bg-zinc-800"
              )}
            >
              <div className="flex items-center gap-2.5 min-w-0">
                <Inbox
                  size={16}
                  className={cn("shrink-0", isInboxActive ? "text-white" : "text-zinc-400")}
                />
                {!isCollapsed && <span className="truncate">Inbox</span>}
              </div>

              {!isCollapsed && (
                <span className="font-mono text-[11px] px-1.5 py-0.2 rounded bg-zinc-800 text-zinc-300 border border-zinc-700/50 shrink-0">
                  {stats.open}
                </span>
              )}
            </button>

            {/* All Tickets Nav Item */}
            <button
              type="button"
              onClick={handleAllTicketsClick}
              title={isCollapsed ? `All Tickets (${stats.total})` : "All tickets in support queue"}
              aria-label={`All Tickets (${stats.total})`}
              className={cn(
                "w-full flex items-center min-h-[44px] sm:min-h-0 rounded-lg text-xs font-medium transition-all duration-micro cursor-pointer focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-zinc-400 active:scale-[0.99]",
                isCollapsed
                  ? "justify-center p-2.5"
                  : "justify-between px-2.5 py-2.5 sm:py-2",
                isAllTicketsActive
                  ? "bg-zinc-900 text-white border border-zinc-800 shadow-sm"
                  : "text-zinc-400 hover:text-zinc-200 hover:bg-zinc-900/60 active:bg-zinc-800"
              )}
            >
              <div className="flex items-center gap-2.5 min-w-0">
                <Layers
                  size={16}
                  className={cn("shrink-0", isAllTicketsActive ? "text-white" : "text-zinc-400")}
                />
                {!isCollapsed && <span className="truncate">All Tickets</span>}
              </div>

              {!isCollapsed && (
                <span className="font-mono text-[11px] px-1.5 py-0.2 rounded bg-zinc-900 text-zinc-400 border border-zinc-800 shrink-0">
                  {stats.total}
                </span>
              )}
            </button>
          </nav>
        </div>
      </div>

      {/* Desktop Collapse / Expand Toggle Button */}
      {onToggleCollapse && (
        <div className="pt-3 border-t border-zinc-800/80">
          <button
            type="button"
            onClick={onToggleCollapse}
            title={isCollapsed ? "Expand sidebar" : "Collapse sidebar"}
            aria-label={isCollapsed ? "Expand sidebar" : "Collapse sidebar"}
            className={cn(
              "w-full flex items-center rounded-lg text-xs font-medium text-zinc-400 hover:text-zinc-200 hover:bg-zinc-900/60 active:bg-zinc-800 transition-all duration-micro cursor-pointer focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-zinc-400 min-h-[36px]",
              isCollapsed ? "justify-center p-2" : "justify-between px-2.5 py-2"
            )}
          >
            <div className="flex items-center gap-2.5 min-w-0">
              {isCollapsed ? (
                <PanelLeftOpen size={16} className="shrink-0 text-zinc-400 hover:text-white" />
              ) : (
                <>
                  <PanelLeftClose size={16} className="shrink-0 text-zinc-400" />
                  <span className="truncate">Collapse sidebar</span>
                </>
              )}
            </div>
          </button>
        </div>
      )}
    </aside>
  );
}

export default Sidebar;
