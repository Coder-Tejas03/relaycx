import React from "react";
import { SearchIcon } from "@animateicons/react/lucide";
import { cn } from "@/lib/utils";

/**
 * Controlled search input component with animated icon and clear button.
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
          "absolute left-3.5 flex items-center pointer-events-none transition-colors duration-200",
          hasValue ? "text-indigo-400 animate-pulse" : "text-zinc-500"
        )}
      >
        <SearchIcon size={18} />
      </div>

      <input
        id="search-tickets-input"
        name="search"
        type="text"
        value={value}
        onChange={(e) => onChange(e.target.value)}
        placeholder={placeholder}
        className={cn(
          "w-full h-10 pl-10 pr-10 rounded-lg bg-zinc-900/80 border border-zinc-800",
          "text-sm text-zinc-100 placeholder:text-zinc-500",
          "focus:outline-none focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500/50",
          "transition-all duration-150"
        )}
      />

      {hasValue && (
        <button
          type="button"
          onClick={() => onChange("")}
          aria-label="Clear search"
          className="absolute right-3 p-1 rounded-full text-zinc-400 hover:text-zinc-200 hover:bg-zinc-800 transition-colors"
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
