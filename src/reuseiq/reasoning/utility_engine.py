
"""
ReUseIQ - Utility Engine

Compares Repair, Reuse and Recycle options
using weighted utility scores.
"""


class UtilityEngine:

    def __init__(self):
        # Weights represent the importance of each factor.
        self.weights = {
            "economic": 0.40,
            "environmental": 0.35,
            "life_extension": 0.25
        }

    def calculate_utility(
        self,
        economic_score,
        environmental_score,
        life_extension_score
    ):
        """
        Calculates weighted utility between 0 and 100.

        All input scores must be between 0 and 100.
        """

        scores = {
            "economic": economic_score,
            "environmental": environmental_score,
            "life_extension": life_extension_score
        }

        for name, score in scores.items():
            if not 0 <= score <= 100:
                raise ValueError(
                    f"{name} score must be between 0 and 100."
                )

        utility = sum(
            scores[name] * self.weights[name]
            for name in self.weights
        )

        return round(utility, 2)

    def compare_options(self, options):
        """
        Calculates utility for multiple options.

        Example:
        options = {
            "Repair": {
                "economic": 80,
                "environmental": 90,
                "life_extension": 75
            }
        }
        """

        results = {}

        for option_name, scores in options.items():

            results[option_name] = self.calculate_utility(
                economic_score=scores["economic"],
                environmental_score=scores["environmental"],
                life_extension_score=scores["life_extension"]
            )

        return dict(
            sorted(
                results.items(),
                key=lambda item: item[1],
                reverse=True
            )
        )
