import React from "react";
import BlurFade from "@/components/magicui/BlurFade";
import SearchBar from "@/components/tickets/SearchBar";
import StatusFilter from "@/components/tickets/StatusFilter";
import TicketTable from "@/components/tickets/TicketTable";
import MetricsRibbon from "@/components/tickets/MetricsRibbon";
import { useTicketsContext } from "@/context/TicketContext";

/**
 * HomePage ("/") renders the operational queue dashboard within AppShell:
 * Top metrics ribbon, search and status filter toolbar, and high-density ticket table.
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
    refresh,
    stats,
  } = useTicketsContext();

  // Silently refresh the queue on mount to ensure fresh state when returning from detail or create pages
  React.useEffect(() => {
    refresh(true);
  }, [refresh]);

  const isFiltered = statusFilter !== "All" || Boolean(searchQuery && searchQuery.trim().length > 0);

  return (
    <div className="p-4 sm:p-6 lg:p-8 space-y-6 max-w-7xl mx-auto">
      {/* Page Heading & Context */}
      <BlurFade delay={0.06}>
        <div className="flex flex-col gap-1 sm:flex-row sm:items-center sm:justify-between">
          <div>
            <h1 className="text-xl sm:text-2xl font-semibold tracking-tight text-white">
              Support Operations Queue
            </h1>
            <p className="text-xs sm:text-sm text-zinc-400 mt-0.5">
              Live customer ticket intake, operational metrics, and triage workbench.
            </p>
          </div>
        </div>
      </BlurFade>

      {/* 4 KPI Cards Ribbon */}
      <BlurFade delay={0.1}>
        <MetricsRibbon
          stats={stats}
          isLoading={isLoading}
          onCardClick={setStatusFilter}
        />
      </BlurFade>

      {/* Controls Bar: Search Bar + Status Filter + Reset Filters */}
      <BlurFade delay={0.14}>
        <div className="flex flex-col sm:flex-row items-stretch sm:items-center justify-between gap-3 p-3 rounded-xl bg-[#212124] border border-white/[0.09] shadow-sm">
          <SearchBar
            value={searchQuery}
            onChange={setSearchQuery}
            placeholder="Search by ticket ID, customer, or subject..."
          />

          <div className="flex items-center justify-start sm:justify-end gap-2.5 overflow-x-auto">
            <StatusFilter
              activeFilter={statusFilter}
              onChange={setStatusFilter}
              counts={stats}
            />

            {isFiltered && (
              <button
                type="button"
                onClick={resetFilters}
                className="px-2.5 py-1.5 rounded-lg text-xs font-medium text-zinc-400 hover:text-white hover:bg-zinc-800 border border-zinc-700/60 transition-all cursor-pointer whitespace-nowrap flex items-center gap-1.5 shrink-0 select-none"
                title="Reset all search and status filters"
              >
                <span>Reset</span>
                <span className="text-[10px] text-zinc-500">✕</span>
              </button>
            )}
          </div>
        </div>
      </BlurFade>

      {/* Ticket Table with skeletons & empty states */}
      <BlurFade delay={0.18}>
        <TicketTable
          tickets={tickets}
          isLoading={isLoading}
          onResetFilters={resetFilters}
          statusFilter={statusFilter}
          searchQuery={searchQuery}
          stats={stats}
        />
      </BlurFade>
    </div>
  );
}
