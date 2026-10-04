import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))
import sync_data as sd


class ClassifyTagGroupTests(unittest.TestCase):
    def group(self, **tag):
        return sd.classify_tag_group(tag)

    def test_plain_litter(self):
        self.assertEqual(self.group(category="food", item="wrapper"), "litter")
        self.assertEqual(self.group(), "litter")

    def test_smoking_and_alcohol_are_substances(self):
        self.assertEqual(self.group(category="smoking", item="butts"), "substances")
        self.assertEqual(self.group(category="alcohol", item="bottle"), "substances")

    def test_extras_follow_their_parent_category(self):
        self.assertEqual(self.group(category="material", parent_category="alcohol", item="glass"), "substances")
        self.assertEqual(self.group(category="material", parent_category="food", item="plastic"), "litter")

    def test_cannabis_custom_tags_are_substances_but_only_custom_ones(self):
        self.assertEqual(self.group(type="custom_tag", item="THC vape"), "substances")
        self.assertEqual(self.group(type="custom_tag", item="Cannabis wrapper"), "substances")
        self.assertEqual(self.group(type="standard", item="weed"), "litter")

    def test_pet_waste_only_for_the_two_dog_waste_items(self):
        self.assertEqual(self.group(category="pets", item="dogshit"), "pet_waste")
        self.assertEqual(self.group(category="pets", item="dogshit_in_bag"), "pet_waste")
        self.assertEqual(self.group(category="pets", item="toy"), "litter")


class ResolveNewTagsFormatTests(unittest.TestCase):
    def test_standard_tag(self):
        entry = {"category_litter_object_id": 5, "category": {"key": "food"}, "object": {"key": "wrapper"},
                 "quantity": 3}
        self.assertEqual(sd.resolve_new_tags_format(entry),
                         [{"type": "standard", "category": "food", "item": "wrapper", "quantity": 3}])

    def test_object_type_kept_only_when_sent(self):
        entry = {"category_litter_object_id": 5, "category": {"key": "dumping"}, "object": {"key": "dumping"},
                 "type": {"key": "small"}}
        self.assertEqual(sd.resolve_new_tags_format(entry)[0]["object_type"], "small")
        entry["type"] = None
        self.assertNotIn("object_type", sd.resolve_new_tags_format(entry)[0])

    def test_missing_keys_and_quantity_get_defaults(self):
        got = sd.resolve_new_tags_format({"category_litter_object_id": 5})
        self.assertEqual(got, [{"type": "standard", "category": "unclassified", "item": "unclassified",
                                "quantity": 1}])

    def test_extra_tags_become_child_entries_with_parent_and_inherited_quantity(self):
        entry = {"category_litter_object_id": 5, "category": {"key": "food"}, "object": {"key": "wrapper"},
                 "quantity": 2,
                 "extra_tags": [{"type": "material", "tag": {"key": "plastic"}},
                                {"type": "custom_tag", "tag": {"key": "receipt"}, "quantity": 7}]}
        standard, material, custom = sd.resolve_new_tags_format(entry)
        self.assertEqual(material, {"type": "material", "category": "material", "item": "plastic", "quantity": 2,
                                    "parent_category": "food", "parent_item": "wrapper"})
        self.assertEqual((custom["type"], custom["item"], custom["quantity"]), ("custom_tag", "receipt", 7))

    def test_entry_without_a_standard_object_gives_only_its_extras(self):
        entry = {"category_litter_object_id": None, "extra_tags": [{"type": "custom_tag", "tag": {"key": "flyer"}}]}
        got = sd.resolve_new_tags_format(entry)
        self.assertEqual([t["item"] for t in got], ["flyer"])
        self.assertIsNone(got[0]["parent_category"])

    def test_empty_entry(self):
        self.assertEqual(sd.resolve_new_tags_format({}), [])


class ResolveSummaryFormatTests(unittest.TestCase):
    KEYS = {"categories": {"8": "food"}, "objects": {"40": "wrapper"}, "materials": {"2": "plastic"},
            "brands": {"9": "acme"}, "custom_tags": {"4": "receipt"}, "types": {"1": "small"}}

    def test_standard_tag_with_every_kind_of_extra(self):
        entry = {"clo_id": 49, "category_id": 8, "object_id": 40, "type_id": 1, "quantity": 2,
                 "materials": [2], "brands": [9], "custom_tags": [4]}
        got = sd.resolve_summary_format(entry, self.KEYS)
        self.assertEqual([(t["type"], t["item"]) for t in got],
                         [("standard", "wrapper"), ("material", "plastic"), ("brand", "acme"),
                          ("custom_tag", "receipt")])
        self.assertEqual(got[0]["category"], "food")
        self.assertEqual(got[0]["object_type"], "small")
        self.assertTrue(all(t["quantity"] == 2 for t in got))
        self.assertTrue(all(t["parent_item"] == "wrapper" for t in got[1:]))

    def test_brands_may_be_a_dict_keyed_by_id(self):
        got = sd.resolve_summary_format({"clo_id": 49, "brands": {"9": 3}}, self.KEYS)
        self.assertEqual(got[1]["item"], "acme")

    def test_unknown_ids_become_unclassified_and_no_type_means_no_object_type(self):
        got = sd.resolve_summary_format({"clo_id": 49, "category_id": 99, "object_id": 98, "type_id": None,
                                         "materials": [97]}, self.KEYS)
        self.assertEqual((got[0]["category"], got[0]["item"]), ("unclassified", "unclassified"))
        self.assertNotIn("object_type", got[0])
        self.assertEqual(got[1]["item"], "unclassified")

    def test_orphan_custom_tag_has_no_standard_entry(self):
        got = sd.resolve_summary_format({"clo_id": None, "custom_tags": [4]}, self.KEYS)
        self.assertEqual([t["type"] for t in got], ["custom_tag"])
        self.assertIsNone(got[0]["parent_category"])


class BuildPhotoPropertiesTests(unittest.TestCase):
    ROWS = []

    def props(self, photo):
        return sd.build_photo_properties(photo, self.ROWS)

    def new_photo(self, *entries):
        return {"id": 1, "datetime": "2026-09-01T10:00:00Z", "filename": "x.jpg", "new_tags": list(entries)}

    def standard(self, category, obj, **extra):
        return {"category_litter_object_id": 1, "category": {"key": category}, "object": {"key": obj}, **extra}

    def test_basic_fields_and_flat_tags(self):
        got = self.props(self.new_photo(self.standard("food", "wrapper")))
        self.assertEqual((got["id"], got["datetime"], got["filename"]), (1, "2026-09-01T10:00:00Z", "x.jpg"))
        self.assertEqual([t["item"] for t in got["tags"]], ["wrapper"])
        self.assertEqual(got["groups"], ["litter"])
        self.assertEqual((got["has_litter"], got["has_pet_waste"], got["has_substances"]), (True, False, False))

    def test_groups_are_sorted_and_flags_follow_them(self):
        got = self.props(self.new_photo(self.standard("smoking", "butts"), self.standard("pets", "dogshit"),
                                        self.standard("food", "wrapper")))
        self.assertEqual(got["groups"], ["litter", "pet_waste", "substances"])
        self.assertEqual((got["has_litter"], got["has_pet_waste"], got["has_substances"]), (True, True, True))

    def test_photo_with_no_tags_counts_as_litter(self):
        got = self.props({"id": 2, "new_tags": []})
        self.assertEqual((got["tags"], got["groups"], got["has_litter"]), ([], ["litter"], True))

    def test_empty_new_tags_falls_back_to_the_summary_format(self):
        photo = {"id": 3, "new_tags": [],
                 "summary": {"tags": [{"clo_id": 1, "category_id": 8, "object_id": 40}],
                             "keys": {"categories": {"8": "alcohol"}, "objects": {"40": "bottle"}}}}
        got = self.props(photo)
        self.assertEqual([t["item"] for t in got["tags"]], ["bottle"])
        self.assertEqual(got["groups"], ["substances"])

    def test_new_tags_win_over_the_summary(self):
        photo = self.new_photo(self.standard("food", "wrapper"))
        photo["summary"] = {"tags": [{"clo_id": 1, "category_id": 8, "object_id": 40}],
                            "keys": {"categories": {"8": "alcohol"}, "objects": {"40": "bottle"}}}
        self.assertEqual([t["item"] for t in self.props(photo)["tags"]], ["wrapper"])

    def test_photo_with_neither_format(self):
        got = self.props({"id": 4})
        self.assertEqual((got["tags"], got["objects"], got["groups"]), ([], [], ["litter"]))


if __name__ == "__main__":
    unittest.main()
