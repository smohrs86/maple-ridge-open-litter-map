# MROLM audit report

Written by `scripts/sync_data.py` on every sync, following the README's "Audit counts". Items are quantities (the map counts items); objects are tagged objects; photos are OLM photos.

- Photos: 3430
- Newest photo: 2026-10-05
- Crosswalk: `config/crosswalk.csv`, SHA-256 starts `cf874a54ce8f`
- Tagged objects: 4129 (5678 items)
- Shown on the map: 4129 objects (5678 items) in 68 layers

## Status counts

| Status | Meaning | Objects | Items | Healthy value |
|---|---|---:|---:|---|
| OK | Matched a map layer | 4129 | 5678 | Most objects |
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
| Household |  | Household Food Can | 1 | 1 | 1 | 0 |
| Household |  | Food Container - Plastic, Paper, Foam | 13 | 13 | 13 | 0 |
| Household |  | Food Container Lid | 7 | 6 | 6 | 0 |
| Household |  | Organic Debris, Misc. | 13 | 12 | 12 | 1 |
| Household |  | Plastic Straws | 15 | 13 | 13 | 0 |
| Household |  | Medical Bandages | 9 | 8 | 8 | 0 |
| Household |  | Latex / Nitrile Glove | 11 | 10 | 10 | 0 |
| Household |  | Party Litter | 53 | 38 | 38 | 0 |
| Household |  | Abandoned Textile Apparel | 37 | 28 | 28 | 0 |
| Household |  | Household misc | 93 | 87 | 86 | 2 |
| Household |  | E-waste Piece | 3 | 3 | 3 | 0 |
| Household |  | Household Plastic Bag | 20 | 19 | 19 | 0 |
| Household |  | Pet Supplies | 2 | 2 | 2 | 0 |
| Household |  | Dental Waste | 7 | 7 | 7 | 0 |
| Household |  | Cotton Swabs | 3 | 3 | 3 | 0 |
| Household |  | Personal Hygiene Product | 1 | 1 | 1 | 0 |
| Household |  | Hygiene Paper | 15 | 13 | 13 | 0 |
| Household |  | Wet Wipes | 127 | 64 | 64 | 0 |
| Convenient Food Drink | Drink | Poly-lined Hot Beverage Cup | 30 | 28 | 28 | 1 |
| Convenient Food Drink | Drink | Hot Beverage Cup Lid | 26 | 25 | 25 | 0 |
| Convenient Food Drink | Drink | Single-Serve Coffee Pod | 2 | 2 | 2 | 0 |
| Convenient Food Drink | Drink | Corrugated Cardboard Cup Sleeve | 9 | 8 | 8 | 0 |
| Convenient Food Drink | Drink | Plastic or Glass Drink Bottle | 26 | 25 | 25 | 0 |
| Convenient Food Drink | Drink | Drink Bottle Cap | 23 | 23 | 23 | 0 |
| Convenient Food Drink | Drink | Drink Broken Glass | 6 | 1 | 1 | 0 |
| Convenient Food Drink | Drink | Aluminum Drink Cans | 11 | 11 | 11 | 1 |
| Convenient Food Drink | Drink | Drink Carton | 0 | 0 | 0 | 0 |
| Convenient Food Drink | Drink | Cold Beverage Cup | 78 | 75 | 75 | 0 |
| Convenient Food Drink | Drink | Drink Box Pouch | 5 | 5 | 5 | 0 |
| Convenient Food Drink | Drink | Cold Beverage Lid | 81 | 78 | 78 | 1 |
| Convenient Food Drink | Drink | Household or Take-out Drink Packaging | 1 | 1 | 1 | 0 |
| Convenient Food Drink | Drink | Pull-tabs | 1 | 1 | 1 | 0 |
| Convenient Food Drink | Drink | Paper Drink Straws | 91 | 87 | 87 | 0 |
| Convenient Food Drink | Drink | Drink Straw Wrapper | 76 | 74 | 73 | 0 |
| Convenient Food Drink | Snack | Metalized Chip Bags | 10 | 10 | 10 | 0 |
| Convenient Food Drink | Snack | Chewed Gum | 13 | 13 | 13 | 0 |
| Convenient Food Drink | Snack | Foil / Plastic Film Snack Wrapper | 256 | 230 | 229 | 0 |
| Convenient Food Drink | Take-out | Cutlery | 6 | 5 | 5 | 0 |
| Convenient Food Drink | Take-out | Napkins | 97 | 81 | 81 | 0 |
| Convenient Food Drink | Take-out | Food Packaging | 134 | 123 | 123 | 0 |
| Convenient Food Drink | Take-out | Condiment Packets | 25 | 19 | 19 | 0 |
| Dumping |  | UNCLASS | 0 | 0 | 0 | 0 |
| Dumping |  | Sml | 5 | 5 | 5 | 4 |
| Dumping |  | Med | 8 | 5 | 5 | 8 |
| Dumping |  | Lrg | 0 | 0 | 0 | 0 |
| Dumping |  | Commercial Dumping | 0 | 0 | 0 | 0 |
| Piece |  | Foil Piece | 50 | 41 | 41 | 0 |
| Piece |  | Styrofoam Piece | 42 | 36 | 36 | 0 |
| Piece |  | Styrofoam Whole | 8 | 8 | 8 | 3 |
| Piece |  | Household or Unknown Metal Piece | 16 | 16 | 16 | 0 |
| Piece |  | Wood Debris | 7 | 7 | 7 | 1 |
| Piece |  | Broken Glass Piece | 5 | 2 | 2 | 0 |
| Piece |  | Paper Piece | 885 | 629 | 629 | 12 |
| Piece |  | Plastic Piece | 833 | 676 | 675 | 0 |
| Piece |  | Motor Vehicle Part Piece | 40 | 23 | 23 | 0 |
| Piece |  | Motor Vehicle Spill | 0 | 0 | 0 | 0 |
| Industrial |  | Industrial Debris | 51 | 50 | 50 | 1 |
| Industrial |  | Flagging Tape | 12 | 11 | 11 | 0 |
| Fecal |  | Pet Waste Unbagged | 54 | 48 | 48 | 54 |
| Fecal |  | Pet Waste Bagged | 51 | 47 | 47 | 46 |
| Smoking |  | Cigarette Butts | 2048 | 1152 | 1152 | 1 |
| Smoking |  | Butane Lighter | 1 | 1 | 1 | 0 |
| Smoking |  | Nicotine Packaging | 23 | 23 | 23 | 0 |
| Smoking |  | Cannabis Packaging | 37 | 33 | 33 | 0 |
| Smoking |  | Nicotine Vape | 1 | 1 | 1 | 0 |
| Smoking |  | Cannabis Vape | 3 | 3 | 3 | 0 |
