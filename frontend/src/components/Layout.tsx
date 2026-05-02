import { useState, useCallback, createContext, useContext } from "react";
import { Outlet } from "react-router-dom";
import { Sidebar } from "./Sidebar";

interface MobileSidebarContextType {
  isOpen: boolean;
  toggle: () => void;
  close: () => void;
}

const MobileSidebarContext = createContext<MobileSidebarContextType>({
  isOpen: false,
  toggle: () => {},
  close: () => {},
});

export function useMobileSidebar() {
  return useContext(MobileSidebarContext);
}

export function Layout() {
  const [sidebarOpen, setSidebarOpen] = useState(false);

  const toggle = useCallback(() => setSidebarOpen((prev) => !prev), []);
  const close = useCallback(() => setSidebarOpen(false), []);

  return (
    <MobileSidebarContext.Provider value={{ isOpen: sidebarOpen, toggle, close }}>
      <div className="flex h-screen w-screen overflow-hidden bg-[#0f0f23]">
        {/* Mobile backdrop */}
        {sidebarOpen && (
          <div
            className="fixed inset-0 bg-black/60 z-40 lg:hidden"
            onClick={close}
            onKeyDown={(e) => e.key === "Escape" && close()}
            role="button"
            tabIndex={0}
            aria-label="Close sidebar"
          />
        )}

        {/* Sidebar — always visible on lg+, slide-over on mobile */}
        <div
          className={`fixed inset-y-0 left-0 z-50 w-64 transform transition-transform duration-300 ease-in-out lg:relative lg:translate-x-0 lg:z-auto ${
            sidebarOpen ? "translate-x-0" : "-translate-x-full"
          }`}
        >
          <Sidebar onNavigate={close} />
        </div>

        <main className="flex-1 overflow-hidden flex flex-col min-w-0">
          {/* Mobile header bar */}
          <div className="flex items-center gap-3 px-4 py-2 bg-[#1a1a2e] border-b border-[#2a2a4a] lg:hidden">
            <button
              type="button"
              onClick={toggle}
              className="p-1.5 rounded-lg text-gray-400 hover:text-white hover:bg-white/5 transition-colors"
              aria-label="Toggle navigation"
            >
              <svg
                className="w-5 h-5"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
                strokeWidth={2}
              >
                <title>Menu</title>
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  d="M3.75 6.75h16.5M3.75 12h16.5m-16.5 5.25h16.5"
                />
              </svg>
            </button>
            <div className="flex items-center gap-2">
              <div className="w-6 h-6 rounded bg-gradient-to-br from-[#00d4ff] to-[#a855f7] flex items-center justify-center">
                <svg
                  className="w-3.5 h-3.5 text-white"
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                  strokeWidth={2}
                  aria-hidden="true"
                >
                  <title>Logo</title>
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    d="M7.5 21L3 16.5m0 0L7.5 12M3 16.5h13.5m0-13.5L21 7.5m0 0L16.5 12M21 7.5H7.5"
                  />
                </svg>
              </div>
              <span className="font-[Outfit] text-sm font-semibold text-white">
                SuanAI SciGraph
              </span>
            </div>
          </div>

          <Outlet />
        </main>
      </div>
    </MobileSidebarContext.Provider>
  );
}
