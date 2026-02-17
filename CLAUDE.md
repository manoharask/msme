# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

```bash
# Run the app
streamlit run app.py

# Seed the database (35 categories, 25 SNPs) — run once after a fresh DB or reset
python utils/seed_graph.py

# Wipe and re-seed the database
python utils/reset_graph.py   # prompts for confirmation
python utils/seed_graph.py

# Test OCR on the sample certificate
python utils/test_ocr.py
```

## Environment Setup

Requires a `.env` file in the repo root (already gitignored):

```
OPENAI_API_KEY=sk-proj-...
NEO4J_URI=neo4j+s://...
NEO4J_USERNAME=neo4j
NEO4J_PASSWORD=...

# Optional — only needed if Tesseract/Poppler are not on PATH
TESSERACT_CMD=/path/to/tesseract
POPPLER_PATH=/path/to/poppler/bin
```

## Architecture

### Data flow
```
User input (voice / manual / PDF)
    → msme_app/services/  (NLP, OCR, categorization)
    → Neo4j graph database
    → Streamlit UI renders results
```

### Streamlit pages
- `app.py` — dashboard: analytics metrics, MSE/SNP/Category tables with filters
- `pages/01_Add_MSE.py` — three-tab onboarding form (Voice, Manual, Udyam Certificate)

Both pages create the Neo4j driver once via `@st.cache_resource`:
```python
@st.cache_resource
def _get_driver():
    return get_driver(load_config())
```

### Services (`msme_app/services/`)
| Module | Purpose |
|---|---|
| `graph_service.py` | All Neo4j queries — the only file that talks to the DB |
| `categorization.py` | Keyword-scoring against 35 categories; caches the category list in `_category_cache` |
| `nlp_service.py` | GPT-4o-mini entity extraction + fuzzy city normalisation |
| `ocr_service.py` | PDF/image → text via Tesseract; LLM fallback via `process_with_fallback()` |
| `whisper_service.py` | Audio transcription; model cached with `@st.cache_resource` |

### Graph schema (Neo4j)
- **Nodes:** `MSE`, `SNP`, `Category`
- **Relationships:** `MSE -[:OFFERS]-> Category`, `SNP -[:SERVES]-> Category`
- `save_mse()` uses `MERGE` on `id` — re-saving the same ID updates the record
- `fetch_analytics_summary()` uses Neo4j 5.x `CALL () {}` subquery syntax — requires Neo4j ≥ 5

### Shared confirm form
`render_confirm_form(prefix)` in `pages/01_Add_MSE.py` is reused by all three tabs. Session state keys are namespaced by `prefix` (`voice_`, `manual_`, `udyam_`). The `form_data_{prefix}` key in session state drives what the form renders.

### Category caching note
`categorize_products()` caches all category rows in a module-level `_category_cache`. If you add or change categories in the DB at runtime, the cache must be reset by restarting the Streamlit process.
