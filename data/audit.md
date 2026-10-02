# MROLM audit report

Written by `scripts/sync_data.py` on every sync, following the README's "Audit counts". Items are quantities (the map counts items); objects are tagged objects; photos are OLM photos.

- Photos: 2836
- Newest photo: 2026-09-29
- Tagged objects: 3523 (5027 items)
- Shown on the map: 3487 objects (4990 items) in 68 layers

## Status counts

| Status | Meaning | Objects | Items | Healthy value |
|---|---|---:|---:|---|
| OK | Matched a map layer | 1821 | 2871 | Most objects |
| REVIEW | Matched a map layer whose crosswalk row has an "OLM data needs fixes" note (shown on the map) | 1666 | 2119 | Falls as the legacy review is done |
| Not used | Matched a row with `include on map = no` (kept off the map) | 36 | 37 | 0 |
| UNCLASS | Household dumping with no size chosen | 0 | 0 | 0 |
| Orphan tags | Custom tag attached to no object (kept off the map) | 0 | 0 | 0 |
| Unmapped | Matched no crosswalk row: a gap in the crosswalk (kept off the map) | 0 | 0 | 0 |
| Tie-breaks | Matched more than one equally specific row; the higher row won | 0 | 0 | Informational |

## REVIEW by OLM key

| OLM key | Objects | Items | Note |
|---|---:|---:|---|
| other/plastic | 561 | 714 | OLM tag review to parse out industrial debris AND other/balloon[Party Litter] objects |
| other/paper | 551 | 805 | OLM tag review parse out [Party Litter] objects |
| food/wrapper | 264 | 294 | OLM tag review of legacy entries; retag food/packaging items |
| food/packaging | 87 | 96 | OLM tag review of legacy entries |
| other/other | 69 | 71 | OLM legacy objects need reclassing |
| industrial/tape | 28 | 29 | OLM legacy objects need reclassing |
| food/bag | 26 | 27 | OLM tag review of legacy entries move take-out bags to food/packaging |
| other/metal | 24 | 24 | OLM tag review to parse out industrial debris objects |
| food/container | 13 | 13 | OLM tag review of legacy entries move take-out containers to food/packaging |
| other/plastic_bag | 13 | 14 | OLM tag review |
| industrial/other | 11 | 12 | OLM tag review of legacy entries in OLM key other/metal and other/plastic and other/other industrial/pipe |
| coffee/sleeve | 8 | 9 | OLM review of OLM key coffee/cup and softdrinks/cup and tag any untagged sleeves |
| marine/styrofoam | 6 | 6 | OLM tag review |
| alcohol/packaging | 5 | 5 | OLM legacy review and reclass THC objects to smoking/packaging with custom tag 'THC' |

## Not used (RECLASS) by OLM key

| OLM key | Objects | Items |
|---|---:|---:|
| other/bags_litter | 11 | 11 |
| industrial/construction | 8 | 8 |
| smoking/box | 7 | 7 |
| civic/other | 3 | 4 |
| other/poster | 3 | 3 |
| civic/blocked_drain | 1 | 1 |
| industrial/pipe | 1 | 1 |
| marine/microplastics | 1 | 1 |
| vehicles/bicycle | 1 | 1 |

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
| Household | Liquor | Liquor Can | 11 | 10 | 10 | 0 |
| Household | Liquor | Liquor Debris | 0 | 0 | 0 | 0 |
| Household | Liquor | Liquor Packaging | 5 | 5 | 5 | 1 |
| Household |  | Batteries | 2 | 2 | 2 | 0 |
| Household |  | Plastic (#4) or Paper Food Bag | 27 | 26 | 26 | 0 |
| Household |  | Corrugated Cardboard Box | 0 | 0 | 0 | 0 |
| Household |  | Household Food Can | 1 | 1 | 1 | 0 |
| Household |  | Food Container - Plastic, Paper, Foam | 13 | 13 | 13 | 0 |
| Household |  | Food Container Lid | 6 | 5 | 5 | 0 |
| Household |  | Organic Debris, Misc. | 8 | 7 | 7 | 1 |
| Household |  | Plastic Straws | 21 | 18 | 18 | 0 |
| Household |  | Medical Bandages | 8 | 7 | 7 | 0 |
| Household |  | Latex / Nitrile Glove | 11 | 10 | 10 | 0 |
| Household |  | Party Litter | 36 | 25 | 25 | 0 |
| Household |  | Abandoned Textile Apparel | 33 | 24 | 24 | 0 |
| Household |  | Household misc | 69 | 67 | 67 | 5 |
| Household |  | E-waste Piece | 2 | 2 | 2 | 0 |
| Household |  | Household Plastic Bag | 14 | 13 | 13 | 1 |
| Household |  | Pet Supplies | 2 | 2 | 2 | 0 |
| Household |  | Dental Waste | 7 | 7 | 7 | 0 |
| Household |  | Cotton Swabs | 3 | 3 | 3 | 0 |
| Household |  | Personal Hygiene Product | 1 | 1 | 1 | 0 |
| Household |  | Hygiene Paper | 12 | 10 | 10 | 0 |
| Household |  | Wet Wipes | 118 | 56 | 56 | 0 |
| Convenient Food Drink | Drink | Poly-lined Hot Beverage Cup | 28 | 26 | 26 | 1 |
| Convenient Food Drink | Drink | Hot Beverage Cup Lid | 24 | 23 | 23 | 0 |
| Convenient Food Drink | Drink | Single-Serve Coffee Pod | 2 | 2 | 2 | 0 |
| Convenient Food Drink | Drink | Corrugated Cardboard Cup Sleeve | 9 | 8 | 8 | 0 |
| Convenient Food Drink | Drink | Plastic or Glass Drink Bottle | 26 | 25 | 25 | 1 |
| Convenient Food Drink | Drink | Drink Bottle Cap | 21 | 21 | 21 | 0 |
| Convenient Food Drink | Drink | Drink Broken Glass | 6 | 1 | 1 | 0 |
| Convenient Food Drink | Drink | Aluminum Drink Cans | 9 | 9 | 9 | 1 |
| Convenient Food Drink | Drink | Drink Carton | 1 | 1 | 1 | 0 |
| Convenient Food Drink | Drink | Cold Beverage Cup | 72 | 69 | 69 | 0 |
| Convenient Food Drink | Drink | Drink Box Pouch | 3 | 3 | 3 | 0 |
| Convenient Food Drink | Drink | Cold Beverage Lid | 77 | 74 | 74 | 1 |
| Convenient Food Drink | Drink | Household or Take-out Drink Packaging | 3 | 3 | 3 | 0 |
| Convenient Food Drink | Drink | Pull-tabs | 2 | 2 | 2 | 1 |
| Convenient Food Drink | Drink | Paper Drink Straws | 72 | 69 | 69 | 0 |
| Convenient Food Drink | Drink | Drink Straw Wrapper | 64 | 63 | 63 | 0 |
| Convenient Food Drink | Snack | Metalized Chip Bags | 9 | 9 | 9 | 0 |
| Convenient Food Drink | Snack | Chewed Gum | 8 | 8 | 8 | 0 |
| Convenient Food Drink | Snack | Foil / Plastic Film Snack Wrapper | 294 | 264 | 263 | 0 |
| Convenient Food Drink | Take-out | Cutlery | 4 | 3 | 3 | 0 |
| Convenient Food Drink | Take-out | Napkins | 84 | 70 | 70 | 0 |
| Convenient Food Drink | Take-out | Food Packaging | 96 | 87 | 87 | 0 |
| Convenient Food Drink | Take-out | Condiment Packets | 22 | 16 | 16 | 0 |
| Dumping |  | UNCLASS | 0 | 0 | 0 | 0 |
| Dumping |  | Sml | 6 | 5 | 5 | 5 |
| Dumping |  | Med | 7 | 4 | 4 | 7 |
| Dumping |  | Lrg | 0 | 0 | 0 | 0 |
| Dumping |  | Commercial Dumping | 0 | 0 | 0 | 0 |
| Piece |  | Foil Piece | 31 | 24 | 24 | 0 |
| Piece |  | Styrofoam Piece | 38 | 32 | 32 | 0 |
| Piece |  | Styrofoam Whole | 6 | 6 | 6 | 1 |
| Piece |  | Household or Unknown Metal Piece | 24 | 24 | 24 | 1 |
| Piece |  | Wood Debris | 2 | 2 | 2 | 1 |
| Piece |  | Broken Glass Piece | 0 | 0 | 0 | 0 |
| Piece |  | Paper Piece | 805 | 551 | 551 | 14 |
| Piece |  | Plastic Piece | 714 | 561 | 561 | 0 |
| Piece |  | Motor Vehicle Part Piece | 32 | 18 | 18 | 0 |
| Piece |  | Motor Vehicle Spill | 3 | 1 | 1 | 0 |
| Industrial |  | Industrial Debris | 12 | 11 | 11 | 0 |
| Industrial |  | Flagging Tape | 29 | 28 | 28 | 0 |
| Fecal |  | Pet Waste Unbagged | 47 | 41 | 41 | 47 |
| Fecal |  | Pet Waste Bagged | 44 | 40 | 40 | 40 |
| Smoking |  | Cigarette Butts | 1790 | 919 | 919 | 1 |
| Smoking |  | Butane Lighter | 1 | 1 | 1 | 0 |
| Smoking |  | Nicotine Packaging | 16 | 16 | 16 | 0 |
| Smoking |  | Cannabis Packaging | 31 | 27 | 27 | 0 |
| Smoking |  | Nicotine Vape | 0 | 0 | 0 | 0 |
| Smoking |  | Cannabis Vape | 3 | 3 | 3 | 0 |
