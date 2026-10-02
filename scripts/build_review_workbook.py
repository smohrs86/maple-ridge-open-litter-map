"""Build the legacy tag review workbook from a raw OLM export and the crosswalk.

Offline and read-only: it reads review/raw/photos_*.json (from
scripts/export_raw_olm.py) and config/crosswalk.csv, and writes a new dated
workbook. It never touches OpenLitterMap and never overwrites an existing
workbook. To keep your edits when rebuilding after a fresh export, pass the
previous workbook:

    python3 scripts/build_review_workbook.py --carry-from review/legacy_tag_review_<date>.xlsx

The unit is the tagged object (one row per tag row on a photo). Statuses: OK,
REVIEW, RECLASS, UNCLASS, ORPHAN TAG, UNMAPPED (see README "Audit counts").
"""
import argparse
import glob
import json
import os
import sys
from collections import Counter, defaultdict
from datetime import date

import openpyxl
from openpyxl.styles import Alignment, Font, PatternFill
from openpyxl.utils import get_column_letter
from openpyxl.worksheet.datavalidation import DataValidation

import crosswalk as cw

OBJECT_COLUMNS = [
    "PhotoID", "Object_No", "PhotoLink", "Date",
    "OLM_key", "OLM_secondary", "OLM_Material", "OLM_Custom",
    "Quantity", "Picked_Up",
    "MROLM local key", "Status", "Notes", "OLM data needs fixes",
    "Change_To_OLMKey", "Change_to_OLM_secondary", "Change_to_OLM_Material", "Change_to_OLM_Custom",
    "Change_to_Picked_Up", "Change_to_Quantity", "Batch_Status", "OLM_Tag_ID", "Review notes",
    "Reviewed",
]
CHANGE_COLUMNS = ["Change_To_OLMKey", "Change_to_OLM_secondary", "Change_to_OLM_Material",
                  "Change_to_OLM_Custom", "Change_to_Picked_Up", "Change_to_Quantity", "Batch_Status",
                  "Review notes"]  # carried on rebuild
BATCH_COLUMNS = ["PhotoID", "Batch_Label", "Current_Tags_JSON", "Target_Tags_JSON", "Batch_Status",
                 "Verified_Before", "Verified_After", "Done_At", "Error_Or_Notes"]
STATUS_VALUES = "pending,dry-run ok,sent,verified ok,failed,skipped"
REMOVE = "[remove]"
EXCEL_CELL_LIMIT = 32767


def newest(pattern):
    files = sorted(glob.glob(pattern))
    if not files:
        sys.exit(f"[CRITICAL ERROR] No files match {pattern}. Run scripts/export_raw_olm.py first.")
    return files[-1]


def tag_details(tag):
    """(olm_key, secondary, materials, customs) for one raw tag row. olm_key is '' for orphans."""
    category = (tag.get("category") or {}).get("key")
    obj = (tag.get("object") or {}).get("key")
    olm_key = f"{category}/{obj}" if category and obj else ""
    secondary = (tag.get("type") or {}).get("key", "")
    extras = tag.get("extra_tags") or []
    materials = [(e.get("tag") or {}).get("key", "") for e in extras if e.get("type") == "material"]
    customs = [(e.get("tag") or {}).get("key", "") for e in extras if e.get("type") == "custom_tag"]
    return olm_key, secondary, materials, customs


def build_object_rows(photos, crosswalk_rows):
    rows, ties, unmapped = [], [], []
    for photo in photos:
        for number, tag in enumerate(photo.get("new_tags") or [], start=1):
            olm_key, secondary, materials, customs = tag_details(tag)
            record = {
                "PhotoID": photo["id"], "Object_No": number, "PhotoLink": photo.get("filename"),
                "Date": str(photo.get("datetime") or "")[:16].replace("T", " "),
                "OLM_key": olm_key, "OLM_secondary": secondary,
                "OLM_Material": "; ".join(materials), "OLM_Custom": "; ".join(customs),
                "Quantity": tag.get("quantity"),
                "Picked_Up": "yes" if tag.get("picked_up") else "no",
                "MROLM local key": "", "Status": "", "Notes": "", "OLM data needs fixes": "",
                "OLM_Tag_ID": tag.get("id"),
            }
            if not olm_key:
                record["Status"] = "ORPHAN TAG"
            else:
                matched, tied = cw.match_tag(crosswalk_rows, olm_key, secondary, materials, customs)
                if matched is None:
                    record["Status"] = "UNMAPPED"
                    unmapped.append(record)
                else:
                    record["MROLM local key"] = matched["MROLM local key"]
                    record["Notes"] = matched["Notes"]
                    record["OLM data needs fixes"] = matched["OLM data needs fixes"]
                    record["Status"] = cw.classify(matched)
                    if tied:
                        ties.append((photo["id"], number, [r["_sheet_row"] for r in tied]))
            rows.append(record)
    return rows, ties, unmapped


def row_key(values, col):
    """Match key for one workbook row: OLM's tag ID, or the object's position if the ID is missing."""
    photo_id = values[col["PhotoID"]]
    if "OLM_Tag_ID" in col and values[col["OLM_Tag_ID"]] is not None:
        return (photo_id, "tag", values[col["OLM_Tag_ID"]])
    return (photo_id, "no", values[col["Object_No"]])


def load_carried_edits(path):
    """Change_*/Batch_Status entries from a previous workbook, keyed to the tag they were made on.
    Also returns the Reviewed dates, which are carried separately (they are not edits)."""
    wb = openpyxl.load_workbook(path, data_only=True)
    ws = wb["Objects"]
    header = [c.value for c in ws[1]]
    col = {name: i for i, name in enumerate(header)}
    carried, reviewed = {}, {}
    for values in ws.iter_rows(min_row=2, values_only=True):
        if "Reviewed" in col and values[col["Reviewed"]] not in (None, ""):
            reviewed[row_key(values, col)] = values[col["Reviewed"]]
        edits = {name: values[col[name]] for name in CHANGE_COLUMNS
                 if name in col and values[col[name]] not in (None, "")}
        if edits:
            carried[row_key(values, col)] = edits
    return carried, reviewed


def apply_carried_edits(rows, carried):
    used = set()
    for record in rows:
        for key in ((record["PhotoID"], "tag", record["OLM_Tag_ID"]), (record["PhotoID"], "no", record["Object_No"])):
            if key in carried:
                record.update(carried[key])
                used.add(key)
                break
    return [k for k in carried if k not in used]


def apply_reviewed(rows, photos, reviewed, through):
    """Fill the Reviewed column: keep carried dates; with --reviewed-through, stamp that date on every
    object that has an edit or note, or whose photo was uploaded before that date."""
    uploaded = {p["id"]: str(p.get("created_at") or "")[:10] for p in photos}
    for record in rows:
        for key in ((record["PhotoID"], "tag", record["OLM_Tag_ID"]), (record["PhotoID"], "no", record["Object_No"])):
            if key in reviewed:
                record["Reviewed"] = reviewed[key]
                break
        if record.get("Reviewed") or not through:
            continue
        edited = any(record.get(name) not in (None, "") for name in CHANGE_COLUMNS)
        if edited or (uploaded.get(record["PhotoID"]) and uploaded[record["PhotoID"]] < through):
            record["Reviewed"] = through


def option_lists(tags_all):
    categories = {c["id"]: c["key"] for c in tags_all["categories"]}
    objects = {o["id"]: o["key"] for o in tags_all["objects"]}
    keys = sorted({f"{categories[co['category_id']]}/{objects[co['litter_object_id']]}"
                   for co in tags_all["category_objects"]
                   if co["category_id"] in categories and co["litter_object_id"] in objects})
    types = sorted(t["key"] for t in tags_all["types"])
    materials = sorted(m["key"] for m in tags_all["materials"])
    return keys, types, materials


def style_header(ws):
    for cell in ws[1]:
        cell.font = Font(bold=True)
        cell.fill = PatternFill("solid", fgColor="DDDDDD")
    ws.freeze_panes = "A2"


def write_workbook(path, rows, photos, keys, types, materials):
    wb = openpyxl.Workbook()

    ws = wb.active
    ws.title = "Objects"
    ws.append(OBJECT_COLUMNS)
    for record in rows:
        ws.append([record.get(name) for name in OBJECT_COLUMNS])
    link_col = OBJECT_COLUMNS.index("PhotoLink") + 1
    for r in range(2, len(rows) + 2):
        cell = ws.cell(r, link_col)
        if cell.value:
            cell.hyperlink = cell.value
            cell.font = Font(color="0563C1", underline="single")
    style_header(ws)
    ws.auto_filter.ref = f"A1:{get_column_letter(len(OBJECT_COLUMNS))}{len(rows) + 1}"
    widths = {"PhotoLink": 30, "Notes": 40, "OLM data needs fixes": 40, "OLM_key": 24, "MROLM local key": 26, "Review notes": 40}
    for i, name in enumerate(OBJECT_COLUMNS, start=1):
        ws.column_dimensions[get_column_letter(i)].width = widths.get(name, 16)

    lists = wb.create_sheet("Lists")
    lists.append(["OLM keys", "Secondary (types)", "Materials"])
    lists.append([None, REMOVE, REMOVE])
    for i in range(max(len(keys), len(types), len(materials))):
        lists.append([keys[i] if i < len(keys) else None, types[i] if i < len(types) else None,
                      materials[i] if i < len(materials) else None])
    style_header(lists)
    last = len(rows) + 1

    def add_validation(column_name, formula, strict):
        col = get_column_letter(OBJECT_COLUMNS.index(column_name) + 1)
        dv = DataValidation(type="list", formula1=formula, allow_blank=True,
                            errorStyle="stop" if strict else "warning", showErrorMessage=True)
        ws.add_data_validation(dv)
        dv.add(f"{col}2:{col}{last}")

    add_validation("Change_To_OLMKey", f"=Lists!$A$3:$A${len(keys) + 2}", strict=True)
    add_validation("Change_to_OLM_secondary", f"=Lists!$B$2:$B${len(types) + 2}", strict=False)
    add_validation("Change_to_OLM_Material", f"=Lists!$C$2:$C${len(materials) + 2}", strict=False)
    add_validation("Change_to_Picked_Up", '"yes,no"', strict=True)
    add_validation("Batch_Status", f'"{STATUS_VALUES}"', strict=True)
    qty_col = get_column_letter(OBJECT_COLUMNS.index("Change_to_Quantity") + 1)
    qty_dv = DataValidation(type="whole", operator="greaterThanOrEqual", formula1="1", allow_blank=True,
                            errorStyle="stop", showErrorMessage=True)
    ws.add_data_validation(qty_dv)
    qty_dv.add(f"{qty_col}2:{qty_col}{last}")

    batch = wb.create_sheet("Photo_Batch")
    batch.append(BATCH_COLUMNS)
    for photo in photos:
        current = json.dumps(photo.get("new_tags") or [], separators=(",", ":"))
        if len(current) > EXCEL_CELL_LIMIT:
            sys.exit(f"[CRITICAL ERROR] Photo {photo['id']} tags exceed the spreadsheet cell limit.")
        batch.append([photo["id"], None, current, None, None, photo.get("verified"), None, None, None])
    style_header(batch)
    dv = DataValidation(type="list", formula1=f'"{STATUS_VALUES}"', allow_blank=True)
    batch.add_data_validation(dv)
    dv.add(f"E2:E{len(photos) + 1}")
    for i in range(1, len(BATCH_COLUMNS) + 1):
        batch.column_dimensions[get_column_letter(i)].width = 22

    guide = wb.create_sheet("Guide")
    guide_rows = [
        ("Sheet", "Purpose"),
        ("Objects", "One row per tagged object. Filter OLM_key (and OLM_Custom) to isolate one group. Object_No is the object's position within its photo. Multiple materials or customs on one object are joined with '; '. Quantity and Picked_Up are shown for reference. OLM_Tag_ID is OLM's ID for that exact tag row, used to match your edits when this workbook is rebuilt."),
        ("Change columns", "Change_To_OLMKey, Change_to_OLM_secondary, Change_to_OLM_Material, Change_to_OLM_Custom: leave blank to keep the current value; type [remove] to remove it; otherwise type the new value. For materials or customs, whatever you type replaces the whole list (write several as 'a; b'). Change_to_Picked_Up: yes or no to correct whether the object was picked up; blank keeps it. Change_to_Quantity: the object's new total quantity (a whole number, 1 or more); blank keeps it. Nothing is sent to OLM by editing this sheet."),
        ("Review notes", "Free-text notes on an object, carried into each rebuild. Never sent to OLM."),
        ("Reviewed", "The date the maintainer reviewed this object in OLM (blank = not yet reviewed). Set by the build script with --reviewed-through: objects with an edit or note, or on a photo uploaded before that date, get the date. Carried into each rebuild. Separate from Status, which comes from the crosswalk."),
        ("Photo_Batch", "One row per photo, filled by the batch script, not by hand. Current_Tags_JSON is a copy of the photo's tags as exported; the raw export file in review/raw/ is the real backup."),
        ("Lists", "Values for the dropdowns, from OLM's tag list."),
        ("", ""),
        ("Status", "Meaning"),
        ("OK", "Maps cleanly to a layer."),
        ("REVIEW", "The matching crosswalk row has a note in 'OLM data needs fixes'."),
        ("RECLASS", "The matching crosswalk row is excluded from the map (retired or out of scope)."),
        ("UNCLASS", "Household dumping with no size chosen."),
        ("ORPHAN TAG", "A custom tag attached to no object."),
        ("UNMAPPED", "No crosswalk row matches this tag."),
        ("", ""),
        ("Batch_Status", "pending, dry-run ok, sent, verified ok, failed, skipped."),
    ]
    for r in guide_rows:
        guide.append(r)
    style_header(guide)
    for r in guide.iter_rows():
        for c in r:
            c.alignment = Alignment(wrap_text=True, vertical="top")
    guide.column_dimensions["A"].width = 18
    guide.column_dimensions["B"].width = 110

    wb.save(path)


def print_report(rows, ties, unmapped, unmatched_edits, carried_count, crosswalk_rows, out_path):
    by_status = Counter(r["Status"] for r in rows)
    print(f"\n[REPORT] {len(rows)} tagged objects on {len({r['PhotoID'] for r in rows})} photos "
          f"({sum(r['Quantity'] or 0 for r in rows)} items).")
    for status in ("OK", "REVIEW", "RECLASS", "UNCLASS", "ORPHAN TAG", "UNMAPPED"):
        print(f"  {status:<11} {by_status.get(status, 0)}")

    review = defaultdict(int)
    for r in rows:
        if r["Status"] == "REVIEW":
            review[r["OLM data needs fixes"]] += 1
    if review:
        print("\n[REPORT] REVIEW items grouped by their note:")
        for note, count in sorted(review.items(), key=lambda kv: -kv[1]):
            print(f"  {count:>5}  {note}")

    reclass = Counter(r["OLM_key"] for r in rows if r["Status"] == "RECLASS")
    if reclass:
        print("\n[REPORT] RECLASS by OLM key:", dict(reclass.most_common()))
    orphans = sorted({r["PhotoID"] for r in rows if r["Status"] == "ORPHAN TAG"})
    if orphans:
        print(f"\n[REPORT] Orphan tags on photos: {orphans}")
    if unmapped:
        print("\n[REPORT] UNMAPPED (a gap in the crosswalk):",
              sorted({(r['OLM_key'], r['OLM_secondary']) for r in unmapped}))
    if ties:
        print(f"\n[REPORT] Tie-breaks ({len(ties)}): photo, object no., crosswalk sheet rows: {ties[:20]}")
    problems = cw.convention_problems(crosswalk_rows)
    if problems:
        print("\n[REPORT] Crosswalk rows where local key = OLM key but include is not 'no':",
              [p["_sheet_row"] for p in problems])
    reviewed_count = sum(1 for r in rows if r.get("Reviewed"))
    print(f"\n[REPORT] Reviewed {reviewed_count} of {len(rows)} objects; {len(rows) - reviewed_count} not yet reviewed.")
    if carried_count:
        print(f"\n[REPORT] Carried over {carried_count - len(unmatched_edits)} of {carried_count} edited rows.")
    if unmatched_edits:
        print(f"[WARN] {len(unmatched_edits)} edited rows in the previous workbook match no tag now "
              f"(the tag may have been changed in OLM): {unmatched_edits[:20]}")
    print(f"\n[SUCCESS] Wrote {out_path}")


def main():
    parser = argparse.ArgumentParser(description="Build the legacy tag review workbook (offline, read-only).")
    parser.add_argument("--raw-dir", default=os.path.join("review", "raw"))
    parser.add_argument("--crosswalk", default=os.path.join("config", "crosswalk.csv"))
    parser.add_argument("--out", default=os.path.join("review", f"legacy_tag_review_{date.today():%Y%m%d}.xlsx"))
    parser.add_argument("--carry-from", help="previous workbook whose Change_*/Batch_Status entries to keep")
    parser.add_argument("--reviewed-through", metavar="YYYY-MM-DD",
                        help="mark every object with an edit or note, or on a photo uploaded before this date, as reviewed on this date")
    args = parser.parse_args()

    if os.path.exists(args.out):
        sys.exit(f"[CRITICAL ERROR] {args.out} already exists. Not overwriting; pick another --out.")

    with open(newest(os.path.join(args.raw_dir, "photos_*.json")), encoding="utf-8") as f:
        photos = json.load(f)
    with open(newest(os.path.join(args.raw_dir, "tags_all_*.json")), encoding="utf-8") as f:
        tags_all = json.load(f)
    crosswalk_rows = cw.load_crosswalk(args.crosswalk)

    rows, ties, unmapped = build_object_rows(photos, crosswalk_rows)
    carried, reviewed = load_carried_edits(args.carry_from) if args.carry_from else ({}, {})
    unmatched_edits = apply_carried_edits(rows, carried) if carried else []
    apply_reviewed(rows, photos, reviewed, args.reviewed_through)

    keys, types, materials = option_lists(tags_all)
    os.makedirs(os.path.dirname(args.out) or ".", exist_ok=True)
    write_workbook(args.out, rows, photos, keys, types, materials)
    print_report(rows, ties, unmapped, unmatched_edits, len(carried), crosswalk_rows, args.out)


if __name__ == "__main__":
    main()
