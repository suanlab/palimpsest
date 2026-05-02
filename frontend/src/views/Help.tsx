const SECTIONS = [
  {
    title: "Citation Network",
    color: "#00d4ff",
    items: [
      "Search for a paper by title to set it as the seed node.",
      "The graph shows papers that cite or are cited by the seed paper.",
      "Double-click any node to expand its direct connections.",
      "Right-click for actions: Expand, Set as Focal, View in Explorer.",
      "Use filters to show/hide retracted or AI-related papers.",
    ],
  },
  {
    title: "Co-authorship Network",
    color: "#2ed573",
    items: [
      "Search for an author to see their collaboration network.",
      "Node size reflects paper count; edge weight reflects shared papers.",
      "Expand a co-author node to discover second-degree collaborators.",
      "Click an author node and use 'View Author Detail' for full profile.",
    ],
  },
  {
    title: "Retraction Cascade",
    color: "#ff4757",
    items: [
      "Search for a retracted paper to trace its contamination spread.",
      "The cascade shows papers that cited the retracted work, even post-retraction.",
      "Red nodes indicate retracted papers; depth shows citation distance.",
      "Contamination score decreases with distance from the retracted source.",
    ],
  },
  {
    title: "AI Diffusion",
    color: "#a855f7",
    items: [
      "Visualizes the penetration of AI/ML research across 26 academic fields.",
      "Adjust the year range to see adoption trends over time.",
      "Toggle between 'title' (keyword-based) and 'concept' (OpenAlex concept) methods.",
      "Node size reflects total papers; color intensity shows AI fraction.",
    ],
  },
  {
    title: "Graph Controls",
    color: "#ffa502",
    items: [
      "Zoom: Use scroll wheel, pinch gesture, or +/- buttons.",
      "Pan: Click and drag on empty space.",
      "Fit: Click the fit button to auto-zoom to show all nodes.",
      "Layout: Switch between Force-directed, Hierarchical, Concentric, Circle, and Grid.",
      "Filters: Toggle Retracted and AI-related node visibility.",
    ],
  },
  {
    title: "Keyboard & Mouse",
    color: "#64748b",
    items: [
      "Left-click a node: Select and highlight its connections.",
      "Double-click a node: Expand its connections.",
      "Right-click a node: Open context menu with actions.",
      "Click empty space: Deselect all nodes.",
      "Scroll wheel: Zoom in/out.",
    ],
  },
];

export function Help() {
  const handleResetWelcome = () => {
    localStorage.removeItem("scigraph_welcome_dismissed");
    window.location.reload();
  };

  return (
    <div className="flex-1 overflow-y-auto p-4 sm:p-8">
      <div className="max-w-4xl mx-auto">
        <div className="mb-8">
          <h1 className="font-[Outfit] text-2xl sm:text-3xl font-bold text-white tracking-tight">
            Help & Guide
          </h1>
          <p className="font-[Outfit] text-sm text-gray-500 mt-1">
            Learn how to use SuanAI SciGraph to explore bibliographic networks.
          </p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-4 sm:gap-6">
          {SECTIONS.map((section) => (
            <div
              key={section.title}
              className="bg-[#16213e] border border-[#2a2a4a] rounded-xl p-5"
            >
              <h2
                className="font-[Outfit] text-base font-semibold mb-3"
                style={{ color: section.color }}
              >
                {section.title}
              </h2>
              <ul className="space-y-2">
                {section.items.map((item, i) => (
                  <li key={i} className="flex items-start gap-2">
                    <span
                      className="mt-1.5 w-1.5 h-1.5 rounded-full shrink-0"
                      style={{ backgroundColor: section.color }}
                    />
                    <span className="font-[Outfit] text-xs text-gray-400 leading-relaxed">
                      {item}
                    </span>
                  </li>
                ))}
              </ul>
            </div>
          ))}
        </div>

        <div className="mt-8 flex flex-col sm:flex-row items-start sm:items-center gap-4 bg-[#16213e] border border-[#2a2a4a] rounded-xl p-5">
          <div className="flex-1">
            <h3 className="font-[Outfit] text-sm font-semibold text-gray-300">
              Show Welcome Screen Again
            </h3>
            <p className="font-[Outfit] text-xs text-gray-500 mt-0.5">
              Reset the onboarding welcome modal to see it on next page load.
            </p>
          </div>
          <button
            type="button"
            onClick={handleResetWelcome}
            className="px-4 py-2 rounded-lg border border-[#2a2a4a] bg-[#0d1b2a] font-[Outfit] text-xs text-gray-300 hover:border-[#3a3a5a] hover:text-white transition-colors"
          >
            Reset Welcome
          </button>
        </div>

        <div className="mt-6 text-center">
          <p className="font-[Outfit] text-xs text-gray-600">
            SuanAI SciGraph v0.2.0 &middot; Powered by OpenAlex &middot; 360M+
            works
          </p>
        </div>
      </div>
    </div>
  );
}
