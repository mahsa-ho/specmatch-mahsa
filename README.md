# SpecMatch

SpecMatch is a FastAPI application that matches messy construction-material records to a canonical catalog, assigns confidence tiers, exposes results through an API, and provides a server-rendered review console for human review.

`backend/app/models/schemas.py` is frozen and was not modified.

## System Overview

The app loads source records and catalog entries from CSV files, runs a lexical matching engine, stores match results, and allows reviewers to accept, override, or reject matches.

## Architecture

```text
data/source_records.csv + data/catalog.csv
        ↓
ingest service
        ↓
SQLite database
        ↓
matching engine
        ↓
matches table
        ↓
FastAPI endpoints + Jinja2 review console
```

## Quick Start

```bash
git clone https://github.com/mahsa-ho/specmatch-mahsa.git
cd specmatch-mahsa
cp .env.example .env
docker compose up --build
```

Open:

```text
http://127.0.0.1:8000
http://127.0.0.1:8000/review
http://127.0.0.1:8000/docs
```

## Running Tests

```bash
docker compose exec api pytest
```

## API Examples

Health:

```bash
curl http://127.0.0.1:8000/health
```

Records:

```bash
curl "http://127.0.0.1:8000/records?limit=10&offset=0"
```

Matches:

```bash
curl "http://127.0.0.1:8000/matches?tier=yellow&limit=50&offset=0"
```

Review decision:

```bash
curl -X POST "http://127.0.0.1:8000/matches/SRC-0001/review" \
  -H "Content-Type: application/json" \
  -d '{"action":"accept","catalog_id":"CAT-0001","note":"Reviewed"}'
```

## Matching Engine Design

The matching engine uses a simple lexical approach that is easy to test and explain.

It normalizes source and catalog text, expands common construction abbreviations, retrieves likely catalog candidates, scores them, assigns a tier, and persists the top candidates.

The score combines:

- string similarity
- category agreement
- unit compatibility

The scoring weights and tier thresholds come from `config/settings.yaml`, not hardcoded constants.

## Tier Distribution

After running the matching engine on the full fixture set, the tier distribution was:

```text
green: 38
yellow: 96
red: 16
```

This distribution is intentional. The engine does not force every record into green. High-confidence matches are auto-accepted, uncertain records are routed to human review, and weak or unknown records land in red.

## Issue Fixes

### Issue #1: Duplicate records after re-running ingest

Root cause: ingest inserted source records again each time it ran.

Fix: made record ingest idempotent by clearing existing records before reloading fixture data.

Test: added a failing test that re-runs ingest and confirms the record count stays 150.

### Issue #2: Wrong confidence tier at threshold boundary

Root cause: the accept threshold used a strict comparison instead of an inclusive boundary.

Fix: changed the tier comparison so scores equal to the accept threshold land in green.

Test: added boundary tests for accept and review thresholds.

### Issue #3: Empty table after switching back to all categories

Root cause: the console treated an empty category query as a real category filter.

Fix: only apply the category filter when the category is non-empty and not `All categories`.

Test: added a test for `category=""`.

## Review Console

The review console at `/review` shows tier counts, source text, candidates, confidence scores, and signal breakdowns.

A reviewer can:

- accept the top candidate
- override with another candidate
- reject the match

Review decisions are persisted through the API.

## AI Usage

I used AI tools to help understand the codebase, plan the implementation, debug errors, and improve tests and documentation.

I reviewed all suggestions before using them and made sure I understood the final code. One example where I corrected AI output was Issue #3: the first test checked `All categories`, but the real bug was caused by an empty category query string, so I changed the test to reproduce the actual failure.

## Deviations from PLAN.md

The main plan stayed the same. The biggest adjustment was adding extra stability tests for health response shape, review console behavior, and matching-engine behavior after the implementation.