import React from "react";
import { SearchIcon } from "@animateicons/react/lucide";
import { cn } from "@/lib/utils";

/**
 * Controlled search input component with subtle monochrome focus states.
 * @param {object} props
 * @param {string} props.value - Controlled input text
 * @param {function(string): void} props.onChange - Callback with new search text
 * @param {string} [props.placeholder] - Optional placeholder text
 * @param {string} [props.className] - Optional container class
 */
export default function SearchBar({
  value = "",
  onChange,
  placeholder = "Search tickets by ID, customer, or subject...",
  className,
}) {
  const hasValue = Boolean(value && value.trim().length > 0);

  return (
    <div className={cn("relative flex items-center w-full max-w-md", className)}>
      <div
        className={cn(
          "absolute left-3.5 flex items-center pointer-events-none transition-colors duration-micro",
          hasValue ? "text-zinc-200" : "text-zinc-500"
        )}
      >
        <SearchIcon size={16} />
      </div>

      <input
        id="search-tickets-input"
        name="search"
        type="text"
        value={value}
        onChange={(e) => onChange(e.target.value)}
        placeholder={placeholder}
        title="Search tickets (/)"
        className={cn(
          "w-full h-10 sm:h-9 min-h-[44px] sm:min-h-0 pl-9 pr-9 rounded-lg bg-[#17171A] border border-white/[0.09]",
          "text-sm sm:text-xs text-zinc-100 placeholder:text-zinc-500",
          "focus:outline-none focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-zinc-400 focus-visible:border-transparent",
          "transition-all duration-micro"
        )}
      />

      {hasValue && (
        <button
          type="button"
          onClick={() => onChange("")}
          aria-label="Clear search"
          className="absolute right-1.5 p-2 min-h-[36px] min-w-[36px] flex items-center justify-center rounded-full text-zinc-500 hover:text-zinc-200 hover:bg-zinc-800 active:scale-90 active:bg-zinc-700 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-zinc-400 transition-all duration-micro cursor-pointer"
        >
          <svg
            className="w-3.5 h-3.5"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
            strokeWidth={2.5}
          >
            <path strokeLinecap="round" strokeLinejoin="round" d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>
      )}
    </div>
  );
}
