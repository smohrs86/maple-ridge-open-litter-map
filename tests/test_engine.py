import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))
import sync_data as sd


def row(key, sec="", mat="", cus="", group="G", sub="", local="X", include="yes", fix="", n=2):
    return {"OLM key": key, "with Secondary Modifier": sec, "with Material tag": mat,
            "with Custom Tag": cus, "MROLM Group": group, "MROLM Subgroup": sub,
            "MROLM local key": local, "include on map": include, "OLM data needs fixes": fix,
            "_sheet_row": n}


def new_tag(category, obj, type_key=None, materials=(), customs=(), quantity=1, picked_up=True):
    extras = [{"type": "material", "tag": {"key": m}} for m in materials]
    extras += [{"type": "custom_tag", "tag": {"key": c}} for c in customs]
    tag = {"category": {"key": category} if category else None, "object": {"key": obj} if obj else None,
           "extra_tags": extras, "quantity": quantity, "picked_up": picked_up}
    if type_key:
        tag["type"] = {"key": type_key}
    return tag


class ExtractObjectsTests(unittest.TestCase):
    def test_new_tags_format(self):
        photo = {"new_tags": [new_tag("dumping", "dumping", type_key="small", materials=["wood"],
                                      customs=["THC"], quantity=3, picked_up=False)]}
        [obj] = sd.extract_objects(photo)
        self.assertEqual(obj, {"olm_key": "dumping/dumping", "secondary": "small", "materials": ["wood"],
                               "customs": ["THC"], "quantity": 3, "picked_up": False})

    def test_orphan_custom_tag_has_no_key(self):
        photo = {"new_tags": [new_tag(None, None, customs=["receipt"])]}
        [obj] = sd.extract_objects(photo)
        self.assertEqual(obj["olm_key"], "")
        self.assertEqual(obj["customs"], ["receipt"])

    def test_summary_format(self):
        photo = {"summary": {
            "tags": [{"clo_id": 1, "category_id": 13, "object_id": 103, "type_id": 7, "quantity": 2,
                      "picked_up": False, "materials": [5], "custom_tags": [9]}],
            "keys": {"categories": {"13": "pets"}, "objects": {"103": "dogshit"}, "types": {"7": "small"},
                     "materials": {"5": "plastic"}, "custom_tags": {"9": "THC"}}}}
        [obj] = sd.extract_objects(photo)
        self.assertEqual(obj, {"olm_key": "pets/dogshit", "secondary": "small", "materials": ["plastic"],
                               "customs": ["THC"], "quantity": 2, "picked_up": False})

    def test_picked_up_keeps_three_states(self):
        self.assertIs(sd.picked_up_state(True), True)
        self.assertIs(sd.picked_up_state(False), False)
        self.assertIsNone(sd.picked_up_state(None))
        photo = {"new_tags": [new_tag("pets", "dogshit", picked_up=None)]}
        self.assertIsNone(sd.extract_objects(photo)[0]["picked_up"])


class ClassifyObjectTests(unittest.TestCase):
    ROWS = [
        row("dumping/dumping", group="Dumping", local="UNCLASS", n=2),
        row("dumping/dumping", sec="small", group="Dumping", local="Sml", n=3),
        row("alcohol/bottle", group="Household", sub="Liquor", local="Liquor Bottle", n=4),
        row("food/wrapper", group="Snack", local="Wrapper", fix="needs a legacy review", n=5),
        row("civic/other", group="", local="civic/other", include="no", n=6),
        row("other/other", mat="Wood", group="Piece", local="Wood", n=7),
        row("other/other", cus="broken glass", group="Piece", local="Glass", n=8),
    ]

    def classify(self, key, **kw):
        raw = {"olm_key": key, "secondary": kw.get("sec", ""), "materials": kw.get("mat", []),
               "customs": kw.get("cus", []), "quantity": 1, "picked_up": kw.get("picked_up", True)}
        return sd.classify_object(raw, self.ROWS)

    def test_ok_object_is_on_map_with_full_name(self):
        got = self.classify("alcohol/bottle")
        self.assertEqual((got["status"], got["on_map"]), ("OK", True))
        self.assertEqual((got["group"], got["subgroup"], got["layer"]), ("Household", "Liquor", "Liquor Bottle"))
        self.assertEqual(got["full_name"], "Household – Liquor – Liquor Bottle")

    def test_full_name_skips_blank_subgroup(self):
        self.assertEqual(self.classify("dumping/dumping", sec="small")["full_name"], "Dumping – Sml")

    def test_unclass_and_review_are_on_map(self):
        self.assertEqual((self.classify("dumping/dumping")["status"], self.classify("dumping/dumping")["on_map"]),
                         ("UNCLASS", True))
        got = self.classify("food/wrapper")
        self.assertEqual((got["status"], got["on_map"]), ("REVIEW", True))

    def test_reclass_unmapped_and_orphan_are_off_map(self):
        self.assertEqual((self.classify("civic/other")["status"], self.classify("civic/other")["on_map"]),
                         ("RECLASS", False))
        self.assertEqual((self.classify("space/rocket")["status"], self.classify("space/rocket")["on_map"]),
                         ("UNMAPPED", False))
        orphan = self.classify("", cus=["receipt"])
        self.assertEqual((orphan["status"], orphan["on_map"], orphan["custom_tags"]),
                         ("ORPHAN TAG", False, ["receipt"]))

    def test_picked_up_is_carried_through(self):
        self.assertIs(self.classify("alcohol/bottle", picked_up=False)["picked_up"], False)
        self.assertIsNone(self.classify("alcohol/bottle", picked_up=None)["picked_up"])

    def test_tie_rows_recorded(self):
        got = self.classify("other/other", mat=["Wood"], cus=["broken glass"])
        self.assertEqual((got["layer"], got["tie_rows"]), ("Wood", [7, 8]))
        self.assertNotIn("tie_rows", self.classify("alcohol/bottle"))


class AuditTests(unittest.TestCase):
    ROWS = ClassifyObjectTests.ROWS

    def feature(self, photo_id, *objects, when="2026-09-01T10:00:00Z"):
        classified = []
        for key, kw in objects:
            raw = {"olm_key": key, "secondary": kw.get("sec", ""), "materials": kw.get("mat", []),
                   "customs": kw.get("cus", []), "quantity": kw.get("qty", 1), "picked_up": kw.get("picked_up", True)}
            classified.append(sd.classify_object(raw, self.ROWS))
        return {"properties": {"id": photo_id, "datetime": when, "objects": classified}}

    def audit(self):
        features = [
            self.feature(1, ("alcohol/bottle", {"qty": 3, "picked_up": False}), ("civic/other", {})),
            self.feature(2, ("", {"cus": ["receipt"]}), ("space/rocket", {}), when="2026-09-20T01:00:00Z"),
            self.feature(3, ("other/other", {"mat": ["Wood"], "cus": ["broken glass"]})),
            self.feature(4, ("food/wrapper", {"qty": 2})),
        ]
        return sd.build_audit(features, self.ROWS, skipped_photos=1)

    def test_summary_and_status_counts(self):
        text = self.audit()
        self.assertIn("- Photos: 4 (1 more skipped: no coordinates)", text)
        self.assertIn("- Newest photo: 2026-09-20", text)
        self.assertIn("- Tagged objects: 6 (9 items)", text)
        self.assertIn("- Shown on the map: 3 objects (6 items) in 3 layers", text)
        self.assertIn("| Not used | ", text)
        self.assertRegex(text, r"\| Orphan tags \| [^|]+ \| 1 \| 1 \| 0 \|")
        self.assertRegex(text, r"\| Unmapped \| [^|]+ \| 1 \| 1 \| 0 \|")
        self.assertRegex(text, r"\| REVIEW \| [^|]+ \| 1 \| 2 \|")

    def test_details_list_photo_ids(self):
        text = self.audit()
        self.assertIn("| 2 | receipt |", text)
        self.assertIn("| space/rocket | 2 |", text)
        self.assertIn("| 3 | other/other | Wood | 7, 8 |", text)
        self.assertIn("| food/wrapper | 1 | 2 | needs a legacy review |", text)
        self.assertIn("| civic/other | 1 | 1 |", text)

    def test_layer_table_includes_empty_layers_and_not_picked_up(self):
        text = self.audit()
        self.assertIn("| Household | Liquor | Liquor Bottle | 3 | 1 | 1 | 3 |", text)
        self.assertIn("| Dumping |  | Sml | 0 | 0 | 0 | 0 |", text)
        self.assertNotIn("civic/other | 0", text)

    def test_no_timestamp_so_unchanged_data_gives_unchanged_file(self):
        self.assertEqual(self.audit(), self.audit())


class LoadCrosswalkTests(unittest.TestCase):
    def write(self, text):
        f = tempfile.NamedTemporaryFile("w", suffix=".csv", delete=False, encoding="utf-8")
        f.write(text)
        f.close()
        self.addCleanup(os.remove, f.name)
        return f.name

    def test_missing_file_stops_the_run(self):
        with self.assertRaises(SystemExit) as stop:
            sd.load_crosswalk("no/such/crosswalk.csv")
        self.assertEqual(stop.exception.code, 1)

    def test_renamed_header_stops_the_run(self):
        path = self.write("OLM key,with Secondary Modifier,with Material tag,with Custom Tag,"
                          "Group,MROLM Subgroup,MROLM local key,include on map,OLM data needs fixes\n"
                          "a/b,,,,G,,X,yes,\n")
        with self.assertRaises(SystemExit):
            sd.load_crosswalk(path)

    def test_real_crosswalk_loads(self):
        path = os.path.join(os.path.dirname(__file__), "..", "config", "crosswalk.csv")
        self.assertTrue(len(sd.load_crosswalk(path)) > 0)


if __name__ == "__main__":
    unittest.main()
