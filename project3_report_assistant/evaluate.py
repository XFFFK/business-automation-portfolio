"""Evaluate retrieval coverage on a fixed synthetic question set."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from assistant import answer


def evaluate(eval_path: Path, docs_dir: Path) -> dict:
    cases = json.loads(eval_path.read_text(encoding="utf-8"))
    results = []
    for case in cases:
        result = answer(case["query"], docs_dir)
        corpus = result["answer"]
        passed = all(term in corpus for term in case["expected"])
        results.append({"query": case["query"], "passed": passed, "citations": result["citations"]})
    passed_count = sum(item["passed"] for item in results)
    return {"cases": len(results), "passed": passed_count, "hit_rate": passed_count / len(results) if results else 0, "results": results}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--evals", type=Path, default=Path(__file__).with_name("evals.json"))
    parser.add_argument("--docs", type=Path, default=Path(__file__).with_name("docs"))
    args = parser.parse_args()
    print(json.dumps(evaluate(args.evals, args.docs), ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
