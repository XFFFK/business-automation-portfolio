"""Small, deterministic business workflow built with the Python standard library.

The workflow keeps the input schema intentionally small: a CSV row describes one
work item and the rule engine adds priority, deadline risk and days remaining.
The ``today`` argument is injectable so reports are reproducible in tests and
in demonstrations.
"""

from __future__ import annotations

import csv
import json
from dataclasses import asdict, dataclass
from datetime import date, datetime
from pathlib import Path
from typing import Iterable, Sequence


REQUIRED_COLUMNS = ("id", "title", "owner", "due_date", "status", "impact")
VALID_STATUSES = {"open", "in_progress", "blocked", "done"}
VALID_IMPACTS = {"low", "medium", "high"}


@dataclass(frozen=True)
class Task:
    """A task after rule-based triage."""

    id: str
    title: str
    owner: str
    due_date: str
    status: str
    impact: str
    days_remaining: int | None
    priority: str
    risk: str


def _parse_date(value: str, field: str = "due_date") -> date:
    try:
        return date.fromisoformat(value)
    except ValueError as exc:
        raise ValueError(f"{field} must use YYYY-MM-DD: {value!r}") from exc


def load_tasks(csv_path: str | Path) -> list[dict[str, str]]:
    """Read and validate the small input CSV schema."""

    path = Path(csv_path)
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames is None:
            raise ValueError("CSV must contain a header row")
        missing = [column for column in REQUIRED_COLUMNS if column not in reader.fieldnames]
        if missing:
            raise ValueError(f"CSV is missing columns: {', '.join(missing)}")
        rows: list[dict[str, str]] = []
        for line_number, row in enumerate(reader, start=2):
            if not any((value or "").strip() for value in row.values()):
                continue
            normalized = {column: (row.get(column) or "").strip() for column in REQUIRED_COLUMNS}
            if not normalized["id"] or not normalized["title"]:
                raise ValueError(f"line {line_number}: id and title are required")
            if normalized["status"] not in VALID_STATUSES:
                raise ValueError(f"line {line_number}: invalid status {normalized['status']!r}")
            if normalized["impact"] not in VALID_IMPACTS:
                raise ValueError(f"line {line_number}: invalid impact {normalized['impact']!r}")
            if normalized["due_date"]:
                _parse_date(normalized["due_date"])
            rows.append(normalized)
    return rows


def _classify(row: dict[str, str], today: date) -> Task:
    status = row["status"]
    due = _parse_date(row["due_date"]) if row["due_date"] else None
    days_remaining = (due - today).days if due else None

    if status == "done":
        priority, risk = "done", "closed"
    elif status == "blocked" or days_remaining is not None and days_remaining < 0:
        priority, risk = "P0", "overdue" if days_remaining is not None and days_remaining < 0 else "blocked"
    elif days_remaining is None:
        priority, risk = "P2", "missing_due_date"
    elif days_remaining <= 2:
        priority, risk = "P1", "due_soon"
    elif days_remaining <= 7 or row["impact"] == "high":
        priority, risk = "P2", "watch"
    else:
        priority, risk = "P3", "on_track"

    return Task(
        id=row["id"],
        title=row["title"],
        owner=row["owner"],
        due_date=row["due_date"],
        status=status,
        impact=row["impact"],
        days_remaining=days_remaining,
        priority=priority,
        risk=risk,
    )


def process_tasks(rows: Iterable[dict[str, str]], today: date | None = None) -> list[Task]:
    """Apply the triage rules and return deterministic priority order."""

    reference_day = today or date.today()
    tasks = [_classify(row, reference_day) for row in rows]
    priority_order = {"P0": 0, "P1": 1, "P2": 2, "P3": 3, "done": 4}
    return sorted(tasks, key=lambda task: (priority_order[task.priority], task.due_date or "9999-12-31", task.id))


def _summary(tasks: Sequence[Task]) -> dict[str, int]:
    return {
        "total": len(tasks),
        "open": sum(task.status != "done" for task in tasks),
        "urgent": sum(task.priority == "P0" for task in tasks),
        "due_soon": sum(task.risk == "due_soon" for task in tasks),
        "completed": sum(task.status == "done" for task in tasks),
    }


def render_markdown(tasks: Sequence[Task], generated_at: datetime) -> str:
    """Render an actionable Markdown daily report."""

    summary = _summary(tasks)
    lines = [
        "# Daily Work Report",
        "",
        f"Generated: `{generated_at.isoformat(timespec='seconds')}`",
        "",
        "## Summary",
        "",
        f"- Total: **{summary['total']}**  ",
        f"- Open: **{summary['open']}**  ",
        f"- Urgent (P0): **{summary['urgent']}**  ",
        f"- Due soon: **{summary['due_soon']}**  ",
        f"- Completed: **{summary['completed']}**",
        "",
        "## Action Queue",
        "",
        "| Priority | Task | Owner | Due | Risk | Status |",
        "| --- | --- | --- | --- | --- | --- |",
    ]
    for task in tasks:
        due = task.due_date or "—"
        lines.append(
            f"| {task.priority} | {task.title} (`{task.id}`) | {task.owner or '—'} | "
            f"{due} | {task.risk} | {task.status} |"
        )
    lines.extend(["", "_Priority rules: P0 = blocked/overdue; P1 = due within 2 days; P2 = watch; P3 = on track._", ""])
    return "\n".join(lines)


def build_result(tasks: Sequence[Task], source: str, generated_at: datetime) -> dict[str, object]:
    return {
        "generated_at": generated_at.isoformat(timespec="seconds"),
        "source": source,
        "summary": _summary(tasks),
        "tasks": [asdict(task) for task in tasks],
    }


def write_outputs(tasks: Sequence[Task], output_dir: str | Path, source: str, generated_at: datetime) -> tuple[Path, Path]:
    """Write the Markdown report and machine-readable JSON result."""

    destination = Path(output_dir)
    destination.mkdir(parents=True, exist_ok=True)
    markdown_path = destination / "daily_report.md"
    json_path = destination / "daily_result.json"
    markdown_path.write_text(render_markdown(tasks, generated_at), encoding="utf-8")
    json_path.write_text(json.dumps(build_result(tasks, source, generated_at), ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return markdown_path, json_path
