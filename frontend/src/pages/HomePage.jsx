import React from "react";
import { Link } from "react-router-dom";
import AppHeader from "@/components/layout/AppHeader";
import BlurFade from "@/components/magicui/BlurFade";
import { Button } from "@/components/ui/button";
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from "@/components/ui/card";

export default function HomePage() {
  return (
    <div className="min-h-screen bg-[#09090B] text-zinc-100">
      <AppHeader ticketCount={0} />

      <main className="mx-auto max-w-7xl px-4 py-8 sm:px-6 lg:px-8">
        <BlurFade delay={0.1}>
          <div className="mb-8 flex flex-col gap-2 sm:flex-row sm:items-center sm:justify-between">
            <div>
              <h1 className="text-2xl font-bold tracking-tight text-white sm:text-3xl">
                Support Ticket Queue
              </h1>
              <p className="mt-1 text-sm text-zinc-400">
                Live dashboard of active customer support requests.
              </p>
            </div>

            <Link to="/tickets/new">
              <Button className="bg-indigo-600 text-white hover:bg-indigo-500">
                + New Ticket
              </Button>
            </Link>
          </div>
        </BlurFade>

        <BlurFade delay={0.2}>
          <Card className="border-zinc-800 bg-[#18181B]">
            <CardHeader>
              <CardTitle className="text-lg text-white">Tickets Queue</CardTitle>
              <CardDescription className="text-zinc-400">
                Phase 2 Shell Active — routing, components, and design system ready.
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="rounded-lg border border-dashed border-zinc-800 p-8 text-center">
                <p className="text-sm text-zinc-400">
                  Ticket queue table will connect to backend API in Phase 3.
                </p>
                <div className="mt-4 flex justify-center gap-3">
                  <Link to="/tickets/TKT-SAMPLE" className="text-xs text-indigo-400 underline underline-offset-4 hover:text-indigo-300">
                    Preview Sample Ticket Detail (/tickets/TKT-SAMPLE) →
                  </Link>
                </div>
              </div>
            </CardContent>
          </Card>
        </BlurFade>
      </main>
    </div>
  );
}
