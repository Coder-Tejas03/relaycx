import React, { useState, useRef, useEffect } from "react";
import { ChevronDown, Check, Plus, X } from "lucide-react";
import { AnimatePresence, motion } from "motion/react";
import { cn } from "@/lib/utils";

/**
 * Custom-built accessible select component adhering to the RelayCX dark design system.
 * Replaces ugly browser native dropdowns with smooth Vercel/Linear-inspired interactions.
 * 
 * Features:
 * - Smooth slide-down and fold-up animations powered by motion/react
 * - Tactile hover background selectors for all options
 * - Non-form custom addition input preventing outer form submission or page reload
 * - Dynamic addition and removal with semantic red hover background for removal
 * - Keyboard navigation & click-outside dismiss
 */
export default function CustomSelect({
  id,
  options = [],
  value,
  onChange,
  placeholder = "Select an option...",
  allowCustomAdd = false,
  customAddPlaceholder = "Add brand...",
  onAddCustom,
  onRemoveCustom,
  canDelete = () => false,
  disabled = false,
  className,
  size = "default",
  dropdownAlign = "left",
}) {
  const [isOpen, setIsOpen] = useState(false);
  const [isAddingNew, setIsAddingNew] = useState(false);
  const [newOptionText, setNewOptionText] = useState("");
  const containerRef = useRef(null);
  const inputRef = useRef(null);

  // Close popup when clicking outside
  useEffect(() => {
    function handleClickOutside(event) {
      if (containerRef.current && !containerRef.current.contains(event.target)) {
        setIsOpen(false);
        setIsAddingNew(false);
      }
    }
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  // Autofocus input when "Add new" mode opens
  useEffect(() => {
    if (isAddingNew && inputRef.current) {
      inputRef.current.focus();
    }
  }, [isAddingNew]);

  // Normalize options into { value, label, icon } objects
  const normalizedOptions = options.map((opt) => {
    if (typeof opt === "object" && opt !== null) {
      return opt;
    }
    return { value: opt, label: opt };
  });

  const selectedOption = normalizedOptions.find((opt) => opt.value === value);

  const handleSelect = (val) => {
    onChange?.(val);
    setIsOpen(false);
    setIsAddingNew(false);
  };

  const handleAddSubmit = (e) => {
    e?.preventDefault?.();
    e?.stopPropagation?.();
    const trimmed = newOptionText.trim();
    if (!trimmed) return;

    onAddCustom?.(trimmed);
    onChange?.(trimmed);
    setNewOptionText("");
    setIsAddingNew(false);
    setIsOpen(false);
  };

  const handleRemove = (e, optValue) => {
    e?.stopPropagation?.();
    e?.preventDefault?.();
    onRemoveCustom?.(optValue);
  };

  const handleKeyDown = (e) => {
    if (e.key === "Escape") {
      setIsOpen(false);
      setIsAddingNew(false);
    } else if (!isOpen && (e.key === "Enter" || e.key === " " || e.key === "ArrowDown")) {
      e.preventDefault();
      if (!disabled) setIsOpen(true);
    }
  };

  return (
    <div ref={containerRef} className={cn("relative w-full", className)}>
      {/* Trigger Button */}
      <button
        id={id}
        type="button"
        role="combobox"
        aria-expanded={isOpen}
        aria-haspopup="listbox"
        disabled={disabled}
        onClick={() => !disabled && setIsOpen(!isOpen)}
        onKeyDown={handleKeyDown}
        className={cn(
          size === "sm"
            ? "h-8 min-h-0 px-2.5 py-1 text-xs"
            : "h-10 sm:h-9 min-h-[44px] sm:min-h-0 px-3 py-2 text-sm",
          "w-full min-w-0 rounded-lg border border-white/[0.09] bg-[#17171A] text-zinc-100 flex items-center justify-between gap-2 transition-all duration-micro outline-none focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-zinc-400 focus-visible:border-transparent hover:border-white/20 active:scale-[0.99] cursor-pointer select-none",
          disabled && "opacity-40 cursor-not-allowed",
          isOpen && "border-white/25 ring-1 ring-white/10 bg-[#1A1A1E]"
        )}
      >
        <span className="flex items-center gap-2 truncate text-left">
          {selectedOption ? (
            <>
              {selectedOption.icon && (
                <span className="shrink-0 text-zinc-400">{selectedOption.icon}</span>
              )}
              <span className="truncate">{selectedOption.label}</span>
            </>
          ) : (
            <span className="text-zinc-500">{placeholder}</span>
          )}
        </span>

        <ChevronDown
          size={size === "sm" ? 13 : 15}
          className={cn(
            "shrink-0 text-zinc-400 transition-transform duration-ui",
            isOpen && "rotate-180 text-zinc-200"
          )}
        />
      </button>

      {/* Floating Animated Dropdown Menu */}
      <AnimatePresence>
        {isOpen && (
          <motion.div
            role="listbox"
            initial={{ opacity: 0, y: -6, scaleY: 0.95 }}
            animate={{ opacity: 1, y: 0, scaleY: 1 }}
            exit={{ opacity: 0, y: -6, scaleY: 0.95 }}
            transition={{ duration: 0.16, ease: [0.16, 1, 0.3, 1] }}
            style={{ transformOrigin: "top" }}
            className={cn(
              "absolute top-full mt-1.5 z-50 overflow-hidden rounded-xl border border-white/[0.12] bg-[#212124] p-1.5 shadow-2xl shadow-black/60",
              dropdownAlign === "right" ? "right-0 min-w-[210px]" : "left-0 right-0 min-w-[200px]"
            )}
          >
            {/* Specular highlight at top edge */}
            <div className="absolute top-0 left-0 right-0 h-[1px] bg-gradient-to-r from-transparent via-zinc-500/50 to-transparent" />

            <div className="max-h-56 overflow-y-auto space-y-0.5 custom-scrollbar pr-0.5">
              {normalizedOptions.map((opt) => {
                const isSelected = opt.value === value;
                const isDeletable = canDelete(opt.value);

                return (
                  <div
                    key={opt.value}
                    role="option"
                    aria-selected={isSelected}
                    onClick={() => handleSelect(opt.value)}
                    className={cn(
                      "group flex items-center justify-between rounded-lg cursor-pointer transition-all duration-micro select-none border border-transparent",
                      size === "sm" ? "px-2 py-1 text-xs" : "px-2.5 py-1.5 text-xs sm:text-sm",
                      isSelected
                        ? "bg-zinc-800 text-white font-medium border-white/[0.08] shadow-sm"
                        : "text-zinc-300 hover:bg-zinc-800/80 hover:text-white hover:border-white/[0.05] active:bg-zinc-700/60 active:scale-[0.99]"
                    )}
                  >
                    <div className="flex items-center gap-2 truncate min-w-0 flex-1 mr-2">
                      {opt.icon && (
                        <span className={cn("shrink-0", isSelected ? "text-white" : "text-zinc-400 group-hover:text-zinc-200")}>
                          {opt.icon}
                        </span>
                      )}
                      <span className="truncate">{opt.label}</span>
                    </div>

                    <div className="flex items-center gap-1 shrink-0">
                      {isSelected && (
                        <Check size={size === "sm" ? 12 : 14} className="text-zinc-200" />
                      )}

                      {isDeletable && (
                        <button
                          type="button"
                          onClick={(e) => handleRemove(e, opt.value)}
                          title={`Remove "${opt.label}"`}
                          className="p-1 rounded-md text-zinc-500 hover:text-red-400 hover:bg-red-500/20 active:bg-red-500/30 transition-colors duration-micro cursor-pointer"
                        >
                          <X size={13} />
                        </button>
                      )}
                    </div>
                  </div>
                );
              })}
            </div>

            {/* Add Custom Option Section (Non-Form to prevent outer form reload) */}
            {allowCustomAdd && (
              <div className="mt-1 pt-1 border-t border-white/[0.08]">
                {isAddingNew ? (
                  <div className="flex items-center gap-1.5 p-1">
                    <input
                      ref={inputRef}
                      type="text"
                      value={newOptionText}
                      onChange={(e) => setNewOptionText(e.target.value)}
                      onKeyDown={(e) => {
                        if (e.key === "Enter") {
                          e.preventDefault();
                          e.stopPropagation();
                          handleAddSubmit(e);
                        } else if (e.key === "Escape") {
                          e.preventDefault();
                          e.stopPropagation();
                          setIsAddingNew(false);
                        }
                      }}
                      placeholder={customAddPlaceholder}
                      className="flex-1 min-w-0 bg-[#17171A] border border-white/[0.12] rounded-md px-2.5 py-1 text-xs text-white placeholder:text-zinc-500 outline-none focus:border-zinc-400 focus:ring-1 focus:ring-zinc-400/30"
                    />
                    <button
                      type="button"
                      onClick={handleAddSubmit}
                      className="px-2.5 py-1 bg-white hover:bg-zinc-200 text-black text-xs font-semibold rounded-md transition-all duration-micro cursor-pointer select-none shrink-0 active:scale-95 shadow-sm"
                    >
                      Add
                    </button>
                    <button
                      type="button"
                      onClick={(e) => {
                        e.preventDefault();
                        e.stopPropagation();
                        setIsAddingNew(false);
                      }}
                      className="p-1 text-zinc-400 hover:text-zinc-200 rounded-md hover:bg-zinc-800 transition-colors cursor-pointer shrink-0"
                    >
                      <X size={13} />
                    </button>
                  </div>
                ) : (
                  <button
                    type="button"
                    onClick={(e) => {
                      e.preventDefault();
                      e.stopPropagation();
                      setIsAddingNew(true);
                    }}
                    className="w-full flex items-center gap-1.5 px-2.5 py-1.5 text-xs text-zinc-400 hover:text-white hover:bg-zinc-800/80 rounded-lg transition-all duration-micro cursor-pointer select-none text-left active:scale-[0.99]"
                  >
                    <Plus size={13} className="text-zinc-400" />
                    <span>Add new brand...</span>
                  </button>
                )}
              </div>
            )}
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
