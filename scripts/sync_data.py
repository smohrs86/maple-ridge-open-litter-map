import argparse
import csv
import os
import sys
import time
import json
import requests

import crosswalk as cw

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


def fetch_all_photos(token, get_new_token=None, max_relogins=3):
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/json"
    }

    all_photos = []
    current_page = 1
    max_safety_pages = 2000  # Hard circuit breaker against infinite loops (8 photos/page = 16,000 photos)
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
            
            current_page += 1
            time.sleep(0.5)
                
        except requests.RequestException as exc:
            print(f"[ERROR] Network exception on page {current_page}: {exc}")
            break

    if current_page > max_safety_pages:
        print(f"[WARN] Circuit breaker triggered at max safety limit ({max_safety_pages} pages).")

    return all_photos, complete


def fetch_and_build_geojson(from_raw=None):
    # Read the crosswalk first: if it can't be used, stop before logging in or writing anything.
    crosswalk_rows = load_crosswalk()

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
        raw_photos, complete = fetch_all_photos(token, get_new_token=lambda: get_auth_token(email, password))

    print(f"\n[DIAGNOSTIC] Total raw photo records fetched from API: {len(raw_photos)}")

    # Never overwrite the live data with a partial or empty fetch. Exiting non-zero
    # stops the workflow before its commit step, so the map keeps its last good data.
    if not complete or not raw_photos:
        print("[CRITICAL ERROR] Fetch was incomplete or returned 0 photos. No files were written.")
        sys.exit(1)

    features = []
    for photo in raw_photos:
        coords = photo.get("geometry", {}).get("coordinates") or [photo.get("lon"), photo.get("lat")]
        if not coords or coords[0] is None or coords[1] is None:
            continue

        properties = build_photo_properties(photo, crosswalk_rows)
        features.append({
            "type": "Feature",
            "geometry": {
                "type": "Point",
                "coordinates": [float(coords[0]), float(coords[1])]
            },
            "properties": properties
        })

    geojson = {
        "type": "FeatureCollection",
        "features": features
    }

    print(f"[DIAGNOSTIC] Total valid georeferenced features compiled: {len(features)}")
    statuses = {}
    for feature in features:
        for obj in feature["properties"]["objects"]:
            statuses[obj["status"]] = statuses.get(obj["status"], 0) + 1
    print(f"[DIAGNOSTIC] Tagged objects by crosswalk status: {dict(sorted(statuses.items()))}")

    target_paths = ["data/litter.geojson", "public/data/litter.geojson"]
    
    for path in target_paths:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(geojson, f, indent=2)
        print(f"[SUCCESS] Exported canonical dataset -> {path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Fetch OLM photos, apply the crosswalk, and write the GeoJSON.")
    parser.add_argument("--from-raw", metavar="PHOTOS_JSON",
                        help="local testing: build from a saved raw export (review/raw/photos_*.json) instead of OLM")
    fetch_and_build_geojson(parser.parse_args().from_raw)
