"""Generate a small, explainable data-quality report from an order CSV."""
from __future__ import annotations

import argparse
import csv
import html
import json
from collections import Counter
from datetime import date
from pathlib import Path

REQUIRED = ("order_id", "customer_id", "amount", "status", "created_at")
VALID_STATUS = {"pending", "paid", "refunded", "cancelled"}


def inspect_rows(rows: list[dict[str, str]]) -> dict:
    issues: list[dict] = []
    seen: Counter[str] = Counter()
    for row_number, row in enumerate(rows, start=2):
        order_id = row.get("order_id", "").strip()
        if order_id:
            seen[order_id] += 1
        for field in REQUIRED:
            if not row.get(field, "").strip():
                issues.append({"row": row_number, "type": "missing", "field": field, "detail": "required value is empty"})
        raw_amount = row.get("amount", "").strip()
        if raw_amount:
            try:
                if float(raw_amount) < 0:
                    issues.append({"row": row_number, "type": "negative_amount", "field": "amount", "detail": raw_amount})
            except ValueError:
                issues.append({"row": row_number, "type": "invalid_number", "field": "amount", "detail": raw_amount})
        status = row.get("status", "").strip()
        if status and status not in VALID_STATUS:
            issues.append({"row": row_number, "type": "invalid_status", "field": "status", "detail": status})
        raw_date = row.get("created_at", "").strip()
        if raw_date:
            try:
                date.fromisoformat(raw_date)
            except ValueError:
                issues.append({"row": row_number, "type": "invalid_date", "field": "created_at", "detail": raw_date})
    for order_id, count in seen.items():
        if count > 1:
            issues.append({"row": "multiple", "type": "duplicate_id", "field": "order_id", "detail": f"{order_id} appears {count} times"})
    by_type = Counter(issue["type"] for issue in issues)
    return {"rows": len(rows), "issue_count": len(issues), "issue_types": dict(sorted(by_type.items())), "issues": issues}


def load_report(path: Path) -> dict:
    with path.open(newline="", encoding="utf-8-sig") as handle:
        return inspect_rows(list(csv.DictReader(handle)))


def render_html(report: dict, source_name: str) -> str:
    cards = "".join(f"<li><strong>{html.escape(kind)}</strong>: {count}</li>" for kind, count in report["issue_types"].items()) or "<li>No issues found</li>"
    rows = "".join(
        f"<tr><td>{html.escape(str(item['row']))}</td><td>{html.escape(item['type'])}</td><td>{html.escape(item['field'])}</td><td>{html.escape(item['detail'])}</td></tr>"
        for item in report["issues"]
    )
    return f"""<!doctype html><meta charset='utf-8'><title>Data quality report</title>
<style>body{{font:16px system-ui;max-width:960px;margin:40px auto;color:#24313d}}.cards{{display:flex;gap:16px}}.card{{padding:16px;background:#eef5f2;border-radius:10px}}table{{border-collapse:collapse;width:100%}}td,th{{padding:8px;border-bottom:1px solid #ddd;text-align:left}}code{{background:#f2f2f2;padding:2px 4px}}</style>
<h1>Order data quality report</h1><p>Source: <code>{html.escape(source_name)}</code></p>
<div class='cards'><div class='card'><b>{report['rows']}</b><br>rows checked</div><div class='card'><b>{report['issue_count']}</b><br>issues found</div></div>
<h2>Issue summary</h2><ul>{cards}</ul><h2>Details</h2><table><tr><th>Row</th><th>Type</th><th>Field</th><th>Detail</th></tr>{rows}</table>"""


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path)
    parser.add_argument("--output", type=Path, default=Path("quality-report.html"))
    parser.add_argument("--json", type=Path, help="also write machine-readable JSON")
    args = parser.parse_args()
    report = load_report(args.input)
    args.output.write_text(render_html(report, args.input.name), encoding="utf-8")
    if args.json:
        args.json.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({k: report[k] for k in ("rows", "issue_count", "issue_types")}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
