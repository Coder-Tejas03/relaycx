import React, { useState } from "react";
import { Link } from "react-router-dom";
import { motion, AnimatePresence } from "motion/react";
import TicketRow from "./TicketRow";
import Pagination from "./Pagination";
import { Button } from "@/components/ui/button";

const PAGE_SIZE = 10;

/**
 * Full ticket queue table with shimmer skeleton loading, contextual empty states,
 * and high-performance smooth-animated pagination (10 records per page).
 * @param {object} props
 * @param {Array<object>} props.tickets - List of ticket objects
 * @param {boolean} props.isLoading - Whether tickets are loading
 * @param {function(): void} [props.onResetFilters] - Handler to reset search and status filter
 * @param {string} [props.statusFilter] - Active filter ("All" | "Open" | "In Progress" | "Closed")
 * @param {string} [props.searchQuery] - Active search query
 * @param {object} [props.stats] - Summary stats { total, open, inProgress, closed }
 */
export default function TicketTable({
  tickets = [],
  isLoading = false,
  onResetFilters,
  statusFilter = "All",
  searchQuery = "",
  stats,
}) {
  const [currentPage, setCurrentPage] = useState(() => {
    try {
      const saved = sessionStorage.getItem("relaycx_queue_page");
      const parsed = parseInt(saved, 10);
      return Number.isFinite(parsed) && parsed > 0 ? parsed : 1;
    } catch {
      return 1;
    }
  });

  // Safely adjust page to 1 when filter or search changes (React recommended pattern)
  const [prevFilter, setPrevFilter] = useState({ statusFilter, searchQuery });
  if (prevFilter.statusFilter !== statusFilter || prevFilter.searchQuery !== searchQuery) {
    setPrevFilter({ statusFilter, searchQuery });
    setCurrentPage(1);
    try {
      sessionStorage.setItem("relaycx_queue_page", "1");
    } catch {
      // ignore storage errors
    }
  }

  // Safe page clamping
  const totalRecords = tickets.length;
  const totalPages = Math.max(1, Math.ceil(totalRecords / PAGE_SIZE));
  const safeCurrentPage = Math.min(Math.max(1, currentPage), totalPages);

  const handlePageChange = (newPage) => {
    const clamped = Math.min(Math.max(1, newPage), totalPages);
    setCurrentPage(clamped);
    try {
      sessionStorage.setItem("relaycx_queue_page", String(clamped));
    } catch {
      // ignore storage errors
    }
  };

  // Slice active page records (max 10 DOM elements rendered)
  const startIndex = (safeCurrentPage - 1) * PAGE_SIZE;
  const endIndex = Math.min(startIndex + PAGE_SIZE, totalRecords);
  const paginatedTickets = tickets.slice(startIndex, endIndex);

  const getEmptyStateContent = () => {
    const totalCount = stats?.total ?? 0;
    const isSearchActive = Boolean(searchQuery && searchQuery.trim().length > 0);
    const isFilterActive = statusFilter && statusFilter !== "All";

    // Scenario 1: Zero tickets exist at all in the system
    if (totalCount === 0 && !isSearchActive) {
      return {
        title: "No tickets yet",
        description: "Customer issues will appear here.",
        action: (
          <Link
            to="/tickets/new"
            className="inline-flex items-center justify-center min-h-[44px] sm:min-h-0 h-10 sm:h-8 px-3.5 rounded-md bg-white hover:bg-zinc-200 text-black text-xs font-medium transition-all duration-micro cursor-pointer select-none shadow-sm mt-2 active:scale-[0.98] focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-zinc-400 focus-visible:ring-offset-2 focus-visible:ring-offset-black"
          >
            Create Ticket
          </Link>
        ),
      };
    }

    // Scenario 2: Search active and yielded zero results
    if (isSearchActive) {
      return {
        title: "No tickets match search",
        description: `No tickets match "${searchQuery.trim()}". Try a different search.`,
        action: onResetFilters ? (
          <Button
            type="button"
            variant="outline"
            size="sm"
            onClick={onResetFilters}
            className="mt-2 min-h-[44px] sm:min-h-0 border-zinc-700/80 bg-zinc-900 hover:bg-zinc-800 text-zinc-300 hover:text-white text-xs cursor-pointer"
          >
            Clear Search
          </Button>
        ) : null,
      };
    }

    // Scenario 3: Filter is "Open" and zero open tickets exist
    if (statusFilter === "Open") {
      return {
        title: "You're all caught up",
        description: "No open tickets need attention.",
        action: onResetFilters ? (
          <Button
            type="button"
            variant="outline"
            size="sm"
            onClick={onResetFilters}
            className="mt-2 min-h-[44px] sm:min-h-0 border-zinc-700/80 bg-zinc-900 hover:bg-zinc-800 text-zinc-300 hover:text-white text-xs cursor-pointer"
          >
            View All Tickets
          </Button>
        ) : null,
      };
    }

    // Scenario 4: Specific status filter active with no matching tickets
    if (isFilterActive) {
      return {
        title: `No ${statusFilter.toLowerCase()} tickets`,
        description: `No ${statusFilter.toLowerCase()} tickets need attention.`,
        action: onResetFilters ? (
          <Button
            type="button"
            variant="outline"
            size="sm"
            onClick={onResetFilters}
            className="mt-2 min-h-[44px] sm:min-h-0 border-zinc-700/80 bg-zinc-900 hover:bg-zinc-800 text-zinc-300 hover:text-white text-xs cursor-pointer"
          >
            View All Tickets
          </Button>
        ) : null,
      };
    }

    // Fallback: General no-match criteria
    return {
      title: "No tickets match criteria",
      description: "No customer tickets match your active filter or search query.",
      action: onResetFilters ? (
        <Button
          type="button"
          variant="outline"
          size="sm"
          onClick={onResetFilters}
          className="mt-2 min-h-[44px] sm:min-h-0 border-zinc-700/80 bg-zinc-900 hover:bg-zinc-800 text-zinc-300 hover:text-white text-xs cursor-pointer"
        >
          Reset Filters
        </Button>
      ) : null,
    };
  };

  const emptyState = getEmptyStateContent();

  return (
    <div className="w-full overflow-hidden rounded-xl border border-white/[0.09] bg-[#212124] shadow-xl shadow-black/30">
      <div className="overflow-x-auto">
        <table className="w-full text-left border-collapse">
          <thead>
            <tr className="border-b border-white/[0.09] bg-[#1A1A1D] text-zinc-400 text-[11px] font-mono font-medium tracking-wider uppercase">
              <th scope="col" className="py-2.5 px-4 w-32">Ticket ID</th>
              <th scope="col" className="py-2.5 px-4 w-60">Customer</th>
              <th scope="col" className="py-2.5 px-4">Subject</th>
              <th scope="col" className="py-2.5 px-4 w-36">Status</th>
              <th scope="col" className="py-2.5 px-4 w-32 text-right">Updated</th>
            </tr>
          </thead>
          <AnimatePresence mode="wait" initial={false}>
            {isLoading ? (
              <motion.tbody
                key="skeleton"
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                exit={{ opacity: 0 }}
                transition={{ duration: 0.12 }}
                className="divide-y divide-white/[0.06]"
              >
                {/* 4 Shimmer Skeleton Rows matching real row height */}
                {Array.from({ length: 4 }).map((_, idx) => (
                  <tr key={`skeleton-${idx}`} className="animate-pulse">
                    <td className="py-3 px-4">
                      <div className="h-3.5 w-20 bg-zinc-800 rounded" />
                    </td>
                    <td className="py-3 px-4">
                      <div className="flex items-center gap-2.5">
                        <div className="size-6 rounded-full bg-zinc-800 shrink-0" />
                        <div className="space-y-1.5">
                          <div className="h-3.5 w-24 bg-zinc-800 rounded" />
                          <div className="h-2.5 w-32 bg-zinc-800/60 rounded" />
                        </div>
                      </div>
                    </td>
                    <td className="py-3 px-4">
                      <div className="h-3.5 w-4/5 bg-zinc-800 rounded" />
                    </td>
                    <td className="py-3 px-4">
                      <div className="h-4.5 w-20 bg-zinc-800 rounded-full" />
                    </td>
                    <td className="py-3 px-4 text-right">
                      <div className="h-3 w-14 bg-zinc-800 rounded ml-auto" />
                    </td>
                  </tr>
                ))}
              </motion.tbody>
            ) : paginatedTickets.length > 0 ? (
              <motion.tbody
                key={`page-${safeCurrentPage}`}
                initial={{ opacity: 0, y: 3 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -3 }}
                transition={{ duration: 0.15, ease: "easeOut" }}
                className="divide-y divide-white/[0.06]"
              >
                {paginatedTickets.map((ticket) => (
                  <TicketRow key={ticket.ticket_id} ticket={ticket} />
                ))}
              </motion.tbody>
            ) : (
              // Context-Aware Empty State
              <motion.tbody
                key="empty"
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                exit={{ opacity: 0 }}
                transition={{ duration: 0.12 }}
              >
                <tr>
                  <td colSpan={5} className="py-16 px-4 text-center">
                    <div className="flex flex-col items-center justify-center space-y-3 max-w-sm mx-auto">
                      <div className="size-10 rounded-full bg-zinc-900 border border-zinc-800 flex items-center justify-center text-zinc-500">
                        <svg
                          className="w-5 h-5"
                          fill="none"
                          viewBox="0 0 24 24"
                          stroke="currentColor"
                          strokeWidth={1.5}
                        >
                          <path
                            strokeLinecap="round"
                            strokeLinejoin="round"
                            d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
                          />
                        </svg>
                      </div>
                      <h3 className="text-sm font-medium text-zinc-200">
                        {emptyState.title}
                      </h3>
                      <p className="text-xs text-zinc-500 text-center">
                        {emptyState.description}
                      </p>
                      {emptyState.action}
                    </div>
                  </td>
                </tr>
              </motion.tbody>
            )}
          </AnimatePresence>
        </table>
      </div>

      {/* Pagination Footer */}
      {!isLoading && totalRecords > 0 && (
        <Pagination
          currentPage={safeCurrentPage}
          totalPages={totalPages}
          totalRecords={totalRecords}
          pageSize={PAGE_SIZE}
          onPageChange={handlePageChange}
          isLoading={isLoading}
        />
      )}
    </div>
  );
}

