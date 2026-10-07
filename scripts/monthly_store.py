"""Monthly data files for the map, plus a small index.

Why: one big GeoJSON grows without limit and every sync re-commits all of it. Here each calendar
month of photos is its own file (data/months/YYYY-MM.geojson), so a sync normally changes only
the newest month. data/index.json lists the months and carries the map's other data (layer tree,
neighbourhoods, zones). The map reads the index, then the month files.

The month is the UTC month of the photo's own `datetime`. It only decides which file a photo is
filed in; the map still filters by local date from the photo's full timestamp.
"""
import hashlib
import json
import os
import re

SCHEMA = 1  # Bump when the shape of a stored feature changes; a mismatch forces a full rebuild
INDEX_NAME = "index.json"
MONTHS_DIR = "months"
UNDATED = "undated"


def month_key(properties):
    match = re.match(r"(\d{4})-(\d{2})", str(properties.get("datetime") or ""))
    return f"{match.group(1)}-{match.group(2)}" if match else UNDATED


def dumps_compact(obj):
    """Compact JSON (no indentation): about half the size, and the server compresses it further."""
    return json.dumps(obj, separators=(",", ":"))


def short_hash(text):
    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:12]


def fingerprint(*parts):
    """Fingerprint of everything a stored feature depends on besides the photo itself.

    parts are bytes or strings (crosswalk version, neighbourhood and zone files). If any change,
    stored features are out of date and the next sync must rebuild everything.
    """
    digest = hashlib.sha256(f"schema={SCHEMA}".encode())
    for part in parts:
        digest.update(part if isinstance(part, bytes) else str(part).encode("utf-8"))
        digest.update(b"\0")
    return digest.hexdigest()[:12]


def split_by_month(features):
    months = {}
    for feature in features:
        months.setdefault(month_key(feature["properties"]), []).append(feature)
    return months


def load_store(data_dir, expected_fingerprint):
    """Read the stored features and dropped-photo list, or return None if they can't be trusted.

    None means "do a full rebuild": no index yet, a damaged or missing month file, a different
    schema, or a crosswalk/zone change since the files were written.
    """
    try:
        with open(os.path.join(data_dir, INDEX_NAME), encoding="utf-8") as f:
            index = json.load(f)
        if index.get("schema") != SCHEMA or index.get("fingerprint") != expected_fingerprint:
            return None
        features = []
        for month in index["months"]:
            with open(os.path.join(data_dir, month["file"]), encoding="utf-8") as f:
                text = f.read()
            if short_hash(text) != month["sha256"]:
                return None
            month_features = json.loads(text)["features"]
            if len(month_features) != month["count"]:
                return None
            features.extend(month_features)
        dropped = [(pid, reason) for pid, reason in index.get("dropped", [])]
        return features, dropped
    except (OSError, ValueError, KeyError, TypeError):
        return None


def write_store(data_dir, features, dropped, meta, fp, write):
    """Write month files, then the index, then remove month files no longer listed.

    `write(path, text)` should be an atomic writer. The index goes last because it is what the
    map reads: until it is swapped in, the map keeps seeing the previous, consistent set.
    Returns the paths written.
    """
    months_dir = os.path.join(data_dir, MONTHS_DIR)
    entries, written = [], []
    for key, month_features in sorted(split_by_month(features).items()):
        text = dumps_compact({"type": "FeatureCollection", "features": month_features})
        rel = f"{MONTHS_DIR}/{key}.geojson"
        path = os.path.join(data_dir, rel)
        # Skip the write when the file is already right, so unchanged months stay untouched
        try:
            with open(path, encoding="utf-8") as f:
                unchanged = f.read() == text
        except OSError:
            unchanged = False
        if not unchanged:
            write(path, text)
            written.append(path)
        entries.append({"key": key, "file": rel, "count": len(month_features), "sha256": short_hash(text)})

    index = {
        "schema": SCHEMA,
        "fingerprint": fp,
        "total": len(features),
        "months": entries,
        "dropped": [[pid, reason] for pid, reason in dropped],
        **meta,
    }
    index_path = os.path.join(data_dir, INDEX_NAME)
    write(index_path, dumps_compact(index))
    written.append(index_path)

    listed = {os.path.basename(e["file"]) for e in entries}
    if os.path.isdir(months_dir):
        for name in os.listdir(months_dir):
            if name.endswith(".geojson") and name not in listed:
                os.remove(os.path.join(months_dir, name))
    return written
