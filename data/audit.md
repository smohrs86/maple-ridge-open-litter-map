# MROLM audit report

Written by `scripts/sync_data.py` on every sync, following the README's "Audit counts". Items are quantities (the map counts items); objects are tagged objects; photos are OLM photos.

- Photos: 2680
- Newest photo: 2026-09-26
- Tagged objects: 3355 (4822 items)
- Shown on the map: 3305 objects (4762 items) in 70 layers

## Status counts

| Status | Meaning | Objects | Items | Healthy value |
|---|---|---:|---:|---|
| OK | Matched a map layer | 1731 | 2757 | Most objects |
| REVIEW | Matched a map layer whose crosswalk row has an "OLM data needs fixes" note (shown on the map) | 1574 | 2005 | Falls as the legacy review is done |
| Not used | Matched a row with `include on map = no` (kept off the map) | 41 | 51 | 0 |
| UNCLASS | Household dumping with no size chosen | 0 | 0 | 0 |
| Orphan tags | Custom tag attached to no object (kept off the map) | 9 | 9 | 0 |
| Unmapped | Matched no crosswalk row: a gap in the crosswalk (kept off the map) | 0 | 0 | 0 |
| Tie-breaks | Matched more than one equally specific row; the higher row won | 0 | 0 | Informational |

## REVIEW by OLM key

| OLM key | Objects | Items | Note |
|---|---:|---:|---|
| other/plastic | 509 | 649 | OLM tag review to parse out industrial debris AND other/balloon[Party Litter] objects |
| other/paper | 507 | 751 | OLM tag review parse out [Party Litter] objects |
| food/wrapper | 260 | 289 | OLM tag review of legacy entries; retag food/packaging items |
| food/packaging | 90 | 99 | OLM tag review of legacy entries |
| other/other | 47 | 49 | OLM legacy objects need reclassing |
| food/bag | 33 | 33 | OLM tag review of legacy entries move take-out bags to food/packaging |
| industrial/tape | 28 | 29 | OLM legacy objects need reclassing |
| other/metal | 24 | 24 | OLM tag review to parse out industrial debris objects |
| alcohol/packaging | 23 | 26 | OLM legacy review and reclass THC objects to smoking/packaging with custom tag 'THC' |
| food/container | 18 | 19 | OLM tag review of legacy entries move take-out containers to food/packaging |
| other/plastic_bag | 11 | 12 | OLM tag review |
| industrial/other | 10 | 11 | OLM tag review of legacy entries in OLM key other/metal and other/plastic and other/other industrial/pipe |
| coffee/sleeve | 7 | 7 | OLM review of OLM key coffee/cup and softdrinks/cup and tag any untagged sleeves |
| marine/styrofoam | 6 | 6 | OLM tag review |
| alcohol/other | 1 | 1 | OLM reclass on existing key data to smoking/vape |

## Not used (RECLASS) by OLM key

| OLM key | Objects | Items |
|---|---:|---:|
| other/bags_litter | 13 | 13 |
| industrial/construction | 8 | 8 |
| smoking/box | 7 | 7 |
| civic/other | 4 | 14 |
| other/poster | 3 | 3 |
| civic/bags_litter | 2 | 2 |
| civic/blocked_drain | 1 | 1 |
| industrial/pipe | 1 | 1 |
| marine/microplastics | 1 | 1 |
| vehicles/bicycle | 1 | 1 |

## Unmapped

None.

## Orphan tags

| Photo ID | Custom tag(s) |
|---|---|
| 546031 | flyer |
| 546044 | business card |
| 546048 | receipt |
| 546050 | receipt |
| 546051 | receipt |
| 546063 | construction waste |
| 546199 | sticker |
| 546407 | receipt |
| 546427 | food waste |

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
| Household | Liquor | Liquor Debris | 1 | 1 | 1 | 0 |
| Household | Liquor | Liquor Packaging | 26 | 23 | 23 | 1 |
| Household |  | Batteries | 2 | 2 | 2 | 0 |
| Household |  | Plastic (#4) or Paper Food Bag | 33 | 33 | 33 | 0 |
| Household |  | Corrugated Cardboard Box | 0 | 0 | 0 | 0 |
| Household |  | Household Food Can | 1 | 1 | 1 | 0 |
| Household |  | Food Container - Plastic, Paper, Foam | 19 | 18 | 18 | 0 |
| Household |  | Food Container Lid | 11 | 10 | 10 | 0 |
| Household |  | Organic Debris, Misc. | 16 | 16 | 16 | 0 |
| Household |  | Plastic Straws | 21 | 18 | 18 | 0 |
| Household |  | Medical Bandages | 5 | 5 | 5 | 0 |
| Household |  | Latex / Nitrile Glove | 11 | 10 | 10 | 0 |
| Household |  | Party Litter | 28 | 20 | 20 | 0 |
| Household |  | Abandoned Textile Apparel | 32 | 23 | 23 | 0 |
| Household |  | Household misc | 47 | 45 | 45 | 5 |
| Household |  | E-waste Piece | 2 | 2 | 2 | 0 |
| Household |  | Household Plastic Bag | 12 | 11 | 11 | 1 |
| Household |  | Pet Supplies | 2 | 2 | 2 | 0 |
| Household |  | Dental Waste | 6 | 6 | 6 | 0 |
| Household |  | Cotton Swabs | 3 | 3 | 3 | 0 |
| Household |  | Personal Hygiene Product | 1 | 1 | 1 | 0 |
| Household |  | Hygiene Paper | 11 | 9 | 9 | 0 |
| Household |  | Wet Wipes | 115 | 54 | 54 | 0 |
| Convenient Food Drink | Drink | Poly-lined Hot Beverage Cup | 28 | 26 | 26 | 0 |
| Convenient Food Drink | Drink | Hot Beverage Cup Lid | 25 | 24 | 24 | 0 |
| Convenient Food Drink | Drink | Single-Serve Coffee Pod | 2 | 2 | 2 | 0 |
| Convenient Food Drink | Drink | Corrugated Cardboard Cup Sleeve | 7 | 7 | 7 | 0 |
| Convenient Food Drink | Drink | Plastic or Glass Drink Bottle | 24 | 23 | 23 | 1 |
| Convenient Food Drink | Drink | Drink Bottle Cap | 19 | 19 | 19 | 0 |
| Convenient Food Drink | Drink | Drink Broken Glass | 6 | 1 | 1 | 0 |
| Convenient Food Drink | Drink | Aluminum Drink Cans | 9 | 9 | 9 | 1 |
| Convenient Food Drink | Drink | Drink Carton | 1 | 1 | 1 | 0 |
| Convenient Food Drink | Drink | Cold Beverage Cup | 72 | 69 | 69 | 1 |
| Convenient Food Drink | Drink | Drink Box Pouch | 3 | 3 | 3 | 0 |
| Convenient Food Drink | Drink | Cold Beverage Lid | 68 | 65 | 65 | 1 |
| Convenient Food Drink | Drink | Household or Take-out Drink Packaging | 2 | 2 | 2 | 0 |
| Convenient Food Drink | Drink | Pull-tabs | 2 | 2 | 2 | 1 |
| Convenient Food Drink | Drink | Paper Drink Straws | 70 | 67 | 67 | 0 |
| Convenient Food Drink | Drink | Drink Straw Wrapper | 64 | 63 | 63 | 0 |
| Convenient Food Drink | Snack | Metalized Chip Bags | 4 | 4 | 4 | 0 |
| Convenient Food Drink | Snack | Chewed Gum | 6 | 6 | 6 | 0 |
| Convenient Food Drink | Snack | Foil / Plastic Film Snack Wrapper | 289 | 260 | 260 | 0 |
| Convenient Food Drink | Take-out | Cutlery | 5 | 4 | 4 | 0 |
| Convenient Food Drink | Take-out | Napkins | 82 | 68 | 68 | 0 |
| Convenient Food Drink | Take-out | Food Packaging | 99 | 90 | 90 | 0 |
| Convenient Food Drink | Take-out | Condiment Packets | 20 | 14 | 14 | 0 |
| Dumping |  | UNCLASS | 0 | 0 | 0 | 0 |
| Dumping |  | Sml | 6 | 6 | 6 | 5 |
| Dumping |  | Med | 5 | 2 | 2 | 5 |
| Dumping |  | Lrg | 0 | 0 | 0 | 0 |
| Dumping |  | Commercial Dumping | 4 | 3 | 3 | 2 |
| Piece |  | Foil Piece | 27 | 20 | 20 | 0 |
| Piece |  | Styrofoam Piece | 38 | 32 | 32 | 0 |
| Piece |  | Styrofoam Whole | 6 | 6 | 6 | 1 |
| Piece |  | Household or Unknown Metal Piece | 24 | 24 | 24 | 1 |
| Piece |  | Wood Debris | 2 | 2 | 2 | 1 |
| Piece |  | Broken Glass Piece | 0 | 0 | 0 | 0 |
| Piece |  | Paper Piece | 751 | 507 | 507 | 14 |
| Piece |  | Plastic Piece | 649 | 509 | 509 | 0 |
| Piece |  | Motor Vehicle Part Piece | 32 | 18 | 18 | 0 |
| Piece |  | Motor Vehicle Spill | 3 | 1 | 1 | 0 |
| Industrial |  | Industrial Debris | 11 | 10 | 10 | 0 |
| Industrial |  | Flagging Tape | 29 | 28 | 28 | 0 |
| Fecal |  | Pet Waste Unbagged | 46 | 40 | 40 | 46 |
| Fecal |  | Pet Waste Bagged | 43 | 39 | 39 | 39 |
| Smoking |  | Cigarette Butts | 1737 | 880 | 880 | 1 |
| Smoking |  | Butane Lighter | 1 | 1 | 1 | 0 |
| Smoking |  | Nicotine Packaging | 12 | 12 | 12 | 0 |
| Smoking |  | Cannabis Packaging | 8 | 8 | 8 | 0 |
| Smoking |  | Nicotine Vape | 0 | 0 | 0 | 0 |
| Smoking |  | Cannabis Vape | 2 | 2 | 2 | 0 |
