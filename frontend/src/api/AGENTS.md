<!-- Parent: ../AGENTS.md -->
<!-- Generated: 2026-04-17 | Updated: 2026-04-17 -->

# api

## Purpose
Typed client for the FastAPI backend. Wraps `fetch` with error handling, base URL resolution, and response typing.

## Key Files

| File | Description |
|------|-------------|
| `graphApi.ts` | Backend client — `fetchJson`, `searchPapers`, `searchAuthors`, `getCitationNetwork`, `getAuthorNetwork`, exports helpers for cascade/diffusion endpoints |

## For AI Agents

### Working In This Directory
- All backend calls go through this module — views and hooks never call `fetch` directly
- Base URL from `import.meta.env.VITE_API_BASE_URL` (defaults to `/api` in production behind FastAPI)
- Errors thrown as typed `ApiError` with status + message
- Response shapes typed via `types/graph.ts` interfaces
- Keep functions pure — no global state, no caching (hooks handle caching)

### Common Patterns
```ts
export async function searchPapers(query: string, limit = 20): Promise<SearchResult[]> {
  return fetchJson<SearchResult[]>(`/search/papers?q=${encodeURIComponent(query)}&limit=${limit}`);
}
```

### Backend Mapping
| Frontend function | Backend route |
|-------------------|---------------|
| `searchPapers` | `GET /api/search/papers` |
| `searchAuthors` | `GET /api/search/authors` |
| `getCitationNetwork` | `GET /api/graph/citation-network` |
| `getAuthorNetwork` | `GET /api/graph/author-network` |

## Dependencies

### Internal
- `../types/graph.ts` — Response type definitions
- `src/research/api/` (backend) — Implements the endpoints consumed here

### External
- Native `fetch` — No axios/ky dependency

<!-- MANUAL: -->
