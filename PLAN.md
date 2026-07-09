# Implementation Plan

## Goal

My goal is to finish the SpecMatch challenge by first understanding the existing code, then adding the matching logic and fixes without breaking the current API contracts.

I want the final version to be simple, tested, and easy for me to explain in the walkthrough call.

## Order of work

1. Run the app with Docker.
2. Open the record table and API docs.
3. Run the existing tests.
4. Read the main files for routes, ingest, settings, templates, tests, and matching.
5. Commit `ARCHITECTURE_NOTES.md` and `PLAN.md` before any code changes.
6. Fix the known issues.
7. Build the matching engine.
8. Connect match results to the API and review page.
9. Add or update tests.
10. Run all tests again.
11. Push to GitHub and check that CI is green.
12. Update the README.

## Matching approach

I plan to keep the matching logic simple and explainable.

First, I will clean the text by lowercasing it, removing extra punctuation, and standardizing spacing.

Then I will compare each source record with catalog records. I will use a few signals:

- text similarity
- category match
- unit match

The final score should use the weights and thresholds from `config/settings.yaml`.

Based on the score, the result should be:

- high confidence: auto-accept
- medium confidence: needs review
- low confidence: reject or no strong match

## Why this approach

The challenge is only 8–12 hours, so I do not want to overbuild it. A simple matching system is easier to test, debug, and explain.

## Risks

- Changing the frozen schema file by mistake
- Misunderstanding an API contract
- Hardcoding values instead of using settings
- Edge cases around confidence thresholds
- Docker or GitHub Actions behaving differently
- Making the solution too complicated

## Time plan

- Setup and tests: 1 hour
- Reading the code: 2 hours
- Notes and plan: 1–2 hours
- Matching logic and fixes: 5–6 hours
- Tests and debugging: 2 hours
- README and final cleanup: 1–2 hours

## AI tool usage

I will use AI tools to help me understand the code, plan the work, debug errors, and improve tests or documentation.

I will review everything before using it and make sure I understand the final code.