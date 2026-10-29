# Retrieval comparison: test

Synthetic educational fixture; evidence recall, not answer quality.

Dataset SHA-256: `e7450b13c9792bdad14edc1e0e509bf1b377e4d1b60ec01c435860a5f5ac1af2`

Python 3.12.14 / Windows-10-10.0.19045-SP0

Requested k: 3

| Run | recall_at_k | mrr_at_k | unsupported_empty_rate | Chunks |
| --- | ---: | ---: | ---: | ---: |
| baseline | 0.9688 | 0.8750 | 0.0000 | 36 |
| candidate | 0.8750 | 0.7500 | 0.0000 | 48 |

## baseline

Configuration: `{"method": "tfidf", "overlap": 8, "size": 48}`
Config + k SHA-256: `3ef59155df499acf9538a6d57c9ea359a90e3e1f8da7f030c6e79d4d413532a7`

Answerable: 16; unsupported: 4.
Incomplete evidence: test-15.
Unsupported with hits: test-17, test-18, test-19, test-20.

## candidate

Configuration: `{"method": "bm25", "overlap": 8, "size": 32}`
Config + k SHA-256: `d5782ed885bd17bf27b08c84c20bc5e3ea1d7061ba3a41c5c050ae9704069d3b`

Answerable: 16; unsupported: 4.
Incomplete evidence: test-04, test-15.
Unsupported with hits: test-17, test-18, test-19, test-20.

## Per-query changes

| Query | Classification | Recall delta | RR delta |
| --- | --- | ---: | ---: |
| test-01 | unchanged | +0.0000 | +0.0000 |
| test-02 | unchanged | +0.0000 | +0.0000 |
| test-03 | unchanged | +0.0000 | +0.0000 |
| test-04 | regression | -1.0000 | -1.0000 |
| test-05 | unchanged | +0.0000 | +0.0000 |
| test-06 | regression | +0.0000 | -0.5000 |
| test-07 | improvement | +0.0000 | +0.1667 |
| test-08 | unchanged | +0.0000 | +0.0000 |
| test-09 | unchanged | +0.0000 | +0.0000 |
| test-10 | unchanged | +0.0000 | +0.0000 |
| test-11 | regression | +0.0000 | -0.5000 |
| test-12 | unchanged | +0.0000 | +0.0000 |
| test-13 | unchanged | +0.0000 | +0.0000 |
| test-14 | unchanged | +0.0000 | +0.0000 |
| test-15 | regression | -0.5000 | -0.3333 |
| test-16 | improvement | +0.0000 | +0.1667 |
| test-17 | unsupported | n/a | n/a |
| test-18 | unsupported | n/a | n/a |
| test-19 | unsupported | n/a | n/a |
| test-20 | unsupported | n/a | n/a |

See the adjacent JSON for questions, evidence, full top-k rankings,
character offsets and scores. Unsupported empty-result rate only measures
no positive lexical score; it is not a calibrated answerability detector.
