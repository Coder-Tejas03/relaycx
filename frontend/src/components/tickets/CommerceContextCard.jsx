import React, { useState, useEffect } from "react";
import { customerApi } from "@/services/api";
import { cn } from "@/lib/utils";
import { toast } from "sonner";
import {
  ShoppingBag,
  Truck,
  Copy,
  Check,
  AlertTriangle,
  CreditCard,
  Crown,
  Server,
  Activity,
  CheckCircle2,
  Clock,
  Info,
} from "lucide-react";

/**
 * The Relevant Operational Context Card.
 * Renders customer's live order, fulfillment tracking, and VIP tier (or developer API metrics)
 * strictly scoped to (client_brand, customer_email) and filtered by issue family relevance rules.
 */
export default function CommerceContextCard({ customerEmail, customerName, clientBrand, issueType }) {
  const [data, setData] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);
  const [copiedTracking, setCopiedTracking] = useState(false);
  const [copiedOrderId, setCopiedOrderId] = useState(false);

  useEffect(() => {
    let isMounted = true;

    async function loadRelevantContext() {
      if (!customerEmail || !clientBrand) {
        setIsLoading(false);
        setData(null);
        return;
      }

      setIsLoading(true);
      setError(null);

      try {
        const result = await customerApi.getRelevantContext(clientBrand, customerEmail, issueType);
        if (isMounted) {
          setData(result);
        }
      } catch (err) {
        if (isMounted) {
          console.error("Failed to load relevant context:", err);
          setError(err.message || "Failed to load relevant context");
        }
      } finally {
        if (isMounted) {
          setIsLoading(false);
        }
      }
    }

    loadRelevantContext();

    return () => {
      isMounted = false;
    };
  }, [clientBrand, customerEmail, issueType]);

  const handleCopyTracking = () => {
    if (data?.tracking_number) {
      navigator.clipboard.writeText(data.tracking_number);
      setCopiedTracking(true);
      toast.success("Tracking identifier copied");
      setTimeout(() => setCopiedTracking(false), 2000);
    }
  };

  const handleCopyOrderId = () => {
    if (data?.order_id) {
      navigator.clipboard.writeText(data.order_id);
      setCopiedOrderId(true);
      toast.success("Order ID copied");
      setTimeout(() => setCopiedOrderId(false), 2000);
    }
  };

  // 1. Loading Skeleton State
  if (isLoading) {
    return (
      <div className="rounded-xl border border-white/[0.09] bg-[#212124] p-5 shadow-xl space-y-3.5">
        <div className="flex items-center justify-between border-b border-white/[0.08] pb-2.5">
          <div className="h-3 w-32 bg-zinc-800 rounded animate-pulse" />
          <div className="h-4 w-12 bg-zinc-800 rounded-full animate-pulse" />
        </div>
        <div className="space-y-2">
          <div className="h-4 w-3/4 bg-zinc-800/80 rounded animate-pulse" />
          <div className="h-3 w-1/2 bg-zinc-800/60 rounded animate-pulse" />
        </div>
        <div className="p-3 bg-[#17171A] rounded-lg border border-white/[0.06] space-y-2">
          <div className="h-3.5 w-2/3 bg-zinc-800 rounded animate-pulse" />
          <div className="h-3 w-4/5 bg-zinc-800/50 rounded animate-pulse" />
        </div>
        <div className="flex justify-between items-center pt-1">
          <div className="h-3 w-20 bg-zinc-800 rounded animate-pulse" />
          <div className="h-3 w-24 bg-zinc-800 rounded animate-pulse" />
        </div>
      </div>
    );
  }

  // 2. Empty / No Records State (e.g. unknown customer or irrelevant domain for this issue type)
  if (!data) {
    return (
      <div className="rounded-xl border border-white/[0.09] bg-[#212124] p-5 shadow-xl space-y-3">
        <div className="flex items-center justify-between border-b border-white/[0.08] pb-2.5">
          <div className="flex items-center gap-1.5">
            <Info size={13} className="text-zinc-400" />
            <h3 className="text-xs font-mono font-medium uppercase tracking-wider text-zinc-400">
              Relevant Context
            </h3>
          </div>
          <span className="text-[10px] font-mono text-zinc-500 bg-zinc-800/60 px-2 py-0.5 rounded border border-zinc-700/40">
            {issueType ? `${issueType} Domain` : "Client Scoped"}
          </span>
        </div>

        <div className="bg-[#17171A] rounded-lg border border-white/[0.06] p-3 text-center space-y-1">
          <p className="text-xs text-zinc-300 font-medium">
            No relevant context for this issue type
          </p>
          <p className="text-[11px] text-zinc-500 leading-relaxed">
            Customer history is available in the panel below.
          </p>
        </div>
        <p className="text-[10px] text-zinc-500 leading-tight">
          System queried operational context scoped to {clientBrand || "client"} and issue relevance rules.
        </p>
      </div>
    );
  }

  // Determine status color accents
  const isDevAccount = data.account_type === "developer";
  const statusLower = (data.shipping_status || "").toLowerCase();

  let statusBadgeColor = "bg-zinc-800 text-zinc-300 border-zinc-700";
  let StatusIcon = Clock;

  if (statusLower.includes("delivered")) {
    statusBadgeColor = "bg-emerald-950/60 text-emerald-300 border-emerald-800/70";
    StatusIcon = CheckCircle2;
  } else if (statusLower.includes("transit")) {
    statusBadgeColor = "bg-blue-950/60 text-blue-300 border-blue-800/70";
    StatusIcon = Truck;
  } else if (statusLower.includes("pending") || statusLower.includes("sync") || statusLower.includes("throttled") || statusLower.includes("rate limit")) {
    statusBadgeColor = "bg-amber-950/60 text-amber-300 border-amber-800/70";
    StatusIcon = AlertTriangle;
  }

  // 3. Technical / Developer API Account (Dev Malhotra)
  if (isDevAccount) {
    return (
      <div className="rounded-xl border border-white/[0.09] bg-[#212124] p-5 shadow-xl space-y-3.5">
        {/* Card Header */}
        <div className="flex items-center justify-between border-b border-white/[0.08] pb-2.5">
          <div className="flex items-center gap-1.5">
            <Server size={14} className="text-cyan-400" />
            <h3 className="text-xs font-mono font-medium uppercase tracking-wider text-zinc-300">
              Relevant Context
            </h3>
          </div>
          <span className="text-[10px] font-mono text-cyan-300 bg-cyan-950/60 px-2 py-0.5 rounded border border-cyan-800/60">
            Developer Account
          </span>
        </div>

        {/* Subscription & Plan */}
        <div className="space-y-1">
          <div className="flex items-center justify-between">
            <button
              type="button"
              onClick={handleCopyOrderId}
              className="group inline-flex items-center gap-1 font-mono-id text-xs text-zinc-200 hover:text-white cursor-pointer transition-colors"
              title="Copy Subscription ID"
            >
              <span className="font-semibold text-zinc-100">{data.order_id}</span>
              {copiedOrderId ? (
                <Check size={11} className="text-emerald-400" />
              ) : (
                <Copy size={11} className="text-zinc-500 group-hover:text-zinc-300" />
              )}
            </button>
            <span className="text-xs font-semibold text-emerald-400 font-mono-id">
              {data.total_amount}
            </span>
          </div>
          <p className="text-xs text-zinc-200 font-medium">
            {data.item_name}
          </p>
        </div>

        {/* Technical Status & Operational Alert */}
        <div className="bg-[#17171A] rounded-lg border border-white/[0.08] p-3 space-y-2">
          <div className="flex items-center justify-between">
            <span className="text-[11px] text-zinc-400 font-medium flex items-center gap-1.5">
              <Activity size={12} className="text-amber-400" />
              Ingress Status
            </span>
            <span className={cn("text-[10px] px-2 py-0.5 rounded-full border font-medium", statusBadgeColor)}>
              {data.shipping_status}
            </span>
          </div>

          {data.dispute_reason && (
            <p className="text-[11px] text-amber-200/90 bg-amber-950/30 border border-amber-900/50 rounded p-2 leading-relaxed">
              {data.dispute_reason}
            </p>
          )}

          {data.technical_details && (
            <div className="space-y-1.5 pt-1 text-[11px] font-mono-id border-t border-zinc-800/80">
              <div className="flex items-center justify-between text-zinc-400">
                <span>Endpoint</span>
                <span className="text-zinc-200">{data.technical_details.endpoint}</span>
              </div>
              <div className="flex items-center justify-between text-zinc-400">
                <span>Monthly Quota</span>
                <span className="text-zinc-200">{data.technical_details.quota}</span>
              </div>
              <div className="flex items-center justify-between text-zinc-400">
                <span>Current Usage</span>
                <span className="text-amber-300 font-semibold">{data.technical_details.current_usage}</span>
              </div>
              <div className="flex items-center justify-between text-zinc-400">
                <span>Ingestion Backlog</span>
                <span className="text-red-400 font-semibold">{data.estimated_delivery}</span>
              </div>
            </div>
          )}
        </div>

        {/* Ingress Gateway Route (Safe Operational Metadata Only - No API Keys) */}
        {data.carrier && (
          <div className="flex items-center justify-between text-xs py-1 border-t border-zinc-800/80">
            <span className="text-zinc-500">Ingress Gateway</span>
            <span className="text-zinc-300 font-medium text-[11px] font-mono-id">{data.carrier}</span>
          </div>
        )}

        {/* Tier & Customer Profile */}
        <div className="flex items-center justify-between text-xs pt-1 border-t border-zinc-800/80">
          <div className="flex items-center gap-1 text-zinc-400">
            <Crown size={12} className="text-amber-400" />
            <span>{data.customer_tier}</span>
          </div>
          <span className="text-[11px] font-mono-id text-zinc-400">
            LTV: {data.customer_lifetime_value}
          </span>
        </div>
      </div>
    );
  }

  // 4. E-Commerce Order Context (Zara Patel, Meera Iyer, Rohan Kapoor, etc.)
  return (
    <div className="rounded-xl border border-white/[0.09] bg-[#212124] p-5 shadow-xl space-y-3.5">
      {/* Card Header */}
      <div className="flex items-center justify-between border-b border-white/[0.08] pb-2.5">
        <div className="flex items-center gap-1.5">
          <ShoppingBag size={14} className="text-emerald-400" />
          <h3 className="text-xs font-mono font-medium uppercase tracking-wider text-zinc-300">
            Relevant Context
          </h3>
        </div>
        <span className="text-[10px] font-mono text-emerald-300 bg-emerald-950/60 px-2 py-0.5 rounded border border-emerald-800/60">
          Live D2C Order
        </span>
      </div>

      {/* Order ID, Amount, and Item */}
      <div className="space-y-1">
        <div className="flex items-center justify-between">
          <button
            type="button"
            onClick={handleCopyOrderId}
            className="group inline-flex items-center gap-1 font-mono-id text-xs text-zinc-200 hover:text-white cursor-pointer transition-colors"
            title="Copy Order ID"
          >
            <span className="font-semibold text-zinc-100">{data.order_id}</span>
            {copiedOrderId ? (
              <Check size={11} className="text-emerald-400" />
            ) : (
              <Copy size={11} className="text-zinc-500 group-hover:text-zinc-300" />
            )}
          </button>
          <span className="text-sm font-semibold text-white font-mono-id">
            {data.total_amount}
          </span>
        </div>
        <p className="text-xs text-zinc-200 font-medium leading-snug">
          {data.item_name}
        </p>
        <span className="text-[11px] font-mono-id text-zinc-500">
          Placed {data.order_date}
        </span>
      </div>

      {/* Status & Operational Notice */}
      <div className="bg-[#17171A] rounded-lg border border-white/[0.08] p-3 space-y-2">
        <div className="flex items-center justify-between">
          <span className="text-[11px] text-zinc-400 font-medium flex items-center gap-1.5">
            <StatusIcon size={12} className={statusLower.includes("delivered") ? "text-emerald-400" : "text-amber-400"} />
            Fulfillment
          </span>
          <span className={cn("text-[10px] px-2 py-0.5 rounded-full border font-medium", statusBadgeColor)}>
            {data.shipping_status}
          </span>
        </div>

        {data.dispute_reason && (
          <p className="text-[11px] text-amber-200/90 bg-amber-950/30 border border-amber-900/50 rounded p-2 leading-relaxed">
            {data.dispute_reason}
          </p>
        )}

        {data.estimated_delivery && (
          <div className="flex items-center justify-between text-[11px] text-zinc-400 pt-0.5">
            <span>Estimated Delivery</span>
            <span className="text-zinc-200 font-medium">{data.estimated_delivery}</span>
          </div>
        )}
      </div>

      {/* Logistics & Courier Tracking */}
      {data.carrier && (
        <div className="space-y-1.5 pt-1 border-t border-zinc-800/80 text-xs">
          <div className="flex items-center justify-between">
            <span className="text-zinc-500">Courier</span>
            <span className="text-zinc-300 font-medium">{data.carrier}</span>
          </div>

          {data.tracking_number && (
            <div className="flex items-center justify-between">
              <span className="text-zinc-500">AWB Tracking</span>
              <button
                type="button"
                onClick={handleCopyTracking}
                className="group inline-flex items-center gap-1 font-mono-id text-[11px] text-zinc-300 hover:text-white cursor-pointer"
                title="Copy Tracking Number"
              >
                <span>{data.tracking_number}</span>
                {copiedTracking ? (
                  <Check size={11} className="text-emerald-400" />
                ) : (
                  <Copy size={11} className="text-zinc-500 group-hover:text-zinc-300" />
                )}
              </button>
            </div>
          )}
        </div>
      )}

      {/* Payment Method & Customer VIP Tier */}
      <div className="space-y-1.5 pt-1 border-t border-zinc-800/80 text-xs">
        <div className="flex items-center justify-between">
          <span className="text-zinc-500 flex items-center gap-1">
            <CreditCard size={11} /> Payment
          </span>
          <span className="text-zinc-300 font-mono-id text-[11px] truncate max-w-[170px]">
            {data.payment_method}
          </span>
        </div>

        {data.customer_tier && (
          <div className="flex items-center justify-between">
            <span className="text-zinc-500 flex items-center gap-1">
              <Crown size={11} className="text-amber-400" /> Tier
            </span>
            <span className="text-amber-300 text-[11px] font-medium">
              {data.customer_tier}
            </span>
          </div>
        )}

        {data.customer_lifetime_value && (
          <div className="flex items-center justify-between">
            <span className="text-zinc-500">Lifetime Value</span>
            <span className="text-zinc-300 font-mono-id text-[11px]">
              {data.customer_lifetime_value}
            </span>
          </div>
        )}
      </div>
    </div>
  );
}
