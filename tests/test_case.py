import tempfile
import unittest
from pathlib import Path

from hunt_sift.core.case import create_case, load_case, write_case
from hunt_sift.core.workspace import ArtifactRecord


class CaseTests(unittest.TestCase):
    def test_case_has_stable_fingerprint(self):
        records = [ArtifactRecord("a.txt", "text", 3, "abc")]
        first = create_case(records)
        second = create_case(records)
        self.assertEqual(first["fingerprint"], second["fingerprint"])
        self.assertTrue(first["offline_only"])

    def test_case_roundtrip(self):
        records = [ArtifactRecord("a.txt", "text", 3, "abc")]
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "case.json"
            write_case(path, records)
            loaded = load_case(path)
            self.assertEqual(loaded["artifact_count"], 1)
            self.assertEqual(loaded["schema"], "hunt-sift.case.v1")
