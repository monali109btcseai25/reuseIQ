
"""
ReUseIQ - Explanation Engine

Generates human-readable explanations
for the AI recommendation.
"""


class ExplanationEngine:

    def generate_explanation(
        self,
        recommendation,
        repairability,
        failure_probability,
        utility_scores,
        safety_status
    ):
        """
        Generates an explanation for the recommendation.
        """

        if safety_status == "unsafe":
            return (
                "ReUseIQ recommends authorized recycling because "
                "the device has been marked unsafe. Repair or reuse "
                "should not be attempted."
            )

        if safety_status == "unknown":
            return (
                "ReUseIQ cannot make a repair or reuse recommendation "
                "because the device safety status is unknown. "
                "A safety assessment is required first."
            )

        explanation = []

        explanation.append(
            f"Final recommendation: {recommendation}."
        )

        explanation.append(
            f"Device repairability score: {repairability}/100."
        )

        explanation.append(
            "Estimated failure probability: "
            f"{failure_probability * 100:.2f}%."
        )

        if recommendation == "Repair":
            explanation.append(
                "Repair is recommended because the device "
                "has sufficient repairability."
            )

        elif recommendation == "Reuse":
            explanation.append(
                "Reuse is recommended as a suitable alternative "
                "to repairing the device."
            )

        elif recommendation == "Recycle":
            explanation.append(
                "Recycling is recommended to support responsible "
                "e-waste management."
            )

        if utility_scores:
            explanation.append("Utility scores:")

            for option, score in utility_scores.items():
                explanation.append(
                    f"{option}: {score}/100"
                )

        return " ".join(explanation)
