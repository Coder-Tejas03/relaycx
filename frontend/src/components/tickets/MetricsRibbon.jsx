import React from "react";
import { Layers, AlertCircle, Clock, CheckCircle2 } from "lucide-react";
import { cn } from "@/lib/utils";

/**
 * Top KPI Metrics Ribbon.
 * Displays real-time operational overview with subtle, aesthetic top-right gradient blooms
 * inspired by the OpenAI Codex dashboard.
 * @param {object} props
 * @param {object} props.stats - { total, open, inProgress, closed, resolutionRate }
 * @param {boolean} [props.isLoading] - Loading state
 * @param {function(string): void} [props.onCardClick] - Callback when clickable KPI card is selected
 */
export default function MetricsRibbon({ stats, isLoading = false, onCardClick }) {
  const cards = [
    {
      title: "Total Volume",
      value: stats.total,
      subtitle: "Total customer inquiries",
      icon: Layers,
      targetFilter: "All",
      isClickable: true,
      tooltip: "Click to show all tickets",
      gradient:
        "radial-gradient(ellipse 130% 100% at 100% 0%, rgba(139, 92, 246, 0.22) 0%, rgba(99, 102, 241, 0.08) 40%, transparent 72%)",
      topLine: "from-transparent via-violet-400/40 to-transparent",
      glowColor: "rgba(139, 92, 246, 0.25)",
      iconColor: "text-violet-400/70 group-hover:text-violet-300",
    },
    {
      title: "Needs Attention",
      value: stats.open,
      subtitle: "Open backlog tickets",
      icon: AlertCircle,
      targetFilter: "Open",
      isClickable: true,
      tooltip: "Click to filter Open tickets",
      gradient:
        "radial-gradient(ellipse 130% 100% at 100% 0%, rgba(59, 130, 246, 0.25) 0%, rgba(14, 165, 233, 0.09) 40%, transparent 72%)",
      topLine: "from-transparent via-blue-400/45 to-transparent",
      glowColor: "rgba(59, 130, 246, 0.28)",
      iconColor: "text-blue-400/70 group-hover:text-blue-300",
    },
    {
      title: "Active Triage",
      value: stats.inProgress,
      subtitle: "In-flight investigations",
      icon: Clock,
      targetFilter: "In Progress",
      isClickable: true,
      tooltip: "Click to filter In Progress tickets",
      gradient:
        "radial-gradient(ellipse 130% 100% at 100% 0%, rgba(245, 158, 11, 0.22) 0%, rgba(234, 88, 12, 0.08) 40%, transparent 72%)",
      topLine: "from-transparent via-amber-400/45 to-transparent",
      glowColor: "rgba(245, 158, 11, 0.25)",
      iconColor: "text-amber-400/70 group-hover:text-amber-300",
    },
    {
      title: "Resolution Rate",
      value: `${stats.resolutionRate}%`,
      subtitle: `${stats.closed} of ${stats.total} resolved`,
      icon: CheckCircle2,
      targetFilter: null,
      isClickable: false,
      tooltip: undefined,
      gradient:
        "radial-gradient(ellipse 130% 100% at 100% 0%, rgba(16, 185, 129, 0.22) 0%, rgba(20, 184, 166, 0.08) 40%, transparent 72%)",
      topLine: "from-transparent via-emerald-400/45 to-transparent",
      glowColor: "rgba(16, 185, 129, 0.25)",
      iconColor: "text-emerald-400/70 group-hover:text-emerald-300",
    },
  ];

  const handleCardAction = (card) => {
    if (card.isClickable && onCardClick && card.targetFilter) {
      onCardClick(card.targetFilter);
    }
  };

  return (
    <div className="grid grid-cols-2 lg:grid-cols-4 gap-3.5">
      {cards.map((card, idx) => {
        const Icon = card.icon;
        return (
          <div
            key={idx}
            role={card.isClickable ? "button" : undefined}
            tabIndex={card.isClickable ? 0 : undefined}
            onClick={() => handleCardAction(card)}
            onKeyDown={(e) => {
              if (card.isClickable && (e.key === "Enter" || e.key === " ")) {
                e.preventDefault();
                handleCardAction(card);
              }
            }}
            title={card.tooltip}
            className={cn(
              "group relative overflow-hidden rounded-xl border border-white/[0.09] bg-[#212124] p-4.5 transition-all duration-200 shadow-sm text-left select-none",
              card.isClickable
                ? "cursor-pointer hover:border-white/[0.25] hover:shadow-lg active:scale-[0.99] focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-zinc-400"
                : "cursor-default"
            )}
          >
            {/* Subtle top edge specular highlight tinted to card theme */}
            <div
              className={cn(
                "absolute top-0 left-0 right-0 h-[1px] bg-gradient-to-r transition-opacity duration-200 opacity-70 group-hover:opacity-100",
                card.topLine
              )}
            />

            {/* Fading color gradient travelling from top-right to left (OpenAI Codex style) */}
            <div
              className="pointer-events-none absolute inset-0 rounded-xl transition-opacity duration-300 opacity-80 group-hover:opacity-100"
              style={{ background: card.gradient }}
            />

            {/* Soft atmospheric ambient blur in the top right corner */}
            <div
              className="pointer-events-none absolute -top-6 -right-6 w-24 h-24 rounded-full blur-2xl transition-all duration-300 opacity-60 group-hover:opacity-90"
              style={{ background: card.glowColor }}
            />

            {/* Card Content */}
            <div className="relative z-10 flex flex-col justify-between h-full">
              <div className="flex items-center justify-between gap-2">
                <span className="text-[11px] font-mono uppercase tracking-wider text-zinc-400 font-medium">
                  {card.title}
                </span>

                {/* Subtle themed icon nestled inside the top-right gradient bloom */}
                <Icon
                  size={15}
                  className={cn("transition-colors duration-200", card.iconColor)}
                />
              </div>

              <div className="mt-3">
                {isLoading ? (
                  <div className="h-7 w-16 bg-zinc-800 animate-pulse rounded my-0.5" />
                ) : (
                  <div className="text-2xl sm:text-3xl font-mono font-semibold tracking-tight text-white">
                    {card.value}
                  </div>
                )}
                <p className="text-xs text-zinc-400 mt-1">
                  {card.subtitle}
                </p>
              </div>
            </div>
          </div>
        );
      })}
    </div>
  );
}

