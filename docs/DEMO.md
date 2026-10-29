# Five-minute demo: check a support-search change

**Scenario:** a support assistant searches internal runbooks before drafting a
reply. You are considering a retrieval change. Before connecting any generator,
check whether the new settings still retrieve the evidence required by known
support questions. This demo uses invented runbooks and runs entirely locally.

## Run the checked-in example

From the repository root, with Python 3.11+:

```console
python -m rrlab --dataset data/fixture.json --split dev --output .scratch/support-demo
```

Open `.scratch/support-demo.md` for the summary and `.scratch/support-demo.json`
for the full evidence and rankings. The default comparison uses TF-IDF/48-word
windows against BM25/32-word windows, both with overlap 8 and k=3. These change
two things at once; use it to learn the report, not to attribute a cause.

## Read the report and decide what to do

The measured dev result has five regressing questions and one improving question.
The candidate's Recall@3 is .7500 versus .8750 for the baseline. Do not adopt
the candidate solely because its ranker or smaller chunks sound preferable.

| Report signal | Inspect in the JSON | Practical next step |
| --- | --- | --- |
| `regression` / negative `recall_delta` | Question's `evidence`, `covered_evidence`, and `hits` in both runs | Identify which required quote disappeared; investigate before adopting the change |
| Negative `rr_delta` with unchanged recall | First chunk containing an evidence quote | Check why irrelevant chunks moved ahead; keep this question as a regression case |
| Correct source document but missing quote | Hit `start`, `end`, and `text` versus the full evidence quote | Try a boundary/overlap change on dev without changing the label |
| `mixed` | Both recall and RR deltas | Decide whether full evidence coverage or early ranking matters for this workflow |
| Unsupported question with hits | `unsupported_with_hits` and returned source text | Plan an answerability check in the application; a nonzero lexical score is insufficient |

For a concrete boundary example, locate `dev-13`: “What happens if overlapping
chunks contain the same evidence?” Its quote occupies source characters
`[245,329)` in `retrieval-labels`. The baseline retrieves the right document
first, but its windows split that quote. The candidate retrieves a window that
contains the whole quote. This individual improvement is retained even though
the candidate loses overall. [Measured results](RESULTS.md) show the exact windows.

`dev-08`, the canary rollback question, regresses under the candidate. Inspect
that row as well: one attractive example cannot establish an overall win.
For multi-document questions, inspect every evidence item; MRR only checks the
first useful result and can hide incomplete coverage.

## Isolate one change

Hold BM25 constant and compare only chunk size on dev:

```console
python -m rrlab --dataset data/fixture.json --split dev --output .scratch/chunk-only --baseline-method bm25 --baseline-size 48 --baseline-overlap 8 --candidate-method bm25 --candidate-size 32 --candidate-overlap 8 --k 3
```

This command is an additional experiment, not the frozen checked-in comparison.
Use the generated report for its actual results; no winning outcome is assumed.
For your own corpus, keep the same baseline while testing a single candidate,
review important failures, then freeze settings before the held-out run.
The tool reports changes; your application's acceptance criteria remain yours.

## Move from the demo to your documents

Follow [the local-corpus steps](../README.md#try-a-small-corpus-of-your-own).
A dataset is a JSON object with `documents` and `questions`; source evidence is
an exact, unique quote, not a chunk ID. For example, this small synthetic input
is valid for a dev-only smoke check:

```json
{
  "documents": [
    {"id": "support-retries", "text": "Reuse the checkout idempotency key after a timeout. Query payment status before retrying."}
  ],
  "questions": [
    {
      "id": "dev-retry", "split": "dev",
      "text": "What should happen before retrying a payment?",
      "evidence": [
        {"doc_id": "support-retries", "quote": "Query payment status before retrying"}
      ]
    },
    {
      "id": "dev-region", "split": "dev",
      "text": "Which region hosts the payment service?",
      "evidence": []
    }
  ]
}
```

Add enough representative questions and a preassigned test partition before
using a real evaluation for decisions. This tiny example is only a schema demo.
Do not put secrets or private support content into the public repository;
the output repeats source text. Local execution alone does not anonymize data.

This is a practical inspection tool, with no claim that it matches a deployed
search system, generates correct answers, or is ready for enterprise deployment.
