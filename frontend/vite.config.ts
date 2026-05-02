import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import tailwindcss from "@tailwindcss/vite";

// Use relative base so the bundle works under any path:
//   - http://localhost:8300/        (FastAPI serving static dist)
//   - https://suanai.github.io/research/   (GitHub Pages under repo path)
// Override per-build via VITE_BASE if absolute base is required.
const base = process.env.VITE_BASE ?? "./";

export default defineConfig({
  base,
  plugins: [react(), tailwindcss()],
  build: {
    chunkSizeWarningLimit: 600,
    rollupOptions: {
      output: {
        manualChunks: {
          "vendor-react": ["react", "react-dom", "react-router-dom"],
          "vendor-cytoscape": [
            "cytoscape",
            "cytoscape-cose-bilkent",
            "react-cytoscapejs",
          ],
        },
      },
    },
  },
  server: {
    port: 3000,
    proxy: {
      "/api": {
        target: "http://localhost:8300",
        changeOrigin: true,
      },
    },
  },
});
