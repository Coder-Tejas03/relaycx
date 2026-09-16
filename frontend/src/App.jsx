import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import { Toaster } from "sonner";
import HomePage from "@/pages/HomePage";
import CreateTicketPage from "@/pages/CreateTicketPage";
import TicketDetailPage from "@/pages/TicketDetailPage";

/**
 * Root Application component.
 * Responsible only for router configuration and global toast notifications.
 */
export default function App() {
  return (
    <BrowserRouter>
      <Toaster position="bottom-right" richColors theme="dark" />
      <Routes>
        <Route path="/" element={<HomePage />} />
        <Route path="/tickets/new" element={<CreateTicketPage />} />
        <Route path="/tickets/:id" element={<TicketDetailPage />} />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </BrowserRouter>
  );
}
