
import unittest

from reuseiq.services.recommendation_service import RecommendationService


class TestRecommendationService(unittest.TestCase):

    def setUp(self):
        self.service = RecommendationService()

    def test_safe_device_recommendation(self):
        result = self.service.recommend(
            damage=0.2,
            repair_cost_ratio=0.3,
            prior_failure_probability=0.2,
            evidence_given_failure=0.8,
            evidence_given_no_failure=0.2,
            option_scores={
                "Repair": {
                    "economic": 85,
                    "environmental": 90,
                    "life_extension": 80
                },
                "Reuse": {
                    "economic": 70,
                    "environmental": 85,
                    "life_extension": 60
                },
                "Recycle": {
                    "economic": 60,
                    "environmental": 80,
                    "life_extension": 30
                }
            },
            safety_status="safe"
        )

        self.assertIn("recommendation", result)
        self.assertIn("repairability_score", result)
        self.assertIn("failure_probability", result)
        self.assertIn("utility_scores", result)
        self.assertIn("explanation", result)

    def test_unsafe_device(self):
        result = self.service.recommend(
            damage=0.5,
            repair_cost_ratio=0.5,
            prior_failure_probability=0.2,
            evidence_given_failure=0.8,
            evidence_given_no_failure=0.2,
            option_scores={
                "Repair": {
                    "economic": 85,
                    "environmental": 90,
                    "life_extension": 80
                },
                "Reuse": {
                    "economic": 70,
                    "environmental": 85,
                    "life_extension": 60
                },
                "Recycle": {
                    "economic": 60,
                    "environmental": 80,
                    "life_extension": 30
                }
            },
            safety_status="unsafe"
        )

        self.assertEqual(result["recommendation"], "Recycle")


if __name__ == "__main__":
    unittest.main()
