
import unittest

from reuseiq.reasoning.fuzzy_engine import FuzzyEngine


class TestFuzzyEngine(unittest.TestCase):

    def setUp(self):
        self.engine = FuzzyEngine()

    def test_low_membership(self):
        result = self.engine.triangular_membership(
            0.0, 0.0, 0.0, 0.5
        )
        self.assertEqual(result, 1.0)

    def test_medium_membership(self):
        result = self.engine.triangular_membership(
            0.5, 0.0, 0.5, 1.0
        )
        self.assertEqual(result, 1.0)

    def test_high_membership(self):
        result = self.engine.triangular_membership(
            1.0, 0.5, 1.0, 1.0
        )
        self.assertEqual(result, 1.0)

    def test_repairability_score(self):
        result = self.engine.calculate_repairability(
            damage=0.2,
            repair_cost_ratio=0.2
        )

        self.assertGreaterEqual(result, 0)
        self.assertLessEqual(result, 100)

    def test_invalid_damage(self):
        with self.assertRaises(ValueError):
            self.engine.calculate_repairability(
                damage=1.5,
                repair_cost_ratio=0.2
            )


if __name__ == "__main__":
    unittest.main()
