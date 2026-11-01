
"""
ReUseIQ - Recommendation Service

Connects all five AI reasoning components
to generate a complete recommendation.
"""

from reuseiq.reasoning.fuzzy_engine import FuzzyEngine
from reuseiq.reasoning.probability_engine import ProbabilityEngine
from reuseiq.reasoning.utility_engine import UtilityEngine
from reuseiq.reasoning.decision_engine import DecisionEngine
from reuseiq.reasoning.explanation import ExplanationEngine


class RecommendationService:

    def __init__(self):
        self.fuzzy_engine = FuzzyEngine()
        self.probability_engine = ProbabilityEngine()
        self.utility_engine = UtilityEngine()
        self.decision_engine = DecisionEngine()
        self.explanation_engine = ExplanationEngine()

    def recommend(
        self,
        damage,
        repair_cost_ratio,
        prior_failure_probability,
        evidence_given_failure,
        evidence_given_no_failure,
        option_scores,
        safety_status
    ):
        """
        Generates a complete ReUseIQ recommendation.

        option_scores example:
        {
            "Repair": {
                "economic": 80,
                "environmental": 90,
                "life_extension": 75
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
        }
        """

        # Step 1: Calculate fuzzy repairability.
        repairability = (
            self.fuzzy_engine.calculate_repairability(
                damage,
                repair_cost_ratio
            )
        )

        # Step 2: Calculate failure probability using Bayes' theorem.
        failure_probability = (
            self.probability_engine.calculate_posterior(
                prior_failure_probability,
                evidence_given_failure,
                evidence_given_no_failure
            )
        )

        # Step 3: Calculate utility scores for each option.
        utility_scores = self.utility_engine.compare_options(
            option_scores
        )

        # Step 4: Select the best eligible option.
        decision = self.decision_engine.recommend(
            options=utility_scores,
            repairability=repairability,
            failure_probability=failure_probability,
            safety_status=safety_status
        )

        # Step 5: Generate a human-readable explanation.
        explanation = self.explanation_engine.generate_explanation(
            recommendation=decision["recommendation"],
            repairability=repairability,
            failure_probability=failure_probability,
            utility_scores=decision["scores"],
            safety_status=safety_status
        )

        # Step 6: Return the complete result.
        return {
            "recommendation": decision["recommendation"],
            "repairability_score": repairability,
            "failure_probability": failure_probability,
            "utility_scores": decision["scores"],
            "reason": decision["reason"],
            "explanation": explanation
        }
