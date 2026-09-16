import React from "react";
import { Link } from "react-router-dom";
import AppHeader from "@/components/layout/AppHeader";
import BlurFade from "@/components/magicui/BlurFade";
import { Button } from "@/components/ui/button";
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";

export default function CreateTicketPage() {
  return (
    <div className="min-h-screen bg-[#09090B] text-zinc-100">
      <AppHeader />

      <main className="mx-auto max-w-3xl px-4 py-8 sm:px-6 lg:px-8">
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

        <BlurFade delay={0.2}>
          <Card className="border-zinc-800 bg-[#18181B] text-zinc-100 shadow-xl">
            <CardHeader className="border-b border-zinc-800/80 pb-6">
              <CardTitle className="text-xl font-semibold text-white">
                Create New Support Ticket
              </CardTitle>
              <CardDescription className="text-sm text-zinc-400">
                Log a customer inquiry or support request. All fields are required.
              </CardDescription>
            </CardHeader>

            <CardContent className="pt-6">
              <form onSubmit={(e) => e.preventDefault()} className="space-y-5">
                <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
                  <div className="space-y-2">
                    <label className="text-xs font-medium text-zinc-300">
                      Customer Name
                    </label>
                    <Input
                      placeholder="e.g. Jane Doe"
                      disabled
                      className="border-zinc-800 bg-zinc-900/80 text-zinc-100 placeholder:text-zinc-500"
                    />
                  </div>

                  <div className="space-y-2">
                    <label className="text-xs font-medium text-zinc-300">
                      Customer Email
                    </label>
                    <Input
                      type="email"
                      placeholder="jane@example.com"
                      disabled
                      className="border-zinc-800 bg-zinc-900/80 text-zinc-100 placeholder:text-zinc-500"
                    />
                  </div>
                </div>

                <div className="space-y-2">
                  <label className="text-xs font-medium text-zinc-300">
                    Subject
                  </label>
                  <Input
                    placeholder="Brief description of the issue"
                    disabled
                    className="border-zinc-800 bg-zinc-900/80 text-zinc-100 placeholder:text-zinc-500"
                  />
                </div>

                <div className="space-y-2">
                  <label className="text-xs font-medium text-zinc-300">
                    Issue Description
                  </label>
                  <Textarea
                    placeholder="Detailed explanation..."
                    disabled
                    rows={4}
                    className="border-zinc-800 bg-zinc-900/80 text-zinc-100 placeholder:text-zinc-500"
                  />
                </div>

                <div className="pt-2">
                  <Button
                    type="submit"
                    disabled
                    className="w-full bg-indigo-600 font-medium text-white hover:bg-indigo-500 sm:w-auto"
                  >
                    Create Ticket (Phase 2 Placeholder)
                  </Button>
                </div>
              </form>
            </CardContent>
          </Card>
        </BlurFade>
      </main>
    </div>
  );
}
