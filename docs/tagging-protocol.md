# Field tagging protocol

These are the tagging conventions used when collecting data for this project. They matter because the crosswalk can only be as consistent as the tagging.

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
| Vehicle parts | `vehicles/car_part`, without a material tag, since materials can't be verified in the field. |
| Out of scope | Civic fixtures and signage (reported to the City instead) and posters, which often name people and could imply wrongdoing unfairly. |

**Retired OLM keys** (not used for new photos; older photos are being reclassified): `civic/bags_litter`, `civic/other`, `coffee/straw`, `industrial/pipe`, `other/bags_litter`, `other/poster`, `smoking/box`.

**Fixes happen at the source.** When older photos were tagged inconsistently, they are corrected in OpenLitterMap itself rather than patched in this repository's code. That way, anyone downloading the data from OLM gets the corrected version too.
