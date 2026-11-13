# Troubleshoot evidence labels

Evidence quotes are anchors into the original document text. Search token
normalization does not change these anchors. This guide describes the current
validator in [rrlab/core.py](../rrlab/core.py); it does not relax validation or
change retrieval scores.

## Copy an exact, unique substring

Consider this synthetic document:

```json
{"id": "queue", "text": "Restart the worker. Verify the queue."}
```

This evidence item preserves the original case and punctuation and occurs once:

```json
{"doc_id": "queue", "quote": "Verify the queue."}
```

The following replacements are rejected for that document:

| Replacement quote | Why |
| --- | --- |
| `verify the queue.` | Case differs from the source |
| `Verify  the queue.` | An extra space changes the substring |
| `Verify the queue!` | Punctuation differs from the source |

Copy from the stored document, rather than retyping, paraphrasing, or copying a
normalized search token. Unicode characters must also match: visually similar
text can contain different code points. Do not normalize or edit a source
silently to make a label pass; if changing the corpus is intentional, version
the data and review the affected labels.

## Count overlapping occurrences

For source text `aaaa`, quote `aaa` starts at offsets 0 and 1. The validator
rejects it because both occurrences count, including overlaps.

A quote can also repeat in ordinary prose. For example, `Retry later.` occurs
twice in `Retry later. Retry later.`. Choose enough surrounding original text
to identify the intended passage uniquely. Keep the quote no longer than needed
to express the evidence: extending it across a chunk boundary can affect coverage.
Do not shorten it until it stops expressing the evidence required by the question.

## Match the error to the record

Validation checks the entire dataset before selecting a split. An invalid test
label can therefore stop a dev run. Fix the source/label inconsistency without
using held-out retrieval results to tune the configuration.

| Error fragment | Inspect |
| --- | --- |
| `evidence references missing document` | The item's `doc_id` and the document IDs |
| `expected nonempty word-bearing string` | The quote's type, emptiness, and word-bearing content |
| `evidence quote must occur exactly once` | Exact characters and all occurrences in the referenced document |
| `duplicate evidence` | Repeated identical `(doc_id, quote)` items within one question |

An empty `evidence` list declares the question unsupported by the selected
corpus. It is not a workaround for a rejected quote. Review that assertion
against the documents.

## Separate label validity from retrieval coverage

A valid quote can still span a chunk boundary and disappear from the retrieved
windows. Preserve the label and inspect the hit offsets; see the
[demo's report walkthrough](DEMO.md#read-the-report-and-decide-what-to-do).
Validation establishes a consistent exact anchor, not that the source supports
the answer, that the label is complete, or that the ranker will retrieve it.

These examples are synthetic character-matching illustrations, not a benchmark
or a report of application performance.
