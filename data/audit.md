# MROLM audit report

Written by `scripts/sync_data.py` on every sync, following the README's "Audit counts". Items are quantities (the map counts items); objects are tagged objects; photos are OLM photos.

- Photos: 4021
- Newest photo: 2026-10-08
- Crosswalk: `config/crosswalk.csv`, SHA-256 starts `cf874a54ce8f`
- Tagged objects: 4755 (6415 items)
- Shown on the map: 4754 objects (6414 items) in 69 layers

## Status counts

| Status | Meaning | Objects | Items | Healthy value |
|---|---|---:|---:|---|
| OK | Matched a map layer | 4754 | 6414 | Most objects |
| REVIEW | Matched a map layer whose crosswalk row has an "OLM data needs fixes" note (shown on the map) | 0 | 0 | Falls as the legacy review is done |
| Not used | Matched a row with `include on map = no` (kept off the map) | 0 | 0 | 0 |
| UNCLASS | Household dumping with no size chosen | 0 | 0 | 0 |
| Orphan tags | Custom tag attached to no object (kept off the map) | 0 | 0 | 0 |
| Unmapped | Matched no crosswalk row: a gap in the crosswalk (kept off the map) | 1 | 1 | 0 |
| Tie-breaks | Matched more than one equally specific row; the higher row won | 0 | 0 | Informational |

## REVIEW by OLM key

None.

## Not used (RECLASS) by OLM key

None.

## Unmapped

| OLM key | Photo IDs |
|---|---|
| medical/other | 556626 |

## Orphan tags

None.

## Tie-breaks

None.

## Crosswalk checks

- Standalone layers (no Group; informational): none
- Subgroup without a Group (error), sheet rows: none
- Map rows with no local key (error), sheet rows: none
- Local key = OLM key but `include on map` is not `no` (error), sheet rows: none

## Layers

| Group | Subgroup | Layer | Items | Objects | Photos | Not picked up (items) |
|---|---|---|---:|---:|---:|---:|
| Household | Liquor | Liquor Bottle | 1 | 1 | 1 | 0 |
| Household | Liquor | Liquor Bottle Cap | 1 | 1 | 1 | 0 |
| Household | Liquor | Liquor Broken Glass | 1 | 1 | 1 | 0 |
| Household | Liquor | Liquor Can | 14 | 13 | 13 | 0 |
| Household | Liquor | Liquor Debris | 0 | 0 | 0 | 0 |
| Household | Liquor | Liquor Packaging | 6 | 6 | 6 | 1 |
| Household |  | Batteries | 3 | 3 | 3 | 0 |
| Household |  | Plastic (#4) or Paper Food Bag | 38 | 37 | 37 | 0 |
| Household |  | Corrugated Cardboard Box | 1 | 1 | 1 | 0 |
| Household |  | Household Food Can | 2 | 2 | 2 | 0 |
| Household |  | Food Container - Plastic, Paper, Foam | 15 | 15 | 15 | 0 |
| Household |  | Food Container Lid | 8 | 7 | 7 | 0 |
| Household |  | Organic Debris, Misc. | 18 | 17 | 17 | 1 |
| Household |  | Plastic Straws | 16 | 14 | 14 | 0 |
| Household |  | Medical Bandages | 9 | 8 | 8 | 0 |
| Household |  | Latex / Nitrile Glove | 11 | 10 | 10 | 0 |
| Household |  | Party Litter | 61 | 45 | 45 | 0 |
| Household |  | Abandoned Textile Apparel | 41 | 32 | 32 | 0 |
| Household |  | Household misc | 118 | 112 | 111 | 2 |
| Household |  | E-waste Piece | 3 | 3 | 3 | 0 |
| Household |  | Household Plastic Bag | 24 | 23 | 23 | 0 |
| Household |  | Pet Supplies | 2 | 2 | 2 | 0 |
| Household |  | Dental Waste | 7 | 7 | 7 | 0 |
| Household |  | Cotton Swabs | 4 | 4 | 4 | 0 |
| Household |  | Personal Hygiene Product | 1 | 1 | 1 | 0 |
| Household |  | Hygiene Paper | 21 | 19 | 19 | 0 |
| Household |  | Wet Wipes | 135 | 69 | 69 | 0 |
| Convenient Food Drink | Drink | Poly-lined Hot Beverage Cup | 31 | 29 | 29 | 1 |
| Convenient Food Drink | Drink | Hot Beverage Cup Lid | 29 | 28 | 28 | 0 |
| Convenient Food Drink | Drink | Single-Serve Coffee Pod | 2 | 2 | 2 | 0 |
| Convenient Food Drink | Drink | Corrugated Cardboard Cup Sleeve | 9 | 8 | 8 | 0 |
| Convenient Food Drink | Drink | Plastic or Glass Drink Bottle | 31 | 30 | 30 | 0 |
| Convenient Food Drink | Drink | Drink Bottle Cap | 25 | 25 | 25 | 0 |
| Convenient Food Drink | Drink | Drink Broken Glass | 80 | 22 | 22 | 0 |
| Convenient Food Drink | Drink | Aluminum Drink Cans | 11 | 11 | 11 | 1 |
| Convenient Food Drink | Drink | Drink Carton | 0 | 0 | 0 | 0 |
| Convenient Food Drink | Drink | Cold Beverage Cup | 83 | 80 | 80 | 0 |
| Convenient Food Drink | Drink | Drink Box Pouch | 5 | 5 | 5 | 0 |
| Convenient Food Drink | Drink | Cold Beverage Lid | 87 | 84 | 84 | 1 |
| Convenient Food Drink | Drink | Household or Take-out Drink Packaging | 1 | 1 | 1 | 0 |
| Convenient Food Drink | Drink | Pull-tabs | 1 | 1 | 1 | 0 |
| Convenient Food Drink | Drink | Paper Drink Straws | 98 | 93 | 93 | 0 |
| Convenient Food Drink | Drink | Drink Straw Wrapper | 80 | 78 | 77 | 0 |
| Convenient Food Drink | Snack | Metalized Chip Bags | 10 | 10 | 10 | 0 |
| Convenient Food Drink | Snack | Chewed Gum | 19 | 19 | 19 | 0 |
| Convenient Food Drink | Snack | Foil / Plastic Film Snack Wrapper | 276 | 250 | 249 | 0 |
| Convenient Food Drink | Take-out | Cutlery | 11 | 10 | 10 | 0 |
| Convenient Food Drink | Take-out | Napkins | 103 | 86 | 86 | 0 |
| Convenient Food Drink | Take-out | Food Packaging | 135 | 124 | 124 | 1 |
| Convenient Food Drink | Take-out | Condiment Packets | 27 | 21 | 21 | 0 |
| Dumping |  | UNCLASS | 0 | 0 | 0 | 0 |
| Dumping |  | Sml | 5 | 5 | 5 | 4 |
| Dumping |  | Med | 8 | 5 | 5 | 8 |
| Dumping |  | Lrg | 0 | 0 | 0 | 0 |
| Dumping |  | Commercial Dumping | 0 | 0 | 0 | 0 |
| Piece |  | Foil Piece | 57 | 48 | 48 | 0 |
| Piece |  | Styrofoam Piece | 44 | 38 | 38 | 0 |
| Piece |  | Styrofoam Whole | 8 | 8 | 8 | 3 |
| Piece |  | Household or Unknown Metal Piece | 21 | 21 | 21 | 0 |
| Piece |  | Wood Debris | 11 | 9 | 9 | 4 |
| Piece |  | Broken Glass Piece | 5 | 2 | 2 | 0 |
| Piece |  | Paper Piece | 1032 | 753 | 753 | 12 |
| Piece |  | Plastic Piece | 967 | 796 | 795 | 0 |
| Piece |  | Motor Vehicle Part Piece | 45 | 28 | 28 | 0 |
| Piece |  | Motor Vehicle Spill | 0 | 0 | 0 | 0 |
| Industrial |  | Industrial Debris | 53 | 52 | 52 | 2 |
| Industrial |  | Flagging Tape | 13 | 12 | 12 | 0 |
| Fecal |  | Pet Waste Unbagged | 61 | 55 | 55 | 61 |
| Fecal |  | Pet Waste Bagged | 53 | 49 | 49 | 48 |
| Smoking |  | Cigarette Butts | 2248 | 1339 | 1339 | 1 |
| Smoking |  | Butane Lighter | 1 | 1 | 1 | 0 |
| Smoking |  | Nicotine Packaging | 24 | 24 | 24 | 0 |
| Smoking |  | Cannabis Packaging | 39 | 35 | 35 | 0 |
| Smoking |  | Nicotine Vape | 1 | 1 | 1 | 0 |
| Smoking |  | Cannabis Vape | 3 | 3 | 3 | 0 |
