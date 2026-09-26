import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))
import crosswalk as cw


def row(key, sec="", mat="", cus="", local="X", include="yes", fix="", n=2):
    return {"OLM key": key, "with Secondary Modifier": sec, "with Material tag": mat,
            "with Custom Tag": cus, "MROLM local key": local, "include on map": include,
            "OLM data needs fixes": fix, "_sheet_row": n}


class MatchTests(unittest.TestCase):
    def test_specific_row_beats_plain_row(self):
        plain, wood = row("other/other", local="misc", n=2), row("other/other", mat="Wood", local="wood", n=3)
        got, tie = cw.match_tag([plain, wood], "other/other", materials=["Wood"])
        self.assertIs(got, wood)
        self.assertEqual(tie, [])

    def test_blank_falls_back_to_plain_row(self):
        plain, wood = row("other/other", local="misc"), row("other/other", mat="Wood", local="wood")
        got, _ = cw.match_tag([plain, wood], "other/other", materials=["Metal"])
        self.assertIs(got, plain)

    def test_ignores_capitals_and_spaces(self):
        thc = row("smoking/vape", cus="THC")
        got, _ = cw.match_tag([thc], " Smoking/Vape ", customs=["  thc "])
        self.assertIs(got, thc)

    def test_first_match_wins_and_tie_is_reported(self):
        a, b = row("other/other", mat="Wood", n=2), row("other/other", cus="broken glass", n=3)
        got, tie = cw.match_tag([a, b], "other/other", materials=["wood"], customs=["Broken Glass"])
        self.assertIs(got, a)
        self.assertEqual(tie, [a, b])

    def test_no_row_is_unmapped(self):
        self.assertEqual(cw.match_tag([row("a/b")], "c/d"), (None, []))

    def test_secondary_modifier(self):
        plain, small = row("dumping/dumping", local="UNCLASS"), row("dumping/dumping", sec="small", local="Sml")
        self.assertIs(cw.match_tag([plain, small], "dumping/dumping", secondary="small")[0], small)
        self.assertIs(cw.match_tag([plain, small], "dumping/dumping")[0], plain)


class StatusTests(unittest.TestCase):
    def test_statuses(self):
        self.assertEqual(cw.classify(row("a/b", include="no")), "RECLASS")
        self.assertEqual(cw.classify(row("a/b", local="UNCLASS")), "UNCLASS")
        self.assertEqual(cw.classify(row("a/b", fix="reclass in OLM")), "REVIEW")
        self.assertEqual(cw.classify(row("a/b")), "OK")
        self.assertEqual(cw.classify(row("a/b", include="no", fix="note")), "RECLASS")

    def test_convention_check(self):
        bad = row("a/b", local="a/b", include="yes")
        good = row("c/d", local="c/d", include="no")
        self.assertEqual(cw.convention_problems([bad, good]), [bad])


if __name__ == "__main__":
    unittest.main()
