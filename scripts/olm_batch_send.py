"""Send ONE photo's planned tag replacement to OpenLitterMap (OLM), then read it back.

Uses a plan saved by scripts/olm_batch_replace.py (review/batches/*_dryrun_*.json).
Without --send it only previews: it logs in, reads the photo, checks it and shows
the request, but sends nothing. Only run with --send after the maintainer has seen
the dry run and explicitly said to send.

    python3 scripts/olm_batch_send.py --plan review/batches/<plan>.json --photo 546290 --credentials-file PATH
    python3 scripts/olm_batch_send.py --plan ... --photo 546290 --credentials-file PATH --send
    python3 scripts/olm_batch_send.py --plan ... --photo 546290 --credentials-file PATH --restore --send

Before sending it refuses if the photo's tags in OLM no longer match the plan's
backup (re-export and re-run the dry run), and it saves the photo's current record
to review/batches/. After sending it reads the photo back and compares. --restore
sends the backup tags instead of the planned ones.
"""
import argparse
import json
import os
import sys
import time
from datetime import datetime

import requests

from export_raw_olm import load_credentials
from olm_batch_replace import to_payload
from sync_data import get_auth_token, get_page_with_retries

TAGS_URL = "https://openlittermap.com/api/v3/tags"


def normalise(body):
    """A comparable form of a request body: tag order and list order don't matter."""
    tags = []
    for t in body["tags"]:
        tags.append({**t, "materials": sorted(t["materials"]), "custom_tags": sorted(t["custom_tags"]),
                     "brands": sorted((b["id"], b["quantity"]) for b in t["brands"])})
    return sorted(json.dumps(t, sort_keys=True) for t in tags)


def read_photo(token, photo_id):
    """The photo's current record from OLM's photo list, or None."""
    headers = {"Authorization": f"Bearer {token}", "Accept": "application/json"}
    response = get_page_with_retries(headers, {"page": 1, "id": photo_id, "per_page": 1})
    if response is None:
        return None
    batch = response.json().get("photos", [])
    return batch[0] if batch and batch[0].get("id") == photo_id else None


def main():
    parser = argparse.ArgumentParser(description="Send one photo's planned tag replacement to OLM.")
    parser.add_argument("--plan", required=True, help="dry-run plan from scripts/olm_batch_replace.py")
    parser.add_argument("--photo", required=True, type=int, help="the one photo ID to send")
    parser.add_argument("--credentials-file", help="owner-only file: email on line 1, password on line 2")
    parser.add_argument("--restore", action="store_true", help="send the backup tags instead of the planned ones")
    parser.add_argument("--send", action="store_true", help="actually send; without it this only previews")
    args = parser.parse_args()

    with open(args.plan, encoding="utf-8") as f:
        plan = json.load(f)
    entry = next((p for p in plan["photos"] if p["photo_id"] == args.photo), None)
    if entry is None:
        sys.exit(f"[CRITICAL ERROR] Photo {args.photo} is not in {args.plan}.")
    if not args.restore and not entry["ok"]:
        sys.exit(f"[CRITICAL ERROR] The dry run blocked photo {args.photo}: {entry['problems']}")
    body = entry["backup_payload"] if args.restore else entry["target_payload"]
    if not body["tags"]:
        sys.exit("[CRITICAL ERROR] Refusing to send an empty tag list (it would clear the photo).")

    email, password = load_credentials(args.credentials_file)
    token = get_auth_token(email, password)
    before = read_photo(token, args.photo)
    if before is None:
        sys.exit(f"[CRITICAL ERROR] Could not read photo {args.photo} from OLM. Nothing was sent.")
    current = {"photo_id": args.photo, "tags": [to_payload(t) for t in before.get("new_tags") or []]}

    if normalise(current) == normalise(body):
        print(f"[INFO] Photo {args.photo} already has these tags. Nothing to send.")
        return 0
    if not args.restore and normalise(current) != normalise(entry["backup_payload"]):
        sys.exit(f"[CRITICAL ERROR] Photo {args.photo} has changed in OLM since the export. "
                 "Re-export, rebuild the workbook and re-run the dry run. Nothing was sent.")

    os.makedirs(os.path.join("review", "batches"), exist_ok=True)
    log_path = os.path.join("review", "batches",
                            f"{plan['label']}_{'restore' if args.restore else 'send'}_{args.photo}_{datetime.now():%Y%m%d-%H%M%S}.json")
    log = {"photo_id": args.photo, "plan": args.plan, "restore": args.restore, "sent": False,
           "before_record": before, "body": body, "verified_before": before.get("verified")}

    def save_log():
        with open(log_path, "w", encoding="utf-8") as f:
            json.dump(log, f, indent=1)
        os.chmod(log_path, 0o600)

    save_log()  # the backup of the current record exists before anything is sent
    print(f"[INFO] Backup of photo {args.photo}'s current record saved to {log_path}")
    print(f"[INFO] verified before: {before.get('verified')}")
    print(f"[INFO] Request (PUT {TAGS_URL}):\n{json.dumps(body, indent=1)}")

    if not args.send:
        print("\n[PREVIEW] Nothing was sent. Add --send to send this one photo.")
        return 0

    headers = {"Authorization": f"Bearer {token}", "Accept": "application/json"}
    try:
        response = requests.put(TAGS_URL, json=body, headers=headers, timeout=60)
        log["http_status"] = response.status_code
        log["success"] = response.headers.get("content-type", "").startswith("application/json") \
            and response.json().get("success") is True
    except requests.RequestException as error:
        log["http_status"], log["success"] = None, False
        log["error"] = str(error)
    log["sent"] = True
    save_log()
    print(f"\n[INFO] Sent. HTTP {log['http_status']}, success={log['success']}")

    time.sleep(2)
    after = read_photo(token, args.photo)
    log["after_record"] = after
    if after is None:
        log["result"] = "could not read back"
    else:
        log["verified_after"] = after.get("verified")
        read_back = {"photo_id": args.photo, "tags": [to_payload(t) for t in after.get("new_tags") or []]}
        log["result"] = "match" if normalise(read_back) == normalise(body) else "MISMATCH"
    save_log()

    print(f"[INFO] verified before: {log['verified_before']}  after: {log.get('verified_after')}")
    if log["result"] == "match":
        print(f"[SUCCESS] Photo {args.photo} read back exactly as sent (tags, quantities, picked_up).")
        print("[NEXT] Check the photo is still visible on the public OLM map before sending more.")
        return 0
    print(f"[FAILED] Read-back result: {log['result']}. Stop here. Details in {log_path}.")
    print(f"[UNDO] python3 scripts/olm_batch_send.py --plan {args.plan} --photo {args.photo} "
          "--credentials-file PATH --restore --send")
    return 1


if __name__ == "__main__":
    sys.exit(main())
