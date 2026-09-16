import React from "react";
import { useNavigate } from "react-router-dom";
import StatusBadge from "./StatusBadge";
import { formatRelativeTime } from "@/lib/utils";

/**
 * Single interactive row in the ticket queue table.
 * Dense, scannable layout with customer avatar initials, monospace IDs, and zero visual clutter.
 * @param {object} props
 * @param {object} props.ticket - Ticket summary object
 */
export default function TicketRow({ ticket }) {
  const navigate = useNavigate();

  const handleRowClick = () => {
    if (ticket?.ticket_id) {
      navigate(`/tickets/${ticket.ticket_id}`);
    }
  };

  const initials = (ticket.customer_name || "??")
    .trim()
    .split(/\s+/)
    .map((part) => part[0])
    .join("")
    .slice(0, 2)
    .toUpperCase();

  return (
    <tr
      onClick={handleRowClick}
      className="group border-b border-zinc-800/60 hover:bg-zinc-900/60 cursor-pointer transition-colors duration-150 select-none"
    >
      {/* Monospace Ticket ID */}
      <td className="py-3 px-4 font-mono-id whitespace-nowrap font-medium text-zinc-400 group-hover:text-zinc-100 transition-colors">
        {ticket.ticket_id}
      </td>

      {/* Customer Avatar + Name & Email */}
      <td className="py-3 px-4 whitespace-nowrap">
        <div className="flex items-center gap-2.5">
          <div className="size-6 rounded-full bg-zinc-900 border border-zinc-700/80 flex items-center justify-center text-[10px] font-mono font-medium text-zinc-300 shrink-0">
            {initials}
          </div>
          <div className="flex flex-col min-w-0">
            <span className="text-sm font-medium text-zinc-200 group-hover:text-white transition-colors truncate max-w-[160px]">
              {ticket.customer_name}
            </span>
            <span className="text-xs text-zinc-500 font-mono-id truncate max-w-[160px]">
              {ticket.customer_email}
            </span>
          </div>
        </div>
      </td>

      {/* Subject */}
      <td className="py-3 px-4 max-w-sm md:max-w-md truncate">
        <span className="text-sm text-zinc-300 font-normal group-hover:text-zinc-100 transition-colors">
          {ticket.subject}
        </span>
      </td>

      {/* Status Badge */}
      <td className="py-3 px-4 whitespace-nowrap">
        <StatusBadge status={ticket.status} />
      </td>

      {/* Relative Time */}
      <td className="py-3 px-4 whitespace-nowrap text-right text-xs font-mono-id text-zinc-500">
        {formatRelativeTime(ticket.created_at)}
      </td>
    </tr>
  );
}
