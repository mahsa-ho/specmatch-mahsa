# Architecture Notes

## My understanding

SpecMatch is a FastAPI app that matches messy construction material records with a clean catalog.

The problem is that construction records are often written in short or inconsistent ways, like abbreviations, missing details, or different formats. Because of that, exact text matching is not enough.

The app loads source records and catalog data from CSV files, then shows the records through API routes and browser pages. The matching part should compare each messy record to catalog items and decide if the match is confident or needs review.

## Record flow

A record starts from:

```text
data/source_records.csv
```

The catalog starts from:

```text
data/catalog.csv
```

From what I saw, the flow is:

```text
data/source_records.csv
→ backend/app/services/ingest.py
→ app startup / data loading
→ GET /records
→ record table page
→ matching service
→ GET /matches
→ review page
```

The ingest service loads the CSV data when the app starts. The `/records` route shows the source records. The `/matches` route is for match results. The browser pages show the record table and review panel.

## API routes

I saw these routes in the FastAPI docs:

```text
GET /health
GET /records
GET /matches
POST /matches/{record_id}/review
GET /
GET /review
```

## Tier thresholds

The match thresholds are in:

```text
config/settings.yaml
```

This means the accept/review/reject boundaries can be changed from the config file instead of changing Python code.

My understanding is:

```text
high score → auto-accept
medium score → human review
low score → reject / no good match
```

If I wanted fewer auto-accepted matches, I would increase the accept threshold in `settings.yaml`.

## Frozen file

The challenge says this file should not be changed:

```text
backend/app/models/schemas.py
```

I will not edit it because it defines the API contracts and CI checks it.

## Error handling

`CONTRIBUTING.md` says external dependency failures should be handled clearly. The app should log useful information and raise the project’s dependency error instead of failing silently.

One example is in `backend/app/services/ingest.py`, where CSV/file reading errors are caught, logged, and re-raised as a dependency error.

## Notes for my implementation

I should keep the routes simple and put most logic inside services. I should also use `settings.yaml` for thresholds and weights instead of hardcoding values in Python.