import argparse
import csv
import hashlib
import os
import sys
import time
import json
import math
import re
from collections import defaultdict
import requests

import crosswalk as cw
import monthly_store as store

LOGIN_URL = "https://openlittermap.com/api/auth/token"
PHOTOS_URL = "https://openlittermap.com/api/v3/user/photos"

assert "v3" in PHOTOS_URL, "PHOTOS_URL must use the v3 endpoint — v1 was removed by OpenLitterMap"

CROSSWALK_PATH = "config/crosswalk.csv"
# Columns the engine reads (by header name, so the sheet's column order doesn't matter).
CROSSWALK_COLUMNS = ("OLM key",) + cw.NARROWING_COLUMNS + (
    "MROLM Group", "MROLM Subgroup", "MROLM local key", "include on map", "OLM data needs fixes")
# Statuses shown on the map. REVIEW is shown normally (decision log, 2026-09-26);
# RECLASS, UNMAPPED and ORPHAN TAG stay off the map and are counted in the audit.
MAP_STATUSES = ("OK", "REVIEW", "UNCLASS")
AUDIT_PATH = "data/audit.md"
# Neighbourhoods and their zones: the map's summary areas (decision log, 2026-10-02). Optional:
# if either file is missing or unusable, photos simply get no zone and the sync carries on.
NEIGHBOURHOODS_PATH = "config/neighbourhoods.csv"
ZONES_PATH = "config/zones.csv"
# Phone GPS can be off by roughly this much (README: 5 to 15 m). OLM sends no per-photo accuracy,
# so one assumed value is used. A photo closer than this to a zone edge is flagged on the map's cards.
GPS_ERROR_M = 15
INCREMENTAL_MIN_PAGES = 25  # about 200 photos (roughly 3 days of collecting) are always re-read
DATA_DIR = "data"
M_PER_DEG_LAT = 111320


def classify_tag_group(tag):  
    category = tag.get("category")  
    parent_category = tag.get("parent_category")  
    item = str(tag.get("item", "")).lower()  
    tag_type = tag.get("type")  
 
    if tag_type == "custom_tag" and any(kw in item for kw in ("thc", "cannabis", "weed")):  
        return "substances"  
    if category in ("smoking", "alcohol"):  
        return "substances"  
    if parent_category in ("smoking", "alcohol"):  
        return "substances"  
    if category == "pets" and item in ("dogshit", "dogshit_in_bag"):  
        return "pet_waste"  
    return "litter"


def resolve_new_tags_format(tag_entry):
    formatted = []
    clo_id = tag_entry.get("category_litter_object_id")
    category = tag_entry.get("category") or {}
    obj = tag_entry.get("object") or {}

    if clo_id is not None:
        formatted.append({
            "type": "standard",
            "category": category.get("key", "unclassified"),
            "item": obj.get("key", "unclassified"),
            "quantity": tag_entry.get("quantity", 1),
        })
        type_key = (tag_entry.get("type") or {}).get("key")
        if type_key:
            formatted[-1]["object_type"] = type_key

    for extra in tag_entry.get("extra_tags") or []:
        tag_info = extra.get("tag") or {}
        formatted.append({
            "type": extra.get("type", "extra"),
            "category": extra.get("type", "extra"),
            "item": tag_info.get("key", "unclassified"),
            "quantity": extra.get("quantity", tag_entry.get("quantity", 1)),
            "parent_category": category.get("key"),
            "parent_item": obj.get("key"),
        })
    return formatted


def resolve_summary_format(tag_entry, keys):
    formatted = []
    clo_id = tag_entry.get("clo_id")
    category_name = keys.get("categories", {}).get(str(tag_entry.get("category_id")))
    object_name = keys.get("objects", {}).get(str(tag_entry.get("object_id")))

    if clo_id is not None:
        formatted.append({
            "type": "standard",
            "category": category_name or "unclassified",
            "item": object_name or "unclassified",
            "quantity": tag_entry.get("quantity", 1),
        })
        type_key = keys.get("types", {}).get(str(tag_entry.get("type_id")))
        if type_key:
            formatted[-1]["object_type"] = type_key

    for mat_id in tag_entry.get("materials") or []:
        formatted.append({
            "type": "material",
            "category": "material",
            "item": keys.get("materials", {}).get(str(mat_id), "unclassified"),
            "quantity": tag_entry.get("quantity", 1),
            "parent_category": category_name,
            "parent_item": object_name,
        })

    brands = tag_entry.get("brands")
    brand_ids = list(brands.keys()) if isinstance(brands, dict) else (brands or [])
    for brand_id in brand_ids:
        formatted.append({
            "type": "brand",
            "category": "brand",
            "item": keys.get("brands", {}).get(str(brand_id), "unclassified"),
            "quantity": tag_entry.get("quantity", 1),
            "parent_category": category_name,
            "parent_item": object_name,
        })

    for custom_id in tag_entry.get("custom_tags") or []:
        formatted.append({
            "type": "custom_tag",
            "category": "custom_tag",
            "item": keys.get("custom_tags", {}).get(str(custom_id), "unclassified"),
            "quantity": tag_entry.get("quantity", 1),
            "parent_category": category_name,
            "parent_item": object_name,
        })

    return formatted


def load_crosswalk(path=CROSSWALK_PATH):
    """Read the crosswalk, or stop the run before anything is written if it can't be used."""
    try:
        rows = cw.load_crosswalk(path)
    except (OSError, UnicodeDecodeError, csv.Error) as exc:
        print(f"[CRITICAL ERROR] Could not read {path}: {exc}. No files were written.")
        sys.exit(1)
    if not rows:
        print(f"[CRITICAL ERROR] {path} has no rows. No files were written.")
        sys.exit(1)
    missing = [col for col in CROSSWALK_COLUMNS if col not in rows[0]]
    if missing:
        print(f"[CRITICAL ERROR] {path} is missing column(s) {missing}. Was a header renamed? No files were written.")
        sys.exit(1)
    print(f"[INFO] Loaded {len(rows)} crosswalk rows from {path}.")
    return rows


def crosswalk_version(path=CROSSWALK_PATH):
    """A short fingerprint of the crosswalk file (first 12 characters of its SHA-256).

    Same file, same fingerprint; any edit changes it. Check by hand with: sha256sum config/crosswalk.csv
    """
    with open(path, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()[:12]


def load_zones(neighbourhoods_path=NEIGHBOURHOODS_PATH, zones_path=ZONES_PATH):
    """Read the neighbourhoods and their zones (rectangles). Returns ([], []) with a warning if they can't be used."""
    try:
        with open(neighbourhoods_path, newline="", encoding="utf-8") as f:
            neighbourhoods = [{"key": r["key"].strip(), "name": r["name"].strip(), "colour": r["colour"].strip()}
                              for r in csv.DictReader(f)]
        with open(zones_path, newline="", encoding="utf-8") as f:
            zones = [{
                "id": r["zone_id"].strip(),
                "neighbourhood": r["neighbourhood"].strip(),
                "letter": r["letter"].strip(),
                "description": r["description"].strip(),
                "south_lat": float(r["south_lat"]), "north_lat": float(r["north_lat"]),
                "west_lon": float(r["west_lon"]), "east_lon": float(r["east_lon"]),
            } for r in csv.DictReader(f)]
    except (OSError, UnicodeDecodeError, csv.Error, KeyError, ValueError) as exc:
        print(f"[WARNING] Could not use the neighbourhood and zone files: {exc}. Photos will have no zone.")
        return [], []

    problem = None
    keys = {n["key"] for n in neighbourhoods}
    if len(keys) != len(neighbourhoods):
        problem = "a neighbourhood key is used twice"
    elif any(not re.fullmatch(r"#[0-9a-fA-F]{6}", n["colour"]) for n in neighbourhoods):
        problem = "a neighbourhood colour is not like #0f7b8a"
    elif len({z["id"] for z in zones}) != len(zones):
        problem = "a zone_id is used twice"
    elif any(z["neighbourhood"] not in keys for z in zones):
        problem = "a zone names a neighbourhood that is not in neighbourhoods.csv"
    elif any(z["south_lat"] >= z["north_lat"] or z["west_lon"] >= z["east_lon"] for z in zones):
        problem = "a zone's south or west edge is not south or west of its north or east edge"
    else:
        for i, a in enumerate(zones):
            for b in zones[i + 1:]:
                if (a["south_lat"] < b["north_lat"] and b["south_lat"] < a["north_lat"]
                        and a["west_lon"] < b["east_lon"] and b["west_lon"] < a["east_lon"]):
                    problem = f"zones {a['id']} and {b['id']} overlap"
    if problem:
        print(f"[WARNING] {zones_path}: {problem}. Photos will have no zone.")
        return [], []
    used = {z["neighbourhood"] for z in zones}
    neighbourhoods = [n for n in neighbourhoods if n["key"] in used]   # only neighbourhoods that have zones
    print(f"[INFO] Loaded {len(zones)} zones in {len(neighbourhoods)} neighbourhood(s).")
    return neighbourhoods, zones


def assign_zone(lat, lon, zones):
    """The zone holding this point, or None. A zone includes its south and west edges, so no point is in two zones."""
    for z in zones:
        if z["south_lat"] <= lat < z["north_lat"] and z["west_lon"] <= lon < z["east_lon"]:
            return z
    return None


def zone_edge_distances(lat, lon, zone, zones):
    """Metres from a point to the nearest edge of its own zone, and to the nearest zone of a different
    neighbourhood (None if there is none). Flat-earth maths, accurate to centimetres at this scale."""
    if zone is None:
        return None, None
    m_per_deg_lon = M_PER_DEG_LAT * math.cos(math.radians(lat))
    to_edge = min((lat - zone["south_lat"]) * M_PER_DEG_LAT, (zone["north_lat"] - lat) * M_PER_DEG_LAT,
                  (lon - zone["west_lon"]) * m_per_deg_lon, (zone["east_lon"] - lon) * m_per_deg_lon)
    others = [z for z in zones if z["neighbourhood"] != zone["neighbourhood"]]
    to_other = None
    for z in others:
        dy = max(z["south_lat"] - lat, 0, lat - z["north_lat"]) * M_PER_DEG_LAT
        dx = max(z["west_lon"] - lon, 0, lon - z["east_lon"]) * m_per_deg_lon
        d = math.hypot(dx, dy)
        to_other = d if to_other is None else min(to_other, d)
    return round(to_edge, 1), None if to_other is None else round(to_other, 1)


def picked_up_state(value):
    """True, False, or None when OLM didn't say."""
    return bool(value) if value in (True, False) else None


def extract_objects(photo):
    """One entry per tagged object, with everything the crosswalk can match on.

    olm_key is "" for an orphan custom tag (a custom tag attached to no object).
    """
    objects = []
    new_tags = photo.get("new_tags")

    if new_tags:
        for entry in new_tags:
            category = (entry.get("category") or {}).get("key")
            obj = (entry.get("object") or {}).get("key")
            extras = entry.get("extra_tags") or []
            objects.append({
                "olm_key": f"{category}/{obj}" if category and obj else "",
                "secondary": (entry.get("type") or {}).get("key") or "",
                "materials": [(e.get("tag") or {}).get("key", "") for e in extras if e.get("type") == "material"],
                "customs": [(e.get("tag") or {}).get("key", "") for e in extras if e.get("type") == "custom_tag"],
                "quantity": entry.get("quantity", 1),
                "picked_up": picked_up_state(entry.get("picked_up")),
            })
    else:
        summary = photo.get("summary") or {}
        keys = summary.get("keys", {})
        for entry in summary.get("tags", []):
            category = keys.get("categories", {}).get(str(entry.get("category_id")))
            obj = keys.get("objects", {}).get(str(entry.get("object_id")))
            objects.append({
                "olm_key": f"{category}/{obj}" if category and obj else "",
                "secondary": keys.get("types", {}).get(str(entry.get("type_id"))) or "",
                "materials": [keys.get("materials", {}).get(str(i), "") for i in entry.get("materials") or []],
                "customs": [keys.get("custom_tags", {}).get(str(i), "") for i in entry.get("custom_tags") or []],
                "quantity": entry.get("quantity", 1),
                "picked_up": picked_up_state(entry.get("picked_up")),
            })
    return objects


def classify_object(raw, crosswalk_rows):
    """Apply the crosswalk to one object (README "Matching rules") and describe it for the map and audit."""
    result = {"status": "", "on_map": False, "group": "", "subgroup": "", "layer": "", "full_name": "",
              "olm_key": raw["olm_key"], "quantity": raw["quantity"], "picked_up": raw["picked_up"]}

    if not raw["olm_key"]:
        result["status"] = "ORPHAN TAG"
        result["custom_tags"] = raw["customs"]
    else:
        row, tied = cw.match_tag(crosswalk_rows, raw["olm_key"], raw["secondary"], raw["materials"], raw["customs"])
        if row is None:
            result["status"] = "UNMAPPED"
        else:
            group, subgroup, layer = (row[c].strip() for c in ("MROLM Group", "MROLM Subgroup", "MROLM local key"))
            result.update(status=cw.classify(row), group=group, subgroup=subgroup, layer=layer,
                          full_name=" – ".join(part for part in (group, subgroup, layer) if part))
            if tied:
                result["tie_rows"] = [r["_sheet_row"] for r in tied]

    result["on_map"] = result["status"] in MAP_STATUSES
    return result


def tree_layers(crosswalk_rows):
    """Map layers as (group, subgroup, layer) in tree order: each Group together, each
    Subgroup together within it, in order of first appearance in the sheet."""
    layers = []
    for r in crosswalk_rows:
        if cw.norm(r["include on map"]) != "yes":
            continue
        layer = tuple(r[c].strip() for c in ("MROLM Group", "MROLM Subgroup", "MROLM local key"))
        if layer not in layers:
            layers.append(layer)
    group_rank = {g: i for i, g in reversed(list(enumerate(l[0] for l in layers)))}
    sub_rank = {gs: i for i, gs in reversed(list(enumerate(l[:2] for l in layers)))}
    return sorted(layers, key=lambda l: (group_rank[l[0]], sub_rank[l[:2]]))


def _cell(text):
    return str(text).replace("|", "\\|")


def build_audit(features, crosswalk_rows, dropped=(), crosswalk_hash=None):
    """The audit report (README "Audit counts") as Markdown.

    `dropped` is a list of (photo id, reason) for photos left out because of their coordinates.
    `crosswalk_hash` is the crosswalk's fingerprint (crosswalk_version), shown so any number can be traced to it.

    No timestamp: an unchanged dataset gives an unchanged file, so the workflow makes no commit.
    """
    objects = [(f["properties"]["id"], o) for f in features for o in f["properties"]["objects"]]

    def items(entries):
        return sum(o["quantity"] or 0 for _, o in entries)

    by_status = defaultdict(list)
    for entry in objects:
        by_status[entry[1]["status"]].append(entry)
    on_map = [e for e in objects if e[1]["on_map"]]
    ties = [e for e in objects if e[1].get("tie_rows")]
    newest = max((f["properties"].get("datetime") or "" for f in features), default="")

    lines = [
        "# MROLM audit report",
        "",
        "Written by `scripts/sync_data.py` on every sync, following the README's \"Audit counts\". "
        "Items are quantities (the map counts items); objects are tagged objects; photos are OLM photos.",
        "",
        f"- Photos: {len(features)}" + (f" ({len(dropped)} more skipped: "
                                      f"{' and '.join(sorted({reason for _, reason in dropped}))})" if dropped else ""),
        f"- Newest photo: {newest[:10] or 'none'}",
        *([f"- Crosswalk: `{CROSSWALK_PATH}`, SHA-256 starts `{crosswalk_hash}`"] if crosswalk_hash else []),
        f"- Tagged objects: {len(objects)} ({items(objects)} items)",
        f"- Shown on the map: {len(on_map)} objects ({items(on_map)} items) in "
        f"{len({(o['group'], o['subgroup'], o['layer']) for _, o in on_map})} layers",
        "",
        "## Status counts",
        "",
        "| Status | Meaning | Objects | Items | Healthy value |",
        "|---|---|---:|---:|---|",
    ]
    status_rows = [
        ("OK", "OK", "Matched a map layer", "Most objects"),
        ("REVIEW", "REVIEW", "Matched a map layer whose crosswalk row has an \"OLM data needs fixes\" note (shown on the map)",
         "Falls as the legacy review is done"),
        ("RECLASS", "Not used", "Matched a row with `include on map = no` (kept off the map)", "0"),
        ("UNCLASS", "UNCLASS", "Household dumping with no size chosen", "0"),
        ("ORPHAN TAG", "Orphan tags", "Custom tag attached to no object (kept off the map)", "0"),
        ("UNMAPPED", "Unmapped", "Matched no crosswalk row: a gap in the crosswalk (kept off the map)", "0"),
    ]
    for status, label, meaning, healthy in status_rows:
        entries = by_status.get(status, [])
        lines.append(f"| {label} | {meaning} | {len(entries)} | {items(entries)} | {healthy} |")
    lines.append(f"| Tie-breaks | Matched more than one equally specific row; the higher row won | "
                 f"{len(ties)} | {items(ties)} | Informational |")

    def keyed_table(title, entries, note_rows=None):
        lines.extend(["", f"## {title}", ""])
        if not entries:
            lines.append("None.")
            return
        grouped = defaultdict(list)
        for entry in entries:
            grouped[entry[1]["olm_key"]].append(entry)
        header = "| OLM key | Objects | Items |" + (" Note |" if note_rows else "")
        lines.extend([header, "|---|---:|---:|" + ("---|" if note_rows else "")])
        for key, group in sorted(grouped.items(), key=lambda kv: (-len(kv[1]), kv[0])):
            note = f" {_cell(note_rows.get(key, ''))} |" if note_rows else ""
            lines.append(f"| {_cell(key)} | {len(group)} | {items(group)} |{note}")

    notes = {}
    for row in crosswalk_rows:
        notes.setdefault(cw.norm(row["OLM key"]), row["OLM data needs fixes"].strip())
    review_notes = {o["olm_key"]: notes.get(cw.norm(o["olm_key"]), "") for _, o in by_status.get("REVIEW", [])}
    keyed_table("REVIEW by OLM key", by_status.get("REVIEW", []), review_notes)
    keyed_table("Not used (RECLASS) by OLM key", by_status.get("RECLASS", []))

    lines.extend(["", "## Unmapped", ""])
    unmapped = by_status.get("UNMAPPED", [])
    if unmapped:
        lines.extend(["| OLM key | Photo IDs |", "|---|---|"])
        per_key = defaultdict(set)
        for pid, o in unmapped:
            per_key[o["olm_key"]].add(pid)
        for key in sorted(per_key):
            lines.append(f"| {_cell(key)} | {', '.join(str(p) for p in sorted(per_key[key]))} |")
    else:
        lines.append("None.")

    lines.extend(["", "## Orphan tags", ""])
    orphans = sorted(by_status.get("ORPHAN TAG", []), key=lambda e: e[0])
    if orphans:
        lines.extend(["| Photo ID | Custom tag(s) |", "|---|---|"])
        lines.extend(f"| {pid} | {_cell(', '.join(o.get('custom_tags') or []))} |" for pid, o in orphans)
    else:
        lines.append("None.")

    lines.extend(["", "## Tie-breaks", ""])
    if ties:
        lines.extend(["| Photo ID | OLM key | Layer used | Tied sheet rows |", "|---|---|---|---|"])
        lines.extend(f"| {pid} | {_cell(o['olm_key'])} | {_cell(o['layer'])} | {', '.join(map(str, o['tie_rows']))} |"
                     for pid, o in sorted(ties, key=lambda e: e[0]))
    else:
        lines.append("None.")

    if dropped:
        lines.extend(["", "## Dropped photos", "", "| Photo ID | Reason |", "|---|---|"])
        lines.extend(f"| {pid} | {reason} |" for pid, reason in sorted(dropped, key=lambda d: str(d[0])))

    included = [r for r in crosswalk_rows if cw.norm(r["include on map"]) == "yes"]
    standalone = sorted({r["MROLM local key"].strip() for r in included if not r["MROLM Group"].strip()})
    orphan_subgroups = [r["_sheet_row"] for r in crosswalk_rows
                        if r["MROLM Subgroup"].strip() and not r["MROLM Group"].strip()]
    no_layer = [r["_sheet_row"] for r in included if not r["MROLM local key"].strip()]
    convention = [r["_sheet_row"] for r in cw.convention_problems(crosswalk_rows)]
    lines.extend([
        "", "## Crosswalk checks", "",
        f"- Standalone layers (no Group; informational): {', '.join(standalone) or 'none'}",
        f"- Subgroup without a Group (error), sheet rows: {', '.join(map(str, orphan_subgroups)) or 'none'}",
        f"- Map rows with no local key (error), sheet rows: {', '.join(map(str, no_layer)) or 'none'}",
        f"- Local key = OLM key but `include on map` is not `no` (error), sheet rows: "
        f"{', '.join(map(str, convention)) or 'none'}",
    ])

    # Every map layer, including empty ones, so a to-do layer at 0 is visible.
    layer_stats = defaultdict(lambda: {"objects": 0, "items": 0, "photos": set(), "left": 0})
    for pid, o in on_map:
        stats = layer_stats[(o["group"], o["subgroup"], o["layer"])]
        stats["objects"] += 1
        stats["items"] += o["quantity"] or 0
        stats["photos"].add(pid)
        if o["picked_up"] is False:
            stats["left"] += o["quantity"] or 0
    layers = tree_layers(crosswalk_rows)
    lines.extend(["", "## Layers", "",
                  "| Group | Subgroup | Layer | Items | Objects | Photos | Not picked up (items) |",
                  "|---|---|---|---:|---:|---:|---:|"])
    for layer in layers:
        s = layer_stats.get(layer, {"objects": 0, "items": 0, "photos": set(), "left": 0})
        lines.append(f"| {' | '.join(_cell(p) for p in layer)} | {s['items']} | {s['objects']} | "
                     f"{len(s['photos'])} | {s['left']} |")

    return "\n".join(lines) + "\n"


def build_photo_properties(photo, crosswalk_rows):
    formatted_tags = []
    new_tags = photo.get("new_tags")

    if new_tags:
        for entry in new_tags:
            formatted_tags.extend(resolve_new_tags_format(entry))
    else:
        summary = photo.get("summary") or {}
        keys = summary.get("keys", {})
        for entry in summary.get("tags", []):
            formatted_tags.extend(resolve_summary_format(entry, keys))

    groups = sorted({classify_tag_group(tag) for tag in formatted_tags}) or ["litter"]

    return {
        "id": photo.get("id"),
        "datetime": photo.get("datetime"),
        "filename": photo.get("filename"),
        "tags": formatted_tags,
        "objects": [classify_object(o, crosswalk_rows) for o in extract_objects(photo)],
        "groups": groups,
        "has_litter": "litter" in groups,
        "has_pet_waste": "pet_waste" in groups,
        "has_substances": "substances" in groups
    }


def get_auth_token(email, password, retries=2, delay=3):
    payload = {"email": email, "password": password}
    headers = {"Accept": "application/json"}
    
    for attempt in range(retries + 1):
        try:
            print(f"[INFO] Authenticating against OLM ({LOGIN_URL})...")
            response = requests.post(LOGIN_URL, json=payload, headers=headers, timeout=30)
            if response.status_code == 200:
                data = response.json()
                token = data.get("token") or data.get("access_token")
                if token:
                    print("[SUCCESS] Obtained session token.")
                    return token
        except requests.RequestException as exc:
            print(f"[WARN] Auth attempt {attempt + 1} failed: {exc}")
        time.sleep(delay)

    print("[CRITICAL ERROR] Failed to authenticate with OLM.")
    sys.exit(1)


class TokenRejected(Exception):
    """OLM answered HTTP 401: the login token is no longer accepted."""


def get_page_with_retries(headers, params, retries=3, base_delay=2):
    """GET one page of photos. Returns the response, or None if it could not be fetched.

    Retries on network errors, HTTP 429 (rate limited) and HTTP 5xx (server trouble),
    waiting base_delay * 2^n seconds between tries (2s, 4s, 8s). HTTP 401 raises
    TokenRejected so the caller can log in again. Other HTTP errors (404, ...) will
    not fix themselves, so they are not retried.
    """
    page = params["page"]
    for attempt in range(retries + 1):
        try:
            response = requests.get(PHOTOS_URL, headers=headers, params=params, timeout=30)
            if response.status_code == 200:
                return response
            if response.status_code == 401:
                raise TokenRejected(f"HTTP 401 on page {page}")
            if response.status_code != 429 and response.status_code < 500:
                print(f"[ERROR] HTTP {response.status_code} received on page {page}. Not retrying.")
                return None
            print(f"[WARN] HTTP {response.status_code} on page {page} (attempt {attempt + 1} of {retries + 1}).")
        except requests.RequestException as exc:
            print(f"[WARN] Network exception on page {page} (attempt {attempt + 1} of {retries + 1}): {exc}")

        if attempt < retries:
            wait = base_delay * (2 ** attempt)
            print(f"[INFO] Waiting {wait}s before retrying page {page}...")
            time.sleep(wait)

    print(f"[ERROR] Page {page} failed after {retries + 1} attempts.")
    return None


def fetch_all_photos(token, get_new_token=None, max_relogins=3, known_ids=None, min_pages=INCREMENTAL_MIN_PAGES):
    """Read OLM's photo pages, newest upload first.

    With known_ids (a set of photo ids already stored), stop at the first page after min_pages
    on which every photo is already known: everything older is stored too. The minimum re-reads
    the newest photos every run so a retag of a recent photo is picked up. Without known_ids,
    read until an empty page (a full read).
    """
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/json"
    }

    all_photos = []
    current_page = 1
    max_safety_pages = 20000  # Hard circuit breaker against infinite loops (8 photos/page = 160,000 photos)
    complete = False  # True only when an empty page confirms we reached the end
    relogins_left = max_relogins  # How many times a rejected (401) token may be replaced in one run

    while current_page <= max_safety_pages:
        params = {"page": current_page}
        print(f"[INFO] Fetching page {current_page} from {PHOTOS_URL}...")

        try:
            try:
                response = get_page_with_retries(headers, params)
            except TokenRejected:
                if get_new_token is None or relogins_left == 0:
                    print(f"[ERROR] OLM rejected the login token on page {current_page} and no re-logins are left.")
                    break
                relogins_left -= 1
                print(f"[WARN] OLM rejected the login token on page {current_page}. Logging in again ({relogins_left} re-logins left after this)...")
                headers["Authorization"] = f"Bearer {get_new_token()}"
                continue  # retry the same page with the new token
            if response is None:
                print(f"[ERROR] Giving up on page {current_page}. Terminating fetch.")
                break

            data = response.json()
            
            # Extract photo records list regardless of response wrapper
            if isinstance(data, dict):
                photos_page = data.get("photos") or data.get("data") or []
            elif isinstance(data, list):
                photos_page = data
            else:
                photos_page = []

            # Page-Until-Empty Termination Check
            if not photos_page:
                print(f"[INFO] Page {current_page} returned 0 records. Reached end of dataset.")
                complete = True
                break

            all_photos.extend(photos_page)
            print(f"[INFO] Page {current_page}: fetched {len(photos_page)} photos (Cumulative total: {len(all_photos)}).")

            if known_ids is not None and current_page >= min_pages \
                    and all(p.get("id") in known_ids for p in photos_page):
                print(f"[INFO] Page {current_page} holds only photos already stored. Stopping early (incremental read).")
                complete = True
                break
            
            current_page += 1
            time.sleep(0.5)
                
        except requests.RequestException as exc:
            print(f"[ERROR] Network exception on page {current_page}: {exc}")
            break

    if current_page > max_safety_pages:
        print(f"[WARN] Circuit breaker triggered at max safety limit ({max_safety_pages} pages).")

    return all_photos, complete


NO_COORDINATES = "no coordinates"
INVALID_COORDINATES = "invalid coordinates"


def read_coordinates(photo):
    """Return (lon, lat, problem) for a raw photo; problem is None when the point is usable.

    A point is unusable if it is missing, not a finite number, outside the globe (longitude
    -180 to 180, latitude -90 to 90) or exactly 0, 0 (the "null island" a failed GPS fix gives).
    """
    geometry = photo.get("geometry") or {}
    coords = geometry.get("coordinates") or [photo.get("lon"), photo.get("lat")]
    if len(coords) < 2 or coords[0] is None or coords[1] is None:
        return None, None, NO_COORDINATES
    try:
        lon, lat = float(coords[0]), float(coords[1])
    except (TypeError, ValueError):
        return None, None, INVALID_COORDINATES
    if not (math.isfinite(lon) and math.isfinite(lat)) or abs(lon) > 180 or abs(lat) > 90 or (lon == 0 and lat == 0):
        return None, None, INVALID_COORDINATES
    return lon, lat, None


def geojson_problems(geojson):
    """Structural problems in the finished GeoJSON, as a list of readable strings (empty = fine)."""
    if geojson.get("type") != "FeatureCollection" or not isinstance(geojson.get("features"), list):
        return ["not a FeatureCollection with a features list"]
    problems = []
    for index, feature in enumerate(geojson["features"]):
        props = feature.get("properties")
        pid = props.get("id") if isinstance(props, dict) else None
        label = f"feature {index} (photo {pid})"
        geometry = feature.get("geometry") or {}
        coords = geometry.get("coordinates")
        if feature.get("type") != "Feature":
            problems.append(f"{label}: type is not Feature")
        elif geometry.get("type") != "Point" or not isinstance(coords, list) or len(coords) != 2:
            problems.append(f"{label}: geometry is not a two-number Point")
        elif not all(isinstance(c, (int, float)) and math.isfinite(c) for c in coords) \
                or abs(coords[0]) > 180 or abs(coords[1]) > 90:
            problems.append(f"{label}: coordinates {coords} are not on the globe")
        elif not isinstance(props, dict) or pid is None or not isinstance(props.get("objects"), list):
            problems.append(f"{label}: properties lack an id or an objects list")
    return problems


def write_atomically(path, text):
    """Write text to path so the file is either the old version or the new one, never half-written.

    The text goes to a temporary file in the same folder first; os.replace then swaps it in
    as a single step. If anything fails, the temporary file is removed and the old file stays.
    """
    folder = os.path.dirname(path) or "."
    os.makedirs(folder, exist_ok=True)
    tmp_path = f"{path}.tmp"
    try:
        with open(tmp_path, "w", encoding="utf-8") as f:
            f.write(text)
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp_path, path)
    except BaseException:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)
        raise


def config_fingerprint():
    """Fingerprint of what stored features depend on besides the photo: crosswalk, neighbourhoods, zones."""
    parts = [crosswalk_version()]
    for path in (NEIGHBOURHOODS_PATH, ZONES_PATH):
        try:
            with open(path, "rb") as f:
                parts.append(f.read())
        except OSError:
            parts.append(b"")
    return store.fingerprint(*parts)


def build_features(raw_photos, crosswalk_rows, zones):
    """Turn raw OLM photos into map features. Returns (features, dropped), dropped being (id, reason) pairs."""
    features, dropped = [], []
    for photo in raw_photos:
        lon, lat, problem = read_coordinates(photo)
        if problem:
            dropped.append((photo.get("id"), problem))
            continue

        properties = build_photo_properties(photo, crosswalk_rows)
        zone = assign_zone(lat, lon, zones)
        zone_edge_m, nbhd_edge_m = zone_edge_distances(lat, lon, zone, zones)
        properties["zone"] = zone["id"] if zone else None
        properties["zone_edge_m"] = zone_edge_m
        properties["nbhd_edge_m"] = nbhd_edge_m
        features.append({
            "type": "Feature",
            "geometry": {
                "type": "Point",
                "coordinates": [lon, lat]
            },
            "properties": properties
        })
    return features, dropped


def merge_features(stored_features, stored_dropped, new_features, new_dropped):
    """Stored photos with the freshly read ones laid over them (a fresh copy replaces a stored one by id).

    Returns (features newest first, dropped list sorted by id).
    """
    by_id = {f["properties"]["id"]: f for f in stored_features}
    dropped = dict(stored_dropped)
    for feature in new_features:
        pid = feature["properties"]["id"]
        by_id[pid] = feature
        dropped.pop(pid, None)
    for pid, reason in new_dropped:
        dropped[pid] = reason
        by_id.pop(pid, None)
    features = sorted(by_id.values(), key=lambda f: f["properties"]["id"], reverse=True)
    return features, sorted(dropped.items(), key=lambda item: (item[0] is None, item[0]))


def fetch_and_build_geojson(from_raw=None, full=False):
    # Read the crosswalk first: if it can't be used, stop before logging in or writing anything.
    crosswalk_rows = load_crosswalk()
    neighbourhoods, zones = load_zones()

    fingerprint = config_fingerprint()
    # Incremental unless forced full, offline, or the stored files are missing, damaged or out of date
    stored = None if (full or from_raw) else store.load_store(DATA_DIR, fingerprint)
    print(f"[INFO] Sync mode: {'incremental' if stored else 'full'}"
          f"{'' if stored or full or from_raw else ' (no usable stored data, or crosswalk/zones changed)'}.")

    if from_raw:
        # Local testing only: build from a saved export (scripts/export_raw_olm.py), no login.
        with open(from_raw, encoding="utf-8") as f:
            raw_photos = json.load(f)
        complete = True
        print(f"[INFO] Offline mode: read {len(raw_photos)} photos from {from_raw}.")
    else:
        email = os.environ.get("OLM_EMAIL", "").strip()
        password = os.environ.get("OLM_PASSWORD", "").strip()

        if not email or not password:
            print("[CRITICAL ERROR] Missing OLM_EMAIL or OLM_PASSWORD environment variables.")
            sys.exit(1)

        token = get_auth_token(email, password)
        known_ids = None
        if stored:
            known_ids = {f["properties"]["id"] for f in stored[0]} | {pid for pid, _ in stored[1] if pid is not None}
        raw_photos, complete = fetch_all_photos(token, get_new_token=lambda: get_auth_token(email, password),
                                                known_ids=known_ids)

    print(f"\n[DIAGNOSTIC] Total raw photo records fetched from API: {len(raw_photos)}")

    # Never overwrite the live data with a partial or empty fetch. Exiting non-zero
    # stops the workflow before its commit step, so the map keeps its last good data.
    if not complete or not raw_photos:
        print("[CRITICAL ERROR] Fetch was incomplete or returned 0 photos. No files were written.")
        sys.exit(1)

    features, dropped = build_features(raw_photos, crosswalk_rows, zones)
    if stored:
        features, dropped = merge_features(stored[0], stored[1], features, dropped)
        print(f"[INFO] Read {len(raw_photos)} recent photos and merged them with {len(stored[0])} stored ones.")
    else:
        features, dropped = merge_features([], [], features, dropped)  # also drops duplicate ids

    geojson = {
        "type": "FeatureCollection",
        # The map's layer tree, in tree order (a GeoJSON "foreign member"; other readers ignore it)
        "mrolm_layers": [{"group": g, "subgroup": s, "layer": l} for g, s, l in tree_layers(crosswalk_rows)],
        # The map's neighbourhoods and their zones (more foreign members), so the map can draw and summarise them
        "mrolm_neighbourhoods": neighbourhoods,
        "mrolm_zones": zones,
        "mrolm_gps_error_m": GPS_ERROR_M,
        "features": features
    }

    print(f"[DIAGNOSTIC] Total valid georeferenced features compiled: {len(features)}")
    if zones:
        in_zone = defaultdict(int)
        for feature in features:
            in_zone[feature["properties"]["zone"]] += 1
        print(f"[DIAGNOSTIC] Photos per zone: {dict(sorted((k or 'outside all zones', v) for k, v in in_zone.items()))}")
    statuses = {}
    for feature in features:
        for obj in feature["properties"]["objects"]:
            statuses[obj["status"]] = statuses.get(obj["status"], 0) + 1
    print(f"[DIAGNOSTIC] Tagged objects by crosswalk status: {dict(sorted(statuses.items()))}")

    # Built before any file is written, so a failure here leaves the last good data live.
    problems = geojson_problems(geojson)
    if problems:
        print(f"[CRITICAL ERROR] The GeoJSON failed its structure check ({len(problems)} problem(s)). No files were written.")
        for problem in problems[:20]:
            print(f"  - {problem}")
        sys.exit(1)
    for pid, reason in dropped:
        print(f"[WARNING] Photo {pid} left off the map: {reason}.")
    audit = build_audit(features, crosswalk_rows, dropped=dropped, crosswalk_hash=crosswalk_version())

    target_paths = ["data/litter.geojson", "public/data/litter.geojson"]

    # Turned into text first, so a serialising error can't touch any file.
    geojson_text = json.dumps(geojson, indent=2)

    for path in target_paths:
        write_atomically(path, geojson_text)
        print(f"[SUCCESS] Exported canonical dataset -> {path}")

    # The new layout: one file per month plus an index (additive; the map prefers it, see index.html)
    meta = {key: value for key, value in geojson.items() if key.startswith("mrolm_")}
    written = store.write_store(DATA_DIR, features, dropped, meta, fingerprint, write_atomically)
    print(f"[SUCCESS] Wrote monthly data -> {len(written)} file(s) changed (including {DATA_DIR}/{store.INDEX_NAME})")

    write_atomically(AUDIT_PATH, audit)
    print(f"[SUCCESS] Wrote audit report -> {AUDIT_PATH}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Fetch OLM photos, apply the crosswalk, and write the GeoJSON.")
    parser.add_argument("--from-raw", metavar="PHOTOS_JSON",
                        help="local testing: build from a saved raw export (review/raw/photos_*.json) instead of OLM")
    parser.add_argument("--full", action="store_true",
                        help="read every photo from OLM and rebuild all files (the default is to read only new and recent photos)")
    args = parser.parse_args()
    fetch_and_build_geojson(args.from_raw, full=args.full)
