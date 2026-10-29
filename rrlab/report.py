"""Canonical comparison reports; no timing or wall-clock fields."""

import hashlib
import json
import platform
import sys

from . import __version__
from .core import chunk_documents, evaluate_query, rank, validate_dataset


def canonical_hash(value):
    raw = json.dumps(value, ensure_ascii=False, sort_keys=True,
                     separators=(",", ":"), allow_nan=False).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def _run(data, questions, config, k):
    if not isinstance(config, dict) or set(config) != {"method", "size", "overlap"}:
        raise ValueError("config must contain exactly method, size, overlap")
    chunks = chunk_documents(data["documents"], config["size"], config["overlap"])
    rows = []
    for question in sorted(questions, key=lambda q: q["id"]):
        hits = rank(chunks, question["text"], config["method"], k)
        rows.append({"id": question["id"], "text": question["text"],
                     "evidence": question["evidence"], "hits": hits,
                     **evaluate_query(hits, question["evidence"])})
    answerable = [row for row in rows if row["evidence"]]
    unsupported = [row for row in rows if not row["evidence"]]
    def mean(group, field):
        return sum(row[field] for row in group) / len(group) if group else None
    return {"config": dict(config), "config_sha256": canonical_hash({**config, "k": k}),
            "chunks": len(chunks), "effective_k_cap": min(k, len(chunks)),
            "answerable_count": len(answerable), "unsupported_count": len(unsupported),
            "metrics": {"recall_at_k": mean(answerable, "recall"),
                        "mrr_at_k": mean(answerable, "rr"),
                        "unsupported_empty_rate": mean(unsupported, "empty_result")},
            "failures": [row["id"] for row in answerable if row["recall"] < 1],
            "unsupported_with_hits": [row["id"] for row in unsupported if row["hits"]],
            "queries": rows}


def compare(data, split, baseline, candidate, k):
    validate_dataset(data)
    if split not in ("dev", "test"):
        raise ValueError("split must be dev or test")
    questions = [q for q in data["questions"] if q["split"] == split]
    if not questions:
        raise ValueError(f"split {split} has no questions")
    runs = {"baseline": _run(data, questions, baseline, k),
            "candidate": _run(data, questions, candidate, k)}
    changes = []
    for old, new in zip(runs["baseline"]["queries"], runs["candidate"]["queries"]):
        if old["evidence"]:
            recall_delta, rr_delta = new["recall"] - old["recall"], new["rr"] - old["rr"]
            deltas = [recall_delta, rr_delta]
            label = ("mixed" if min(deltas) < 0 < max(deltas) else
                     "regression" if min(deltas) < 0 else
                     "improvement" if max(deltas) > 0 else "unchanged")
        else:
            recall_delta = rr_delta = None
            label = "unsupported"
        changes.append({"id": old["id"], "recall_delta": recall_delta,
                        "rr_delta": rr_delta, "classification": label,
                        "baseline_empty": old["empty_result"],
                        "candidate_empty": new["empty_result"]})
    return {"schema_version": 1, "implementation_version": __version__,
            "runtime": {"python": platform.python_version(),
                        "implementation": sys.implementation.name,
                        "platform": platform.platform()},
            "dataset_sha256": canonical_hash(data), "split": split, "k": k,
            "runs": runs, "comparison": changes}


def markdown_summary(report):
    lines = [f"# Retrieval comparison: {report['split']}", "",
             "Synthetic educational fixture; evidence recall, not answer quality.", "",
             f"Dataset SHA-256: `{report['dataset_sha256']}`", "",
             f"Python {report['runtime']['python']} / {report['runtime']['platform']}", "",
             f"Requested k: {report['k']}", "",
             "| Run | recall_at_k | mrr_at_k | unsupported_empty_rate | Chunks |",
             "| --- | ---: | ---: | ---: | ---: |"]
    for name, run in report["runs"].items():
        values = ["n/a" if value is None else f"{value:.4f}"
                  for value in run["metrics"].values()]
        lines.append(f"| {name} | {' | '.join(values)} | {run['chunks']} |")
    for name, run in report["runs"].items():
        lines += ["", f"## {name}", "",
                  f"Configuration: `{json.dumps(run['config'], sort_keys=True)}`",
                  f"Config + k SHA-256: `{run['config_sha256']}`", "",
                  f"Answerable: {run['answerable_count']}; unsupported: {run['unsupported_count']}.",
                  f"Incomplete evidence: {', '.join(run['failures']) or 'none'}.",
                  f"Unsupported with hits: {', '.join(run['unsupported_with_hits']) or 'none'}."]
    lines += ["", "## Per-query changes", "",
              "| Query | Classification | Recall delta | RR delta |",
              "| --- | --- | ---: | ---: |"]
    for row in report["comparison"]:
        values = ["n/a" if row[key] is None else f"{row[key]:+.4f}"
                  for key in ("recall_delta", "rr_delta")]
        lines.append(f"| {row['id']} | {row['classification']} | {' | '.join(values)} |")
    lines += ["", "See the adjacent JSON for questions, evidence, full top-k rankings,",
              "character offsets and scores. Unsupported empty-result rate only measures",
              "no positive lexical score; it is not a calibrated answerability detector.", ""]
    return "\n".join(lines)
