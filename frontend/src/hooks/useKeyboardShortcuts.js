import { useEffect } from "react";
import { useLocation, useNavigate } from "react-router-dom";
import { useTicketsContext } from "@/context/TicketContext";

/**
 * Determines whether an element is an interactive text input.
 * Used to avoid intercepting typing in inputs, textareas, selects, or contenteditable nodes.
 * @param {EventTarget | null} target
 * @returns {boolean}
 */
function isTextInput(target) {
  if (!target || !(target instanceof HTMLElement)) return false;
  const tagName = target.tagName;
  return (
    tagName === "INPUT" ||
    tagName === "TEXTAREA" ||
    tagName === "SELECT" ||
    target.isContentEditable
  );
}

/**
 * Global Keyboard Shortcuts Hook
 *
 * Implements the 4 core RelayCX keyboard accelerators:
 * - /         -> Focus search input (queue page, when not in a text input)
 * - C         -> Navigate to Create Ticket (from any page, when not in a text input)
 * - Escape    -> Clear search if active; navigate back if on ticket detail with empty search
 * - N         -> Focus note textarea (ticket detail page only, when not in a text input)
 *
 * Also triggers Command Palette on Cmd/Ctrl + K.
 *
 * @param {object} options
 * @param {function(): void} options.onTogglePalette - Toggle command palette open state
 * @param {boolean} [options.isPaletteOpen] - Whether the command palette is currently open
 */
export function useKeyboardShortcuts({ onTogglePalette, isPaletteOpen = false }) {
  const location = useLocation();
  const navigate = useNavigate();
  const { searchQuery, setSearchQuery } = useTicketsContext();

  useEffect(() => {
    const handleKeyDown = (event) => {
      const isCmdOrCtrl = event.metaKey || event.ctrlKey;
      const key = event.key;

      // 1. Universal Accelerator: Cmd/Ctrl + K (Toggle Command Palette)
      // Enabled from anywhere, even when typing in text fields
      if (isCmdOrCtrl && (key === "k" || key === "K")) {
        event.preventDefault();
        onTogglePalette?.();
        return;
      }

      // If Command Palette is open, let Command Palette handle its own keyboard events
      if (isPaletteOpen) {
        return;
      }

      const activeEl = document.activeElement;
      const isSearchInputFocused = activeEl?.id === "search-tickets-input";

      // 2. Escape handling:
      // Case A: Search input is focused -> clear text or blur
      // Case B: In queue page with active search query (even if blurred) -> clear search
      // Case C: On ticket detail page (when not typing in another input) -> navigate back
      if (key === "Escape") {
        if (isSearchInputFocused) {
          event.preventDefault();
          if (activeEl.value || (searchQuery && searchQuery.trim().length > 0)) {
            setSearchQuery("");
            activeEl.value = "";
          }
          activeEl.blur();
          return;
        }

        // If user is typing in another text input / textarea (e.g. note composer), let Escape do nothing or blur
        if (isTextInput(event.target)) {
          return;
        }

        // If on queue page and there is an active search query, clear it
        if (location.pathname === "/" && searchQuery && searchQuery.trim().length > 0) {
          event.preventDefault();
          setSearchQuery("");
          return;
        }

        // If on ticket detail page, navigate back
        const isTicketDetail =
          location.pathname.startsWith("/tickets/") && location.pathname !== "/tickets/new";
        if (isTicketDetail) {
          event.preventDefault();
          // Dispatch custom event to let TicketDetailPage check for unsaved notes
          const eventHandled = !window.dispatchEvent(
            new CustomEvent("relaycx:navigate-back", { cancelable: true })
          );
          if (!eventHandled) {
            navigate("/");
          }
          return;
        }

        return;
      }

      // All remaining single-key shortcuts MUST NOT fire if the user is in a text input
      if (isTextInput(event.target)) {
        return;
      }

      // Ensure modifier keys are NOT held (avoids conflicts with Cmd+C copy, Cmd+/ comment, etc.)
      if (event.metaKey || event.ctrlKey || event.altKey) {
        return;
      }

      // 3. / -> Focus search input (queue page only)
      if (key === "/") {
        if (location.pathname === "/") {
          event.preventDefault();
          const searchInput = document.getElementById("search-tickets-input");
          if (searchInput) {
            searchInput.focus();
            searchInput.select?.();
          }
        }
        return;
      }

      // 4. C -> Navigate to Create Ticket (from any page)
      if (key === "c" || key === "C") {
        event.preventDefault();
        navigate("/tickets/new");
        return;
      }

      // 5. N -> Focus note textarea (ticket detail page only)
      if (key === "n" || key === "N") {
        const isTicketDetail =
          location.pathname.startsWith("/tickets/") && location.pathname !== "/tickets/new";
        if (isTicketDetail) {
          event.preventDefault();
          const noteInput = document.getElementById("internal-note-input");
          if (noteInput) {
            noteInput.focus();
            noteInput.scrollIntoView({ behavior: "smooth", block: "center" });
          }
        }
        return;
      }
    };

    document.addEventListener("keydown", handleKeyDown);
    return () => {
      document.removeEventListener("keydown", handleKeyDown);
    };
  }, [
    location.pathname,
    navigate,
    searchQuery,
    setSearchQuery,
    onTogglePalette,
    isPaletteOpen,
  ]);
}

export default useKeyboardShortcuts;
