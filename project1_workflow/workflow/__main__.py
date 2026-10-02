"""Command-line entry point for ``python -m workflow``."""

from __future__ import annotations

import argparse
import csv
from datetime import date, datetime, timezone
from pathlib import Path

from .core import load_tasks, process_tasks, write_outputs


DEMO_ROWS = [
    {"id": "OPS-001", "title": "修复客户导入失败记录", "owner": "Lin", "due_date": "2026-10-01", "status": "open", "impact": "high"},
    {"id": "OPS-002", "title": "整理本周销售回访", "owner": "Mina", "due_date": "2026-10-04", "status": "in_progress", "impact": "medium"},
    {"id": "OPS-003", "title": "确认新员工账号权限", "owner": "Kai", "due_date": "2026-10-10", "status": "blocked", "impact": "medium"},
    {"id": "OPS-004", "title": "归档已完成合同", "owner": "Lin", "due_date": "2026-09-29", "status": "done", "impact": "low"},
]


def _write_demo_csv(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=["id", "title", "owner", "due_date", "status", "impact"])
        writer.writeheader()
        writer.writerows(DEMO_ROWS)


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Turn task CSV into a prioritized daily report")
    subparsers = parser.add_subparsers(dest="command", required=True)
    run = subparsers.add_parser("run", help="process an existing CSV")
    run.add_argument("--input", required=True, type=Path)
    run.add_argument("--out", default=Path("out"), type=Path)
    run.add_argument("--date", type=date.fromisoformat, help="reference date (YYYY-MM-DD)")
    demo = subparsers.add_parser("demo", help="generate synthetic input and process it")
    demo.add_argument("--out", default=Path("out"), type=Path)
    demo.add_argument("--date", type=date.fromisoformat, help="reference date (YYYY-MM-DD)")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _build_parser().parse_args(argv)
    output_dir = args.out
    if args.command == "demo":
        input_path = output_dir / "demo_tasks.csv"
        _write_demo_csv(input_path)
    else:
        input_path = args.input
    reference_day = args.date or date.today()
    generated_at = datetime.combine(reference_day, datetime.min.time(), tzinfo=timezone.utc)
    tasks = process_tasks(load_tasks(input_path), today=reference_day)
    markdown_path, json_path = write_outputs(tasks, output_dir, str(input_path), generated_at)
    print(f"Processed {len(tasks)} tasks")
    print(f"Markdown: {markdown_path}")
    print(f"JSON: {json_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
