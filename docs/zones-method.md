# How the map's neighbourhoods and zones work

Written 2026-10-02. The map summarises litter by **neighbourhood** (zoomed out) and by **zone** (zoomed in). This page records how they are built and why, so someone else can repeat or change it. Neighbourhood names come from the City of Maple Ridge Planning Department's neighbourhoods map: see [maple-ridge-community-areas.md](maple-ridge-community-areas.md).

## What it is for

MROLM holds one volunteer's data. It is a live model of how a map fed by many users could summarise litter by area, not a basis for comparing neighbourhoods. A single collector's route says more about where they walked than about where litter is. The cards show that, with collection days and dates.

## The files

- `config/neighbourhoods.csv`: one row per neighbourhood: `key`, `name`, `colour`.
- `config/zones.csv`: one row per zone: `zone_id`, `neighbourhood`, `letter`, `description`, and the rectangle `south_lat`, `north_lat`, `west_lon`, `east_lon`.
- `scripts/sync_data.py` gives every photo its `zone`, its `zone_edge_m` and its `nbhd_edge_m`, and writes the lists into the GeoJSON. Photos' dots are never moved.

A zone's id is `<neighbourhood>_zone_<letter>`, for example `cottonwood_zone_A`. Letters run north to south, so A is the top zone, and they are never reused. A neighbourhood appears only if it has at least one zone, and a zone is added where there are photos.

## Why zones are placed where they are

Phone GPS can be off by about 5 to 15 m (README), and OLM sends no accuracy value with a photo, so a photo cannot be corrected individually without inventing an error. The method designs the error out and reports what is left:

1. **Zone edges go where collecting is sparse.** Collecting clusters at intersections. Edges placed exactly on the cross streets had 24% of photos (677 of 2,812) within 15 m of an edge, so drift would keep flipping them between zones. Moving each edge to the quietest spot within 60 m cut that to 2.9%. The six zones' latitude edges are those quiet spots.
2. **Zones straddle the road.** The data runs along 240 St, which is also the line between neighbourhoods on the City's map. Measured against the OpenStreetMap centreline, the main collecting line is the west sidewalk (10 to 20 m west): 1,443 photos are more than 15 m west, 1,210 are within 15 m, and 161 are more than 15 m east. Nothing is more than 35 m east. Cutting zones down the road would split most photos by drift, so each zone covers the road and both sidewalks and belongs to one neighbourhood, the one holding most of its photos. All six belong to Cottonwood.
3. **Each card reports the uncertainty.** It says how many photos are within 15 m (`mrolm_gps_error_m`, set in `sync_data.py`) of a zone or neighbourhood edge.
4. **Not used: weighting each photo by its GPS error circle.** Without a measured accuracy per photo it would add precision the data does not have.

East Maple Ridge and Albion have no zones because no photo is far enough east of 240 St to belong to them. To add a neighbourhood later, add it to `neighbourhoods.csv`, add its zones to `zones.csv` (rectangles must not overlap), and run the sync.

## What the map shows

- The panel's colour key is a checkbox tree like the litter layers: a neighbourhood and its zones. Ticking the neighbourhood ticks all its zones. A ticked area is drawn on the map and has a filled swatch with its letter; an unticked one is not drawn and has an empty swatch that still shows the letter. The neighbourhood's shape is drawn while any of its zones is ticked. The ticks also filter the data: with any zone unticked, the dots, clusters, counts and neighbourhood totals include only photos in the ticked zones (photos outside every zone are left out then; with all zones ticked nothing is left out). This changed on 2026-10-03; before that the ticks only showed or hid the overlay.
- Zoom decides which kind is drawn: zoomed out (below `ZONE_ZOOM` in `index.html`, now 14, a first guess) the neighbourhoods, zoomed in the zones. Each has a flat fill in the neighbourhood's colour, with no gradients.
- Nothing is labelled until you point at it. Hovering or tapping an area, or pointing at its row in the key (at any zoom), shows its **label** (the zone letter or the neighbourhood name, at its centre) and one **card**. The card sits in the free space between the panel and the zones, or on the east side if that is wider, level with the area. On a phone it sits at the bottom.
- A zone card gives items, items left in place, photos, collection days, the most common layers, and how many photos are within 15 m of an edge. A neighbourhood card adds its zones ranked by items found.
- Counts show where collecting happened, not necessarily where litter is. Colour only identifies an area; it never means "more" or "less".

## Considered and dropped: a density score

A score of items found per visit, with a gauge, was tried on paper and dropped. A fair density needs fixed blocks, planned repeat coverage and a recorded effort per visit. In this data a visit covered between 18% and 94% of a zone's length (median), so counting every day would favour zones that were only passed through. MROLM is a proof of a system, not a measurement of density, so it shows plain counts.

## Limits and checks

- `ZONE_ZOOM` (14) is a first guess. Change it in `index.html` if the switch between the views feels too early or too late.
- Zones are rectangles. They cannot follow a slanted road exactly; the road's slant across the data is about 22 m, and the east and west margins (about 24 m past the last photo east, 35 m west) absorb it.
- The latitude edges are tuned to this one dataset. Re-check the quiet spots as more data arrives; they are edits to `zones.csv`.
- The sync logs a warning and gives photos no zone if either file is missing, malformed, or has overlapping zones. It never stops the run.
- Zone edges follow road centrelines and intersections from OpenStreetMap, © OpenStreetMap contributors (ODbL), credited in the map's attribution corner.
