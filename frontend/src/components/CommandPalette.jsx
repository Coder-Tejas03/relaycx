import React, { useState, useEffect, useRef, useMemo } from "react";
import { useLocation, useNavigate } from "react-router-dom";
import { motion, AnimatePresence } from "motion/react";
import {
  Search,
  Plus,
  Inbox,
  Layers,
  FileText,
  Play,
  CheckCircle2,
  RotateCcw,
  CornerDownLeft,
} from "lucide-react";
import { useTicketsContext } from "@/context/TicketContext";
import { cn } from "@/lib/utils";

/**
 * Command Palette (Cmd/Ctrl + K) Modal
 *
 * Lightweight, zero-external-library command center providing keyboard-first navigation
 * and contextual ticket actions.
 *
 * @param {object} props
 * @param {boolean} props.isOpen - Whether palette modal is visible
 * @param {function(): void} props.onClose - Dismiss callback
 */
export function CommandPalette({ isOpen, onClose }) {
  const location = useLocation();
  const navigate = useNavigate();
  const { setStatusFilter } = useTicketsContext();

  const [query, setQuery] = useState("");
  const [selectedIndex, setSelectedIndex] = useState(0);
  const [prevIsOpen, setPrevIsOpen] = useState(isOpen);

  // Automatically reset search query and selection whenever palette is opened
  if (isOpen !== prevIsOpen) {
    setPrevIsOpen(isOpen);
    if (isOpen) {
      setQuery("");
      setSelectedIndex(0);
    }
  }

  const inputRef = useRef(null);
  const listRef = useRef(null);
  const containerRef = useRef(null);

  const isTicketDetail =
    location.pathname.startsWith("/tickets/") && location.pathname !== "/tickets/new";

  // Build commands list based on current route context
  const commands = useMemo(() => {
    const list = [
      {
        id: "create-ticket",
        title: "Create ticket",
        category: "Navigation",
        shortcut: "C",
        icon: Plus,
        action: () => {
          onClose();
          navigate("/tickets/new");
        },
      },
      {
        id: "go-inbox",
        title: "Go to Inbox",
        category: "Navigation",
        icon: Inbox,
        action: () => {
          onClose();
          setStatusFilter("Open");
          if (location.pathname !== "/") {
            navigate("/");
          }
        },
      },
      {
        id: "go-all-tickets",
        title: "Go to All Tickets",
        category: "Navigation",
        icon: Layers,
        action: () => {
          onClose();
          setStatusFilter("All");
          if (location.pathname !== "/") {
            navigate("/");
          }
        },
      },
      {
        id: "focus-search",
        title: "Focus search",
        category: "Navigation",
        shortcut: "/",
        icon: Search,
        action: () => {
          onClose();
          if (location.pathname !== "/") {
            navigate("/");
          }
          setTimeout(() => {
            const searchInput = document.getElementById("search-tickets-input");
            if (searchInput) {
              searchInput.focus();
              searchInput.select?.();
            }
          }, 60);
        },
      },
    ];

    // Contextual ticket-specific commands
    if (isTicketDetail) {
      list.push(
        {
          id: "add-internal-note",
          title: "Add internal note",
          category: "Ticket Actions",
          shortcut: "N",
          icon: FileText,
          action: () => {
            onClose();
            setTimeout(() => {
              const noteInput = document.getElementById("internal-note-input");
              if (noteInput) {
                noteInput.focus();
                noteInput.scrollIntoView({ behavior: "smooth", block: "center" });
              }
            }, 60);
          },
        },
        {
          id: "mark-in-progress",
          title: "Mark In Progress",
          category: "Ticket Actions",
          icon: Play,
          action: () => {
            onClose();
            window.dispatchEvent(
              new CustomEvent("relaycx:ticket-status-change", {
                detail: { status: "In Progress" },
              })
            );
          },
        },
        {
          id: "resolve-ticket",
          title: "Resolve ticket",
          category: "Ticket Actions",
          icon: CheckCircle2,
          action: () => {
            onClose();
            window.dispatchEvent(
              new CustomEvent("relaycx:ticket-status-change", {
                detail: { status: "Closed" },
              })
            );
          },
        },
        {
          id: "reopen-ticket",
          title: "Reopen ticket",
          category: "Ticket Actions",
          icon: RotateCcw,
          action: () => {
            onClose();
            window.dispatchEvent(
              new CustomEvent("relaycx:ticket-status-change", {
                detail: { status: "Open" },
              })
            );
          },
        }
      );
    }

    return list;
  }, [isTicketDetail, location.pathname, navigate, onClose, setStatusFilter]);

  // Filter commands by search query
  const filteredCommands = useMemo(() => {
    const q = query.trim().toLowerCase();
    if (!q) return commands;
    return commands.filter((cmd) => {
      const matchTitle = cmd.title.toLowerCase().includes(q);
      const matchCategory = cmd.category.toLowerCase().includes(q);
      const matchShortcut = cmd.shortcut?.toLowerCase().includes(q);
      return matchTitle || matchCategory || matchShortcut;
    });
  }, [commands, query]);

  // Derive safe active index within bounds of filtered list
  const activeIndex =
    filteredCommands.length === 0
      ? 0
      : Math.min(selectedIndex, filteredCommands.length - 1);

  const handleClose = () => {
    setQuery("");
    setSelectedIndex(0);
    onClose();
  };

  const executeCommand = (command) => {
    handleClose();
    command.action();
  };

  const handleQueryChange = (e) => {
    setQuery(e.target.value);
    setSelectedIndex(0);
  };

  // Autofocus input and prevent background scrolling when opened
  useEffect(() => {
    if (!isOpen) return;

    const timer = setTimeout(() => {
      inputRef.current?.focus();
    }, 30);
    document.body.style.overflow = "hidden";

    return () => {
      clearTimeout(timer);
      document.body.style.overflow = "";
    };
  }, [isOpen]);

  // Scroll active item into view
  useEffect(() => {
    if (!isOpen || !listRef.current) return;
    const activeItem = listRef.current.querySelector(
      `[data-index="${activeIndex}"]`
    );
    if (activeItem) {
      activeItem.scrollIntoView({ block: "nearest" });
    }
  }, [activeIndex, isOpen]);

  // Keyboard navigation inside modal
  const handleKeyDown = (e) => {
    if (e.key === "Escape") {
      e.preventDefault();
      e.stopPropagation();
      handleClose();
      return;
    }

    if (e.key === "ArrowDown") {
      e.preventDefault();
      if (filteredCommands.length > 0) {
        setSelectedIndex((prev) => (prev + 1) % filteredCommands.length);
      }
      return;
    }

    if (e.key === "ArrowUp") {
      e.preventDefault();
      if (filteredCommands.length > 0) {
        setSelectedIndex((prev) =>
          (prev - 1 + filteredCommands.length) % filteredCommands.length
        );
      }
      return;
    }

    if (e.key === "Enter") {
      e.preventDefault();
      if (filteredCommands[activeIndex]) {
        executeCommand(filteredCommands[activeIndex]);
      }
      return;
    }

    // Focus Trap: keep Tab key within modal
    if (e.key === "Tab") {
      e.preventDefault();
      inputRef.current?.focus();
    }
  };

  if (!isOpen) return null;

  return (
    <AnimatePresence>
      <div
        role="dialog"
        aria-modal="true"
        aria-label="Command Palette"
        className="fixed inset-0 z-50 flex items-start justify-center pt-[15vh] px-4"
      >
        {/* Backdrop */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          transition={{ duration: 0.15 }}
          className="fixed inset-0 bg-black/75 backdrop-blur-sm"
          onClick={handleClose}
        />

        {/* Command Palette Card */}
        <motion.div
          ref={containerRef}
          initial={{ opacity: 0, scale: 0.96, y: -8 }}
          animate={{ opacity: 1, scale: 1, y: 0 }}
          exit={{ opacity: 0, scale: 0.96, y: -8 }}
          transition={{ duration: 0.15, ease: "easeOut" }}
          className="relative z-10 w-full max-w-lg rounded-xl border border-white/[0.09] bg-[#212124] shadow-2xl shadow-black/90 overflow-hidden flex flex-col"
          onKeyDown={handleKeyDown}
        >
          {/* Search Header */}
          <div className="relative flex items-center border-b border-white/[0.08] px-3.5 bg-[#1B1B1E]">
            <Search size={16} className="text-zinc-500 shrink-0 mr-2.5" />
            <input
              ref={inputRef}
              type="text"
              value={query}
              onChange={handleQueryChange}
              placeholder="Type a command or search..."
              className="w-full h-12 bg-transparent text-sm text-zinc-100 placeholder:text-zinc-500 focus:outline-none focus:ring-0 selection:bg-zinc-800"
            />
            <button
              type="button"
              onClick={handleClose}
              className="px-1.5 py-0.5 rounded text-[10px] font-mono font-medium text-zinc-400 bg-zinc-800/80 border border-zinc-700/60 hover:text-zinc-200 hover:bg-zinc-700 transition-colors cursor-pointer"
            >
              ESC
            </button>
          </div>

          {/* Commands List */}
          <div
            ref={listRef}
            className="max-h-72 overflow-y-auto p-1.5 space-y-0.5 select-none"
          >
            {filteredCommands.length === 0 ? (
              <div className="py-8 text-center text-xs text-zinc-500">
                No commands found matching &ldquo;{query}&rdquo;
              </div>
            ) : (
              filteredCommands.map((command, idx) => {
                const isSelected = idx === activeIndex;
                const IconComponent = command.icon;
                return (
                  <div
                    key={command.id}
                    data-index={idx}
                    onClick={() => executeCommand(command)}
                    onMouseEnter={() => setSelectedIndex(idx)}
                    className={cn(
                      "flex items-center justify-between px-3 py-2.5 rounded-lg text-xs font-medium cursor-pointer transition-colors duration-micro",
                      isSelected
                        ? "bg-zinc-800 text-white shadow-sm"
                        : "text-zinc-300 hover:bg-zinc-800/60 hover:text-zinc-100"
                    )}
                  >
                    <div className="flex items-center gap-2.5 min-w-0">
                      <IconComponent
                        size={15}
                        className={cn(
                          "shrink-0",
                          isSelected ? "text-white" : "text-zinc-400"
                        )}
                      />
                      <span className="truncate">{command.title}</span>
                    </div>

                    <div className="flex items-center gap-1.5 shrink-0 ml-2">
                      {command.category === "Ticket Actions" && (
                        <span className="text-[10px] font-mono uppercase tracking-wider text-zinc-500 px-1.5 py-0.5 rounded bg-zinc-900/60 border border-zinc-800">
                          Ticket
                        </span>
                      )}
                      {command.shortcut && (
                        <kbd className="font-mono text-[10px] text-zinc-400 bg-zinc-900 px-1.5 py-0.5 rounded border border-zinc-800">
                          {command.shortcut}
                        </kbd>
                      )}
                      {isSelected && (
                        <CornerDownLeft size={12} className="text-zinc-400 ml-1" />
                      )}
                    </div>
                  </div>
                );
              })
            )}
          </div>

          {/* Footer Keyboard Hints */}
          <div className="flex items-center justify-between px-3 py-2 border-t border-white/[0.06] bg-[#17171A] text-[10px] text-zinc-500 font-mono">
            <div className="flex items-center gap-3">
              <span className="flex items-center gap-1">
                <kbd className="px-1 py-0.2 rounded bg-zinc-900 border border-zinc-800 text-zinc-400">
                  ↑
                </kbd>
                <kbd className="px-1 py-0.2 rounded bg-zinc-900 border border-zinc-800 text-zinc-400">
                  ↓
                </kbd>
                <span>Navigate</span>
              </span>
              <span className="flex items-center gap-1">
                <kbd className="px-1 py-0.2 rounded bg-zinc-900 border border-zinc-800 text-zinc-400">
                  ↵
                </kbd>
                <span>Select</span>
              </span>
            </div>
            <span className="flex items-center gap-1">
              <kbd className="px-1 py-0.2 rounded bg-zinc-900 border border-zinc-800 text-zinc-400">
                esc
              </kbd>
              <span>Close</span>
            </span>
          </div>
        </motion.div>
      </div>
    </AnimatePresence>
  );
}

export default CommandPalette;
