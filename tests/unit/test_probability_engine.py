
import unittest

from reuseiq.reasoning.probability_engine import ProbabilityEngine


class TestProbabilityEngine(unittest.TestCase):

    def setUp(self):
        self.engine = ProbabilityEngine()

    def test_bayes_calculation(self):
        result = self.engine.calculate_posterior(
            prior_probability=0.30,
            evidence_given_failure=0.80,
            evidence_given_no_failure=0.10
        )

        self.assertAlmostEqual(result, 0.7742, places=4)

    def test_low_risk(self):
        result = self.engine.classify_risk(0.20)
        self.assertEqual(result, "Low Risk")

    def test_medium_risk(self):
        result = self.engine.classify_risk(0.50)
        self.assertEqual(result, "Medium Risk")

    def test_high_risk(self):
        result = self.engine.classify_risk(0.80)
        self.assertEqual(result, "High Risk")

    def test_invalid_probability(self):
        with self.assertRaises(ValueError):
            self.engine.classify_risk(1.5)


if __name__ == "__main__":
    unittest.main()
