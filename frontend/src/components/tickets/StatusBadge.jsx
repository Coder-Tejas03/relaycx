import React from "react";
import { STATUS_STYLES } from "@/constants";
import { cn } from "@/lib/utils";

/**
 * Renders a color-coded pill badge for a ticket status with subtle monochrome container and semantic dot.
 * @param {object} props
 * @param {"Open" | "In Progress" | "Closed"} props.status - Current status string
 * @param {string} [props.className] - Additional class names
 */
export default function StatusBadge({ status = "Open", className }) {
  const styles = STATUS_STYLES[status] || STATUS_STYLES["Open"];

  return (
    <span
      className={cn(
        "inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-xs font-medium border transition-colors select-none",
        className
      )}
      style={{
        backgroundColor: styles.bg,
        color: styles.text,
        borderColor: styles.border,
      }}
    >
      <span
        className="w-1.5 h-1.5 rounded-full shrink-0"
        style={{ backgroundColor: styles.dot || styles.text }}
      />
      {status}
    </span>
  );
}
