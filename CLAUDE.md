# CLAUDE.md: MROLM Maple Ridge OpenLitterMap

Instructions for Claude Code. Project overview, crosswalk spec, tagging protocol, and decision log: @README.md

## Project
MROLM is a $0/month, fully automated citizen-science GIS project. It pulls my personal OpenLitterMap (OLM) litter records from Maple Ridge, BC, reshapes them for local use, and publishes an interactive web map on GitHub Pages.
Repo: https://github.com/smohrs86/maple-ridge-open-litter-map · Live map: https://smohrs86.github.io/maple-ridge-open-litter-map/

## Roles
- **Me:** beginner vibe coder, OLM volunteer, and maintainer of the crosswalk spreadsheet. Explain what you're doing and why in plain language, including what each terminal command does before you run it.
- **Claude:** my software engineer for open-science and environmental data. Priorities, in order: don't break the working pipeline, keep it $0, keep it simple, explain the "why."

## Architecture
OLM v3 API → `scripts/sync_data.py` on GitHub Actions (`.github/workflows/sync_data.yml`, every 12h) → `data/litter.geojson` + copy in `public/data/` → `index.html` (MapLibre + CARTO Positron)
- Login uses the `OLM_EMAIL` / `OLM_PASSWORD` repo secrets. The script reads pages until an empty page comes back. The workflow commits only when the data changed.
- Each point is one photo: `id`, `datetime`, `filename` (photo URL), `tags[]`, `groups[]`, and the flags `has_litter`, `has_pet_waste`, `has_substances`.
- Stage 2 (the crosswalk engine and layer tree map) is specified in README.md. The README's matching rules, tagging protocol, and decision log are the spec. Follow them, and flag any conflict.

## Current task
Stage 2, in three steps. Do them in order and don't start the next step until I say so.
1. **I finish the crosswalk** in my Google Sheet. Nothing for Claude to do yet. When I'm done, I'll export it as `config/crosswalk.csv` (or give you the file's path).
2. **We review the crosswalk together.** Check it against the README rules: every included row has a Group and a local key, no Subgroup is missing its Group, no duplicate or conflicting rows, and `include on map = no` agrees with the "local key = OLM key" convention. Report problems; don't fix the sheet yourself.
3. **We plan the code build.** Write a plan for me to approve before changing any code: the engine in `scripts/sync_data.py` that reads `config/crosswalk.csv` and applies the README's matching rules, the audit report, then the layer tree map in `index.html`.

Other candidates for later, from the README's Hardening list: write the GeoJSON atomically, add automated tests for tag parsing and crosswalk matching, and validate coordinates and the GeoJSON structure before publishing. Known bug: `groups` in `build_photo_properties` is built from a set, so its order changes on each run and can cause unnecessary data commits (fix: `sorted()`).

**Done: page-request retries** (commit `367f445`, 2026-09-24). `get_page_with_retries` in `scripts/sync_data.py` makes up to 4 attempts per page (the first try plus 3 retries), waiting 2s, 4s, then 8s. It retries on network errors, HTTP 429, and HTTP 5xx, and does not retry other HTTP errors (401, 404). If every attempt fails, `fetch_all_photos` returns `complete=False` and the safety guard stops the run. Tested against a mock API; a real workflow run still needs to be checked.

**Done: the 1,600-photo cap fix** (commit `96943f2`, 2026-09-24). `fetch_all_photos` returns `(photos, complete)`, and `complete` is True only when an empty page is reached. `max_safety_pages` is 2000 (up to 16,000 photos). `fetch_and_build_geojson` exits with code 1 before writing any files if the fetch is incomplete or empty, so the workflow skips its commit and the live map keeps its last good data. The next workflow run brought the map from 1,600 to 2,491 points.

## How we work
- Always `git pull` before starting. The GitHub Actions bot commits new data every 12 hours.
- Check the actual code before answering. Point out anywhere the README and code disagree.
- Make one change at a time. Show me the diff and explain it before committing. Ask before any `git push`.
- Category changes belong in the crosswalk spreadsheet, not the code. Tagging mistakes get fixed in OLM itself, not patched in code.
- Never put credentials in any file. For a local test run, I set `OLM_EMAIL` / `OLM_PASSWORD` as environment variables in my own terminal.
- After a local test run, don't commit the regenerated `data/` or `public/data/` files. Restore them with `git restore data/ public/data/` and let the workflow publish the data.
- No servers, no paid APIs, no build step: plain Python, HTML, and JS.
- Verify bylaw and policy citations before they go in anything shared with the City.
