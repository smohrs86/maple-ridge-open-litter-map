import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))

from olm_batch_replace import TagList, apply_change, is_orphan, matches_summary, to_payload  # noqa: E402

TAGS = TagList({
    "categories": [{"id": 8, "key": "food"}, {"id": 12, "key": "other"}],
    "objects": [{"id": 53, "key": "wrapper"}, {"id": 90, "key": "paper"}],
    "category_objects": [{"id": 65, "category_id": 8, "litter_object_id": 53},
                         {"id": 109, "category_id": 12, "litter_object_id": 90}],
    "types": [{"id": 1, "key": "beer"}],
    "materials": [{"id": 2, "key": "plastic"}, {"id": 5, "key": "paper"}],
    "category_object_types": [],
})

# The real orphan on photo 546048 (a lone "receipt" custom tag), as the export returns it.
ORPHAN_PHOTO = {
    "id": 546048,
    "new_tags": [{"id": 611444, "category_litter_object_id": None, "litter_object_type_id": None, "quantity": 1,
                  "picked_up": False, "extra_tags": [{"type": "custom_tag", "quantity": 1,
                                                      "tag": {"id": 6286, "key": "receipt"}}]}],
    "summary": {"tags": [{"clo_id": None, "category_id": 0, "object_id": 0, "type_id": None, "quantity": 1,
                          "picked_up": False, "materials": [], "brands": [], "custom_tags": [6286]}],
                "keys": {"custom_tags": {"6286": "receipt"}}},
}
OBJECT_TAG = {"id": 1, "category_litter_object_id": 65, "litter_object_type_id": None, "quantity": 2,
              "picked_up": True, "extra_tags": [{"type": "material", "quantity": 1, "tag": {"id": 2, "key": "plastic"}}]}


class OrphanTests(unittest.TestCase):
    def test_orphan_uses_custom_only_format(self):
        payload = to_payload(ORPHAN_PHOTO["new_tags"][0])
        self.assertTrue(is_orphan(payload))
        self.assertEqual(payload, {"custom": True, "key": "receipt", "quantity": 1, "picked_up": False,
                                   "materials": [], "brands": [], "custom_tags": []})

    def test_orphan_backup_matches_olm_summary(self):
        self.assertTrue(matches_summary([to_payload(t) for t in ORPHAN_PHOTO["new_tags"]], ORPHAN_PHOTO))

    def test_orphan_given_a_key_becomes_an_object_and_keeps_its_custom_tag(self):
        problems = []
        new = apply_change(to_payload(ORPHAN_PHOTO["new_tags"][0]),
                           {"Change_To_OLMKey": "other/paper", "Change_to_Picked_Up": "yes"}, TAGS, problems)
        self.assertEqual(problems, [])
        self.assertEqual(new["category_litter_object_id"], 109)
        self.assertEqual(new["custom_tags"], ["receipt"])
        self.assertIs(new["picked_up"], True)
        self.assertEqual(new["quantity"], 1)

    def test_orphan_without_a_key_stays_an_orphan(self):
        problems = []
        new = apply_change(to_payload(ORPHAN_PHOTO["new_tags"][0]), {"Change_to_Picked_Up": "yes"}, TAGS, problems)
        self.assertEqual(problems, [])
        self.assertTrue(is_orphan(new))
        self.assertIs(new["picked_up"], True)

    def test_orphan_cannot_take_a_material_without_a_key(self):
        problems = []
        apply_change(to_payload(ORPHAN_PHOTO["new_tags"][0]), {"Change_to_OLM_Material": "paper"}, TAGS, problems)
        self.assertTrue(problems)


class PickedUpTests(unittest.TestCase):
    def test_picked_up_changes_only_when_asked(self):
        problems = []
        new = apply_change(to_payload(OBJECT_TAG), {"Change_to_Picked_Up": "no"}, TAGS, problems)
        self.assertEqual(problems, [])
        self.assertIs(new["picked_up"], False)
        unchanged = apply_change(to_payload(OBJECT_TAG), {"Change_To_OLMKey": "other/paper"}, TAGS, [])
        self.assertIs(unchanged["picked_up"], True)
        self.assertEqual(unchanged["materials"], [2])

    def test_picked_up_value_must_be_yes_or_no(self):
        problems = []
        apply_change(to_payload(OBJECT_TAG), {"Change_to_Picked_Up": "maybe"}, TAGS, problems)
        self.assertTrue(problems)


class QuantityTests(unittest.TestCase):
    def test_quantity_changes_only_when_asked(self):
        problems = []
        new = apply_change(to_payload(OBJECT_TAG), {"Change_to_Quantity": "3"}, TAGS, problems)
        self.assertEqual(problems, [])
        self.assertEqual(new["quantity"], 3)
        unchanged = apply_change(to_payload(OBJECT_TAG), {"Change_To_OLMKey": "other/paper"}, TAGS, [])
        self.assertEqual(unchanged["quantity"], 2)

    def test_quantity_read_back_from_excel_as_a_decimal(self):
        problems = []
        new = apply_change(to_payload(OBJECT_TAG), {"Change_to_Quantity": "10.0"}, TAGS, problems)
        self.assertEqual(problems, [])
        self.assertEqual(new["quantity"], 10)

    def test_quantity_must_be_a_whole_number_of_one_or_more(self):
        for bad in ("0", "-1", "2.5", "two"):
            problems = []
            apply_change(to_payload(OBJECT_TAG), {"Change_to_Quantity": bad}, TAGS, problems)
            self.assertTrue(problems, bad)


if __name__ == "__main__":
    unittest.main()
