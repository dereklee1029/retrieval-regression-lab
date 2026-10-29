# Retrieval comparison: dev

Synthetic educational fixture; evidence recall, not answer quality.

Dataset SHA-256: `e7450b13c9792bdad14edc1e0e509bf1b377e4d1b60ec01c435860a5f5ac1af2`

Python 3.12.14 / Windows-10-10.0.19045-SP0

Requested k: 3

| Run | recall_at_k | mrr_at_k | unsupported_empty_rate | Chunks |
| --- | ---: | ---: | ---: | ---: |
| baseline | 0.8750 | 0.8438 | 0.0000 | 36 |
| candidate | 0.7500 | 0.6875 | 0.0000 | 48 |

## baseline

Configuration: `{"method": "tfidf", "overlap": 8, "size": 48}`
Config + k SHA-256: `3ef59155df499acf9538a6d57c9ea359a90e3e1f8da7f030c6e79d4d413532a7`

Answerable: 16; unsupported: 4.
Incomplete evidence: dev-09, dev-13.
Unsupported with hits: dev-17, dev-18, dev-19, dev-20.

## candidate

Configuration: `{"method": "bm25", "overlap": 8, "size": 32}`
Config + k SHA-256: `d5782ed885bd17bf27b08c84c20bc5e3ea1d7061ba3a41c5c050ae9704069d3b`

Answerable: 16; unsupported: 4.
Incomplete evidence: dev-08, dev-09, dev-10, dev-16.
Unsupported with hits: dev-17, dev-18, dev-19, dev-20.

## Per-query changes

| Query | Classification | Recall delta | RR delta |
| --- | --- | ---: | ---: |
| dev-01 | unchanged | +0.0000 | +0.0000 |
| dev-02 | regression | +0.0000 | -0.5000 |
| dev-03 | unchanged | +0.0000 | +0.0000 |
| dev-04 | regression | +0.0000 | -0.5000 |
| dev-05 | unchanged | +0.0000 | +0.0000 |
| dev-06 | unchanged | +0.0000 | +0.0000 |
| dev-07 | unchanged | +0.0000 | +0.0000 |
| dev-08 | regression | -1.0000 | -1.0000 |
| dev-09 | unchanged | +0.0000 | +0.0000 |
| dev-10 | regression | -1.0000 | -0.5000 |
| dev-11 | unchanged | +0.0000 | +0.0000 |
| dev-12 | unchanged | +0.0000 | +0.0000 |
| dev-13 | improvement | +1.0000 | +1.0000 |
| dev-14 | unchanged | +0.0000 | +0.0000 |
| dev-15 | unchanged | +0.0000 | +0.0000 |
| dev-16 | regression | -1.0000 | -1.0000 |
| dev-17 | unsupported | n/a | n/a |
| dev-18 | unsupported | n/a | n/a |
| dev-19 | unsupported | n/a | n/a |
| dev-20 | unsupported | n/a | n/a |

See the adjacent JSON for questions, evidence, full top-k rankings,
character offsets and scores. Unsupported empty-result rate only measures
no positive lexical score; it is not a calibrated answerability detector.
