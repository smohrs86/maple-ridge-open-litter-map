# Maple Ridge neighbourhoods: what the City publishes

Written 2026-10-02. Purpose: record which community areas the City of Maple Ridge (COMR) publishes, what it calls them, and where it describes their boundaries, as the reference for Stage 3 zone summaries. Everything is cited to a COMR page or document. This is about geography only. Building zoning, bylaws and municipal policy are out of scope until Stage 4.

## What we use

The COMR Planning Department publishes a neighbourhoods map. MROLM uses the most recent version and cites it:

> City of Maple Ridge, Planning Department. *Maple Ridge Neighbourhoods* (map, dated 5 March 2025, scale 1:22,000). [Neighbourhoods map (JPEG)](https://www.mapleridge.ca/sites/default/files/2025-04/Neighbourhoods_NewLogo%20-%20From%20Planning%20Mar%202025_1.jpeg), shown on [Our Neighbourhoods](https://www.mapleridge.ca/explore-maple-ridge/our-neighbourhoods). Retrieved 2026-10-02.

The map's own footer states that the City makes no guarantee regarding its accuracy or the present status of the information. MROLM's zones carry the same caveat.

When a newer map is published, we switch to it, update this citation and record the date in `docs/decision-log.md`.

## What the areas are called

The words COMR itself uses, in the sources checked:

| Word | Where COMR uses it |
|---|---|
| **Neighbourhoods** | The map title ("Maple Ridge Neighbourhoods"), the Our Neighbourhoods web pages, and the Town Centre plan, which describes itself as "a neighbourhood" |
| **Area Plans** | Planning documents in OCP chapter 10 (Albion, Hammond, Silver Valley, Town Centre). An Area Plan "can apply to a group of neighbourhoods, or a single neighbourhood" |
| **Communities** | Historical only: the Town Centre plan says that before 1874 Maple Ridge was made up of a number of historic communities |
| **Hamlets** | Inside the Silver Valley plan only (Blaney, Forest, Horse) |
| **Zones** | Used for the Zoning Bylaw (building use). Not a name for these areas |
| **Quarters** | Not used |

MROLM's map will say **neighbourhoods**, matching the City's map title and avoiding confusion with building zones. "Zone summaries" stays as the internal feature name.

Residents also use several overlapping names for one place: a historic name, a street number, a compass name. The map solves this by showing the one name the City prints on its map. Alternate names can be noted on a zone (see open questions).

## The 24 neighbourhoods on the map

Names as printed on the 5 March 2025 map:

- **West and central:** Hammond, West Maple Ridge, Town Centre, Central Maple Ridge, Yennadon, Cottonwood
- **North:** South Alouette, Alouette, Silver Valley, Golden Ears
- **East and north-east:** East Maple Ridge, Smith, Websters Corners, Allco, Whispering Falls, Blue Mountain, Rothsay
- **South-east and floodplain:** Albion, Albion Flats, Albion Industrial, Thornhill, Spilsbury, Whonnock, Ruskin

Features printed on the map as boundary lines or labels. Street numbers were read from the image by eye, so treat them as approximate:

- **South edge of the city:** Fraser River, with the Lougheed Highway and the Haney Bypass along it
- **West edge:** labelled "City of Pitt Meadows / City of Maple Ridge", along about 203 St
- **East edge:** labelled "City of Maple Ridge / District of Mission"
- **Rivers and creeks:** Alouette River, North Alouette River, Kanaka Creek, Whonnock Creek
- **Roads:** Lougheed Hwy, Dewdney Trunk Rd, 112, 124, 128 and 132 Ave, and north-south streets including 207, 210, 216, 224, 228, 232, 240, 248, 256, 264 and 272 St

## Other COMR pages that name areas

**Our Neighbourhoods web pages** ([page](https://www.mapleridge.ca/node/2372)) list ten: Albion/Kanaka, Port Hammond, Port Haney, Ruskin, Silver Valley, Thornhill, Town Centre, Webster's Corners, Whonnock, Yennadon. Port Haney, Port Hammond and Albion/Kanaka are not polygons on the map. The page spells Webster's with an apostrophe, and the map does not.

**OCP Area Plans** ([page](https://www.mapleridge.ca/your-government/plans-strategies/official-community-plan-area-plans)). Boundary wording found:

| Area Plan | Wording | Source |
|---|---|---|
| Town Centre (OCP 10.4) | Historic core "bounded by Ontario Street (224th Street), Dewdney Trunk Road, Hinch Road (225th Street), and Lougheed Highway". Since expanded "as far north as 124th Avenue, west to 221st Street, and east to Burnette Street". The 2025 update added River Bend. | [Town Centre plan](https://www.mapleridge.ca/sites/default/files/2025-09/Attachment-A2-Town-Centre-Area-Plan-Update-Official-Community-Plan-Amending-Bylaw-No-8060-2025-escribe.pdf), section 1.1 |
| Hammond (OCP 10.5) | West: City of Pitt Meadows and Katzie First Nation. South: Fraser River. North: Lougheed Highway and Dewdney Trunk Road commercial areas. East: single-family residential. Boundary on "Schedule 1". | [Hammond page](https://www.mapleridge.ca/your-government/plans-strategies/official-community-plan-area-plans/area-neighbourhood-plans-0) |
| Silver Valley (OCP 10.3) | Described by features: Alouette River, North Alouette River, Millionaire Creek, Golden Ears Park, Malcolm Knapp Research Forest. Boundary is on a figure in the plan. | [Silver Valley plan](https://www.mapleridge.ca/media/file/2025-11-27-silver-valley-area-plan) |
| Albion (OCP 10.2) | No overall wording found. The North East Albion sub-area is "bound by the Kanaka Creek Regional Park to the north", existing Albion developments to the southwest, and rural residential to the east. | [Albion plan 2026](https://www.mapleridge.ca/media/file/albion-area-plan-2026pdf) |
| Lougheed Transit Corridor (adopted January 2026) and North 256 Street Industrial Lands (proposed) | Boundaries not checked | [Plans list](https://www.mapleridge.ca/your-government/plans-strategies/official-community-plan-area-plans/official-community-plan) |

Area Plan boundaries and neighbourhood-map boundaries are different. For example, the Albion Area Plan is much smaller than the neighbourhoods called Albion, Albion Flats, Albion Industrial and Cottonwood.

**Other lines the City names:** the Urban Area Boundary (OCP Schedule B), the Agricultural Land Reserve, and the municipal edges (Pitt Meadows, Mission, Fraser River).

## What was not found

- No downloadable boundary file (shapefile or GeoJSON) for the neighbourhoods. The map is a JPEG.
- No written boundary for each of the 24 neighbourhoods.
- No stated licence for the map.
- The Area Plans page links two City map tools, [Land Development Map](https://apps.vertigisstudio.com/web/?app=8b409970fec048b0940b60fe1e225e39) and [RidgeView](https://apps.vertigisstudio.com/web/?app=58c7b2da978d47cca53f48a5492ad9e2). Neither was checked for an export.

## Getting exact boundaries

The map shows where the lines are, but MROLM needs them as data to count photos per neighbourhood. In order:

1. **Ask Planning** whether a boundary file exists, and what the reuse terms are (planning@mapleridge.ca, 604-467-7341, the contact on the plan pages). Use the project's SimpleLogin alias as the reply address, never the personal one.
2. **Check the City's map tools** for an export.
3. **Cross-reference** the map with other published sources, such as street centrelines and the rivers and creeks the map follows.
4. **Derive the polygons from the map image** with a documented, repeatable method (georeference the JPEG, trace each boundary, snap to roads and watercourses). Label the result as derived from the City's map and approximate, and keep the method in `docs/` so someone else can repeat it.

Before any polygons go in the repo, confirm reuse permission. MROLM's own data licence is ODbL.

## Open questions

1. Several neighbourhoods are mostly park or forest (Golden Ears, Allco, Blue Mountain, Alouette). Show empty ones, or only those with at least one photo?
2. Port Haney, Port Hammond and Albion/Kanaka appear on the web pages but not as map polygons. Ignore them, or add them as notes on the nearest neighbourhood?
3. Which route in "Getting exact boundaries" do we try first? Route 1 (ask Planning) costs nothing and can run while we work on route 4.
