import React, { useState } from "react";
import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import { Toaster } from "sonner";
import { TicketProvider } from "@/context/TicketContext";
import AppShell from "@/components/layout/AppShell";
import HomePage from "@/pages/HomePage";
import CreateTicketPage from "@/pages/CreateTicketPage";
import TicketDetailPage from "@/pages/TicketDetailPage";
import CommandPalette from "@/components/CommandPalette";
import { useKeyboardShortcuts } from "@/hooks/useKeyboardShortcuts";

/**
 * AppContent wraps layout, global keyboard shortcuts, command palette modal, and routes.
 * Positioned inside BrowserRouter and TicketProvider for full routing and context awareness.
 */
function AppContent() {
  const [paletteOpen, setPaletteOpen] = useState(false);

  useKeyboardShortcuts({
    onTogglePalette: () => setPaletteOpen((prev) => !prev),
    isPaletteOpen: paletteOpen,
  });

  return (
    <>
      <Toaster position="bottom-right" richColors={false} theme="dark" />
      <AppShell>
        <Routes>
          <Route path="/" element={<HomePage />} />
          <Route path="/tickets/new" element={<CreateTicketPage />} />
          <Route path="/tickets/:id" element={<TicketDetailPage />} />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </AppShell>
      <CommandPalette
        isOpen={paletteOpen}
        onClose={() => setPaletteOpen(false)}
      />
    </>
  );
}

/**
 * Root Application component.
 * Configures central TicketProvider, persistent AppShell layout, and application routing.
 */
export default function App() {
  return (
    <BrowserRouter>
      <TicketProvider>
        <AppContent />
      </TicketProvider>
    </BrowserRouter>
  );
}
