# Frozen comparison

Recorded after the initial dev run and before held-out rankings were evaluated.

- Dataset canonical SHA-256 at the original freeze:
  `431de9730cfd581785561f58a91562eba0b6868c9a48253e9b01f3a822dd7ed8`
- Baseline: TF-IDF cosine, size 48 words, overlap 8, k=3.
- Candidate: BM25 (k1=1.5, b=.75), size 32 words, overlap 8, k=3.
- Dev: baseline Recall@3 .8750 / MRR@3 .84375; candidate .7500 / .6875.
- Both configurations returned hits on all four unsupported dev questions.

Decision: keep both original configurations for the demonstration. The candidate
regressed; do not replace it to manufacture a win. Baseline would be preferred
on dev if a choice were necessary. No tuning or parameter sweep was performed.
Run test with these exact settings. Test results must not change this choice.
The same documents are available to both splits; this is question-held-out only.

The comparison changes both scoring and chunking; it cannot isolate which
change causes a difference. One-variable experiments are future dev work.

## English-only editorial update

After the original evaluation, the unlabelled non-English example token in the
normalization document was replaced with the accented English word `naïve`.
No question, evidence label, split or configuration changed. Both splits were
rerun for the release; all aggregate metrics and per-query classifications are
unchanged. This editorial update was not chosen to improve retrieval scores.
The released dataset canonical SHA-256 is:
`e7450b13c9792bdad14edc1e0e509bf1b377e4d1b60ec01c435860a5f5ac1af2`.
