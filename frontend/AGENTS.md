<!-- Parent: ../AGENTS.md -->
<!-- Generated: 2026-04-04 | Updated: 2026-04-04 -->

# frontend

## Purpose
React + TypeScript SPA for interactive bibliographic graph exploration. Visualizes citation networks, co-authorship graphs, retraction contamination cascades, and AI adoption diffusion.

## Key Files

| File | Description |
|------|-------------|
| `package.json` | Dependencies: React 19, Cytoscape 3.33, D3-Force 3, React Router, Tailwind CSS |
| `vite.config.ts` | Vite build config with React plugin, code-splitting (vendor-react, vendor-cytoscape) |
| `tsconfig.json` | TypeScript root configuration |
| `tsconfig.app.json` | App-specific TypeScript settings |
| `eslint.config.js` | ESLint configuration |
| `index.html` | HTML entry point |
| `.env` | Environment variables |

## Subdirectories

| Directory | Purpose |
|-----------|---------|
| `src/` | Application source code (see `src/AGENTS.md`) |
| `dist/` | Built output (served by FastAPI in production) |
| `public/` | Static assets |

## For AI Agents

### Working In This Directory
- Use `npm install` for dependency changes, not `yarn` or `pnpm`
- Built `dist/` is served by the FastAPI backend as static files
- Vite dev server for local development

### Building & Running
```bash
cd frontend
npm install                  # Install dependencies
npm run dev                  # Vite dev server
npm run build                # Production build → dist/
```

### Testing Requirements
- No test framework currently configured
- Verify builds pass: `npm run build`

## Dependencies

### Internal
- `src/research/api/` — Backend REST API consumed by this frontend

### External
- React 19, React Router 7
- Cytoscape 3.33 + cose-bilkent, fcose layouts + node-html-label
- D3-Force 3 for physics simulation
- Tailwind CSS 4
- Vite 6

<!-- MANUAL: -->
