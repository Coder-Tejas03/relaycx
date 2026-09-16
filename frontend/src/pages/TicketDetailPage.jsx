import React from "react";
import { Link, useParams } from "react-router-dom";
import AppHeader from "@/components/layout/AppHeader";
import BlurFade from "@/components/magicui/BlurFade";
import BorderBeam from "@/components/magicui/BorderBeam";
import { Badge } from "@/components/ui/badge";
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from "@/components/ui/card";

export default function TicketDetailPage() {
  const { id } = useParams();

  return (
    <div className="min-h-screen bg-[#09090B] text-zinc-100">
      <AppHeader />

      <main className="mx-auto max-w-7xl px-4 py-8 sm:px-6 lg:px-8">
        <BlurFade delay={0.1}>
          <div className="mb-6">
            <Link
              to="/"
              className="inline-flex items-center gap-1.5 text-xs font-medium text-zinc-400 transition hover:text-white"
            >
              ← Back to Tickets Queue
            </Link>
          </div>
        </BlurFade>

        <div className="grid grid-cols-1 gap-6 lg:grid-cols-3">
          {/* Left / Main Column */}
          <div className="space-y-6 lg:col-span-2">
            <BlurFade delay={0.2}>
              <div className="relative overflow-hidden rounded-xl border border-zinc-800 bg-[#18181B] p-6 shadow-xl">
                <BorderBeam size={220} duration={14} colorFrom="#6366F1" colorTo="#A855F7" />

                <div className="flex items-start justify-between gap-4">
                  <div>
                    <span className="font-mono-id tracking-wider text-xs">
                      {id || "TKT-UNKNOWN"}
                    </span>
                    <h1 className="mt-2 text-xl font-bold tracking-tight text-white sm:text-2xl">
                      Ticket Detail Placeholder
                    </h1>
                    <p className="mt-1 text-xs text-zinc-400">
                      customer@example.com
                    </p>
                  </div>

                  <Badge className="border border-indigo-500/30 bg-indigo-500/10 text-indigo-400">
                    Open
                  </Badge>
                </div>

                <div className="mt-6 border-t border-zinc-800 pt-4 text-sm text-zinc-300">
                  <p>
                    Full ticket description, customer issue details, and internal notes timeline will populate dynamically via the API in Phase 3.
                  </p>
                </div>
              </div>
            </BlurFade>

            <BlurFade delay={0.3}>
              <Card className="border-zinc-800 bg-[#18181B]">
                <CardHeader>
                  <CardTitle className="text-base text-white">Internal Notes</CardTitle>
                  <CardDescription className="text-xs text-zinc-400">
                    Chronological activity log and agent resolution console.
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="rounded-lg border border-dashed border-zinc-800 p-6 text-center text-xs text-zinc-500">
                    Note console and AnimatedList timeline activate in Phase 3.
                  </div>
                </CardContent>
              </Card>
            </BlurFade>
          </div>

          {/* Right Column: Metadata & Controls */}
          <div className="space-y-6">
            <BlurFade delay={0.25}>
              <Card className="border-zinc-800 bg-[#18181B]">
                <CardHeader className="pb-3">
                  <CardTitle className="text-sm font-semibold text-white">Ticket Status</CardTitle>
                </CardHeader>
                <CardContent className="space-y-3">
                  <div className="flex gap-2">
                    <span className="rounded-md bg-indigo-600 px-3 py-1.5 text-xs font-medium text-white">
                      Open
                    </span>
                    <span className="rounded-md border border-zinc-800 bg-zinc-900 px-3 py-1.5 text-xs font-medium text-zinc-400">
                      In Progress
                    </span>
                    <span className="rounded-md border border-zinc-800 bg-zinc-900 px-3 py-1.5 text-xs font-medium text-zinc-400">
                      Closed
                    </span>
                  </div>
                </CardContent>
              </Card>
            </BlurFade>

            <BlurFade delay={0.35}>
              <Card className="border-zinc-800 bg-[#18181B]">
                <CardHeader className="pb-3">
                  <CardTitle className="text-sm font-semibold text-white">Audit Information</CardTitle>
                </CardHeader>
                <CardContent className="space-y-2 text-xs">
                  <div className="flex justify-between py-1 border-b border-zinc-800/60">
                    <span className="text-zinc-400">Ticket ID</span>
                    <span className="font-mono-id">{id}</span>
                  </div>
                  <div className="flex justify-between py-1 border-b border-zinc-800/60">
                    <span className="text-zinc-400">Created</span>
                    <span className="text-zinc-300">Just now</span>
                  </div>
                  <div className="flex justify-between py-1">
                    <span className="text-zinc-400">Notes Count</span>
                    <span className="text-zinc-300">0</span>
                  </div>
                </CardContent>
              </Card>
            </BlurFade>
          </div>
        </div>
      </main>
    </div>
  );
}
