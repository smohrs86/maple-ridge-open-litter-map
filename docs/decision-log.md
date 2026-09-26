# Decision log

Key design decisions, so the reasoning isn't lost.

| Date | Decision | Why |
|---|---|---|
| 2026-09 | Classification rules live in a spreadsheet (the crosswalk), not in code | The maintainer can change categories without programming |
| 2026-09 | Most specific crosswalk row wins; unlisted modifiers flatten to the plain row | Keeps the sheet small while allowing detail where it matters |
| 2026-09 | Household dumping sizes (small, medium, large) are separate layers | Small items and large loads are different problems, so they need separate counts |
| 2026-09 | A permanent `UNCLASS` row catches dumping photos without a size | Nothing is silently lost; it works whatever code OLM uses for "not sure" |
| 2026-09 | Column `include on map` is the only on/off switch; "local key = OLM key" is a consistency check | Two competing rules would contradict each other |
| 2026-09 | Audit counts for "not used" and "unmapped" | Data problems become visible numbers instead of silent gaps |
| 2026-09 | Liquor packaging reclassified: boxes to `food/box`, whole items to `food/packaging`, pieces by material | Cannabis packaging moved to smoking + `THC`; the alcohol key was inconsistent |
| 2026-09 | The "low occurrence" group is retired; rare items join their logical parent | Richer data: a bottle cap belongs with drinks, not in a miscellaneous pile |
| 2026-09 | Three-level layer tree: Group → Subgroup → Layer | Some topics (like straws or drinks) need a middle level; others don't |
| 2026-09 | Map counts are items, not photos | One photo can hold many items; photo counts go in the audit |
| 2026-09-25 | The municipal stream columns (Maple Ridge name, Maple Ridge stream, Vancouver audit category) and "In my sample" were removed from the crosswalk, and `alcohol/packaging` was made an included layer, Liquor Packaging | The crosswalk was reviewed before public release. Stream columns were redundant and confusing at this stage and will be rebuilt one at a time in Stage 4. "In my sample" came from a check made when a paging error had cut the data pull short, and the full data set makes it unnecessary |
| 2026-09-24 | An incomplete or empty fetch fails the sync instead of publishing partial data | A 200-page cap had silently cut the map to 1,600 photos; a failed run leaves the last good data live |
| 2026-09-24 | Page requests retry with increasing waits (2s, 4s, 8s) on network errors, 429, and 5xx | Brief hiccups shouldn't waste a 12-hour run |
| 2026-09-25 | If OLM rejects the login token (HTTP 401) mid-run, log in again and retry the page, up to 3 times per run | A token was rejected at page 173 of 313 and the run had to stop; a fresh login recovers it |
| 2026-09-25 | The workflow runs `git pull --rebase` before pushing its data commit | A push to `main` during a sync made the bot's push fail and lost that run's data |
| 2026-09-25 | Each photo's `groups` list is sorted | A set gave a random order every run, causing large pointless data commits |
| 2026-09-25 | OLM's object type is kept as `object_type` on standard tags, and the crosswalk's "with Secondary Modifier" column matches against it. "Skip / not sure" saves no type and falls to the blank row | Dumping sizes and drink types were being dropped |
| 2026-09-25 | Build order: crosswalk engine and layer tree map, then legacy review and reclass, then GIS map features, then municipal streams | The review is the biggest human effort and the streams depend on a finished tree and conformed data |
| 2026-09-25 | Claude maintains the REVIEW backlog workbook after the maintainer's OLM edits, and the audit reports orphan tags on their own line, separate from unmapped | The backlog is too large to work by hand, and orphan tags are tagging errors fixed in OLM, while unmapped means a gap in the crosswalk |
| 2026-09-25 | Legacy tag review is done per tagged object, and retired, excluded, and orphan tags are reclassed in OLM | Counts are items, not photos, and fixes happen at the source |
| 2026-09-25 | Work happens directly on `main`: local copy, local test, then push. No feature branches, staging site, or preview deploys | Branches are confusing to track for a solo beginner, and a display error on the public map carries no data risk. Free GitHub Pages sites are always public, so a private test site is not possible at $0 |
| 2026-09-25 | Audit control and reporting rank above deployment safety. Data-shape changes are additive, or the workflow is run right after the push | The value of the project is data that can be confirmed clean. The map can lag the data by up to 12 hours, so old and new shapes must both work in the meantime |
