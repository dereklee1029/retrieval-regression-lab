"""CLI entry point; all input and output paths are explicit."""

import argparse
import json
from pathlib import Path

from .report import compare, markdown_summary


def main(argv=None):
    parser = argparse.ArgumentParser(description="Compare two offline lexical retrieval configurations.")
    parser.add_argument("--dataset", type=Path, required=True)
    parser.add_argument("--split", choices=("dev", "test"), default="dev")
    parser.add_argument("--output", type=Path, required=True, help="output stem for .json and .md")
    parser.add_argument("--k", type=int, default=3)
    for name, method, size in (("baseline", "tfidf", 48), ("candidate", "bm25", 32)):
        parser.add_argument(f"--{name}-method", choices=("tfidf", "bm25"), default=method)
        parser.add_argument(f"--{name}-size", type=int, default=size)
        parser.add_argument(f"--{name}-overlap", type=int, default=8)
    args = parser.parse_args(argv)
    try:
        targets = [args.output.with_suffix(ext) for ext in (".json", ".md")]
        if any(path.resolve() == args.dataset.resolve() for path in targets):
            raise ValueError("output must not overwrite the input dataset")
        with args.dataset.open(encoding="utf-8") as handle:
            data = json.load(handle)
        configs = [{key: getattr(args, f"{name}_{key}")
                    for key in ("method", "size", "overlap")}
                   for name in ("baseline", "candidate")]
        report = compare(data, args.split, *configs, args.k)
        # Serialize before touching output so validation/serialization errors leave no report.
        payloads = [json.dumps(report, indent=2, ensure_ascii=False, allow_nan=False) + "\n",
                    markdown_summary(report)]
        args.output.parent.mkdir(parents=True, exist_ok=True)
        for path, payload in zip(targets, payloads):
            path.write_text(payload, encoding="utf-8", newline="\n")
        print(f"Wrote {targets[0]} and {targets[1]}")
    except (OSError, ValueError, TypeError, RecursionError) as error:
        parser.error(str(error))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
