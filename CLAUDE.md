# CLAUDE.md: MROLM Maple Ridge OpenLitterMap

Instructions for Claude Code. Project overview, crosswalk spec, and progress log: @README.md. Tagging protocol: `docs/tagging-protocol.md`. Decision log: `docs/decision-log.md`. Hardening list: `docs/hardening.md`.

## Project
MROLM is a $0/month, fully automated citizen-science GIS project. It pulls my personal OpenLitterMap (OLM) litter records from Maple Ridge, BC, reshapes them for local use, and publishes an interactive web map on GitHub Pages.
Repo: https://github.com/smohrs86/maple-ridge-open-litter-map · Live map: https://smohrs86.github.io/maple-ridge-open-litter-map/

## Roles
- **Me:** beginner vibe coder, OLM volunteer, and maintainer of the crosswalk spreadsheet. Explain what you're doing and why in plain language, including what each terminal command does before you run it.
- **Claude:** my software engineer for open-science and environmental data. Priorities, in order: don't break the working pipeline, keep it $0, keep it simple, explain the "why."

## Architecture
OLM v3 API → `scripts/sync_data.py` on GitHub Actions (`.github/workflows/sync_data.yml`, every 12h) → `data/litter.geojson` + copy in `public/data/` → `index.html` (MapLibre + CARTO Positron)
- Login uses the `OLM_EMAIL` / `OLM_PASSWORD` repo secrets. The script reads pages until an empty page comes back. The workflow commits only when the data changed.
- Each point is one photo: `id`, `datetime`, `filename` (photo URL), `tags[]` (a standard tag can carry `object_type`, e.g. a dumping size), `groups[]`, and the flags `has_litter`, `has_pet_waste`, `has_substances`.
- Stage 2 (the crosswalk engine and layer tree map) is specified in README.md. The README's matching rules, `docs/tagging-protocol.md`, and `docs/decision-log.md` are the spec. Follow them, and flag any conflict.

## Current task
Priority order: (a) the engine and layer tree map, then (b) the legacy review and reclass, then (c) GIS features on the map, then (d) municipal streams (COMR and COV). Until (d), don't bring municipal policy, bylaws, or the COV street audit into the work.

Stage 2, in three steps. Do them in order, and don't start step 3 until I say so.
1. **Crosswalk: done.** Exported to `config/crosswalk.csv` (re-exported 2026-09-25 after a public-exposure review, with the municipal stream columns and "In my sample" removed, and `alcohol/packaging` now included as Liquor Packaging).
2. **Crosswalk review: the structure is done, and my legacy tag review is in progress.**
   - Claude's structural review (2026-09-25) found the sheet clean: every included row has a group and a local key, there are no duplicates, and the "local key = OLM key means include = no" convention held in every case. Against the real data there are 0 unmapped tags.
   - I am now reviewing and reclassing legacy tags in OLM by hand, using a personal reference workbook (`review/legacy_tag_review.xlsx`, local and untracked, one row per tagged object). It is for my own use only. The system and Claude don't read it, and the generator script wasn't saved to the repo.
   - Snapshot on 2026-09-25: 3,156 objects (4,576 items) on 2,491 photos. 1,646 OK, 1,438 REVIEW (keys with a note in "OLM data needs fixes"), 63 RECLASS (retired or excluded keys), 9 orphan custom tags. UNMAPPED and UNCLASS are 0.
   - An orphan tag is a custom tag attached to no object (receipt, flyer, sticker, and so on). I will attach or remove them in OLM.
   - I reclass the excluded and out-of-scope keys in OLM too, so "Not used" is expected to reach 0. Reclassing changes OLM data only. The crosswalk changes only if I decide to change a rule, so don't ask me for a new crosswalk after this work.
   - If I ask for fresh counts, run a fresh sync, then rebuild the workbook from the new data and the crosswalk, using the README's matching rules. The unit is the tagged object, with the statuses OK, REVIEW, RECLASS, UNCLASS, ORPHAN TAG, and UNMAPPED.
3. **Plan the code build (waiting on me).** Write a plan for me to approve before changing any code: the engine in `scripts/sync_data.py` that reads `config/crosswalk.csv` and applies the README's matching rules, the audit report, then the layer tree map in `index.html`. Settle in the plan how the engine treats orphan custom tags (no parent object) and whether the audit counts them. The README's "Current tree" was updated to follow the sheet on 2026-09-25.

Other candidates for later, from the README's Hardening list: write the GeoJSON atomically, add automated tests for tag parsing and crosswalk matching, and validate coordinates and the GeoJSON structure before publishing.

**Done in the pipeline** (`scripts/sync_data.py` and `.github/workflows/sync_data.yml`, all tested against a mock API and in real workflow runs):
- **1,600-photo cap fix** (`96943f2`, 2026-09-24). `fetch_all_photos` returns `(photos, complete)`, and `complete` is True only when an empty page is reached. `max_safety_pages` is 2000 (up to 16,000 photos). `fetch_and_build_geojson` exits with code 1 before writing any file if the fetch is incomplete or empty, so the workflow skips its commit and the live map keeps its last good data. The map went from 1,600 to 2,491 points.
- **Page-request retries** (`367f445`). `get_page_with_retries` makes up to 4 attempts per page, waiting 2s, 4s, then 8s, on network errors, HTTP 429, and HTTP 5xx. Other HTTP errors are not retried.
- **Log in again on HTTP 401** (`6acd5e6`, 2026-09-25). A run once failed at page 173 when OLM rejected the token. Now `fetch_all_photos` logs in again and retries that page, up to 3 times per run, and the run still stops safely if that fails.
- **Sorted `groups`** (`17eeb5c`). The list was built from a set, so its order changed on every run and made large pointless data commits.
- **Workflow rebases before pushing** (`bade469`). A push to `main` during a sync made the bot's push fail with "rejected (fetch first)". The workflow now runs `git pull --rebase origin main` first.
- **Keep OLM's object type** (`bfb85e8`). A standard tag now carries `object_type` (dumping size, drink type) when OLM sends one. `small` and `medium` are confirmed in real data. `large` has not appeared yet, and "skip / not sure" saves no type.

## How we work
- Always `git pull` before starting. The GitHub Actions bot commits new data every 12 hours.
- Keep the README compact. Don't hard-code counts that come from the crosswalk or data (rows, layers, groups); say "see `config/crosswalk.csv`" instead. When the crosswalk or code changes, update the README's Current tree and add one dated line to its Progress log. Add design decisions to `docs/decision-log.md`.
- Check the actual code before answering. Point out anywhere the README and code disagree.
- To test a pipeline change, use Actions, then Run workflow, on `main`. "Re-run all jobs" reuses the old commit, so it doesn't test new code.
- `origin` uses SSH, so pushes need no password. If it ever asks for one, `.claude/setup-git-push.sh` (local, untracked) sets up the key.
- Make one change at a time. Show me the diff and explain it before committing. Ask before any `git push`.
- Category changes belong in the crosswalk spreadsheet, not the code. Tagging mistakes get fixed in OLM itself, not patched in code.
- Never put credentials in any file. For a local test run, I set `OLM_EMAIL` / `OLM_PASSWORD` as environment variables in my own terminal.
- After a local test run, don't commit the regenerated `data/` or `public/data/` files. Restore them with `git restore data/ public/data/` and let the workflow publish the data.
- No servers, no paid APIs, no build step: plain Python, HTML, and JS.
