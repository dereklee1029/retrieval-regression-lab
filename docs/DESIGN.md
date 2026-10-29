# Retrieval Regression Lab: design

An educational, CPU-only Python CLI for comparing lexical retrieval changes on
original synthetic operational documentation. No APIs, keys, models, network
calls, external datasets, telemetry, hosting, or runtime dependencies.

## Decisions

Use standard-library TF-IDF cosine and BM25 rather than embedding downloads or a
service: inspectable formulas, easy setup, deterministic output. Word-window
chunking uses Unicode token offsets into the original text. Labels identify a
document and an exact, unique evidence quote; a hit must contain the complete
quote. Chunk IDs are diagnostic only. Recall measures recovered evidence labels;
MRR measures the first evidence-bearing chunk. Repeated overlapping hits count
once for recall but consume ranks. Unsupported questions are excluded from
Recall/MRR; their empty-result rate is reported separately, without implying
that lexical matches prove answerability.

Two fixed configurations compare TF-IDF/48 words/8 overlap against BM25/32/8.
Both return positive-score chunks only, with chunk ID ascending for ties. No
stemming, synonym expansion, stopword list, generative answers, tuning loop, or
production claims. k is a positive integer and capped by available chunks.

Dataset: 12 fictional runbooks, 40 manually authored question records, immutable
dev/test assignments (20 each). Questions and evidence quotes remain readable
JSON. Validate the entire dataset before evaluating either split. Duplicate IDs,
duplicate normalized document bodies, absent references, ambiguous quotes, bad
types, and empty/tokenless text are errors. Different IDs cannot hide duplicates.

Reports include all query rankings, evidence coverage, failures, delta categories,
canonical SHA-256 dataset/config hashes, implementation version and runtime.
No timestamps or timings so repeated reports on one runtime are byte-identical.
Platform metadata may differ across machines. Dev results inform discussion;
test is run once with frozen configurations and never used to select settings.

## Non-goals and limits

This is retrieval evaluation, not full RAG, hallucination detection, calibrated
abstention, a real-world benchmark, or enterprise deployment. Tiny synthetic
data and lexical overlap can produce inflated results. English-oriented word
tokenization recognizes Unicode words but is not language-aware segmentation.
Untrusted JSON is validated, not executed. Small in-memory corpus only.
