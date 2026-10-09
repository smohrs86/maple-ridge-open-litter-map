# Field tagging protocol

These are the tagging conventions used when collecting data for this project. They matter because the crosswalk can only be as consistent as the tagging.

**Where litter is collected.** Public ground (streets and sidewalks) and, on Adopt-a-Block routes, up to one arm's length into residential frontage. Nothing is collected from frontage that is fenced off or posted with a sign, or from places that are hard or unsafe to reach. Places where litter accumulates on public ground, such as culverts, are recorded, because where litter collects matters as much as what it is.

**Which side of the street (from 2026-10-07).** Streets are worked with the road always on the collector's right: along one side, across at the far end, and back along the other side. This keeps outings consistent, and it means the side of the street can later be worked out from the direction of travel, because phone GPS is often not precise enough to tell the two sidewalks apart. Trails and parks have no side. Outings before 2026-10-07 don't follow this rule reliably.

**What is picked up.** Sharps are picked up with tongs and gloves into a biohazard container. Litter soiled with human waste or body fluids (for example a soiled diaper or wipes) and dangerous or toxic items (for example a damaged car battery) are not picked up; they are photographed and tagged as left in place.

**Photos.** Following OLM's upload tips ("close-up, object fills frame" and "no people, no personal info"): one item, or a tight group of the same item, per photo, with no wide shots. Litter is photographed as it is found, because moving or rearranging it would change what the record shows. The order of preference is:
1. Photograph it as it is found, in a tight frame.
2. If personal information would show, crop, angle, or frame the photo to keep faces, licence plates, house numbers, addresses, and anything showing a name or account number (mail, receipts, IDs) out of the shot.
3. If the litter is buried in vegetation (plants, brambles, grass) and can't be identified as it lies, uncover it and photograph it where it was found.
4. Only if it still can't be identified in place, dig it out and arrange it as one tight group for the photo. This is the only case where litter is moved.

Items that carry a person's contact details or address, such as business cards and garage sale signs, are only photographed if the text is unreadable in the frame; if the text can't be hidden, the photo is skipped or deleted. Every effort is made to keep personal information out of frame; if some still gets through, email the project at the contact address in the README. Some older photos are wide shots from before this rule.

| Situation | How it's tagged |
|---|---|
| Household dumping | `dumping/dumping` with a size, measured by the item's longest dimension. **Small:** can be carried away by hand, under 30 cm (e.g. a ladle). **Medium:** can't be carried away but smaller than a fridge or couch, 30–90 cm (e.g. a printer). **Large:** bigger than a full garbage bag, over 90 cm (e.g. an ironing board). Always choose a size; unsized photos land in UNCLASS. |
| Commercial dumping | `dumping/other` |
| Cigarette butts | `smoking/butts`. OLM allows a maximum of 10 per photo, so large clusters are split across photos taken at the same spot. |
| Cannabis products | `smoking/packaging` or `smoking/vape` with the custom tag `THC`. Alcohol keys are no longer used for cannabis. |
| Hot vs cold drinks | Hot takeout cups and lids: `coffee/cup`, `coffee/lid`. Cold drinks, including cold coffee: `softdrinks/cup`, `softdrinks/lid`. |
| Straws | Takeout straws (paper): `softdrinks/straw`. Household plastic straws: `food/straw`. |
| Polystyrene | Whole blocks: `marine/styrofoam`. Fragments: `marine/polystyrene_fragment`. |
| Industrial debris | `industrial/other` for everything industrial except tape, which is `industrial/tape`. |
| Unidentifiable paper | `other/paper`, including napkins and tissue that can't be identified once wet or aged. |
| Party litter | `other/balloon`, with a shared custom tag on every associated item using the pattern `PAR` + date + letter, e.g. `PAR20260922A`. |
| Wood pieces | `other/other` with material `Wood`, for wood debris that can't be identified as industrial. Wood that is clearly a commercial or industrial piece goes under `industrial/other`. |
| Broken glass pieces | `other/other` with the custom tag `broken glass`, for a single piece of broken glass. |
| E-waste pieces | `other/other` with the custom tag `E-waste`, for a piece of household electronic waste. Spell it with the hyphen: capitals and spaces don't matter, but `ewaste` won't match. |
| Pieces | A piece is part of an item that has come away from its parent. Tag every piece you pick up as its own object, classed by main material: mostly plastic, or assumed plastic, `other/plastic`; mostly foil (a gum wrapper piece, a small metallic ball) `food/tinfoil`; paper or cardboard `other/paper`. If the parent is there too, tag it under its own key: a run-over lid in three bits is `softdrinks/lid` ×1 plus `other/plastic` ×2. MROLM doesn't record which piece came from which parent; the photos preserve that for finer visual analysis beyond this project's scope. The custom tag `Piece` is no longer used for tracking: the key alone puts a piece in its MROLM layer (Plastic Piece, Foil Piece, Paper Piece, and so on) through the crosswalk, so `Piece` and the legacy `Partial` are optional and ignored. |
| Lighters | `smoking/lighters` for a whole lighter only. A lighter piece is tagged by what it is: `other/plastic` or `other/metal` by main material, `other/other` + `E-waste` for an electronic part, or `other/other` if neither fits. |
| Foil pieces | `food/tinfoil`, for any foil piece, whether from household foil, wrappers, or bags. |
| Vehicle parts | `vehicles/car_part`, without a material tag, since materials can't be verified in the field. |
| Out of scope | Civic fixtures and signage, and litter problems on private property such as accumulation behind a fence: not photographed, and reported to the City when that is reasonable. Posters, which often name people and could imply wrongdoing unfairly. Waterways, which need their own monitoring method. |

**Retired OLM keys** (not used for new photos; older photos are being reclassified): `civic/bags_litter`, `civic/other`, `coffee/straw`, `industrial/pipe`, `other/bags_litter`, `other/poster`, `smoking/box`.

**Fixes happen at the source.** When older photos were tagged inconsistently, they are corrected in OpenLitterMap itself rather than patched in this repository's code. That way, anyone downloading the data from OLM gets the corrected version too.
