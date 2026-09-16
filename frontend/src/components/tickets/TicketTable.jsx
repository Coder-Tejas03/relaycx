import React from "react";
import TicketRow from "./TicketRow";
import { Button } from "@/components/ui/button";

/**
 * Full ticket queue table with shimmer skeleton loading and empty state.
 * @param {object} props
 * @param {Array<object>} props.tickets - List of ticket objects
 * @param {boolean} props.isLoading - Whether tickets are loading
 * @param {function(): void} [props.onResetFilters] - Handler to reset search and status filter
 */
export default function TicketTable({
  tickets = [],
  isLoading = false,
  onResetFilters,
}) {
  return (
    <div className="w-full overflow-hidden rounded-xl border border-zinc-800/80 bg-zinc-900/40 backdrop-blur-sm shadow-xl shadow-black/20">
      <div className="overflow-x-auto">
        <table className="w-full text-left border-collapse">
          <thead>
            <tr className="border-b border-zinc-800/80 bg-zinc-900/60 text-zinc-400 text-xs font-semibold tracking-wider uppercase">
              <th scope="col" className="py-3 px-4 w-32">Ticket ID</th>
              <th scope="col" className="py-3 px-4 w-60">Customer</th>
              <th scope="col" className="py-3 px-4">Subject</th>
              <th scope="col" className="py-3 px-4 w-36">Status</th>
              <th scope="col" className="py-3 px-4 w-28 text-right">Created</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-zinc-800/50">
            {isLoading ? (
              // 4 Shimmer Skeleton Rows matching real row height
              Array.from({ length: 4 }).map((_, idx) => (
                <tr key={`skeleton-${idx}`} className="animate-pulse">
                  <td className="py-4 px-4">
                    <div className="h-4 w-20 bg-zinc-800 rounded" />
                  </td>
                  <td className="py-4 px-4 space-y-2">
                    <div className="h-4 w-28 bg-zinc-800 rounded" />
                    <div className="h-3 w-36 bg-zinc-800/60 rounded" />
                  </td>
                  <td className="py-4 px-4">
                    <div className="h-4 w-4/5 bg-zinc-800 rounded" />
                  </td>
                  <td className="py-4 px-4">
                    <div className="h-5 w-20 bg-zinc-800 rounded-full" />
                  </td>
                  <td className="py-4 px-4 text-right">
                    <div className="h-3 w-14 bg-zinc-800 rounded ml-auto" />
                  </td>
                </tr>
              ))
            ) : tickets.length > 0 ? (
              tickets.map((ticket) => (
                <TicketRow key={ticket.ticket_id} ticket={ticket} />
              ))
            ) : (
              // Empty State
              <tr>
                <td colSpan={5} className="py-16 px-4 text-center">
                  <div className="flex flex-col items-center justify-center space-y-3 max-w-sm mx-auto">
                    <div className="w-12 h-12 rounded-full bg-zinc-800/80 flex items-center justify-center text-zinc-500">
                      <svg
                        className="w-6 h-6"
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
                    <h3 className="text-base font-medium text-zinc-200">
                      No tickets found
                    </h3>
                    <p className="text-xs text-zinc-400 text-center">
                      No customer tickets match your active filter or search query.
                    </p>
                    {onResetFilters && (
                      <Button
                        type="button"
                        variant="outline"
                        size="sm"
                        onClick={onResetFilters}
                        className="mt-2 border-zinc-700 bg-zinc-800/50 hover:bg-zinc-800 text-zinc-200 text-xs"
                      >
                        Reset Filters
                      </Button>
                    )}
                  </div>
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
