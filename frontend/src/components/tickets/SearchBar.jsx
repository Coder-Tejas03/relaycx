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
          "absolute left-3.5 flex items-center pointer-events-none transition-colors duration-150",
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
        className={cn(
          "w-full h-9 pl-9 pr-9 rounded-lg bg-[#17171A] border border-white/[0.09]",
          "text-xs text-zinc-100 placeholder:text-zinc-500",
          "focus:outline-none focus:border-zinc-500 focus:ring-1 focus:ring-zinc-600/40",
          "transition-all duration-150"
        )}
      />

      {hasValue && (
        <button
          type="button"
          onClick={() => onChange("")}
          aria-label="Clear search"
          className="absolute right-2.5 p-1 rounded-full text-zinc-500 hover:text-zinc-200 hover:bg-zinc-800 transition-colors cursor-pointer"
        >
          <svg
            className="w-3 h-3"
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
