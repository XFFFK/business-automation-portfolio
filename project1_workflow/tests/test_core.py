from datetime import date, datetime, timezone
import json
import tempfile
import unittest
from pathlib import Path

from workflow.core import load_tasks, process_tasks, render_markdown, write_outputs


TODAY = date(2026, 10, 2)


def row(task_id="A", **overrides):
    values = {"id": task_id, "title": "Task", "owner": "A", "due_date": "2026-10-10", "status": "open", "impact": "medium"}
    values.update(overrides)
    return values


class WorkflowTests(unittest.TestCase):
    def test_overdue_task_is_p0(self):
        task = process_tasks([row(due_date="2026-10-01")], TODAY)[0]
        self.assertEqual((task.priority, task.risk, task.days_remaining), ("P0", "overdue", -1))

    def test_blocked_task_is_p0_even_when_due_later(self):
        task = process_tasks([row(status="blocked")], TODAY)[0]
        self.assertEqual((task.priority, task.risk), ("P0", "blocked"))

    def test_due_soon_task_is_p1(self):
        task = process_tasks([row(due_date="2026-10-04")], TODAY)[0]
        self.assertEqual((task.priority, task.risk), ("P1", "due_soon"))

    def test_done_task_is_closed_and_sorted_last(self):
        tasks = process_tasks([row("open", due_date="2026-10-03"), row("done", status="done", due_date="2026-09-01")], TODAY)
        self.assertEqual(tasks[0].id, "open")
        self.assertEqual((tasks[1].priority, tasks[1].risk), ("done", "closed"))

    def test_missing_due_date_is_watchable_without_crashing(self):
        task = process_tasks([row(due_date="", impact="low")], TODAY)[0]
        self.assertEqual((task.priority, task.risk, task.days_remaining), ("P2", "missing_due_date", None))

    def test_load_tasks_rejects_unknown_status(self):
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "tasks.csv"
            source.write_text("id,title,owner,due_date,status,impact\nA,Task,A,2026-10-10,later,low\n", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "invalid status"):
                load_tasks(source)

    def test_outputs_have_human_and_machine_readable_content(self):
        tasks = process_tasks([row(due_date="2026-10-04")], TODAY)
        generated_at = datetime(2026, 10, 2, tzinfo=timezone.utc)
        with tempfile.TemporaryDirectory() as directory:
            markdown_path, json_path = write_outputs(tasks, directory, "tasks.csv", generated_at)
            self.assertIn("Action Queue", markdown_path.read_text(encoding="utf-8"))
            payload = json.loads(json_path.read_text(encoding="utf-8"))
            self.assertEqual(payload["summary"]["due_soon"], 1)
            self.assertEqual(payload["tasks"][0]["priority"], "P1")

    def test_markdown_contains_generated_timestamp_and_task_title(self):
        tasks = process_tasks([row()], TODAY)
        report = render_markdown(tasks, datetime(2026, 10, 2, 9, 30, tzinfo=timezone.utc))
        self.assertIn("2026-10-02T09:30:00+00:00", report)
        self.assertIn("Task (`A`)", report)


if __name__ == "__main__":
    unittest.main()
