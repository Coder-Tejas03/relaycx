import React from "react";
import { useNavigate } from "react-router-dom";
import StatusBadge from "./StatusBadge";
import { formatRelativeTime } from "@/lib/utils";

/**
 * Single interactive row in the ticket queue table.
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

  return (
    <tr
      onClick={handleRowClick}
      className="group border-b border-zinc-800/60 hover:bg-zinc-800/40 cursor-pointer transition-colors duration-150 select-none"
    >
      {/* Monospace Ticket ID */}
      <td className="py-3.5 px-4 font-mono-id whitespace-nowrap font-medium text-zinc-400 group-hover:text-indigo-400 transition-colors">
        {ticket.ticket_id}
      </td>

      {/* Customer Name & Email (stacked) */}
      <td className="py-3.5 px-4 whitespace-nowrap">
        <div className="flex flex-col">
          <span className="text-sm font-medium text-zinc-200 group-hover:text-white transition-colors">
            {ticket.customer_name}
          </span>
          <span className="text-xs text-zinc-500 font-mono-id">
            {ticket.customer_email}
          </span>
        </div>
      </td>

      {/* Subject */}
      <td className="py-3.5 px-4 max-w-sm md:max-w-md truncate">
        <span className="text-sm text-zinc-300 font-normal">
          {ticket.subject}
        </span>
      </td>

      {/* Status Badge */}
      <td className="py-3.5 px-4 whitespace-nowrap">
        <StatusBadge status={ticket.status} />
      </td>

      {/* Relative Time */}
      <td className="py-3.5 px-4 whitespace-nowrap text-right text-xs font-mono-id text-zinc-500">
        {formatRelativeTime(ticket.created_at)}
      </td>
    </tr>
  );
}
