import React from "react";
import { ChevronLeft, ChevronRight } from "lucide-react";

/**
 * High-density queue pagination component matching RelayCX design principles.
 * Features crisp active indicators, responsive range counter, keyboard navigation,
 * and safe clamping across edge cases.
 *
 * @param {object} props
 * @param {number} props.currentPage - Current active page (1-based)
 * @param {number} props.totalPages - Total calculated pages
 * @param {number} props.totalRecords - Total matching records count
 * @param {number} [props.pageSize=10] - Number of items per page
 * @param {function(number): void} props.onPageChange - Handler invoked on page switch
 * @param {boolean} [props.isLoading=false] - Whether data is loading
 */
export default function Pagination({
  currentPage = 1,
  totalPages = 1,
  totalRecords = 0,
  pageSize = 10,
  onPageChange,
  isLoading = false,
}) {
  if (totalRecords === 0) {
    return null;
  }

  const safeCurrentPage = Math.min(Math.max(1, currentPage), Math.max(1, totalPages));
  const startRecord = (safeCurrentPage - 1) * pageSize + 1;
  const endRecord = Math.min(safeCurrentPage * pageSize, totalRecords);

  // Compute smart page window with ellipsis for large page lists
  const getPageNumbers = () => {
    if (totalPages <= 7) {
      return Array.from({ length: totalPages }, (_, i) => i + 1);
    }

    if (safeCurrentPage <= 4) {
      return [1, 2, 3, 4, 5, "...", totalPages];
    }

    if (safeCurrentPage >= totalPages - 3) {
      return [1, "...", totalPages - 4, totalPages - 3, totalPages - 2, totalPages - 1, totalPages];
    }

    return [1, "...", safeCurrentPage - 1, safeCurrentPage, safeCurrentPage + 1, "...", totalPages];
  };

  const pages = getPageNumbers();

  const handlePrev = () => {
    if (safeCurrentPage > 1 && !isLoading) {
      onPageChange(safeCurrentPage - 1);
    }
  };

  const handleNext = () => {
    if (safeCurrentPage < totalPages && !isLoading) {
      onPageChange(safeCurrentPage + 1);
    }
  };

  const handlePageClick = (page) => {
    if (page !== "..." && page !== safeCurrentPage && !isLoading) {
      onPageChange(page);
    }
  };

  return (
    <nav
      aria-label="Queue table pagination"
      className="flex flex-col sm:flex-row items-center justify-between gap-3 px-4 py-3 border-t border-white/[0.08] bg-[#1A1A1D]/80 select-none"
    >
      {/* Record Range Counter */}
      <div className="text-xs text-zinc-400 font-normal tracking-tight">
        Showing{" "}
        <span className="font-mono font-medium text-zinc-200">
          {startRecord}–{endRecord}
        </span>{" "}
        of{" "}
        <span className="font-mono font-medium text-zinc-200">
          {totalRecords}
        </span>{" "}
        tickets
      </div>

      {/* Pagination Controls */}
      <div className="flex items-center gap-1.5 sm:gap-1">
        {/* Previous Button */}
        <button
          type="button"
          onClick={handlePrev}
          disabled={safeCurrentPage <= 1 || isLoading}
          aria-label="Previous page"
          className="inline-flex items-center gap-1 px-2.5 py-1.5 rounded-lg text-xs font-medium text-zinc-300 bg-zinc-900/90 border border-zinc-800 hover:text-white hover:bg-zinc-800 active:scale-95 disabled:opacity-30 disabled:pointer-events-none disabled:cursor-not-allowed focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-zinc-400 transition-all duration-micro cursor-pointer shadow-xs"
        >
          <ChevronLeft className="size-3.5 shrink-0" />
          <span className="hidden sm:inline">Prev</span>
        </button>

        {/* Page Number Buttons */}
        <div className="flex items-center gap-1 mx-1">
          {pages.map((page, idx) => {
            if (page === "...") {
              return (
                <span
                  key={`ellipsis-${idx}`}
                  className="px-1.5 py-1 text-xs text-zinc-500 font-mono select-none"
                >
                  …
                </span>
              );
            }

            const isCurrent = page === safeCurrentPage;

            return (
              <button
                key={`page-${page}`}
                type="button"
                onClick={() => handlePageClick(page)}
                disabled={isLoading}
                aria-label={`Page ${page}`}
                aria-current={isCurrent ? "page" : undefined}
                className={`min-w-[28px] h-7 px-2 rounded-lg text-xs font-mono font-medium transition-all duration-micro cursor-pointer flex items-center justify-center focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-zinc-400 active:scale-95 shadow-xs ${
                  isCurrent
                    ? "bg-white text-black font-semibold shadow-sm border border-white"
                    : "text-zinc-400 hover:text-zinc-100 hover:bg-zinc-800/80 border border-transparent"
                }`}
              >
                {page}
              </button>
            );
          })}
        </div>

        {/* Next Button */}
        <button
          type="button"
          onClick={handleNext}
          disabled={safeCurrentPage >= totalPages || isLoading}
          aria-label="Next page"
          className="inline-flex items-center gap-1 px-2.5 py-1.5 rounded-lg text-xs font-medium text-zinc-300 bg-zinc-900/90 border border-zinc-800 hover:text-white hover:bg-zinc-800 active:scale-95 disabled:opacity-30 disabled:pointer-events-none disabled:cursor-not-allowed focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-zinc-400 transition-all duration-micro cursor-pointer shadow-xs"
        >
          <span className="hidden sm:inline">Next</span>
          <ChevronRight className="size-3.5 shrink-0" />
        </button>
      </div>
    </nav>
  );
}
