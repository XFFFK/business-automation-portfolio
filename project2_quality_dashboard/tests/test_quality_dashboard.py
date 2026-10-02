import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[1]))
from quality_dashboard import inspect_rows


class QualityDashboardTests(unittest.TestCase):
    def test_detects_expected_issue_types(self):
        report = inspect_rows([
            {"order_id": "1", "customer_id": "", "amount": "-1", "status": "wat", "created_at": "2026-99-01"},
            {"order_id": "1", "customer_id": "C2", "amount": "2", "status": "paid", "created_at": "2026-09-30"},
        ])
        self.assertEqual(report["rows"], 2)
        self.assertEqual(report["issue_types"], {"duplicate_id": 1, "invalid_date": 1, "invalid_status": 1, "missing": 1, "negative_amount": 1})

    def test_clean_rows_have_no_issues(self):
        report = inspect_rows([{"order_id": "1", "customer_id": "C1", "amount": "2", "status": "paid", "created_at": "2026-09-30"}])
        self.assertEqual(report["issue_count"], 0)


if __name__ == "__main__":
    unittest.main()
