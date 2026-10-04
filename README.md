# MROLM · Maple Ridge Open Litter Map

**An interactive web map of citizen-science litter records from Maple Ridge, British Columbia, updated automatically from OpenLitterMap.**

**Live map:** https://smohrs86.github.io/maple-ridge-open-litter-map/

Litter is photographed and tagged in the field using [OpenLitterMap](https://openlittermap.com) (OLM), an open citizen-science platform. MROLM is an independent volunteer project, not part of OpenLitterMap. It pulls those records from the OLM API every 12 hours, sorts each tagged item into local litter categories, and publishes the result as a free, interactive web map. The goal is good open data for citizen science: a consistent, well-documented record of where litter is, what it is, and how that changes over time.

> **Status: proof of concept achieved (2026-09-27).** The map is live and updates automatically. Refinements are ongoing: older tags in OpenLitterMap are still being cleaned up, so some categories will shift as that's finished.

**Contact:** questions, interest in contributing, or data inquiries: mrolm.unsaved516@simplelogin.com

---

## Project status at a glance

| Area | Status | Notes |
|---|---|---|
| Data pipeline (OLM API → GeoJSON) | ✅ Built | Runs automatically every 12 hours |
| Public web map | ✅ Built | MapLibre map on GitHub Pages |
| Crosswalk logic and layer tree design | ✅ Designed | Exported to `config/crosswalk.csv`. Structure reviewed and clean |
| Crosswalk engine (code that applies the crosswalk) | ✅ Built | Reads `config/crosswalk.csv` on every sync and writes an audit report, `data/audit.md` |
| Layer tree map interface | ✅ Built | Group → Subgroup → Layer checkboxes, picked-up rings, date filter, popups |
| GIS features on the map | ✅ Built | Stage 3 complete 2026-10-03: a neighbourhood total, then numbered clusters, then dots by zoom level, neighbourhood and zone views with hover cards, date selection, and a Reset filters button |
| Municipal waste stream | ⬜ Only if COMR takes part | A view in the City of Maple Ridge's own litter categories, built only if the City publishes or uses them (Stage 4) |
| Cleanup of older tags in OLM | ✅ Done | The maintainer reviewed every photo and reclassed legacy tags in OLM (roadmap step 4), completed 2026-10-02 |

---

## Proof of concept: achieved (2026-09-27)

The proof of concept asked one question: can litter records made with OpenLitterMap's global tagging schema be translated into local terms, with a crosswalk the maintainer controls as the tool that manages the local schema? It can. The live map shows every tagged item in local categories, and changing a category means editing the crosswalk, not the code.

The original criteria, with 5 and 8 moved to refinements because they improve quality rather than test the idea (5 was completed 2026-10-02):

1. ✅ **The engine applies the crosswalk.** Every run reads `config/crosswalk.csv` and puts each tag into exactly one layer, following the matching rules below. Unmapped = 0.
2. ✅ **The audit report is published on every run**, with the counts in the audit table below. Tie-breaks are reviewed and either fixed in the crosswalk or accepted.
3. ✅ **The layer tree works on the live map:** Group → Subgroup → Layer checkboxes that cascade, item counts that roll up, empty layers hidden, and full layer names in popups.
4. ✅ **Counts are spot-checked.** For about five layers, the map count matches a manual count of the same tags in OLM.
5. ✅ **Legacy data is conformed enough to trust** (completed 2026-10-02, after a full photo review and 166 photos retagged in OLM). Not used = 0 and UNCLASS = 0. Orphan tags are tracked in the audit with their photo IDs and fixed in OLM, or accepted as a known gap. The REVIEW backlog is tracked by Claude, which rebuilds the review workbook after the maintainer's OLM edits, and its remaining count is recorded in the progress log at each check.
6. ✅ **The pipeline stays safe.** An incomplete fetch leaves the last good data live, and the tree map data is produced by the workflow without manual fixes.
7. ✅ **A basic test exists** for crosswalk matching: a specific row beats the plain row, blank falls back, capitals and spacing are ignored, and the first match wins.
8. ➡️ *Refinement:* **A newcomer can understand it in five minutes.** The README opens with what the map shows, and the live link works.

Not part of the proof of concept: GIS features, municipal streams, a license, and a contributor guide.

---

## Progress log

Newest first, one line per change. Claude updates this whenever it updates the README.

- **2026-10-03:** Crosswalk re-exported after the legacy review: the "OLM data needs fixes" notes were cleared and other notes tidied, so every object now shows as OK (REVIEW = 0). No rule changes (group, subgroup, local key and include are unchanged on every row).
- **2026-10-03:** Stage 3 declared complete. Richer popups were confirmed achieved; the design review leftovers (colour, footer wording, contrast) were set aside on purpose.
- **2026-10-03:** Map areas ticks now filter the data (dots, clusters, counts, neighbourhood totals), not just the shaded overlay. The neighbourhood hover tag waits for the clusters, so it no longer doubles the bubble's name.
- **2026-10-03:** Hardening: the map now says so when something fails to load: a blocked map library, the basemap (or slow loading), the data (failed or empty, with the reason) and missing basemap tiles, each as one dismissible message, with Reload where it helps.
- **2026-10-03:** Hardening: accessibility first pass. The panel and map have names, the item count is announced when a filter changes, and a folded "Summary in words" section gives the same facts as plain text. Dots are still mouse and touch only.
- **2026-10-03:** Hardening: tests added for the older Stage 1 tag flattening and group rules (`tests/test_tags.py`). No code change.
- **2026-10-03:** Hardening: the audit now records a short fingerprint (SHA-256) of `config/crosswalk.csv`, so any number can be traced to the crosswalk that produced it.
- **2026-10-03:** Hardening: the sync checks each photo's coordinates (missing, not a number, off the globe, or 0, 0) and drops bad ones with their IDs in the audit; it also checks the GeoJSON's structure and stops before writing if it fails. A clean run's output is unchanged.
- **2026-10-03:** Hardening: the sync now writes the GeoJSON copies and the audit atomically (temporary file, then swap), so an interrupted run can't leave a half-written file. Palette-validator item dropped from `docs/hardening.md` as not worth the cost.
- **2026-10-03:** Heatmap and the Dots | Heatmap switch removed. Zoom decides the view: a total per neighbourhood when zoomed out, numbered clusters (items, following every filter) in the middle, and the dots when zoomed in. Tapping a bubble or cluster zooms in.
- **2026-10-02:** iPhone improvements, tested on the maintainer's phone: bigger tap targets and 16 px date inputs on touch screens (so Safari no longer zooms on focus), and a "Reset filters" button at the top of the panel that puts layers, dates, areas, "Left in place only" and the Dots view back to how the page loads.
- **2026-10-02:** Panel folds into sections (Litter layers open; Dates and Map areas folded, with a status on each summary line), the shaded areas get a one-line explanation and a pointer cursor.
- **2026-10-02:** Date selection: a tick list of collection days, month and weekday/weekend chips, presets, and From/To all edit one set of selected days; the map, the layer counts and the area cards follow it.
- **2026-10-02:** Map gets neighbourhood and zone views: a checkbox tree in the panel, zoom chooses which shows, zones lettered A at the top, and a label and one card that appear only on hover or tap (method in [docs/zones-method.md](docs/zones-method.md)). The sync adds `zone`, `zone_edge_m` and `nbhd_edge_m` to each photo from `config/neighbourhoods.csv` and `config/zones.csv`; dots are not moved. Zone tests added. A density score was considered and dropped.
- **2026-10-02:** Roadmap changed. Stage 3 zone summaries will use the City of Maple Ridge's neighbourhoods (source notes in [docs/maple-ridge-community-areas.md](docs/maple-ridge-community-areas.md)). Stage 4 now happens only if COMR publishes or uses litter categories and takes part, and there is no stream for any other city.
- **2026-10-02:** Legacy review complete. 166 photos retagged in OLM from the maintainer's review page edits (one test photo, a batch of 10, then 155), each read back exactly as sent; the fresh export matches the plan for all 166. Check after the export (2,814 photos, 3,488 tagged objects): OK 1,835, REVIEW 1,653 (keys that carry a fix note, all reviewed), RECLASS 0, orphan tags 0, UNMAPPED 0, UNCLASS 0. The merge step now rejects unrecognised `[bracket]` words.
- **2026-10-02:** Review workbook has a `Reviewed` date column (`--reviewed-through`); full photo review pass done, with personal-information photos deleted in OLM. Tagging protocol adds the photo order of preference and contact-detail items (business cards, garage sale signs).
- **2026-10-02:** Tagging protocol: where litter is collected, what is picked up, a close-up photo method with no personal details in frame, and private-property problems and waterways out of scope.
- **2026-09-28:** Review page: a "New quantity" field per object, merged into the workbook's `Change_to_Quantity` column.
- **2026-09-28:** Second batch of legacy tags fixed in OLM: 82 photos (92 objects), from the maintainer's review page edits, each read back exactly as sent. Legacy review check after a fresh export (2,835 photos, 3,522 tagged objects): REVIEW 1,665, RECLASS 37, orphan tags 0, UNMAPPED 0, UNCLASS 0.
- **2026-09-28:** Batch quantity changes: the review workbook has a `Change_to_Quantity` column, and the dry run allows a quantity change only when that column asks for one. Added because quantity edits on OLM's website often didn't save.
- **2026-09-28:** Tagging protocol: the custom tag `Piece` is no longer used; pieces are identified by key through the crosswalk.
- **2026-09-28:** Crosswalk: Butane Lighter (`smoking/lighters`) is now for whole lighters only; lighter pieces are tagged by material or as E-waste (see `docs/tagging-protocol.md`).
- **2026-09-28:** Local review page (`scripts/build_review_page.py`): one card per photo with its objects' tags, status, and fix notes, editable change fields, and filters. Edits are exported from the browser and merged into the review workbook by `scripts/merge_review_edits.py`, which reports first and skips conflicts. Never published.
- **2026-09-28:** Local photo gallery for the legacy review (`scripts/build_photo_gallery.py`): every photo with its ID and date, searchable by ID, date range and OLM key. It is built from the raw export and never published.
- **2026-09-28:** First batch of legacy tags fixed in OLM through the API: 19 `alcohol/packaging` objects reclassed (18 to Cannabis Packaging, 1 to `food/bag`) after a dry run, a one-photo test, and a small batch, each photo read back and still public. New tools: an offline dry run and a one-photo send with backup, read-back, and undo ([method](docs/olm-batch-review-method.md)). Legacy review check after a fresh export (2,836 photos, 3,520 tagged objects): REVIEW 1,648, RECLASS 41, orphan tags 9, UNMAPPED 0, UNCLASS 0.
- **2026-09-27:** Contact email added for questions, contributors, and data inquiries.
- **2026-09-27:** Map panel gets a one-line plain-text summary linking to this repository, and the page names its official address (canonical link) for search engines.
- **2026-09-27:** Licenses added: MIT for the code, ODbL 1.0 for the data (as OpenLitterMap requires), with "© OpenLitterMap & Contributors" now credited on the map.
- **2026-09-27:** README opening rewritten so search engines and link scrapers see what the map is first: the live link and an "independent project" line. Proof of concept declared achieved; legacy cleanup (criterion 5) and the newcomer read-through (8) continue as refinements.
- **2026-09-27:** Map gets a favicon, a link-preview image (title card beside the real litter points), and a page description, so shared links show a proper preview card.
- **2026-09-26:** Map gets a Dots | Heatmap switch (heat weighted by items, fading into the dots at street level), a "Left in place only" filter for both views, and an MROLM title block.
- **2026-09-26:** Spot check passed (proof-of-concept criterion 4). An independent recount from OLM's raw export matched the live map for Pet Waste Unbagged, Dumping – Sml, Cannabis Packaging, Wood Debris, and E-waste Piece. The maintainer's searches on the OLM website (`dogshit`, `dogshit_in`, `dumping`, custom `E-waste`) matched the predicted photo and tag totals exactly.
- **2026-09-26:** Stage 2 is live after the first push-triggered sync. The map now always checks for fresh data, so a new sync shows right away instead of after the browser's 10-minute cache.
- **2026-09-26:** Stage 2 engine and map built and tested locally: the sync applies the crosswalk to every tagged object, writes `data/audit.md`, and runs when the crosswalk changes. The map has the Group → Subgroup → Layer tree, group colour families, hollow rings for items left in place, a local-time date filter, and photo popups.
- **2026-09-26:** Legacy review check after a fresh export (2,680 photos, 3,355 tagged objects): REVIEW 1,574 (114 of them from newly uploaded photos on keys that carry a fix note), RECLASS 41, orphan tags 9, UNMAPPED 0, UNCLASS 0.
- **2026-09-26:** Crosswalk updated: tinfoil moves to Piece as Foil Piece, Organic Debris becomes "Organic Debris, Misc.", and a new E-waste Piece layer (`other/other` with custom tag `E-waste`) is added under Household. Notes were tidied for publication. Git now stores the crosswalk with plain line endings so re-exports only show real edits.
- **2026-09-26:** README now lists exactly which fields the pipeline publishes per point.
- **2026-09-26:** Review workbook builder and a shared, tested crosswalk matcher added (offline, read-only). The first build matched the earlier snapshot except for 22 objects moving between REVIEW and RECLASS.
- **2026-09-26:** Draft method for batch-fixing OLM tags through the API, with a review spreadsheet and a read-only raw export script: [docs/olm-batch-review-method.md](docs/olm-batch-review-method.md). Nothing has been written to OLM yet.
- **2026-09-25:** Working method recorded: work directly on `main`, test locally, no branches or staging site. Audit and reporting are the top priority for the engine build.
- **2026-09-25:** Crosswalk finished and re-exported after review; municipal stream columns removed. Pipeline now logs in again on a rejected token, keeps groups in a stable order, rebases before pushing, and keeps OLM's object type. Tagging protocol, decision log, and hardening list moved to `docs/`. Proof-of-concept criteria added.
- **2026-09-24:** Fixed the photo cap that had cut the map short; an incomplete fetch now fails the sync instead of publishing partial data. Page requests retry with increasing waits.
- **2026-09-17:** Stage 1 complete: automated 12-hour pipeline, GeoJSON output, and a basic filter map on GitHub Pages.

---

## Why this project exists

OpenLitterMap uses one global tagging system for litter everywhere in the world. That's what makes it powerful, but a global category like `other/plastic` or `dumping/dumping` doesn't answer local questions:

- Is dumping in Maple Ridge mostly small household items or large loads?
- Are single-use regulations (like the move to paper straws) showing up in what's actually found on the ground?
- Where are hazards like broken glass, vapes, and loose dog waste concentrated near trails and waterways?

MROLM adds a **local layer of meaning** on top of the OLM data, without changing the original data. Every local category traces back to an exact OLM tag, so the local view stays transparent and reproducible.

---

## How it works

```mermaid
flowchart LR
    A[Field photo<br/>tagged in OLM app] --> B[OpenLitterMap<br/>API v3]
    B --> C[GitHub Actions<br/>every 12 hours]
    C --> D[scripts/sync_data.py]
    D --> E[litter.geojson]
    E --> F[Web map<br/>index.html]
    X[config/crosswalk.csv] --> D
    D --> G[audit.md]
```

1. **Collect.** Litter is photographed, geotagged, and tagged in the OpenLitterMap app.
2. **Fetch.** A scheduled GitHub Actions workflow (`.github/workflows/sync_data.yml`) runs `scripts/sync_data.py`. The script logs in to the OLM API and requests photos page by page until an empty page comes back.
3. **Reshape.** Each photo's tags are flattened into a simple list. Material, brand, and custom tags stay linked to the item they describe.
4. **Classify.** The script reads `config/crosswalk.csv` and gives every tagged object its Group, Subgroup, and Layer, following the matching rules below. If the crosswalk is missing or a column it needs was renamed, the run stops before writing anything.
5. **Publish.** The result is saved as `data/litter.geojson` (plus a copy in `public/data/`), with the audit report in `data/audit.md`. The workflow commits them only if something changed. It also runs as soon as a new `config/crosswalk.csv` is pushed.
6. **Display.** `index.html` loads the GeoJSON into a MapLibre map with the layer tree, a date filter, and photo popups.

### What each map point contains

Each point on the map is one OLM photo. Its properties are:

| Property | Meaning |
|---|---|
| `id` | The OLM photo ID |
| `datetime` | When the photo was taken |
| `filename` | Link to the photo on OLM's storage |
| `tags` | Every tag on the photo, with `type` (standard, material, brand, custom_tag), `category`, `item`, and `quantity`. Standard tags may also carry `object_type`, the type OLM saved for the object (for example a dumping size or a drink type); it is absent when none was chosen. Material, brand, and custom tags also record `parent_category` and `parent_item`. |
| `objects` | One entry per tagged object, as classified by the crosswalk: `status` (OK, REVIEW, RECLASS, UNCLASS, ORPHAN TAG, or UNMAPPED), `on_map`, `group`, `subgroup`, `layer`, `full_name`, `olm_key`, `quantity`, and `picked_up` (true, false, or null when OLM didn't say). Orphan tags also list their `custom_tags`, and tie-breaks list the tied sheet rows in `tie_rows`. |
| `groups`, `has_litter`, `has_pet_waste`, `has_substances` | The Stage 1 broad groups and flags. No longer used by the map; kept so older copies of the map keep working |

The file also carries `mrolm_layers`, the full layer tree in display order.

---

## The crosswalk

Related docs: [field tagging protocol](docs/tagging-protocol.md) (how items are tagged in the field) and [decision log](docs/decision-log.md) (why the design is the way it is).

The crosswalk is the heart of Stage 2. It's a lookup table that says: *when a photo has this OpenLitterMap tag, treat it as this local object, and show it in this place on the map.*

It is maintained as a Google Sheet by the project maintainer. It is exported to `config/crosswalk.csv` in this repository. The pipeline reads that file on every run, so **changing the map's categories means editing the spreadsheet, not the code.** After an edit, the whole sheet is exported and pushed, and the map updates within minutes.

The local categories were built using the City of Vancouver litter audit and Maple Ridge municipal classifications as guides.

### Columns

The code reads columns **by their header name, not their position**, so columns can be added or reordered safely. Renaming a header requires a matching change in the code.

| Column | Used by | Purpose |
|---|---|---|
| OLM key | Code | The OLM category/item, e.g. `softdrinks/cup` |
| with Secondary Modifier | Code | Narrows the match to one app option, e.g. `small` |
| with Material tag | Code | Narrows the match to one material, e.g. `Wood` |
| with Custom Tag | Code | Narrows the match to one custom tag, e.g. `THC` |
| MROLM Group | Code | Top level of the map's layer tree, e.g. `Drinks` |
| MROLM Subgroup | Code | Optional middle level, e.g. `Hot` |
| MROLM local key | Code | The layer name: the checkbox that holds the data |
| include on map | Code | `yes` shows the row on the map; `no` sends it to the "not used" count |
| low occurance group | Retired | Replaced by the layer tree (see the [decision log](docs/decision-log.md)) |
| Notes, reason, OLM data needs fixes | People | Documentation and to-do notes; ignored by the code |

### Matching rules

For each tag on a photo, the engine finds exactly one crosswalk row:

1. **Most specific row first.** A row with a modifier, material, or custom tag that matches beats the plain row for that OLM key.
2. **Blank means "anything else."** If a tag has a modifier, material, or custom tag that isn't listed, it falls back to the row where that column is blank. For example, a `softdrinks/bottle` tagged "water" in the app matches the plain `softdrinks/bottle` row.
3. **Matching ignores capitals and extra spaces.** `THC`, `thc`, and `THC ` are treated as the same custom tag.
4. **First match wins.** If one tag matches two specific rows, the row higher in the sheet wins, and the audit report lists every case where this happened.
5. **Nothing is deleted.** Flattening only decides which layer an item appears in. The original material, brand, and custom tags stay in the data, so it remains possible to count, say, cold cups tagged as plastic.

### Audit counts

Every run writes a small audit report, [`data/audit.md`](data/audit.md), so data problems are visible instead of silent. It also lists REVIEW and Not used objects by OLM key, orphan tags and unmapped tags with photo IDs, crosswalk structure checks, and every layer's items, photos, and not-picked-up items:

| Count | Meaning | Healthy value |
|---|---|---|
| **Not used** | Tags matching a row with `include on map = no` (retired OLM keys) | 0, once older photos are fixed in OLM |
| **Unmapped** | Tags matching no row at all: a gap in the crosswalk | 0 |
| **UNCLASS** | Household dumping photos with no size chosen | 0, once older photos are given a size |
| **Standalone layers** | Layers with no group | Informational: check nothing was missed |
| **Orphan tags** | Custom tags attached to no object (usually typos or leftovers). Listed by photo ID, kept off the map layers, and fixed in OLM | 0 |
| **Tie-breaks** | Tagged objects that matched more than one equally specific row, for example one object with both a matching material and a matching custom tag | Informational |

A convention in the sheet supports this: when a row's local key is identical to its OLM key, the key is retired. The code checks that every such row also says `include on map = no` and flags any row where the two disagree.

### Layer tree rules

The map shows an expandable tree of checkboxes, up to three levels deep: **Group → Subgroup → Layer**.

1. **Counts roll up.** A Subgroup's count is the sum of its layers, and a Group's count is the sum of everything inside it.
2. **Counts are items, not photos.** A photo showing 3 cans counts as 3. Photo counts appear in the audit report.
3. **A blank Subgroup is fine.** The layer sits directly under its Group.
4. **A blank Group means standalone.** The layer appears at the top level on its own.
5. **A Subgroup without a Group is an error**, flagged in the audit report.
6. **A Subgroup with only one layer shows as a single checkbox**, with no extra click to expand.
7. **Empty layers are hidden.** A layer with nothing in it doesn't show a checkbox, so to-do layers like UNCLASS disappear once they reach zero.
8. **Checkboxes cascade.** Ticking a Group turns everything inside it on or off. Unticking one layer leaves its parents partly ticked.
9. **Full names outside the tree.** Short layer names like `Sml` only need to make sense in the tree. In popups and exports, the full path is shown, e.g. *Dumping – Sml*.

A photo with several kinds of litter appears in every layer that applies to it. That's intended.

### How the map shows it

- **One dot per layer per photo.** A photo with cans and cigarette butts gets two dots, drawn a few pixels apart in a small cluster. The cluster is a display offset only; the photo's location is never moved.
- **Colour hints at the group.** Each group has its own colour family (a fixed, colour-blind-tested order that is never recycled), subgroups shift the hue slightly, and layers are lighter or darker shades. With this many layers, colour alone can't identify one, so tick a layer on its own or click a dot: the popup names it in full.
- **Filled dot = picked up, hollow ring = left in place.** A ring means at least one of those items was left where it was found (for example dog waste). **Left in place only** narrows either view to those items.
- **Totals, clusters and dots by zoom.** Zoomed out, each neighbourhood is one bubble with its total items and its name; tap it to zoom in. Zooming in, those fade into numbered clusters (each number is the items the filters count; tap one to zoom into it), and the clusters fade into the individual dots, which can be tapped for details. Every number follows the same checkboxes, dates and "Left in place only" filter. Clusters are one neutral colour and the dots keep the layer colours and the rings for items left in place. The zoom levels are constants at the top of `index.html`. A heatmap was built first (2026-09-26) and removed (2026-10-03): with this data, clusters say more.
- **Date filter.** From and To dates use Maple Ridge local time. OLM stores times in UTC, so without this, evening collections would land on the next day. The tree's counts follow the chosen dates.
- **Popups** show the full layer name, the item count, picked up or left in place, the local date and time, other layers in the same photo, and a link to the photo on OLM.
- **Dot positions come from the phone's GPS**, so they are usually within about 5 to 15 metres of where the photo was taken, and more near buildings and trees. Zoomed in, a dot can appear on a building near where the litter actually was.

### Current tree (from `config/crosswalk.csv`, 2026-09-26)

Some layers sit directly under a group, with no subgroup.

```
Household
├── Liquor          Liquor Bottle, Liquor Bottle Cap, Liquor Broken Glass, Liquor Can, Liquor Debris, Liquor Packaging
└── (no subgroup)   Batteries, Plastic (#4) or Paper Food Bag, Corrugated Cardboard Box, Household Food Can,
                    Food Container - Plastic, Paper, Foam, Food Container Lid, Organic Debris, Misc.,
                    Plastic Straws, Medical Bandages, Latex / Nitrile Glove, Party Litter,
                    Abandoned Textile Apparel, Household misc, E-waste Piece, Household Plastic Bag,
                    Pet Supplies, Dental Waste, Cotton Swabs, Personal Hygiene Product, Hygiene Paper, Wet Wipes
Convenient Food Drink
├── Drink           Poly-lined Hot Beverage Cup, Hot Beverage Cup Lid, Single-Serve Coffee Pod,
│                   Corrugated Cardboard Cup Sleeve, Plastic or Glass Drink Bottle, Drink Bottle Cap,
│                   Drink Broken Glass, Aluminum Drink Cans, Drink Carton, Cold Beverage Cup, Drink Box Pouch,
│                   Cold Beverage Lid, Household or Take-out Drink Packaging, Pull-tabs, Paper Drink Straws,
│                   Drink Straw Wrapper
├── Snack           Metalized Chip Bags, Chewed Gum, Foil / Plastic Film Snack Wrapper
└── Take-out        Cutlery, Napkins, Food Packaging, Condiment Packets
Dumping             UNCLASS, Sml, Med, Lrg, Commercial Dumping
Industrial          Industrial Debris, Flagging Tape
Piece               Foil Piece, Styrofoam Piece, Styrofoam Whole, Household or Unknown Metal Piece, Wood Debris,
                    Broken Glass Piece, Paper Piece, Plastic Piece, Motor Vehicle Part Piece, Motor Vehicle Spill
Fecal               Pet Waste Unbagged, Pet Waste Bagged
Smoking             Cigarette Butts, Butane Lighter, Nicotine Packaging, Cannabis Packaging, Nicotine Vape,
                    Cannabis Vape
```

---

---

## Roadmap

### Stage 2 — Local classification (current)

Priority order: the code that applies the crosswalk and displays the points (steps 2 and 3), then the legacy review and reclass (step 4, which is the largest amount of human effort), then Stage 3, then Stage 4.

1. ✅ **Finish the crosswalk.** Done 2026-09-25: exported to `config/crosswalk.csv`, with structural checks clean and no unmapped tags in the current data.
2. ✅ **Build the crosswalk engine.** Done 2026-09-26: `scripts/sync_data.py` reads the CSV, applies the matching rules, and writes `data/audit.md` alongside the GeoJSON.
3. ✅ **Build the layer tree map.** Done 2026-09-26: the expandable tree with counts, picked-up rings, a date filter, and photo popups replaced the three fixed checkboxes.
4. **Clean up older tags in OLM (in progress).** The maintainer is reclassing tagged objects directly in OLM: tags on retired or excluded keys, tags the crosswalk flags for review ("OLM data needs fixes"), and orphan custom tags, meaning custom tags attached to no object. The aim is for the audit counts to reach zero.
5. ✅ **Confirm OLM's modifier codes.** Done 2026-09-25: the API sends an object's type as `type` (`new_tags` format) or `type_id` (summary format), and the pipeline keeps it as `object_type`. `small` and `medium` are confirmed in real data; `large` has not appeared yet.

### Stage 3 — GIS features on the map

Once the layer tree works and the legacy data is conformed, add features that make the spatial data easier to read:

- ✅ Clustering with a neighbourhood total, clusters, dots zoom sequence (2026-10-03). A heatmap was built early (2026-09-26) and removed
- ✅ Neighbourhood and zone views (built 2026-10-02): the City of Maple Ridge's neighbourhoods when zoomed out and lettered zones inside them when zoomed in (A at the top), with a checkbox tree in the panel (a neighbourhood and its zones) to show or hide each. Pointing at an area, or its row in the key, shows its label and one card (items, items left in place, photos, collection days, most common layers, and how many photos sit within the assumed GPS error of an edge; a neighbourhood card ranks its zones). Zones sit where there are photos and edges go where collecting is sparse, so GPS drift matters little. A density score was considered and dropped. How and why: [docs/zones-method.md](docs/zones-method.md). The neighbourhoods come from the Planning Department's map: see [docs/maple-ridge-community-areas.md](docs/maple-ridge-community-areas.md)
- ✅ Date selection (built 2026-10-02): the panel picks a set of collection days with a tick list of the days (with items per day), month chips, weekday and weekend chips, presets (All, None, Last 7 days, Last 30 days) and the From/To boxes. A chip ticks or unticks its days, so months can be mixed. Time of day, comparing two groups side by side, and a click-and-drag strip of photos per day are still open
- ✅ Richer popups (achieved; confirmed by the maintainer 2026-10-03): a dot's popup shows the layer's full name, items, picked-up status, local time, the other items in the same photo, and a link to the photo. It links to the photo rather than embedding a preview.

### Stage 4 — Municipal waste stream (only if COMR takes part)

Stage 3's neighbourhood summaries already describe the data in the City's own geography. Stage 4 would go further and show the objects in the City of Maple Ridge's own litter categories, as a "view as" switch on top of the MROLM layer tree. It needs the City to publish or use a litter-count scheme and to take an interest, because MROLM's groups are a volunteer's logic and a stream is only meaningful if it follows the City's own categories. If that happens, each object class is matched to the City's scheme, one stream at a time. There is no stream for any other city, because the map shows Maple Ridge and a second city's categories would confuse readers. The project is complete without Stage 4.

Ongoing reliability work is listed in [docs/hardening.md](docs/hardening.md).

---

## Repository structure

```
.
├── .github/workflows/sync_data.yml   Workflow that runs the pipeline (every 12 hours and on crosswalk changes)
├── scripts/sync_data.py              Fetches OLM data, applies the crosswalk, writes the GeoJSON and audit
├── scripts/crosswalk.py              The crosswalk matching rules, shared by the pipeline and review tools
├── scripts/export_raw_olm.py         Read-only raw export for the legacy review (local use)
├── scripts/build_review_workbook.py  Builds the legacy review workbook from an export (local use)
├── tests/                            Unit tests: python3 -m unittest discover -s tests
├── data/litter.geojson               Published dataset
├── data/audit.md                     Audit report from the latest sync
├── public/data/litter.geojson        Copy of the dataset for hosting
├── index.html                        The web map
├── assets/                           Favicon and link-preview image
├── docs/                             Tagging protocol, decision log, hardening list, batch review method, zones method, Maple Ridge neighbourhood sources
├── config/crosswalk.csv              The crosswalk, exported from the spreadsheet
├── config/neighbourhoods.csv         The map's neighbourhoods and their colours
├── config/zones.csv                  The lettered zones inside each neighbourhood (rectangles)
├── data/LICENSE.md                   Data license (ODbL 1.0, from OpenLitterMap)
└── LICENSE                           Code license (MIT)
```

---

## Running it yourself

The pipeline needs an OpenLitterMap account. Its email and password are stored as **GitHub repository secrets** named `OLM_EMAIL` and `OLM_PASSWORD` (Settings → Secrets and variables → Actions). They are never written into the code.

- **Automatic:** the workflow runs every 12 hours, and whenever a push changes `config/crosswalk.csv`.
- **On demand:** go to the Actions tab, choose *Sync OpenLitterMap GeoJSON Data*, and click *Run workflow*.
- **Locally:** with Python 3.11 installed:

```bash
pip install requests
export OLM_EMAIL="you@example.com"
export OLM_PASSWORD="your-password"
python scripts/sync_data.py
```

To test without logging in, build from a saved raw export instead: `python scripts/sync_data.py --from-raw review/raw/photos_<date>.json` (see the [batch review method](docs/olm-batch-review-method.md) for making one). Run the unit tests with `python3 -m unittest discover -s tests`.

Then open `index.html` through a local web server (for example, `python -m http.server`) rather than directly from the file system, so the browser allows it to load the GeoJSON.

After a local test run, restore the data files with `git restore data/ public/data/` and don't commit them. The workflow publishes the data.

---

## Cost

The project is designed to cost nothing to run.

| Component | Technology | Cost |
|---|---|---|
| Data processing | GitHub Actions | $0 (well within the free monthly minutes) |
| Hosting | GitHub Pages | $0 |
| Map | MapLibre GL JS with CARTO Positron basemap | $0 |
| Storage | GeoJSON files in the repository | $0 |

---

## Data, privacy, and licensing

**Source.** All litter records come from the maintainer's own OpenLitterMap contributions. Photos are hosted by OpenLitterMap; this repository stores only links to them.

**What's published.** Each map point contains only these fields: photo ID, date and time, a link to the photo on OpenLitterMap, litter tags, each tagged object's crosswalk layer and picked-up status, and the Stage 1 group flags. The audit report adds counts and photo IDs. Location comes from latitude and longitude only. Any other information OpenLitterMap supplies with a record is outside this project's scope and is discarded by the pipeline before anything is saved.

**Location precision.** Coordinates are published at the precision OLM records. They come from the phone's GPS when the photo was taken, which is usually accurate to about 5 to 15 metres, so a dot can sit on a nearby building rather than on the sidewalk where the litter was. Dots are never moved or snapped to roads. Collection routes are visible on the map by design. Contributors should avoid uploading photos that reveal their home, identify other people, or show private property details.

**What's deliberately left out.** Posters and signage that name individuals or businesses are not recorded, because a litter map could unfairly imply wrongdoing.

**Licensing.** The code is under the [MIT License](LICENSE). The litter data (`data/` and `public/data/`) is derived from OpenLitterMap, so it follows OpenLitterMap's data license, the [Open Database License (ODbL) 1.0](https://opendatacommons.org/licenses/odbl/1-0/): anyone may reuse it with the credit "© OpenLitterMap & Contributors", and adapted versions that are shared publicly must stay under the ODbL. See [data/LICENSE.md](data/LICENSE.md). The map shows the same credit in its attribution corner.

---

## Acknowledgements

- [OpenLitterMap](https://openlittermap.com), the open-source, open-data citizen science platform this project is built on
- [MapLibre GL JS](https://maplibre.org) for map rendering
- [CARTO](https://carto.com) for the Positron basemap
- Everyone who picks up litter in Maple Ridge, tagged or not

Questions, ideas, and corrections are welcome through this repository's Issues.
