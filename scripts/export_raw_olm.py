"""Read-only export of your raw OLM photo records and OLM's tag list.

Nothing here writes to OpenLitterMap. The output is a local backup that a later
review/batch-change script will use, so it keeps everything OLM sends (tag IDs,
verified, picked_up, coordinates, addresses). Never commit it.

Run from the repo root, with OLM_EMAIL / OLM_PASSWORD set in your own terminal:
    python3 scripts/export_raw_olm.py
"""
import json
import os
import sys
import time
from collections import Counter
from datetime import datetime

import requests

from sync_data import TokenRejected, get_auth_token, get_page_with_retries, PHOTOS_URL

TAGS_URL = "https://openlittermap.com/api/tags/all"
OUT_DIR = os.path.join("review", "raw")
PER_PAGE = 100  # OLM caps this at 100; far fewer requests than the default of 8
MAX_PAGES = 400  # circuit breaker (40,000 photos)


def fetch_all_raw_photos(token, get_new_token, max_relogins=3):
    headers = {"Authorization": f"Bearer {token}", "Accept": "application/json"}
    photos, page, relogins_left = [], 1, max_relogins
    while page <= MAX_PAGES:
        try:
            response = get_page_with_retries(headers, {"page": page, "per_page": PER_PAGE})
        except TokenRejected:
            if relogins_left == 0:
                print("[ERROR] Token rejected and no re-logins left.")
                return photos, False
            relogins_left -= 1
            headers["Authorization"] = f"Bearer {get_new_token()}"
            continue
        if response is None:
            return photos, False
        data = response.json()
        batch = data.get("photos", []) if isinstance(data, dict) else []
        if not batch:
            print(f"[INFO] Page {page} was empty: reached the end.")
            return photos, True
        photos.extend(batch)
        print(f"[INFO] Page {page}: {len(batch)} photos (total {len(photos)}).")
        page += 1
        time.sleep(0.5)
    print("[WARN] Hit the page limit before an empty page.")
    return photos, False


def fetch_tag_list(token):
    headers = {"Authorization": f"Bearer {token}", "Accept": "application/json"}
    for attempt in range(4):
        try:
            response = requests.get(TAGS_URL, headers=headers, timeout=60)
            if response.status_code == 200:
                return response.json()
            print(f"[WARN] Tag list HTTP {response.status_code} (attempt {attempt + 1}).")
        except requests.RequestException as exc:
            print(f"[WARN] Tag list error (attempt {attempt + 1}): {exc}")
        time.sleep(2 * (2 ** attempt))
    return None


def write_json_atomically(path, obj):
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(obj, f, indent=1)
    os.chmod(tmp, 0o600)  # raw records are private: owner-only
    os.replace(tmp, path)


def summarise(photos):
    """Counts only, no photo contents, so it is safe to paste into a chat."""
    verified = Counter(str(p.get("verified")) for p in photos)
    tag_picked_up, photo_picked_up = Counter(), Counter()
    tagged = 0
    for p in photos:
        photo_picked_up[str(p.get("picked_up"))] += 1
        tags = p.get("new_tags") or []
        tagged += bool(tags)
        for t in tags:
            tag_picked_up[str(t.get("picked_up"))] += 1
    return {
        "photos": len(photos),
        "photos_with_new_tags": tagged,
        "verified_values": dict(verified),
        "photo_level_picked_up": dict(photo_picked_up),
        "tag_level_picked_up": dict(tag_picked_up),
        "record_fields": sorted(photos[0].keys()) if photos else [],
    }


def main():
    email = os.environ.get("OLM_EMAIL", "").strip()
    password = os.environ.get("OLM_PASSWORD", "").strip()
    if not email or not password:
        print("[CRITICAL ERROR] Set OLM_EMAIL and OLM_PASSWORD in your terminal first.")
        sys.exit(1)

    token = get_auth_token(email, password)
    photos, complete = fetch_all_raw_photos(token, lambda: get_auth_token(email, password))
    if not complete or not photos:
        print("[CRITICAL ERROR] Fetch incomplete or empty. Nothing was written.")
        sys.exit(1)

    tag_list = fetch_tag_list(token)
    if tag_list is None:
        print("[CRITICAL ERROR] Could not fetch OLM's tag list. Nothing was written.")
        sys.exit(1)

    os.makedirs(OUT_DIR, exist_ok=True)
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    write_json_atomically(os.path.join(OUT_DIR, f"photos_{stamp}.json"), photos)
    write_json_atomically(os.path.join(OUT_DIR, f"tags_all_{stamp}.json"), tag_list)
    summary = summarise(photos)
    write_json_atomically(os.path.join(OUT_DIR, f"summary_{stamp}.json"), summary)

    print(f"\n[SUCCESS] Saved photos_{stamp}.json, tags_all_{stamp}.json and summary_{stamp}.json in {OUT_DIR}/")
    print(json.dumps(summary, indent=1))


if __name__ == "__main__":
    main()
