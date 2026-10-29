import copy
import math
import unittest

from rrlab.core import chunk_documents, evaluate_query, rank, validate_dataset


def fixture():
    return {"documents": [{"id": "a", "text": "red green blue"},
                          {"id": "b", "text": "green yellow"}],
            "questions": [{"id": "q", "split": "dev", "text": "red",
                           "evidence": [{"doc_id": "a", "quote": "red"}]}]}


class CoreTests(unittest.TestCase):
    def test_metrics_hand_computed_and_overlapping_hits_deduplicated(self):
        evidence = [{"doc_id": "a", "quote": "red"},
                    {"doc_id": "b", "quote": "blue"}]
        hits = [{"doc_id": "x", "text": "noise"},
                {"doc_id": "a", "text": "red"},
                {"doc_id": "a", "text": "red"}]
        result = evaluate_query(hits, evidence)
        self.assertEqual(result["recall"], 0.5)
        self.assertEqual(result["rr"], 0.5)
        self.assertEqual(result["covered_evidence"], [0])

    def test_partial_quote_is_not_a_hit(self):
        result = evaluate_query([{"doc_id": "a", "text": "red"}],
                                [{"doc_id": "a", "quote": "red green"}])
        self.assertEqual((result["recall"], result["rr"]), (0, 0))

    def test_unsupported_metrics_are_null(self):
        self.assertEqual(evaluate_query([], []),
                         {"recall": None, "rr": None, "covered_evidence": [],
                          "empty_result": True})

    def test_chunks_keep_unicode_offsets_and_tail(self):
        text = "Café  naïve\nred green blue"
        chunks = chunk_documents([{"id": "a", "text": text}], 3, 1)
        self.assertEqual([c["text"] for c in chunks],
                         ["Café  naïve\nred", "red green blue"])
        for chunk in chunks:
            self.assertEqual(text[chunk["start"]:chunk["end"]], chunk["text"])

    def test_bad_chunk_settings(self):
        for size, overlap in [(0, 0), (3, 3), (3, -1), (True, 0)]:
            with self.subTest(size=size, overlap=overlap), self.assertRaises(ValueError):
                chunk_documents(fixture()["documents"], size, overlap)

    def test_ranking_ties_no_zero_scores_and_k_cap(self):
        chunks = chunk_documents(fixture()["documents"], 10, 0)
        for method in ("tfidf", "bm25"):
            hits = rank(chunks, "green", method, 999)
            self.assertEqual(len(hits), 2)
            self.assertEqual(rank(chunks, "absent", method, 1), [])
            self.assertEqual(rank(chunks, "", method, 1), [])
            tie = copy.deepcopy(chunks)
            tie[1]["text"] = tie[0]["text"]
            self.assertEqual([h["id"] for h in rank(tie[::-1], "red", method, 2)],
                             sorted(c["id"] for c in tie))
        for k in (0, -1, True):
            with self.assertRaises(ValueError):
                rank(chunks, "green", "tfidf", k)

    def test_tfidf_cosine_hand_calculation(self):
        chunks = chunk_documents(fixture()["documents"], 10, 0)
        hits = rank(chunks, "red", "tfidf", 2)
        rare = math.log(3 / 2) + 1
        expected = rare / math.sqrt(2 * rare ** 2 + 1)
        self.assertAlmostEqual(hits[0]["score"], expected)

    def test_bm25_hand_calculation(self):
        chunks = chunk_documents(fixture()["documents"], 10, 0)
        hits = rank(chunks, "red", "bm25", 2)
        expected = math.log(2) * 2.5 / (1 + 1.5 * (0.25 + 0.75 * 3 / 2.5))
        self.assertAlmostEqual(hits[0]["score"], expected)

    def test_valid_data(self):
        validate_dataset(fixture())

    def test_invalid_data(self):
        cases = []
        for key in ("documents", "questions"):
            data = fixture()
            data[key] = []
            cases.append(data)
            data = fixture()
            data[key].append(copy.deepcopy(data[key][0]))
            cases.append(data)
        for doc in ({"id": "c", "text": " RED  green BLUE "},
                    {"id": "c", "text": "!!!"}):
            data = fixture()
            data["documents"].append(doc)
            cases.append(data)
        for evidence in ([{"doc_id": "missing", "quote": "red"}],
                         [{"doc_id": "a", "quote": "absent"}],
                         [{"doc_id": "a", "quote": ""}]):
            data = fixture()
            data["questions"][0]["evidence"] = evidence
            cases.append(data)
        data = fixture()
        data["questions"][0]["split"] = "train"
        cases.append(data)
        data = fixture()
        data["documents"][0]["text"] = "red red"
        cases.append(data)
        for data in cases:
            with self.subTest(data=data), self.assertRaises(ValueError):
                validate_dataset(data)


if __name__ == "__main__":
    unittest.main()
