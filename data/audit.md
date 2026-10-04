# MROLM audit report

Written by `scripts/sync_data.py` on every sync, following the README's "Audit counts". Items are quantities (the map counts items); objects are tagged objects; photos are OLM photos.

- Photos: 3113
- Newest photo: 2026-10-04
- Crosswalk: `config/crosswalk.csv`, SHA-256 starts `cf874a54ce8f`
- Tagged objects: 3802 (5299 items)
- Shown on the map: 3801 objects (5298 items) in 67 layers

## Status counts

| Status | Meaning | Objects | Items | Healthy value |
|---|---|---:|---:|---|
| OK | Matched a map layer | 3801 | 5298 | Most objects |
| REVIEW | Matched a map layer whose crosswalk row has an "OLM data needs fixes" note (shown on the map) | 0 | 0 | Falls as the legacy review is done |
| Not used | Matched a row with `include on map = no` (kept off the map) | 1 | 1 | 0 |
| UNCLASS | Household dumping with no size chosen | 0 | 0 | 0 |
| Orphan tags | Custom tag attached to no object (kept off the map) | 0 | 0 | 0 |
| Unmapped | Matched no crosswalk row: a gap in the crosswalk (kept off the map) | 0 | 0 | 0 |
| Tie-breaks | Matched more than one equally specific row; the higher row won | 0 | 0 | Informational |

## REVIEW by OLM key

None.

## Not used (RECLASS) by OLM key

| OLM key | Objects | Items |
|---|---:|---:|
| other/bags_litter | 1 | 1 |

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
| Household | Liquor | Liquor Can | 12 | 11 | 11 | 0 |
| Household | Liquor | Liquor Debris | 0 | 0 | 0 | 0 |
| Household | Liquor | Liquor Packaging | 5 | 5 | 5 | 1 |
| Household |  | Batteries | 2 | 2 | 2 | 0 |
| Household |  | Plastic (#4) or Paper Food Bag | 37 | 36 | 36 | 0 |
| Household |  | Corrugated Cardboard Box | 0 | 0 | 0 | 0 |
| Household |  | Household Food Can | 1 | 1 | 1 | 0 |
| Household |  | Food Container - Plastic, Paper, Foam | 13 | 13 | 13 | 0 |
| Household |  | Food Container Lid | 6 | 5 | 5 | 0 |
| Household |  | Organic Debris, Misc. | 11 | 10 | 10 | 1 |
| Household |  | Plastic Straws | 14 | 12 | 12 | 0 |
| Household |  | Medical Bandages | 8 | 7 | 7 | 0 |
| Household |  | Latex / Nitrile Glove | 11 | 10 | 10 | 0 |
| Household |  | Party Litter | 45 | 30 | 30 | 0 |
| Household |  | Abandoned Textile Apparel | 35 | 26 | 26 | 0 |
| Household |  | Household misc | 87 | 81 | 80 | 2 |
| Household |  | E-waste Piece | 3 | 3 | 3 | 0 |
| Household |  | Household Plastic Bag | 13 | 12 | 12 | 0 |
| Household |  | Pet Supplies | 2 | 2 | 2 | 0 |
| Household |  | Dental Waste | 7 | 7 | 7 | 0 |
| Household |  | Cotton Swabs | 3 | 3 | 3 | 0 |
| Household |  | Personal Hygiene Product | 1 | 1 | 1 | 0 |
| Household |  | Hygiene Paper | 12 | 10 | 10 | 0 |
| Household |  | Wet Wipes | 126 | 63 | 63 | 0 |
| Convenient Food Drink | Drink | Poly-lined Hot Beverage Cup | 29 | 27 | 27 | 1 |
| Convenient Food Drink | Drink | Hot Beverage Cup Lid | 26 | 25 | 25 | 0 |
| Convenient Food Drink | Drink | Single-Serve Coffee Pod | 2 | 2 | 2 | 0 |
| Convenient Food Drink | Drink | Corrugated Cardboard Cup Sleeve | 9 | 8 | 8 | 0 |
| Convenient Food Drink | Drink | Plastic or Glass Drink Bottle | 25 | 24 | 24 | 0 |
| Convenient Food Drink | Drink | Drink Bottle Cap | 21 | 21 | 21 | 0 |
| Convenient Food Drink | Drink | Drink Broken Glass | 6 | 1 | 1 | 0 |
| Convenient Food Drink | Drink | Aluminum Drink Cans | 11 | 11 | 11 | 1 |
| Convenient Food Drink | Drink | Drink Carton | 0 | 0 | 0 | 0 |
| Convenient Food Drink | Drink | Cold Beverage Cup | 75 | 72 | 72 | 0 |
| Convenient Food Drink | Drink | Drink Box Pouch | 5 | 5 | 5 | 0 |
| Convenient Food Drink | Drink | Cold Beverage Lid | 80 | 77 | 77 | 1 |
| Convenient Food Drink | Drink | Household or Take-out Drink Packaging | 1 | 1 | 1 | 0 |
| Convenient Food Drink | Drink | Pull-tabs | 1 | 1 | 1 | 0 |
| Convenient Food Drink | Drink | Paper Drink Straws | 86 | 82 | 82 | 0 |
| Convenient Food Drink | Drink | Drink Straw Wrapper | 70 | 68 | 67 | 0 |
| Convenient Food Drink | Snack | Metalized Chip Bags | 10 | 10 | 10 | 0 |
| Convenient Food Drink | Snack | Chewed Gum | 12 | 12 | 12 | 0 |
| Convenient Food Drink | Snack | Foil / Plastic Film Snack Wrapper | 240 | 214 | 213 | 0 |
| Convenient Food Drink | Take-out | Cutlery | 5 | 4 | 4 | 0 |
| Convenient Food Drink | Take-out | Napkins | 94 | 79 | 79 | 0 |
| Convenient Food Drink | Take-out | Food Packaging | 131 | 120 | 120 | 0 |
| Convenient Food Drink | Take-out | Condiment Packets | 25 | 19 | 19 | 0 |
| Dumping |  | UNCLASS | 0 | 0 | 0 | 0 |
| Dumping |  | Sml | 5 | 5 | 5 | 4 |
| Dumping |  | Med | 7 | 4 | 4 | 7 |
| Dumping |  | Lrg | 0 | 0 | 0 | 0 |
| Dumping |  | Commercial Dumping | 0 | 0 | 0 | 0 |
| Piece |  | Foil Piece | 46 | 39 | 39 | 0 |
| Piece |  | Styrofoam Piece | 38 | 32 | 32 | 0 |
| Piece |  | Styrofoam Whole | 8 | 8 | 8 | 3 |
| Piece |  | Household or Unknown Metal Piece | 16 | 16 | 16 | 0 |
| Piece |  | Wood Debris | 7 | 7 | 7 | 1 |
| Piece |  | Broken Glass Piece | 5 | 2 | 2 | 0 |
| Piece |  | Paper Piece | 844 | 592 | 592 | 12 |
| Piece |  | Plastic Piece | 794 | 638 | 637 | 0 |
| Piece |  | Motor Vehicle Part Piece | 33 | 19 | 19 | 0 |
| Piece |  | Motor Vehicle Spill | 0 | 0 | 0 | 0 |
| Industrial |  | Industrial Debris | 48 | 47 | 47 | 1 |
| Industrial |  | Flagging Tape | 12 | 11 | 11 | 0 |
| Fecal |  | Pet Waste Unbagged | 53 | 47 | 47 | 53 |
| Fecal |  | Pet Waste Bagged | 50 | 46 | 46 | 45 |
| Smoking |  | Cigarette Butts | 1849 | 994 | 994 | 1 |
| Smoking |  | Butane Lighter | 1 | 1 | 1 | 0 |
| Smoking |  | Nicotine Packaging | 23 | 23 | 23 | 0 |
| Smoking |  | Cannabis Packaging | 35 | 31 | 31 | 0 |
| Smoking |  | Nicotine Vape | 0 | 0 | 0 | 0 |
| Smoking |  | Cannabis Vape | 3 | 3 | 3 | 0 |
