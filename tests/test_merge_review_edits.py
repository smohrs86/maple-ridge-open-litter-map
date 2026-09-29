import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))

from merge_review_edits import EDIT_FIELDS, plan_merge  # noqa: E402

LISTS = {"keys": {"food/tinfoil", "other/plastic"}, "types": {"small"}, "materials": {"foil", "plastic"}}


def row(**values):
    return {f: values.get(f, "") for f in EDIT_FIELDS}


def edit(field, was, now, photo=1, tag=10):
    return {"photo_id": photo, "tag_id": tag, "field": field, "was": was, "now": now}


class PlanMergeTests(unittest.TestCase):
    def outcome(self, current, e):
        plan = plan_merge(current, [e], LISTS)
        return [name for name, items in plan.items() if items]

    def test_clean_edit_is_applied(self):
        self.assertEqual(self.outcome({(1, 10): row()}, edit("Change_To_OLMKey", "", "food/tinfoil")), ["apply"])

    def test_clearing_a_value_is_applied(self):
        current = {(1, 10): row(**{"Review notes": "old note"})}
        self.assertEqual(self.outcome(current, edit("Review notes", "old note", "")), ["apply"])

    def test_same_value_already_in_workbook(self):
        current = {(1, 10): row(Change_To_OLMKey="food/tinfoil")}
        self.assertEqual(self.outcome(current, edit("Change_To_OLMKey", "", "food/tinfoil")), ["already"])

    def test_workbook_changed_since_page_was_built_is_a_conflict(self):
        current = {(1, 10): row(Change_to_OLM_Custom="Piece")}
        self.assertEqual(self.outcome(current, edit("Change_to_OLM_Custom", "", "THC")), ["conflict"])

    def test_unknown_tag_is_missing(self):
        self.assertEqual(self.outcome({(1, 10): row()}, edit("Change_To_OLMKey", "", "food/tinfoil", tag=99)), ["missing"])

    def test_unknown_key_or_material_is_invalid(self):
        self.assertEqual(self.outcome({(1, 10): row()}, edit("Change_To_OLMKey", "", "food/foil")), ["invalid"])
        self.assertEqual(self.outcome({(1, 10): row()}, edit("Change_to_OLM_Material", "", "foil; tin")), ["invalid"])

    def test_remove_allowed_for_type_and_material_but_not_key(self):
        self.assertEqual(self.outcome({(1, 10): row()}, edit("Change_to_OLM_Material", "", "[remove]")), ["apply"])
        self.assertEqual(self.outcome({(1, 10): row()}, edit("Change_To_OLMKey", "", "[remove]")), ["invalid"])

    def test_custom_tags_and_notes_are_free_text(self):
        self.assertEqual(self.outcome({(1, 10): row()}, edit("Change_to_OLM_Custom", "", "Piece; anything")), ["apply"])

    def test_picked_up_must_be_yes_or_no(self):
        self.assertEqual(self.outcome({(1, 10): row()}, edit("Change_to_Picked_Up", "", "yes")), ["apply"])
        self.assertEqual(self.outcome({(1, 10): row()}, edit("Change_to_Picked_Up", "", "maybe")), ["invalid"])

    def test_quantity_must_be_a_whole_number_of_one_or_more(self):
        self.assertEqual(self.outcome({(1, 10): row()}, edit("Change_to_Quantity", "", "2")), ["apply"])
        for bad in ("0", "2.5", "two", "[remove]"):
            self.assertEqual(self.outcome({(1, 10): row()}, edit("Change_to_Quantity", "", bad)), ["invalid"], bad)

    def test_unknown_field_is_rejected(self):
        self.assertEqual(self.outcome({(1, 10): row()}, edit("OLM_key", "", "food/tinfoil")), ["bad_field"])


if __name__ == "__main__":
    unittest.main()
