# MROLM audit report

Written by `scripts/sync_data.py` on every sync, following the README's "Audit counts". Items are quantities (the map counts items); objects are tagged objects; photos are OLM photos.

- Photos: 3110
- Newest photo: 2026-10-03
- Crosswalk: `config/crosswalk.csv`, SHA-256 starts `cbc16e748d62`
- Tagged objects: 3799 (5296 items)
- Shown on the map: 3798 objects (5295 items) in 67 layers

## Status counts

| Status | Meaning | Objects | Items | Healthy value |
|---|---|---:|---:|---|
| OK | Matched a map layer | 1990 | 3028 | Most objects |
| REVIEW | Matched a map layer whose crosswalk row has an "OLM data needs fixes" note (shown on the map) | 1808 | 2267 | Falls as the legacy review is done |
| Not used | Matched a row with `include on map = no` (kept off the map) | 1 | 1 | 0 |
| UNCLASS | Household dumping with no size chosen | 0 | 0 | 0 |
| Orphan tags | Custom tag attached to no object (kept off the map) | 0 | 0 | 0 |
| Unmapped | Matched no crosswalk row: a gap in the crosswalk (kept off the map) | 0 | 0 | 0 |
| Tie-breaks | Matched more than one equally specific row; the higher row won | 0 | 0 | Informational |

## REVIEW by OLM key

| OLM key | Objects | Items | Note |
|---|---:|---:|---|
| other/plastic | 638 | 794 | OLM tag review to parse out industrial debris AND other/balloon[Party Litter] objects |
| other/paper | 592 | 844 | OLM tag review parse out [Party Litter] objects |
| food/wrapper | 212 | 238 | OLM tag review of legacy entries; retag food/packaging items |
| food/packaging | 120 | 131 | OLM tag review of legacy entries |
| other/other | 90 | 99 | OLM legacy objects need reclassing |
| industrial/other | 47 | 48 | OLM tag review of legacy entries in OLM key other/metal and other/plastic and other/other industrial/pipe |
| food/bag | 36 | 37 | OLM tag review of legacy entries move take-out bags to food/packaging |
| other/metal | 16 | 16 | OLM tag review to parse out industrial debris objects |
| food/container | 13 | 13 | OLM tag review of legacy entries move take-out containers to food/packaging |
| other/plastic_bag | 12 | 13 | OLM tag review |
| industrial/tape | 11 | 12 | OLM legacy objects need reclassing |
| coffee/sleeve | 8 | 9 | OLM review of OLM key coffee/cup and softdrinks/cup and tag any untagged sleeves |
| marine/styrofoam | 8 | 8 | OLM tag review |
| alcohol/packaging | 5 | 5 | OLM legacy review and reclass THC objects to smoking/packaging with custom tag 'THC' |

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
| Convenient Food Drink | Snack | Foil / Plastic Film Snack Wrapper | 238 | 212 | 211 | 0 |
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
| Fecal |  | Pet Waste Bagged | 49 | 45 | 45 | 44 |
| Smoking |  | Cigarette Butts | 1849 | 994 | 994 | 1 |
| Smoking |  | Butane Lighter | 1 | 1 | 1 | 0 |
| Smoking |  | Nicotine Packaging | 23 | 23 | 23 | 0 |
| Smoking |  | Cannabis Packaging | 35 | 31 | 31 | 0 |
| Smoking |  | Nicotine Vape | 0 | 0 | 0 | 0 |
| Smoking |  | Cannabis Vape | 3 | 3 | 3 | 0 |
