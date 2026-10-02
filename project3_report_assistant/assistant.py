"""Explainable local document retrieval with paragraph-level citations."""
from __future__ import annotations

import argparse
import html
import json
import re
from pathlib import Path

TOKEN_RE = re.compile(r"[\w\u4e00-\u9fff]+", re.UNICODE)


def tokens(text: str) -> list[str]:
    """Return words plus Chinese bigrams so unsegmented questions still match."""
    result: list[str] = []
    for token in TOKEN_RE.findall(text):
        if not token.strip():
            continue
        if all("\u4e00" <= char <= "\u9fff" for char in token):
            result.extend(token[index:index + 2] for index in range(len(token) - 1))
        else:
            result.append(token.lower())
    return result


def paragraphs(path: Path) -> list[str]:
    blocks = [block.strip() for block in path.read_text(encoding="utf-8").split("\n\n")]
    return [block for block in blocks if block and not block.startswith("#")]


def search(query: str, docs_dir: Path, limit: int = 3) -> list[dict]:
    query_tokens = tokens(query)
    if not query_tokens:
        return []
    hits: list[dict] = []
    for path in sorted(docs_dir.glob("*.md")):
        for paragraph_number, text in enumerate(paragraphs(path), start=1):
            lower = text.lower()
            score = sum(lower.count(token) for token in query_tokens)
            if score:
                hits.append({"document": path.name, "paragraph": paragraph_number, "score": score, "text": text, "citation": f"{path.name}#p{paragraph_number}"})
    return sorted(hits, key=lambda item: (-item["score"], item["document"], item["paragraph"]))[:limit]


def answer(query: str, docs_dir: Path) -> dict:
    hits = search(query, docs_dir)
    if not hits:
        return {"query": query, "answer": "没有在资料中找到依据。", "citations": [], "hits": []}
    best_score = hits[0]["score"]
    hits = [hit for hit in hits if hit["score"] == best_score]
    cited = " ".join(f"{hit['text']} [{hit['citation']}]" for hit in hits)
    return {"query": query, "answer": cited, "citations": [hit["citation"] for hit in hits], "hits": hits}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("query")
    parser.add_argument("--docs", type=Path, default=Path(__file__).with_name("docs"))
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    result = answer(args.query, args.docs)
    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(result["answer"])
        if result["citations"]:
            print("引用：" + ", ".join(result["citations"]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


