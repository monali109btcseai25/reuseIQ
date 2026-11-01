
"""
ReUseIQ - Probability Reasoning Engine

Uses Bayes' theorem to update the probability
of device failure using observed evidence.
"""


class ProbabilityEngine:

    def calculate_posterior(
        self,
        prior_probability,
        evidence_given_failure,
        evidence_given_no_failure
    ):
        """
        Applies Bayes' theorem.

        prior_probability:
            Initial probability of device failure.

        evidence_given_failure:
            Probability of observing the evidence
            when the device has a failure.

        evidence_given_no_failure:
            Probability of observing the evidence
            when the device has no failure.
        """

        values = [
            prior_probability,
            evidence_given_failure,
            evidence_given_no_failure
        ]

        for value in values:
            if not 0 <= value <= 1:
                raise ValueError(
                    "All probabilities must be between 0 and 1."
                )

        numerator = (
            evidence_given_failure * prior_probability
        )

        denominator = (
            numerator
            + evidence_given_no_failure
            * (1 - prior_probability)
        )

        if denominator == 0:
            raise ValueError(
                "Cannot calculate probability with these inputs."
            )

        posterior = numerator / denominator

        return round(posterior, 4)

    def classify_risk(self, probability):
        """Classifies the estimated failure probability."""

        if not 0 <= probability <= 1:
            raise ValueError(
                "Probability must be between 0 and 1."
            )

        if probability < 0.30:
            return "Low Risk"

        elif probability < 0.70:
            return "Medium Risk"

        return "High Risk"
