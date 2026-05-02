# Semantic Scholar API Key Application

## How do you plan to use Semantic Scholar API in your project?

We are conducting a **science of science** research project analyzing how retracted papers propagate through citation networks and how scientific self-correction mechanisms operate. Specifically, we use the Semantic Scholar API to retrieve **citation context and intent data** — understanding *how* papers are cited (supporting, contrasting, methodological, background), not just *how many times*. This is critical because our research measures "knowledge contamination" from retracted papers: we need to distinguish whether citing papers actually propagate a retracted claim versus merely referencing it in passing. We also use the **paper metadata and embedding endpoints** to compute semantic similarity between retracted papers and their citers, enabling us to assess whether contamination is substantive or superficial. Our pipeline processes batches of ~500 retracted papers and their ~20,000 direct citers, structured as nightly batch jobs with efficient pagination and caching to minimize redundant requests.

## Which endpoints do you plan to use?

- **`GET /graph/v1/paper/{paper_id}`** — with fields: `citations.contexts`, `citations.intents`, `references`, `embedding`, `tldr`
- **`POST /graph/v1/paper/batch`** — batch retrieval of paper metadata for up to 500 papers per request
- **`GET /graph/v1/paper/{paper_id}/citations`** — paginated citation traversal with context and intent fields
- **`GET /graph/v1/paper/{paper_id}/references`** — reference chain analysis for disruption index computation
- **`GET /recommendations/v1/papers/forpaper/{paper_id}`** — identifying semantically related works for field-level analysis

## How many requests per day do you anticipate using?

**5,000–10,000 requests per day** during active data collection phases (approximately 2–3 weeks per research cycle), dropping to **500–1,000 requests per day** during steady-state analysis. We use aggressive local caching (diskcache with 24-hour TTL) and batch endpoints to minimize request volume. All requests include appropriate backoff handling for rate limits.
