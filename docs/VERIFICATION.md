# Verification record

Environment: CPython 3.12.14, Windows 10 x64 build 19045. Runtime dependencies:
none. No hosted CI or external service is required.

## Commands and outcomes

1. `python -m unittest discover -v`: **16 tests passed**.
   Core tests cover hand-computed TF-IDF and BM25 scores, hand-computed evidence
   recall/RR, overlap deduplication, partial evidence, unsupported null metrics,
   Unicode offsets/tails, invalid window options, positive-only ranking, ties,
   k bounds, duplicate documents/IDs, missing/ambiguous quotes and labels.
   Report/CLI tests cover canonical hashes, deterministic comparisons, failures,
   missing/invalid files, absent split, bad options, output/input collisions and
   fixed fixture partition counts.
2. Built a wheel using the preinstalled free build tools without network:
   `python -m pip wheel . --no-build-isolation --no-deps --no-index --wheel-dir .scratch/wheels`.
   Build succeeded.
3. Created a clean venv with `python -m venv .venv` (no system site packages).
   Installed the wheel using `--no-index --no-deps`; installation succeeded.
   `.venv\Scripts\python -m unittest discover -v`: **16 tests passed**.
4. From outside the repository, invoked the installed `rrlab` entry point with
   absolute dataset/output paths. It generated both reports. An import check
   confirmed the package came from the venv's `site-packages`, not source.
5. Ran dev and test reports twice from separate CLI processes. JSON and Markdown
   pairs were byte-identical. Reports omit timing fields, so no exclusions were
   necessary. Hashes below are file-byte hashes, distinct from canonical hashes
   embedded inside the reports.

| Artifact | SHA-256 |
| --- | --- |
| dev.json | `70cbfecf7d5bd0d3d5d83f6dc2d5087c4b1c627c642e3133d241ff4866946f65` |
| dev.md | `7cead05b4047aecefe2b4edf55e1365eb86f8b10d6c6dd6dae2817787a6917d7` |
| test.json | `77203c8305c201632959c83b685c26cff56db95e8f1897fd7c5e766001792c82` |
| test.md | `92c870fd94421f35364b12e1ade5f6aeb8a3b3a356b32882895693820e48db41` |

## Independent review

A fresh reviewer read code, tests, labels and documentation and ran the suite.
No implementation defect was found. Additional probes checked 28 Unicode/window/
overlap combinations, invalid k and empty datasets. Four different Python hash
seeds produced identical reports. Both stored JSON and Markdown reports matched
fresh reconstruction. Review noted pending results/verification documentation,
untracked reports and plan checkboxes; all were completed before handoff.

The final English-only example-token edit was followed by another full 16-test
run and two CLI runs per split. Both file pairs matched byte-for-byte. The
editorial change and unchanged evaluation choices are recorded in CONFIG_FREEZE.

No speed, memory, external benchmark, Linux/macOS, or production deployment
validation was performed. The fixture and tests do not establish general ranking
quality or validate every possible malformed input.
