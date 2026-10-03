# Hardening (ongoing)

- ✅ **Protect the published data from partial runs.** Done 2026-09-24: if the API fails partway through, the run stops before writing any files and the map keeps the previous data. The photo limit was also raised from 1,600 to 16,000.
- ✅ **Retries for page requests.** Done 2026-09-24: each page gets up to 3 retries, waiting 2, 4, then 8 seconds, for network errors, HTTP 429, and HTTP 5xx. If a page still fails, the run stops and the map keeps the previous data.
- ✅ **Log in again on HTTP 401.** Done 2026-09-25, after a token was rejected part-way through a run.
- ✅ **Stable output.** Done 2026-09-25: each photo's `groups` are sorted, so unchanged data no longer produces large commits.
- ✅ **Workflow push race.** Done 2026-09-25: the workflow rebases onto `main` before pushing its data commit.
- ✅ **Atomic writes.** Done 2026-10-03: the GeoJSON copies and the audit are written to a temporary file and swapped in with `os.replace`, so an interrupted run can't leave a half-written file (`write_atomically` in `scripts/sync_data.py`, tested in `tests/test_atomic_write.py`).
- ✅ **Automated tests for crosswalk matching and the engine.** Done 2026-09-26: `tests/` covers the matching rules, object extraction from both OLM tag formats, picked-up states, map visibility, the audit report, and crosswalk loading. The older Stage 1 tag flattening (`tags`) is not yet tested.
- Validate coordinates and the GeoJSON structure before publishing, and report anything dropped in the audit.
- Record which crosswalk version (for example its file hash) produced each audit report, so any number on the map can be traced back.
- Improve map accessibility: keyboard support, screen reader labels, and a text summary of the data.
- Show clear messages if the basemap or data fails to load.
- Simplify the two copies of the GeoJSON into one.
