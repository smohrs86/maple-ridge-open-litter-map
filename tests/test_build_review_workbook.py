import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))

from build_review_workbook import apply_reviewed  # noqa: E402

PHOTOS = [{"id": 1, "created_at": "2026-09-30T02:28:22.000000Z"},
          {"id": 2, "created_at": "2026-10-03T10:00:00.000000Z"}]


def record(photo_id, tag_id, **extra):
    return {"PhotoID": photo_id, "Object_No": 1, "OLM_Tag_ID": tag_id, **extra}


class ApplyReviewedTest(unittest.TestCase):
    def test_uploaded_before_date_is_stamped(self):
        rows = [record(1, 10), record(2, 20)]
        apply_reviewed(rows, PHOTOS, {}, "2026-10-02")
        self.assertEqual(rows[0]["Reviewed"], "2026-10-02")
        self.assertNotIn("Reviewed", rows[1])

    def test_edit_or_note_counts_as_reviewed_even_on_a_newer_photo(self):
        rows = [record(2, 20, **{"Review notes": "retagged in OLM"})]
        apply_reviewed(rows, PHOTOS, {}, "2026-10-02")
        self.assertEqual(rows[0]["Reviewed"], "2026-10-02")

    def test_carried_date_is_kept(self):
        rows = [record(1, 10)]
        apply_reviewed(rows, PHOTOS, {(1, "tag", 10): "2026-09-01"}, "2026-10-02")
        self.assertEqual(rows[0]["Reviewed"], "2026-09-01")

    def test_nothing_stamped_without_a_date(self):
        rows = [record(1, 10, **{"Review notes": "x"})]
        apply_reviewed(rows, PHOTOS, {}, None)
        self.assertNotIn("Reviewed", rows[0])


if __name__ == "__main__":
    unittest.main()
