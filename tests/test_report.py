import copy
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from rrlab.report import compare, canonical_hash, markdown_summary
from tests.test_core import fixture


class ReportTests(unittest.TestCase):
    def test_hash_is_key_order_independent(self):
        self.assertEqual(canonical_hash({"a": 1, "b": 2}),
                         canonical_hash({"b": 2, "a": 1}))
        self.assertNotEqual(canonical_hash({"a": 1}), canonical_hash({"a": 2}))

    def test_comparison_is_deterministic_and_auditable(self):
        data = fixture()
        data["questions"].append({"id": "u", "split": "dev", "text": "absent",
                                  "evidence": []})
        a = {"method": "tfidf", "size": 3, "overlap": 0}
        b = {"method": "bm25", "size": 1, "overlap": 0}
        report = compare(data, "dev", a, b, 1)
        self.assertEqual(report, compare(data, "dev", a, b, 1))
        self.assertEqual(report["runs"]["baseline"]["metrics"]["recall_at_k"], 1)
        self.assertEqual(report["runs"]["baseline"]["metrics"]["unsupported_empty_rate"], 1)
        self.assertEqual(len(report["comparison"]), 2)
        self.assertIn("dataset_sha256", report)
        self.assertIn("recall_at_k", markdown_summary(report))

    def test_regression_and_failure_are_preserved(self):
        data = fixture()
        data["questions"][0]["evidence"][0]["quote"] = "red green"
        a = {"method": "tfidf", "size": 3, "overlap": 0}
        b = {"method": "bm25", "size": 1, "overlap": 0}
        report = compare(data, "dev", a, b, 1)
        self.assertEqual(report["comparison"][0]["classification"], "regression")
        self.assertEqual(report["runs"]["candidate"]["failures"], ["q"])

    def test_empty_split_and_unknown_config_are_errors(self):
        a = {"method": "tfidf", "size": 3, "overlap": 0}
        for split in ("test", "oops"):
            with self.assertRaises(ValueError):
                compare(fixture(), split, a, a, 1)
        b = {**a, "surprise": 5}
        with self.assertRaises(ValueError):
            compare(fixture(), "dev", a, b, 1)

    def test_cli_success_and_bad_inputs(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            dataset = root / "data.json"
            dataset.write_text(json.dumps(fixture()), encoding="utf-8")
            output = root / "result"
            base = [sys.executable, "-m", "rrlab", "--dataset", str(dataset),
                    "--split", "dev", "--output", str(output)]
            result = subprocess.run(base, capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertTrue(output.with_suffix(".json").is_file())
            self.assertTrue(output.with_suffix(".md").is_file())
            for args in (["--k", "0"], ["--candidate-overlap", "32"],
                         ["--dataset", str(root / "missing")], ["--split", "test"],
                         ["--output", str(dataset.with_suffix(""))]):
                result = subprocess.run(base + args, capture_output=True, text=True)
                self.assertEqual(result.returncode, 2, result.stderr)
                self.assertNotIn("Traceback", result.stderr)
            dataset.write_text("{", encoding="utf-8")
            result = subprocess.run(base, capture_output=True, text=True)
            self.assertEqual(result.returncode, 2)

    def test_fixture_split_counts_and_labels(self):
        data = json.loads(Path("data/fixture.json").read_text(encoding="utf-8"))
        self.assertEqual(len(data["questions"]), 40)
        for split in ("dev", "test"):
            subset = [q for q in data["questions"] if q["split"] == split]
            self.assertEqual(len(subset), 20)
            self.assertEqual(sum(not q["evidence"] for q in subset), 4)
        a = {"method": "tfidf", "size": 48, "overlap": 8}
        # Validate all labels without evaluating held-out rankings.
        from rrlab.core import validate_dataset
        validate_dataset(data)


if __name__ == "__main__":
    unittest.main()
