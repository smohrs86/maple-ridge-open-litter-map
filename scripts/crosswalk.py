"""Crosswalk matching, following the rules in README.md ("Matching rules").

Pure functions with no network or file writes, so the review workbook builder and
(later) the sync engine can share one implementation and tests can cover it.
"""
import csv

NARROWING_COLUMNS = ("with Secondary Modifier", "with Material tag", "with Custom Tag")


def norm(value):
    """Ignore capitals and extra spaces: 'THC', 'thc' and ' THC ' are the same."""
    return " ".join(str(value or "").lower().split())


def load_crosswalk(path):
    """Read the CSV by header name. Each row keeps its sheet row number (header = 1)."""
    with open(path, newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    for i, row in enumerate(rows, start=2):
        row["_sheet_row"] = i
    return rows


def _row_matches(row, olm_key, secondary, materials, customs):
    if norm(row["OLM key"]) != norm(olm_key):
        return False
    wanted_secondary = norm(row["with Secondary Modifier"])
    wanted_material = norm(row["with Material tag"])
    wanted_custom = norm(row["with Custom Tag"])
    if wanted_secondary and wanted_secondary != norm(secondary):
        return False
    if wanted_material and wanted_material not in {norm(m) for m in materials}:
        return False
    if wanted_custom and wanted_custom not in {norm(c) for c in customs}:
        return False
    return True


def _specificity(row):
    return sum(1 for col in NARROWING_COLUMNS if norm(row[col]))


def match_tag(rows, olm_key, secondary="", materials=(), customs=()):
    """Return (row, tie_rows). row is None when nothing matches (UNMAPPED).

    1. The most specific matching row wins (more narrowing columns filled in).
    2. A blank narrowing column means "anything else", so it matches any tag.
    3. Capitals and extra spaces are ignored.
    4. On an equal-specificity tie, the row higher in the sheet wins, and every
       tied row is returned in tie_rows so the audit can list it.
    """
    candidates = [r for r in rows if _row_matches(r, olm_key, secondary, materials, customs)]
    if not candidates:
        return None, []
    top = max(_specificity(r) for r in candidates)
    best = [r for r in candidates if _specificity(r) == top]
    return best[0], (best if len(best) > 1 else [])


def classify(row):
    """Status for a tag that matched a crosswalk row (see README "Audit counts")."""
    if norm(row["include on map"]) == "no":
        return "RECLASS"
    if norm(row["MROLM local key"]) == "unclass":
        return "UNCLASS"
    if norm(row["OLM data needs fixes"]):
        return "REVIEW"
    return "OK"


def convention_problems(rows):
    """Rows where local key == OLM key (a retired key) but include on map is not 'no'."""
    return [r for r in rows
            if norm(r["MROLM local key"]) == norm(r["OLM key"]) and norm(r["include on map"]) != "no"]
