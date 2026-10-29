# Retrieval Regression Lab Implementation Plan

**Goal:** ship a reproducible offline retrieval comparison with honest failures.
**Architecture:** validated JSON -> offset-preserving chunks -> lexical ranker ->
evidence metrics -> JSON/Markdown report.
**Tech stack:** Python 3.11+, standard library; setuptools for optional install.
**Spec:** [DESIGN.md](DESIGN.md).

## Constraints and review focus

No costs, downloads at runtime, keys, private data, or network functionality.
Review empty inputs, Unicode offsets, overlap boundaries, label references,
ranking ties, invalid k, unsupported-question semantics, and reproducibility.

## Tasks (execute inline)

- [x] 1. Write `tests/test_core.py` for hand-computed metrics, chunks, validation,
  and ranking. Run red; implement `rrlab/core.py`; run green and commit.
- [x] 2. Author `data/fixture.json` with 12 synthetic docs and 40 fixed dev/test
  questions. Write CLI/report tests red; implement `rrlab/__main__.py` and
  `rrlab/report.py` with explicit split/output paths and canonical hashes.
  Validate data; run all tests; commit.
- [x] 3. Add README, license, reproducibility notes and actual reports. Install
  into clean venv, run tests and CLI smoke. Repeat reports and compare bytes.
  Freeze choices on dev before executing test. Commit.
- [x] 4. Fresh independent reviewer inspects code/data/docs and runs checks.
  Reproduce important findings as red tests, fix once, rerun aggregate suite.
  Verify clean git commit and hand off publication if repo creation unavailable.
