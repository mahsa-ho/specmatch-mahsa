# Contributing conventions

These conventions are enforced in review. Existing code follows them; new
code must too.

## Commits

- Imperative subject line, max 72 characters ("Add tier filter to matches
  endpoint", not "Added..." or "adds...").
- One logical change per commit. Tests that reproduce a bug are committed
  **before** the commit that fixes it.
- Reference issues in the body or subject with `#N` (e.g. `Fixes #2`).

## Logging

- Every log line is a structured event emitted through
  `app.core.logging.log_event(logger, level, event, **fields)`.
- `event` is a snake_case identifier (`ingest_completed`, `review_persisted`).
  All context goes in keyword fields — never interpolate values into the
  event string.
- Do not use `print()` or bare `logger.info("did a thing: %s", x)`.

## Error handling

> Every call to an external dependency (filesystem, network, subprocess,
> database file) must catch the dependency's specific exception type at the
> call site, log a structured `dependency_failure` event that includes the
> dependency name and enough context to reproduce, and re-raise as
> `app.core.errors.DependencyError` using `raise ... from exc`.

Never swallow a dependency failure, and never let a raw `OSError` (or
similar) escape a service function.

## Configuration

- Scoring weights and tier thresholds live in `config/settings.yaml` and are
  read through `app.config.get_settings()`. They must never be hardcoded.
- `backend/app/models/schemas.py` is frozen. CI fails if it changes.

## Code style

- Type annotations on all public function signatures.
- FastAPI routers stay thin: request/response handling only, logic in
  `services/`.
