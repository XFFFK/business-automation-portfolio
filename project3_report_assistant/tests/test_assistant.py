import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[1]))
from assistant import answer, search


class ReportAssistantTests(unittest.TestCase):
    def setUp(self):
        self.docs = Path(__file__).parents[1] / "docs"

    def test_answer_contains_evidence_and_citation(self):
        result = answer("退款需要保留什么", self.docs)
        self.assertIn("订单号", result["answer"])
        self.assertTrue(result["citations"])
        self.assertRegex(result["citations"][0], r"\.md#p\d+")

    def test_unknown_question_is_explicit(self):
        result = answer("积分怎么兑换", self.docs)
        self.assertEqual(result["answer"], "没有在资料中找到依据。")
        self.assertEqual(result["citations"], [])

    def test_search_is_ranked(self):
        hits = search("周报 指标", self.docs)
        self.assertEqual(hits[0]["document"], "metrics.md")


if __name__ == "__main__":
    unittest.main()
