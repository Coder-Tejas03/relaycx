import React, { useState, useEffect } from "react";
import { Link } from "react-router-dom";
import { ticketApi } from "@/services/api";
import StatusBadge from "@/components/tickets/StatusBadge";
import { formatRelativeTime, formatDateTime, cn } from "@/lib/utils";
import { History, ChevronDown, ShieldCheck } from "lucide-react";
import { AnimatePresence, motion } from "motion/react";

/**
 * Customer History Panel.
 * Collapsible audit view displaying prior tickets submitted by the customer
 * strictly scoped to the active client brand, enforcing cross-brand isolation.
 *
 * @param {object} props
 * @param {string} props.clientBrand - Active client brand (e.g. "UrbanFit", "Nova Audio")
 * @param {string} props.customerEmail - Customer email address
 * @param {string} props.currentTicketId - The active ticket ID to exclude from history
 */
export default function CustomerHistoryPanel({
  clientBrand,
  customerEmail,
  currentTicketId,
}) {
  const [isOpen, setIsOpen] = useState(false);
  const [history, setHistory] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    let isMounted = true;

    async function loadCustomerHistory() {
      if (!clientBrand || !customerEmail) {
        setIsLoading(false);
        setHistory([]);
        return;
      }

      setIsLoading(true);
      setError(null);

      try {
        const data = await ticketApi.getCustomerHistory(
          clientBrand,
          customerEmail,
          currentTicketId
        );
        if (isMounted) {
          setHistory(Array.isArray(data) ? data : []);
        }
      } catch (err) {
        if (isMounted) {
          console.error("Failed to load customer history:", err);
          setError(err.message || "Failed to load customer history");
        }
      } finally {
        if (isMounted) {
          setIsLoading(false);
        }
      }
    }

    loadCustomerHistory();

    return () => {
      isMounted = false;
    };
  }, [clientBrand, customerEmail, currentTicketId]);

  const priorCount = history.length;

  return (
    <div className="rounded-xl border border-white/[0.09] bg-[#212124] shadow-xl overflow-hidden">
      {/* Collapsible Panel Header */}
      <button
        type="button"
        aria-expanded={isOpen}
        aria-controls="customer-history-content"
        onClick={() => setIsOpen(!isOpen)}
        className="w-full p-5 flex items-center justify-between gap-3 text-left transition-colors duration-micro hover:bg-white/[0.02] cursor-pointer select-none outline-none focus-visible:ring-2 focus-visible:ring-zinc-400 focus-visible:ring-inset"
      >
        <div className="flex items-center gap-2 min-w-0">
          <History size={14} className="text-zinc-400 shrink-0" />
          <h3 className="text-xs font-mono font-medium uppercase tracking-wider text-zinc-400 truncate">
            Customer History
          </h3>

          {/* Quick Counter Badge */}
          {isLoading ? (
            <span className="inline-block size-3.5 rounded-full bg-zinc-800 animate-pulse shrink-0" />
          ) : (
            <span
              className={cn(
                "text-[10px] font-mono px-2 py-0.5 rounded-full border shrink-0 transition-colors",
                priorCount > 0
                  ? "bg-zinc-800/90 text-zinc-200 border-zinc-700/80 font-medium"
                  : "bg-zinc-900/60 text-zinc-500 border-zinc-800/60"
              )}
            >
              {priorCount === 1 ? "1 prior" : `${priorCount} prior`}
            </span>
          )}
        </div>

        <div className="flex items-center gap-2 shrink-0">
          <span className="text-[11px] text-zinc-500 hidden sm:inline">
            {isOpen ? "Hide" : "Show"}
          </span>
          <ChevronDown
            size={15}
            className={cn(
              "text-zinc-400 transition-transform duration-ui",
              isOpen && "rotate-180 text-zinc-200"
            )}
          />
        </div>
      </button>

      {/* Animated Collapsible Body */}
      <AnimatePresence initial={false}>
        {isOpen && (
          <motion.div
            id="customer-history-content"
            role="region"
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: "auto", opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            transition={{ duration: 0.2, ease: [0.16, 1, 0.3, 1] }}
            className="overflow-hidden border-t border-white/[0.08]"
          >
            <div className="p-5 pt-3.5 space-y-3">
              {isLoading ? (
                // Loading Skeleton Rows
                <div className="space-y-2 animate-pulse">
                  <div className="p-3 bg-[#17171A] rounded-lg border border-white/[0.06] space-y-2">
                    <div className="flex justify-between items-center">
                      <div className="h-3.5 w-24 bg-zinc-800 rounded" />
                      <div className="h-4 w-12 bg-zinc-800 rounded-full" />
                    </div>
                    <div className="h-3 w-4/5 bg-zinc-800/60 rounded" />
                  </div>
                  <div className="p-3 bg-[#17171A] rounded-lg border border-white/[0.06] space-y-2">
                    <div className="flex justify-between items-center">
                      <div className="h-3.5 w-24 bg-zinc-800 rounded" />
                      <div className="h-4 w-12 bg-zinc-800 rounded-full" />
                    </div>
                    <div className="h-3 w-3/5 bg-zinc-800/60 rounded" />
                  </div>
                </div>
              ) : error ? (
                // Error State
                <div className="bg-red-950/30 border border-red-900/40 rounded-lg p-3 text-center space-y-1">
                  <p className="text-xs text-red-300 font-medium">Failed to load history</p>
                  <p className="text-[11px] text-red-400/80">{error}</p>
                </div>
              ) : priorCount === 0 ? (
                // Clean Empty State
                <div className="bg-[#17171A] rounded-lg border border-white/[0.06] p-3.5 text-center space-y-1">
                  <p className="text-xs text-zinc-300 font-medium">No prior tickets</p>
                  <p className="text-[11px] text-zinc-500 leading-relaxed">
                    No prior tickets found for this customer under {clientBrand || "this brand"}.
                  </p>
                </div>
              ) : (
                // List of Prior Tickets
                <div className="space-y-2">
                  {history.map((item) => (
                    <Link
                      key={item.ticket_id}
                      to={`/tickets/${item.ticket_id}`}
                      className="block p-3 rounded-lg bg-[#17171A] border border-white/[0.06] hover:border-white/20 hover:bg-[#1C1C20] transition-all duration-micro group cursor-pointer"
                    >
                      <div className="flex items-center justify-between gap-2 mb-1.5">
                        <div className="flex items-center gap-1.5 min-w-0">
                          <span className="font-mono-id text-xs font-semibold text-zinc-200 group-hover:text-white transition-colors">
                            {item.ticket_id}
                          </span>
                          <span
                            className="text-[10px] font-mono px-1.5 py-0.5 rounded bg-zinc-800 text-zinc-400 border border-zinc-700/60 font-medium shrink-0"
                            title={`Intake Classification: ${item.intake_issue_type || item.issue_type || "GEN"}`}
                          >
                            {item.intake_issue_type || item.issue_type || "GEN"}
                          </span>
                        </div>
                        <StatusBadge status={item.status} className="text-[10px] py-0 px-2 shrink-0" />
                      </div>

                      <p className="text-xs text-zinc-300 group-hover:text-zinc-100 font-medium truncate mb-1.5">
                        {item.subject}
                      </p>

                      <div className="flex items-center justify-between text-[10px] text-zinc-500 font-mono-id">
                        <span title={formatDateTime(item.created_at)}>
                          {formatRelativeTime(item.created_at)}
                        </span>
                        <span className="text-zinc-400 group-hover:text-zinc-200 group-hover:translate-x-0.5 transition-all">
                          View ticket ›
                        </span>
                      </div>
                    </Link>
                  ))}
                </div>
              )}

              {/* Brand Isolation Notice */}
              <div className="flex items-center gap-1.5 pt-1 text-[10px] text-zinc-500 font-mono">
                <ShieldCheck size={11} className="text-zinc-400 shrink-0" />
                <span className="truncate">
                  Isolated to {clientBrand || "active client"} brand domain.
                </span>
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
