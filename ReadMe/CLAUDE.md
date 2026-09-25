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
Fix the 1,600-photo cap in `scripts/sync_data.py`.
- **Problem:** `max_safety_pages = 200` and OLM returns 8 photos per page, so the fetch stops at 1,600 photos and publishes them. The oldest photos drop off the map as new ones are added. The data had 2,168 points on 2026-09-18; every sync since 2026-09-19 has had exactly 1,600. A sync on 2026-09-19 also published a partial fetch of 1,472.
- **Fix (planned, tested against a mock API in a Claude.ai chat):**
  - `fetch_all_photos` returns `(photos, complete)`. `complete` is True only when an empty page is reached. An HTTP error, a network error, or hitting the cap returns False.
  - Raise `max_safety_pages` to 2000 (up to 16,000 photos).
  - In `fetch_and_build_geojson`, if the fetch is not complete or returned 0 photos, print an error and `sys.exit(1)` before writing any files. The workflow then stops before its commit step, so the live map keeps its last good data.
- **Next after this:** retries with increasing wait times for page requests.

## How we work
- Always `git pull` before starting. The GitHub Actions bot commits new data every 12 hours.
- Check the actual code before answering. Point out anywhere the README and code disagree.
- Make one change at a time. Show me the diff and explain it before committing. Ask before any `git push`.
- Category changes belong in the crosswalk spreadsheet, not the code. Tagging mistakes get fixed in OLM itself, not patched in code.
- Never put credentials in any file. For a local test run, I set `OLM_EMAIL` / `OLM_PASSWORD` as environment variables in my own terminal.
- After a local test run, don't commit the regenerated `data/` or `public/data/` files. Restore them with `git restore data/ public/data/` and let the workflow publish the data.
- No servers, no paid APIs, no build step: plain Python, HTML, and JS.
- Verify bylaw and policy citations before they go in anything shared with the City.
