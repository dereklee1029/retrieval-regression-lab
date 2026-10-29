# Retrieval Regression Lab

A local check before changing an internal support knowledge search: **which
questions will lose the evidence needed to answer them?**

Suppose a support assistant searches runbooks for payment retries, database
timeouts and rollback procedures. You want to shorten its search chunks or
switch its lexical ranker. Run a small set of labeled support questions against
both settings first, then inspect exactly which answers lose source evidence.
Use the report to decide what to investigate before adopting the change.

Compare TF-IDF cosine and BM25 with configurable word-window chunking. Reports
retain every top-k chunk, evidence coverage, per-query changes and failures.
Labels point to source documents and exact evidence quotes, so re-chunking does
not require relabeling. It runs as an offline evaluation step alongside your
application; it does not connect to a live search service or generate answers.
The included runbooks are synthetic examples, not a customer deployment or a
production benchmark. Start with the [five-minute support-search demo](docs/DEMO.md).

## Run locally

Python 3.11+; tested on Python 3.12.14, Windows 10 x64. From this repository:

```console
python -m unittest discover -v
python -m rrlab --dataset data/fixture.json --split dev --output reports/my-dev
```

No installation or downloads are needed for these commands. Runtime uses only
the standard library: CPU only, no API keys, models, external datasets, network
calls, telemetry, accounts or paid services.

Optional installation into a virtual environment:

```console
python -m venv .venv
# Windows PowerShell:
.venv\Scripts\python -m pip install .
.venv\Scripts\rrlab --dataset data/fixture.json --split dev --output reports/my-dev
# macOS/Linux: use .venv/bin/python and .venv/bin/rrlab instead.
```

Installation may fetch the free setuptools/wheel build tools. Evaluation never
fetches anything. Data stays in the repository, not in the installed package;
pass an explicit dataset path from any working directory. No hosted CI is set up.

## Compare a change

```console
python -m rrlab --dataset data/fixture.json --split dev --output reports/chunk-change --baseline-method bm25 --baseline-size 48 --baseline-overlap 8 --candidate-method bm25 --candidate-size 32 --candidate-overlap 8 --k 3
```

The output stem produces `.json` (machine-readable, full rankings) and `.md`
(human-readable summary). Existing output reports are replaced. A dataset cannot
also be an output path. Errors explain invalid data/options and exit with code 2.
The tool validates the entire dataset, even when running only one split.

Start with `regression` and `mixed` rows in the Markdown report, then open those
question IDs in the JSON. A lower recall means some labeled evidence disappeared;
lower reciprocal rank means the first useful evidence moved down or disappeared.
Check the source quote against the returned chunk offsets. A boundary problem
calls for a chunking experiment; the wrong source calls for examining lexical
overlap and ranking. Keep failed questions in the evaluation set rather than
rewriting labels to improve the score. See the [report walkthrough](docs/DEMO.md#read-the-report-and-decide-what-to-do).

The checked-in comparison deliberately changes **both** scoring and chunk size:
TF-IDF/48/8 versus BM25/32/8 at k=3. It demonstrates regression reporting, not
causal attribution to BM25. To isolate chunking or scoring, change one variable
at a time on dev. These defaults were fixed before held-out evaluation; no
parameter sweep or test-driven score selection was performed.

## How evaluation works

- Chunk windows preserve original character offsets and text. Sizes count
  Unicode `\w+` tokens; `0 <= overlap < size`. Chunks exclude leading/trailing
  non-word characters. An evidence quote crossing a boundary may not fit any
  chunk: that is an exposed retrieval failure, not a relabeling opportunity.
- Search tokens use NFKC and case folding. Exact evidence matching uses the
  original case and characters. No stemming, stopwords or multilingual segmenter.
- Only positive lexical scores are returned. Exact score ties use chunk ID order.
  k must be a positive integer; values exceeding the chunk count are capped.
- **Recall@k** is the fraction of a question's labeled evidence items fully
  contained in its top-k chunks. Repeated coverage of one item counts once.
  **MRR@k** averages `1 / first relevant chunk rank`, or zero for no hit.
  Both are macro-averages over answerable questions; MRR needs only one piece
  of evidence and does not imply that all required evidence was recovered.
- Unsupported questions have an empty evidence list. Their Recall/MRR is null
  and excluded from those averages. `unsupported_empty_rate` is the fraction
  receiving no positive-score chunks. A lexical hit is not proof of support;
  this baseline does not provide calibrated abstention or hallucination detection.
- A negative metric delta is a regression, a positive delta an improvement;
  opposing recall/RR signs are `mixed`. Unsupported rows are labeled separately.

Exact scoring formulas are documented in [`rrlab/core.py`](rrlab/core.py).
TF-IDF uses raw counts, smoothed IDF and cosine similarity; out-of-vocabulary
query terms are discarded. BM25 uses k1=1.5, b=0.75 and unique query terms.

## Data and reports

[`data/fixture.json`](data/fixture.json) contains 12 original fictional runbooks
and 40 manually authored questions: 20 dev and 20 held-out test, with four
unsupported questions per split. Most labels contain one quote; one question
per split requires two documents. All names, thresholds and operational policies
are invented. No customer data or actual work history is represented.

The fixture has strong lexical overlap and is much too small to establish
general retrieval quality. The split is by question, not by document, and the
same corpus is indexed for both splits. Labels were authored alongside the
documents; held-out means untouched by configuration selection, not an external
blind benchmark. See [`docs/RESULTS.md`](docs/RESULTS.md) for measured results
and [`docs/CONFIG_FREEZE.md`](docs/CONFIG_FREEZE.md) for the frozen comparison.

To add data, preserve the documents/questions schema shown in the fixture.
Evidence is `{ "doc_id": "source-id", "quote": "unique original text" }`.
IDs must be unique ASCII letters/digits/underscore/hyphen per record collection.
Empty/tokenless inputs, duplicate normalized document bodies, duplicate evidence,
missing references and non-unique/missing quotes are rejected. New fixture
versions change the canonical dataset hash. Inspect every unsupported label
manually; empty evidence is an author assertion, not an automated discovery.

## Try a small corpus of your own

1. Choose a small set of documents you are permitted to use. Start with public
   or sanitized support articles. Remove credentials, personal data and internal
   identifiers before creating a dataset. The CLI accepts JSON text, not arbitrary
   PDFs, web pages, or a live search index; extract/review text yourself.
2. Save the fixture schema as `local-data/support.json`. Use stable source IDs,
   write representative questions, and quote the exact evidence needed from each
   source. Include questions the selected corpus cannot answer. Have someone
   familiar with the documents review those labels.
3. Assign dev/test questions before trying settings. Use dev for experiments;
   freeze the configuration, then run test once for your decision. If questions
   repeat the same intent, keep them together to reduce leakage. For a stronger
   check, create a separate corpus version from new documents later.
4. Run locally and inspect the regressions:

```console
python -m rrlab --dataset local-data/support.json --split dev --output local-reports/support-dev
```

`local-data/` and `local-reports/` are git-ignored convenience locations. Ignoring
files is not access control: keep them on an appropriate local disk and inspect
what you share. Reports include questions, exact evidence quotes and retrieved
source text, so treat them with the same sensitivity as the documents. Hashes
are for reproducibility, not anonymization. Do not upload private data or its
reports to this public repository.

This evaluates the local lexical implementations and word windows in this repo.
If your application uses embeddings, different chunk boundaries, filters or
permissions, its rankings can differ; this report does not validate that live
pipeline. There is no automatic deployment gate or permission enforcement.

## Reproducibility and limits

```console
python -m rrlab --dataset data/fixture.json --split dev --output reports/repeat-a
python -m rrlab --dataset data/fixture.json --split dev --output reports/repeat-b
```

On one Python/platform, the two JSON and Markdown files should be byte-identical.
Reports have no clocks/timings. Runtime metadata can differ across platforms;
floating-point libraries may introduce tiny cross-platform score differences.
Canonical SHA-256 hashes cover the entire parsed dataset (including metadata)
and each config plus k. Key order/JSON whitespace do not affect hashes; list
order does. Algorithm constants belong to implementation version 0.1.0.

The implementation is intentionally small and recomputes the index per query;
it targets tiny in-memory fixtures rather than large-corpus throughput. It has
no statistical significance claims, answer generation, external relevance
judgments, calibrated thresholds, or deployment/security hardening. Report writes
are sequential, so an output I/O failure can leave only one of the two files.

Architecture and tradeoffs: [`docs/DESIGN.md`](docs/DESIGN.md).
Verification evidence: [`docs/VERIFICATION.md`](docs/VERIFICATION.md).

MIT licensed.
