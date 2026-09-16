import { useTicketsContext } from "@/context/TicketContext";

/**
 * Backward-compatible hook delegating to central TicketContext.
 */
export function useTickets() {
  return useTicketsContext();
}

export default useTickets;
