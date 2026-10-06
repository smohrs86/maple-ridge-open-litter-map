# MROLM audit report

Written by `scripts/sync_data.py` on every sync, following the README's "Audit counts". Items are quantities (the map counts items); objects are tagged objects; photos are OLM photos.

- Photos: 3734
- Newest photo: 2026-10-06
- Crosswalk: `config/crosswalk.csv`, SHA-256 starts `cf874a54ce8f`
- Tagged objects: 4454 (6059 items)
- Shown on the map: 4454 objects (6059 items) in 68 layers

## Status counts

| Status | Meaning | Objects | Items | Healthy value |
|---|---|---:|---:|---|
| OK | Matched a map layer | 4454 | 6059 | Most objects |
| REVIEW | Matched a map layer whose crosswalk row has an "OLM data needs fixes" note (shown on the map) | 0 | 0 | Falls as the legacy review is done |
| Not used | Matched a row with `include on map = no` (kept off the map) | 0 | 0 | 0 |
| UNCLASS | Household dumping with no size chosen | 0 | 0 | 0 |
| Orphan tags | Custom tag attached to no object (kept off the map) | 0 | 0 | 0 |
| Unmapped | Matched no crosswalk row: a gap in the crosswalk (kept off the map) | 0 | 0 | 0 |
| Tie-breaks | Matched more than one equally specific row; the higher row won | 0 | 0 | Informational |

## REVIEW by OLM key

None.

## Not used (RECLASS) by OLM key

None.

## Unmapped

None.

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
| Household | Liquor | Liquor Can | 13 | 12 | 12 | 0 |
| Household | Liquor | Liquor Debris | 0 | 0 | 0 | 0 |
| Household | Liquor | Liquor Packaging | 5 | 5 | 5 | 1 |
| Household |  | Batteries | 2 | 2 | 2 | 0 |
| Household |  | Plastic (#4) or Paper Food Bag | 38 | 37 | 37 | 0 |
| Household |  | Corrugated Cardboard Box | 0 | 0 | 0 | 0 |
| Household |  | Household Food Can | 2 | 2 | 2 | 0 |
| Household |  | Food Container - Plastic, Paper, Foam | 14 | 14 | 14 | 0 |
| Household |  | Food Container Lid | 8 | 7 | 7 | 0 |
| Household |  | Organic Debris, Misc. | 13 | 12 | 12 | 1 |
| Household |  | Plastic Straws | 16 | 14 | 14 | 0 |
| Household |  | Medical Bandages | 9 | 8 | 8 | 0 |
| Household |  | Latex / Nitrile Glove | 11 | 10 | 10 | 0 |
| Household |  | Party Litter | 59 | 43 | 43 | 0 |
| Household |  | Abandoned Textile Apparel | 40 | 31 | 31 | 0 |
| Household |  | Household misc | 104 | 98 | 97 | 2 |
| Household |  | E-waste Piece | 3 | 3 | 3 | 0 |
| Household |  | Household Plastic Bag | 21 | 20 | 20 | 0 |
| Household |  | Pet Supplies | 2 | 2 | 2 | 0 |
| Household |  | Dental Waste | 7 | 7 | 7 | 0 |
| Household |  | Cotton Swabs | 4 | 4 | 4 | 0 |
| Household |  | Personal Hygiene Product | 1 | 1 | 1 | 0 |
| Household |  | Hygiene Paper | 18 | 16 | 16 | 0 |
| Household |  | Wet Wipes | 133 | 67 | 67 | 0 |
| Convenient Food Drink | Drink | Poly-lined Hot Beverage Cup | 30 | 28 | 28 | 1 |
| Convenient Food Drink | Drink | Hot Beverage Cup Lid | 26 | 25 | 25 | 0 |
| Convenient Food Drink | Drink | Single-Serve Coffee Pod | 2 | 2 | 2 | 0 |
| Convenient Food Drink | Drink | Corrugated Cardboard Cup Sleeve | 9 | 8 | 8 | 0 |
| Convenient Food Drink | Drink | Plastic or Glass Drink Bottle | 29 | 28 | 28 | 0 |
| Convenient Food Drink | Drink | Drink Bottle Cap | 25 | 25 | 25 | 0 |
| Convenient Food Drink | Drink | Drink Broken Glass | 23 | 6 | 6 | 0 |
| Convenient Food Drink | Drink | Aluminum Drink Cans | 11 | 11 | 11 | 1 |
| Convenient Food Drink | Drink | Drink Carton | 0 | 0 | 0 | 0 |
| Convenient Food Drink | Drink | Cold Beverage Cup | 81 | 78 | 78 | 0 |
| Convenient Food Drink | Drink | Drink Box Pouch | 5 | 5 | 5 | 0 |
| Convenient Food Drink | Drink | Cold Beverage Lid | 85 | 82 | 82 | 1 |
| Convenient Food Drink | Drink | Household or Take-out Drink Packaging | 1 | 1 | 1 | 0 |
| Convenient Food Drink | Drink | Pull-tabs | 1 | 1 | 1 | 0 |
| Convenient Food Drink | Drink | Paper Drink Straws | 95 | 90 | 90 | 0 |
| Convenient Food Drink | Drink | Drink Straw Wrapper | 77 | 75 | 74 | 0 |
| Convenient Food Drink | Snack | Metalized Chip Bags | 10 | 10 | 10 | 0 |
| Convenient Food Drink | Snack | Chewed Gum | 18 | 18 | 18 | 0 |
| Convenient Food Drink | Snack | Foil / Plastic Film Snack Wrapper | 273 | 247 | 246 | 0 |
| Convenient Food Drink | Take-out | Cutlery | 8 | 7 | 7 | 0 |
| Convenient Food Drink | Take-out | Napkins | 103 | 86 | 86 | 0 |
| Convenient Food Drink | Take-out | Food Packaging | 135 | 124 | 124 | 1 |
| Convenient Food Drink | Take-out | Condiment Packets | 27 | 21 | 21 | 0 |
| Dumping |  | UNCLASS | 0 | 0 | 0 | 0 |
| Dumping |  | Sml | 5 | 5 | 5 | 4 |
| Dumping |  | Med | 8 | 5 | 5 | 8 |
| Dumping |  | Lrg | 0 | 0 | 0 | 0 |
| Dumping |  | Commercial Dumping | 0 | 0 | 0 | 0 |
| Piece |  | Foil Piece | 52 | 43 | 43 | 0 |
| Piece |  | Styrofoam Piece | 44 | 38 | 38 | 0 |
| Piece |  | Styrofoam Whole | 8 | 8 | 8 | 3 |
| Piece |  | Household or Unknown Metal Piece | 18 | 18 | 18 | 0 |
| Piece |  | Wood Debris | 8 | 8 | 8 | 1 |
| Piece |  | Broken Glass Piece | 5 | 2 | 2 | 0 |
| Piece |  | Paper Piece | 965 | 688 | 688 | 12 |
| Piece |  | Plastic Piece | 904 | 738 | 737 | 0 |
| Piece |  | Motor Vehicle Part Piece | 42 | 25 | 25 | 0 |
| Piece |  | Motor Vehicle Spill | 0 | 0 | 0 | 0 |
| Industrial |  | Industrial Debris | 52 | 51 | 51 | 1 |
| Industrial |  | Flagging Tape | 13 | 12 | 12 | 0 |
| Fecal |  | Pet Waste Unbagged | 61 | 55 | 55 | 61 |
| Fecal |  | Pet Waste Bagged | 52 | 48 | 48 | 47 |
| Smoking |  | Cigarette Butts | 2155 | 1251 | 1251 | 1 |
| Smoking |  | Butane Lighter | 1 | 1 | 1 | 0 |
| Smoking |  | Nicotine Packaging | 24 | 24 | 24 | 0 |
| Smoking |  | Cannabis Packaging | 38 | 34 | 34 | 0 |
| Smoking |  | Nicotine Vape | 1 | 1 | 1 | 0 |
| Smoking |  | Cannabis Vape | 3 | 3 | 3 | 0 |
