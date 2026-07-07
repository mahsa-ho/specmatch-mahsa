# SpecMatch

Material matching service and review console. A service that matches messy
construction-material records to a canonical catalog, assigns confidence
tiers, and exposes the results through an API and a server-rendered review
console.

This is the **starter repository** for the SpecMatch take-home challenge.
Read the challenge document you received for the full task description.
Note: `backend/app/models/schemas.py` is frozen — CI verifies it is
unmodified.

## Quick start (Docker)

```bash
cp .env.example .env
docker compose up --build
```

API and console: http://localhost:8000 (console at `/`, API docs at `/docs`).

## Local development

```bash
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

## Tests

```bash
cd backend
pytest
```

## Layout

```
backend/app/            FastAPI application
  models/schemas.py     API contracts — FROZEN, do not modify
  routers/              health & records implemented; matches stubbed
  services/ingest.py    CSV ingest (runs at startup)
  services/matching/    interfaces defined; engine is yours to build
  templates/            record table implemented; review panel stubbed
  core/                 logging, errors, storage
backend/tests/          existing tests — pass on a clean clone
config/settings.yaml    tier thresholds & scoring weights
data/                   fixture CSVs (~150 source records, ~800 catalog entries)
```

See `CONTRIBUTING.md` for the commit, logging, and error-handling
conventions, and `CLAUDE.md` for AI-assistant context.
