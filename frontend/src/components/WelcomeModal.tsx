import { useState, useEffect, useCallback } from "react";

const STORAGE_KEY = "scigraph_welcome_dismissed";

interface Feature {
  title: string;
  description: string;
  color: string;
  path: string;
}

const FEATURES: Feature[] = [
  {
    title: "Citation Network",
    description:
      "Explore citation relationships between papers. Search for a seed paper and progressively expand its connections.",
    color: "#00d4ff",
    path: "/citation",
  },
  {
    title: "Co-authorship",
    description:
      "Visualize author collaboration networks. Find research clusters and key collaborators.",
    color: "#2ed573",
    path: "/coauthorship",
  },
  {
    title: "Retraction Cascade",
    description:
      "Trace how retracted papers contaminate the citation network through downstream citations.",
    color: "#ff4757",
    path: "/contamination",
  },
  {
    title: "AI Diffusion",
    description:
      "Analyze the spread of AI/ML research across 26 academic fields over time.",
    color: "#a855f7",
    path: "/ai-diffusion",
  },
];

const TIPS = [
  "Right-click any node to see context actions like Expand, Set as Focal, or View Details.",
  "Double-click a node to expand its connections in the graph.",
  "Use the layout selector to switch between force-directed, hierarchical, and other layouts.",
  "Click a node to see its details in the right sidebar panel.",
];

export function WelcomeModal() {
  const [show, setShow] = useState(false);

  useEffect(() => {
    const dismissed = localStorage.getItem(STORAGE_KEY);
    if (!dismissed) {
      setShow(true);
    }
  }, []);

  const handleDismiss = useCallback(() => {
    localStorage.setItem(STORAGE_KEY, "1");
    setShow(false);
  }, []);

  if (!show) return null;

  return (
    <div className="fixed inset-0 z-[100] flex items-center justify-center p-4">
      {/* Backdrop */}
      <div
        className="absolute inset-0 bg-black/70 backdrop-blur-sm"
        onClick={handleDismiss}
        onKeyDown={(e) => e.key === "Escape" && handleDismiss()}
        role="button"
        tabIndex={0}
        aria-label="Close welcome"
      />

      {/* Modal */}
      <div className="relative w-full max-w-2xl bg-[#16213e] border border-[#2a2a4a] rounded-2xl shadow-2xl overflow-hidden">
        {/* Header */}
        <div className="px-6 pt-8 pb-4 text-center">
          <div className="w-14 h-14 mx-auto rounded-xl bg-gradient-to-br from-[#00d4ff] to-[#a855f7] flex items-center justify-center mb-4">
            <svg
              className="w-7 h-7 text-white"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
              strokeWidth={2}
            >
              <title>SciGraph</title>
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                d="M7.5 21L3 16.5m0 0L7.5 12M3 16.5h13.5m0-13.5L21 7.5m0 0L16.5 12M21 7.5H7.5"
              />
            </svg>
          </div>
          <h2 className="font-[Outfit] text-2xl font-bold text-white">
            Welcome to SuanAI SciGraph
          </h2>
          <p className="font-[Outfit] text-sm text-gray-400 mt-2">
            Interactive graph explorer for science of science research.
            <br />
            360M+ papers, 86M+ authors, 1B+ citations.
          </p>
        </div>

        {/* Features */}
        <div className="px-6 pb-4 grid grid-cols-1 sm:grid-cols-2 gap-3">
          {FEATURES.map((f) => (
            <div
              key={f.path}
              className="p-3 bg-[#0d1b2a] rounded-lg border border-[#2a2a4a]/50"
            >
              <p
                className="font-[Outfit] text-sm font-semibold"
                style={{ color: f.color }}
              >
                {f.title}
              </p>
              <p className="font-[Outfit] text-xs text-gray-500 mt-1 leading-relaxed">
                {f.description}
              </p>
            </div>
          ))}
        </div>

        {/* Tips */}
        <div className="px-6 pb-4">
          <p className="font-[Outfit] text-[11px] uppercase tracking-wider text-gray-500 mb-2">
            Quick Tips
          </p>
          <ul className="space-y-1.5">
            {TIPS.map((tip, i) => (
              <li key={i} className="flex items-start gap-2">
                <span className="mt-1.5 w-1 h-1 rounded-full bg-[#00d4ff] shrink-0" />
                <span className="font-[Outfit] text-xs text-gray-400">
                  {tip}
                </span>
              </li>
            ))}
          </ul>
        </div>

        {/* Footer */}
        <div className="px-6 pb-6 flex justify-center">
          <button
            type="button"
            onClick={handleDismiss}
            className="px-8 py-2.5 rounded-lg bg-gradient-to-r from-[#00d4ff] to-[#a855f7] font-[Outfit] text-sm font-semibold text-white hover:opacity-90 transition-opacity"
          >
            Get Started
          </button>
        </div>
      </div>
    </div>
  );
}
