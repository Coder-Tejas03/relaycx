import React from "react";
import AppHeader from "@/components/layout/AppHeader";
import BlurFade from "@/components/magicui/BlurFade";
import SearchBar from "@/components/tickets/SearchBar";
import StatusFilter from "@/components/tickets/StatusFilter";
import TicketTable from "@/components/tickets/TicketTable";
import { useTickets } from "@/hooks/useTickets";

/**
 * HomePage ("/") renders the core support queue dashboard with live search,
 * status filtering, shimmer loading states, and instant navigation to ticket details.
 */
export default function HomePage() {
  const {
    tickets,
    isLoading,
    searchQuery,
    setSearchQuery,
    statusFilter,
    setStatusFilter,
    resetFilters,
  } = useTickets();

  const isFiltered = statusFilter !== "All" || Boolean(searchQuery && searchQuery.trim().length > 0);

  return (
    <div className="min-h-screen bg-[var(--bg-base)] text-zinc-100 antialiased selection:bg-indigo-500/30 selection:text-indigo-200">
      <AppHeader ticketCount={isLoading ? null : tickets.length} />

      <main className="mx-auto max-w-7xl px-4 py-8 sm:px-6 lg:px-8 space-y-6">
        <BlurFade delay={0.08}>
          <div className="flex flex-col gap-1 sm:flex-row sm:items-center sm:justify-between">
            <div>
              <h1 className="text-2xl sm:text-3xl font-bold tracking-tight text-white">
                Ticket Queue
              </h1>
              <p className="text-xs sm:text-sm text-zinc-400 mt-1">
                Live monitoring, search, and resolution pipeline for customer inquiries.
              </p>
            </div>
          </div>
        </BlurFade>

        {/* Controls Bar: Search Bar + Status Filter + Reset Filters */}
        <BlurFade delay={0.14}>
          <div className="flex flex-col sm:flex-row items-stretch sm:items-center justify-between gap-3.5 p-3 rounded-2xl bg-zinc-900/40 border border-zinc-800/80 backdrop-blur-sm">
            <SearchBar
              value={searchQuery}
              onChange={setSearchQuery}
              placeholder="Search by ticket ID, customer name, email, or subject..."
            />

            <div className="flex items-center justify-start sm:justify-end gap-2.5 overflow-x-auto">
              <StatusFilter
                activeFilter={statusFilter}
                onChange={setStatusFilter}
              />

              {isFiltered && (
                <button
                  type="button"
                  onClick={resetFilters}
                  className="px-2.5 py-1.5 rounded-lg text-xs font-medium text-zinc-400 hover:text-indigo-400 hover:bg-zinc-800/60 border border-zinc-800 transition-all cursor-pointer whitespace-nowrap flex items-center gap-1.5 shrink-0 select-none animate-in fade-in duration-150"
                  title="Reset all search and status filters"
                >
                  <span>Reset Filters</span>
                  <span className="text-[10px] text-zinc-500">✕</span>
                </button>
              )}
            </div>
          </div>
        </BlurFade>

        {/* Ticket Table with skeletons & empty states */}
        <BlurFade delay={0.2}>
          <TicketTable
            tickets={tickets}
            isLoading={isLoading}
            onResetFilters={resetFilters}
          />
        </BlurFade>
      </main>
    </div>
  );
}
