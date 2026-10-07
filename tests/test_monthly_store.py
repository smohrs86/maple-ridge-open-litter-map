import os
import sys
import tempfile
import unittest
from unittest import mock

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))
import monthly_store as ms
import sync_data as sd


def feature(pid, when="2026-10-03T12:00:00.000000Z"):
    return {"type": "Feature", "geometry": {"type": "Point", "coordinates": [-122.6, 49.2]},
            "properties": {"id": pid, "datetime": when, "objects": []}}


class MonthKeyTests(unittest.TestCase):
    def test_month_from_datetime(self):
        self.assertEqual(ms.month_key({"datetime": "2026-09-29T18:40:01.000000Z"}), "2026-09")

    def test_missing_or_bad_datetime_goes_to_undated(self):
        self.assertEqual(ms.month_key({}), ms.UNDATED)
        self.assertEqual(ms.month_key({"datetime": "yesterday"}), ms.UNDATED)


class StoreRoundTripTests(unittest.TestCase):
    def write(self, tmp, features, dropped=(), fp="abc"):
        return ms.write_store(tmp, features, list(dropped), {"mrolm_layers": []}, fp, sd.write_atomically)

    def test_round_trip_and_files_per_month(self):
        with tempfile.TemporaryDirectory() as tmp:
            feats = [feature(3, "2026-10-01T00:00:00Z"), feature(2, "2026-09-30T00:00:00Z"), feature(1, "2026-09-01T00:00:00Z")]
            self.write(tmp, feats, [(9, "no coordinates")])
            self.assertEqual(sorted(os.listdir(os.path.join(tmp, "months"))), ["2026-09.geojson", "2026-10.geojson"])
            loaded = ms.load_store(tmp, "abc")
            self.assertEqual(sorted(f["properties"]["id"] for f in loaded[0]), [1, 2, 3])
            self.assertEqual(loaded[1], [(9, "no coordinates")])

    def test_different_fingerprint_or_schema_means_rebuild(self):
        with tempfile.TemporaryDirectory() as tmp:
            self.write(tmp, [feature(1)])
            self.assertIsNone(ms.load_store(tmp, "other"))

    def test_missing_index_means_rebuild(self):
        with tempfile.TemporaryDirectory() as tmp:
            self.assertIsNone(ms.load_store(tmp, "abc"))

    def test_damaged_month_file_means_rebuild(self):
        with tempfile.TemporaryDirectory() as tmp:
            self.write(tmp, [feature(1)])
            with open(os.path.join(tmp, "months", "2026-10.geojson"), "a", encoding="utf-8") as f:
                f.write(" ")
            self.assertIsNone(ms.load_store(tmp, "abc"))

    def test_unchanged_month_is_not_rewritten_and_stale_month_is_removed(self):
        with tempfile.TemporaryDirectory() as tmp:
            self.write(tmp, [feature(2, "2026-10-01T00:00:00Z"), feature(1, "2026-09-01T00:00:00Z")])
            written = self.write(tmp, [feature(3, "2026-10-02T00:00:00Z"), feature(2, "2026-10-01T00:00:00Z")])
            self.assertFalse(any(p.endswith("2026-09.geojson") for p in written))
            self.assertEqual(os.listdir(os.path.join(tmp, "months")), ["2026-10.geojson"])


class MergeTests(unittest.TestCase):
    def test_fresh_copy_replaces_stored_and_new_photos_are_added_newest_first(self):
        old = feature(5)
        old["properties"]["objects"] = ["old"]
        new = feature(5)
        new["properties"]["objects"] = ["retagged"]
        merged, dropped = sd.merge_features([feature(4), old], [], [new, feature(6)], [])
        self.assertEqual([f["properties"]["id"] for f in merged], [6, 5, 4])
        self.assertEqual(merged[1]["properties"]["objects"], ["retagged"])

    def test_a_photo_that_becomes_dropped_leaves_the_features_and_one_that_recovers_leaves_the_list(self):
        merged, dropped = sd.merge_features([feature(1), feature(2)], [(7, "no coordinates")],
                                            [feature(7)], [(1, "invalid coordinates")])
        self.assertEqual(sorted(f["properties"]["id"] for f in merged), [2, 7])
        self.assertEqual(dropped, [(1, "invalid coordinates")])


class IncrementalFetchTests(unittest.TestCase):
    """fetch_all_photos with known_ids stops once a page (after the minimum) holds only stored photos."""

    def run_fetch(self, pages, **kwargs):
        requested = []

        def fake_page(headers, params):
            requested.append(params["page"])
            body = pages[params["page"] - 1] if params["page"] <= len(pages) else []
            return mock.Mock(json=lambda: {"photos": [{"id": i} for i in body]})

        with mock.patch.object(sd, "get_page_with_retries", fake_page), mock.patch.object(sd.time, "sleep"):
            photos, complete = sd.fetch_all_photos("token", **kwargs)
        return photos, complete, requested

    def test_stops_at_first_fully_known_page_after_the_minimum(self):
        pages = [[100, 99], [98, 97], [96, 95], [94, 93]]
        known = {98, 97, 96, 95, 94, 93}
        photos, complete, requested = self.run_fetch(pages, known_ids=known, min_pages=1)
        self.assertTrue(complete)
        self.assertEqual(requested, [1, 2])  # page 2 is the first fully known page

    def test_minimum_pages_are_always_read(self):
        pages = [[3, 2], [1, 0], [-1, -2]]
        photos, complete, requested = self.run_fetch(pages, known_ids={3, 2, 1, 0, -1, -2}, min_pages=3)
        self.assertEqual(requested, [1, 2, 3])
        self.assertTrue(complete)

    def test_without_known_ids_reads_to_the_empty_page(self):
        photos, complete, requested = self.run_fetch([[3], [2], [1]])
        self.assertEqual(requested, [1, 2, 3, 4])
        self.assertTrue(complete)
        self.assertEqual(len(photos), 3)


if __name__ == "__main__":
    unittest.main()
