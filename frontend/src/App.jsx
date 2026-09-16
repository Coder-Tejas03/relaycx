import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import { Toaster } from "sonner";
import { TicketProvider } from "@/context/TicketContext";
import AppShell from "@/components/layout/AppShell";
import HomePage from "@/pages/HomePage";
import CreateTicketPage from "@/pages/CreateTicketPage";
import TicketDetailPage from "@/pages/TicketDetailPage";

/**
 * Root Application component.
 * Configures central TicketProvider, persistent AppShell layout, and application routing.
 */
export default function App() {
  return (
    <BrowserRouter>
      <TicketProvider>
        <Toaster position="bottom-right" richColors={false} theme="dark" />
        <AppShell>
          <Routes>
            <Route path="/" element={<HomePage />} />
            <Route path="/tickets/new" element={<CreateTicketPage />} />
            <Route path="/tickets/:id" element={<TicketDetailPage />} />
            <Route path="*" element={<Navigate to="/" replace />} />
          </Routes>
        </AppShell>
      </TicketProvider>
    </BrowserRouter>
  );
}
