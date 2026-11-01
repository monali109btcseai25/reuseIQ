
import unittest

from reuseiq.reasoning.explanation import ExplanationEngine


class TestExplanationEngine(unittest.TestCase):

    def setUp(self):
        self.engine = ExplanationEngine()

    def test_repair_explanation(self):
        result = self.engine.generate_explanation(
            recommendation="Repair",
            repairability=85,
            failure_probability=0.20,
            utility_scores={
                "Repair": 90,
                "Reuse": 75,
                "Recycle": 60
            },
            safety_status="safe"
        )

        self.assertIn("Repair", result)
        self.assertIn("85/100", result)

    def test_unsafe_explanation(self):
        result = self.engine.generate_explanation(
            recommendation="Recycle",
            repairability=20,
            failure_probability=0.80,
            utility_scores={},
            safety_status="unsafe"
        )

        self.assertIn("unsafe", result)

    def test_unknown_safety_explanation(self):
        result = self.engine.generate_explanation(
            recommendation="Safety Assessment Required",
            repairability=50,
            failure_probability=0.50,
            utility_scores={},
            safety_status="unknown"
        )

        self.assertIn("unknown", result)


if __name__ == "__main__":
    unittest.main()
