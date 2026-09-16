import React, { useState } from "react";
import AppHeader from "./AppHeader";
import Sidebar from "./Sidebar";

/**
 * Global AppShell Layout
 * Anchors the viewport with a sticky pitch-black top header and persistent left sidebar,
 * framing the elevated charcoal workbench canvas (#121214).
 * @param {object} props
 * @param {React.ReactNode} props.children
 */
export function AppShell({ children }) {
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  return (
    <div className="min-h-screen bg-black text-zinc-100 antialiased flex flex-col selection:bg-zinc-800 selection:text-white">
      {/* Persistent Pitch-Black Top Header */}
      <AppHeader
        mobileMenuOpen={mobileMenuOpen}
        onToggleMobileMenu={() => setMobileMenuOpen((prev) => !prev)}
      />

      <div className="flex-1 flex w-full relative">
        {/* Desktop Pitch-Black Sidebar (persistent, sticky below header) */}
        <div className="hidden md:block sticky top-14 h-[calc(100vh-3.5rem)]">
          <Sidebar />
        </div>

        {/* Mobile Sidebar Overlay Drawer */}
        {mobileMenuOpen && (
          <div className="fixed inset-0 top-14 z-30 flex md:hidden">
            <div
              className="fixed inset-0 bg-black/80 backdrop-blur-sm"
              onClick={() => setMobileMenuOpen(false)}
            />
            <div className="relative z-40 w-64 bg-black h-full shadow-2xl">
              <Sidebar onNavigate={() => setMobileMenuOpen(false)} />
            </div>
          </div>
        )}

        {/* Main Content Workbench: Elevated Dark Charcoal/Graphite Canvas (#1B1B1E) */}
        <main className="flex-1 min-w-0 bg-[#1B1B1E] overflow-y-auto min-h-[calc(100vh-3.5rem)]">
          {children}
        </main>
      </div>
    </div>
  );
}

export default AppShell;
