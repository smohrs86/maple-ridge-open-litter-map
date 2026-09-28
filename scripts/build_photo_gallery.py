"""Build a local photo gallery page for the legacy tag review.

Offline and read-only: it reads the newest raw export (review/raw/photos_*.json,
from scripts/export_raw_olm.py) and writes review/photo_gallery.html, one page
you open in your browser. Each photo shows its OLM photo ID and date; you can
search by photo ID, date range and OLM key. The images load straight from
OLM's photo storage, only as you scroll to them. Keep the page local: it lists
all your photo addresses.

    python3 scripts/build_photo_gallery.py
"""
import argparse
import glob
import json
import os
import sys

PAGE = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>MROLM Photo Gallery</title>
<style>
  :root { --bg: #f4f4f2; --panel: #ffffff; --text: #1d1d1b; --muted: #6b6b66; --line: #d9d9d4; --accent: #2f6f4f; }
  @media (prefers-color-scheme: dark) {
    :root { --bg: #161615; --panel: #22221f; --text: #ececea; --muted: #a3a39c; --line: #3a3a36; --accent: #7cc19b; }
  }
  * { box-sizing: border-box; }
  body { margin: 0; background: var(--bg); color: var(--text); font: 15px/1.4 system-ui, sans-serif; }
  header { position: sticky; top: 0; z-index: 2; background: var(--panel); border-bottom: 1px solid var(--line);
           padding: 12px 16px; display: flex; flex-wrap: wrap; gap: 10px 16px; align-items: end; }
  h1 { font-size: 17px; margin: 0 12px 0 0; align-self: center; }
  label { display: flex; flex-direction: column; font-size: 12px; color: var(--muted); gap: 3px; }
  input, select, button { font: inherit; color: var(--text); background: var(--bg); border: 1px solid var(--line);
                          border-radius: 6px; padding: 6px 8px; }
  #ids { width: 220px; } #key { max-width: 300px; }
  button { cursor: pointer; }
  #count { color: var(--muted); font-size: 13px; align-self: center; }
  main { padding: 16px; display: grid; gap: 12px; grid-template-columns: repeat(auto-fill, minmax(var(--size, 300px), 1fr)); }
  figure { margin: 0; position: relative; background: var(--panel); border: 1px solid var(--line); border-radius: 8px;
           overflow: hidden; aspect-ratio: 3 / 4; }
  figure a { display: block; width: 100%; height: 100%; }
  figure img { width: 100%; height: 100%; object-fit: cover; display: block; }
  figcaption { position: absolute; top: 0; left: 0; right: 0; padding: 6px 8px; font-size: 13px; font-weight: 600;
               color: #fff; background: linear-gradient(rgba(0,0,0,.75), rgba(0,0,0,0)); text-shadow: 0 1px 2px #000;
               display: flex; justify-content: space-between; gap: 8px; pointer-events: none; }
  nav { display: flex; gap: 8px; justify-content: center; align-items: center; padding: 8px 16px 24px; }
  .empty { grid-column: 1 / -1; color: var(--muted); text-align: center; padding: 40px 0; }
</style>
</head>
<body>
<header>
  <h1>MROLM Photo Gallery</h1>
  <label>Photo ID(s)<input id="ids" placeholder="e.g. 546290, 5529" autocomplete="off"></label>
  <label>From<input id="from" type="date"></label>
  <label>To<input id="to" type="date"></label>
  <label>OLM key<select id="key"><option value="">All keys</option></select></label>
  <label>Size<input id="size" type="range" min="180" max="600" step="20" value="300"></label>
  <button id="clear" type="button">Clear</button>
  <span id="count"></span>
</header>
<main id="grid"></main>
<nav><button id="prev" type="button">Previous</button><span id="pageinfo"></span><button id="next" type="button">Next</button></nav>
<script>
const PHOTOS = __DATA__;  // [id, "YYYY-MM-DD HH:MM", photo URL, [OLM keys]], newest first
const PER_PAGE = 60;
const $ = id => document.getElementById(id);
let page = 0, shown = PHOTOS;

const keyCounts = {};
PHOTOS.forEach(p => p[3].forEach(k => keyCounts[k] = (keyCounts[k] || 0) + 1));
Object.keys(keyCounts).sort().forEach(k => $("key").add(new Option(`${k} (${keyCounts[k]})`, k)));

function applyFilters() {
  const ids = $("ids").value.split(/[\\s,;]+/).filter(Boolean);
  const from = $("from").value, to = $("to").value, key = $("key").value;
  shown = PHOTOS.filter(p => {
    const id = String(p[0]), day = p[1].slice(0, 10);
    if (ids.length && !ids.some(x => id.startsWith(x))) return false;
    if (from && day < from) return false;
    if (to && day > to) return false;
    if (key && !p[3].includes(key)) return false;
    return true;
  });
  page = 0;
  render();
}

function render() {
  const pages = Math.max(1, Math.ceil(shown.length / PER_PAGE));
  page = Math.min(page, pages - 1);
  const slice = shown.slice(page * PER_PAGE, (page + 1) * PER_PAGE);
  $("grid").innerHTML = slice.length ? "" : '<p class="empty">No photos match.</p>';
  for (const [id, date, url] of slice) {
    const fig = document.createElement("figure");
    fig.innerHTML = `<a href="${url}" target="_blank" rel="noopener"><img loading="lazy" alt="OLM photo ${id}" src="${url}"></a>` +
                    `<figcaption><span>${id}</span><span>${date}</span></figcaption>`;
    $("grid").append(fig);
  }
  $("count").textContent = `${shown.length} of ${PHOTOS.length} photos`;
  $("pageinfo").textContent = `Page ${page + 1} of ${pages}`;
  $("prev").disabled = page === 0;
  $("next").disabled = page >= pages - 1;
}

["ids", "from", "to", "key"].forEach(id => $(id).addEventListener("input", applyFilters));
$("size").addEventListener("input", e => document.documentElement.style.setProperty("--size", e.target.value + "px"));
$("prev").onclick = () => { page--; render(); scrollTo(0, 0); };
$("next").onclick = () => { page++; render(); scrollTo(0, 0); };
$("clear").onclick = () => { ["ids", "from", "to", "key"].forEach(id => $(id).value = ""); applyFilters(); };
render();
</script>
</body>
</html>
"""


def main():
    parser = argparse.ArgumentParser(description="Build a local photo gallery page from the newest raw export.")
    parser.add_argument("--raw-dir", default=os.path.join("review", "raw"))
    parser.add_argument("--out", default=os.path.join("review", "photo_gallery.html"))
    args = parser.parse_args()

    files = sorted(glob.glob(os.path.join(args.raw_dir, "photos_*.json")))
    if not files:
        sys.exit("[CRITICAL ERROR] No raw export found. Run scripts/export_raw_olm.py first.")
    with open(files[-1], encoding="utf-8") as f:
        photos = json.load(f)

    rows = []
    for p in photos:
        keys = sorted({f"{t['category']['key']}/{t['object']['key']}"
                       for t in p.get("new_tags") or [] if t.get("category") and t.get("object")})
        rows.append([p["id"], str(p.get("datetime") or "")[:16].replace("T", " "), p.get("filename") or "", keys])
    rows.sort(key=lambda r: r[1], reverse=True)

    # "</" is escaped so no photo data can close the script tag early
    data = json.dumps(rows, separators=(",", ":")).replace("</", "<\\/")
    with open(args.out, "w", encoding="utf-8") as f:
        f.write(PAGE.replace("__DATA__", data))
    os.chmod(args.out, 0o600)
    print(f"[SUCCESS] Wrote {args.out} with {len(rows)} photos from {files[-1]}")


if __name__ == "__main__":
    main()
