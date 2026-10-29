# Measured results

These are actual CLI runs on Python 3.12.14, CPython, Windows 10 build 19045.
They measure retrieval on a tiny synthetic fixture, not production performance.
There are 16 answerable and four unsupported questions per split. Requested k=3.

| Split | Configuration | Recall@3 | MRR@3 | Unsupported empty rate |
| --- | --- | ---: | ---: | ---: |
| dev | TF-IDF, size 48, overlap 8 | 0.87500 | 0.84375 | 0.00000 |
| dev | BM25, size 32, overlap 8 | 0.75000 | 0.68750 | 0.00000 |
| test | TF-IDF, size 48, overlap 8 | 0.96875 | 0.87500 | 0.00000 |
| test | BM25, size 32, overlap 8 | 0.87500 | 0.75000 | 0.00000 |

The 48-word configuration produces 36 chunks; the 32-word configuration produces
48. Dev has five regressing questions, one improving question and ten unchanged
answerable questions. Test has four regressing, two improving and ten unchanged
answerable questions. Four unsupported rows per split are classified separately.
Regressions include a decrease in either recall or reciprocal rank.

## What the failures show

1. **Chunk boundaries can matter more than finding the right document.** For
   `dev-13`, the evidence quote spans source characters `[245,329)` in
   `retrieval-labels`. The 48-word windows are `[0,318)`, `[274,579)`,
   `[541,684)`: none contains the complete quote, even though the first-ranked
   baseline chunk comes from the correct document. The candidate's `[178,370)`
   window contains it and ranks first. Labels stay unchanged across both runs.
2. **A configuration change can honestly regress.** The candidate has lower
   aggregate Recall@3 and MRR@3 on both splits. This experiment changes scoring
   and window size together, so it cannot attribute the decline to BM25 or
   smaller chunks individually. No settings were replaced after seeing test.
3. **Positive lexical scores do not establish answerability.** Every unsupported
   question receives hits from both configurations, yielding empty-result rate
   zero. The corpus shares words such as backup, payment and deployment with
   those questions, but contains none of their requested evidence. There is
   no claim of hallucination detection or successful abstention.

`test-15` requires two documents. Baseline retrieves one of its two evidence
items (recall .5); candidate retrieves neither. MRR and evidence recall expose
different aspects of this failure. Inspect the JSON instead of inferring answer
quality from an aggregate number.

Raw artifacts: [dev JSON](../reports/dev.json), [dev summary](../reports/dev.md),
[test JSON](../reports/test.json), [test summary](../reports/test.md).
Frozen pre-test decision: [CONFIG_FREEZE.md](CONFIG_FREEZE.md).

## Reproduce

```console
python -m rrlab --dataset data/fixture.json --split dev --output reports/dev
python -m rrlab --dataset data/fixture.json --split test --output reports/test
```

Test reruns are reproducibility checks of already-frozen settings, not new
selection trials. Different Python/platform metadata changes report bytes;
compare metric/query content separately for cross-platform runs. Never use this
small question-held-out result to claim broad benchmark superiority.
