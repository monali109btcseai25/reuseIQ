
import unittest

from reuseiq.reasoning.decision_engine import DecisionEngine


class TestDecisionEngine(unittest.TestCase):

    def setUp(self):
        self.engine = DecisionEngine()

    def test_repair_recommendation(self):
        options = {
            "Repair": 90,
            "Reuse": 75,
            "Recycle": 60
        }

        result = self.engine.recommend(
            options=options,
            repairability=85,
            failure_probability=0.20,
            safety_status="safe"
        )

        self.assertEqual(result["recommendation"], "Repair")

    def test_unsafe_device(self):
        result = self.engine.recommend(
            options={"Repair": 90, "Recycle": 60},
            repairability=90,
            failure_probability=0.10,
            safety_status="unsafe"
        )

        self.assertEqual(result["recommendation"], "Recycle")
        self.assertEqual(result["scores"], {})

    def test_unknown_safety(self):
        result = self.engine.recommend(
            options={"Repair": 90},
            repairability=90,
            failure_probability=0.10,
            safety_status="unknown"
        )

        self.assertEqual(
            result["recommendation"],
            "Safety Assessment Required"
        )

    def test_high_failure_risk_blocks_repair(self):
        options = {
            "Repair": 95,
            "Reuse": 80,
            "Recycle": 60
        }

        result = self.engine.recommend(
            options=options,
            repairability=90,
            failure_probability=0.85,
            safety_status="safe"
        )

        self.assertEqual(result["recommendation"], "Reuse")


if __name__ == "__main__":
    unittest.main()
