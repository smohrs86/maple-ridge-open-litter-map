import os
import sys
import tempfile
import unittest
from unittest import mock

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))
import sync_data as sd


class WriteAtomicallyTests(unittest.TestCase):
    def test_creates_folder_and_file_and_leaves_no_temp(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "new", "out.txt")
            sd.write_atomically(path, "hello")
            with open(path, encoding="utf-8") as f:
                self.assertEqual(f.read(), "hello")
            self.assertEqual(os.listdir(os.path.dirname(path)), ["out.txt"])

    def test_replaces_existing_file(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "out.txt")
            sd.write_atomically(path, "old")
            sd.write_atomically(path, "new")
            with open(path, encoding="utf-8") as f:
                self.assertEqual(f.read(), "new")

    def test_failure_keeps_old_file_and_removes_temp(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "out.txt")
            sd.write_atomically(path, "old")
            with mock.patch.object(sd.os, "replace", side_effect=OSError("disk full")):
                with self.assertRaises(OSError):
                    sd.write_atomically(path, "new")
            with open(path, encoding="utf-8") as f:
                self.assertEqual(f.read(), "old")
            self.assertEqual(os.listdir(tmp), ["out.txt"])


if __name__ == "__main__":
    unittest.main()
