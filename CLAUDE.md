# SpecMatch — AI assistant context

SpecMatch matches messy construction-material records to a canonical
catalog, assigns confidence tiers, and exposes the results through a
FastAPI API and a server-rendered (Jinja2) review console.

## Layout

- `backend/app/` — FastAPI application; `routers/` stay thin, logic lives
  in `services/`.
- `backend/app/models/schemas.py` — API contracts. **FROZEN: never modify.**
- `backend/app/services/matching/` — matching interfaces; the engine
  implementation goes here.
- `config/settings.yaml` — scoring weights and tier thresholds. Read them
  via `app.config.get_settings()`; never hardcode.
- `data/` — fixture CSVs ingested at startup.

## Commands

- Run locally: `cd backend && uvicorn app.main:app --reload`
- Tests: `cd backend && pytest`
- Full stack: `docker compose up --build` (API + console on :8000)

## Conventions

See CONTRIBUTING.md for the commit, logging, and error-handling rules.
Follow them in generated code.

---

Extend this file with project-specific rules as you work (Section 08 of
the challenge).
