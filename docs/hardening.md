# Hardening (ongoing)

- ✅ **Protect the published data from partial runs.** Done 2026-09-24: if the API fails partway through, the run stops before writing any files and the map keeps the previous data. The photo limit was also raised from 1,600 to 16,000.
- ✅ **Retries for page requests.** Done 2026-09-24: each page gets up to 3 retries, waiting 2, 4, then 8 seconds, for network errors, HTTP 429, and HTTP 5xx. If a page still fails, the run stops and the map keeps the previous data.
- ✅ **Log in again on HTTP 401.** Done 2026-09-25, after a token was rejected part-way through a run.
- ✅ **Stable output.** Done 2026-09-25: each photo's `groups` are sorted, so unchanged data no longer produces large commits.
- ✅ **Workflow push race.** Done 2026-09-25: the workflow rebases onto `main` before pushing its data commit.
- Write the GeoJSON atomically, so an interrupted run can't leave a half-written file.
- Add automated tests for tag parsing and crosswalk matching.
- Validate coordinates and the GeoJSON structure before publishing.
- Improve map accessibility: keyboard support, screen reader labels, and a text summary of the data.
- Show clear messages if the basemap or data fails to load.
- Simplify the two copies of the GeoJSON into one.
