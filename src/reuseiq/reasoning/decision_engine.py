
"""
ReUseIQ - Decision Engine

Combines fuzzy reasoning, probability and utility
to generate a final e-waste recommendation.
"""


class DecisionEngine:

    def __init__(self):
        self.repairability_threshold = 40
        self.high_risk_threshold = 0.70

    def recommend(
        self,
        options,
        repairability,
        failure_probability,
        safety_status
    ):
        """
        Generates a recommendation.

        options:
            Dictionary containing utility scores for
            Repair, Reuse and Recycle.

        repairability:
            Fuzzy repairability score from 0 to 100.

        failure_probability:
            Estimated failure probability from 0 to 1.

        safety_status:
            "safe", "unsafe" or "unknown".
        """

        if not 0 <= repairability <= 100:
            raise ValueError("Repairability must be 0-100.")

        if not 0 <= failure_probability <= 1:
            raise ValueError(
                "Failure probability must be between 0 and 1."
            )

        if safety_status not in {"safe", "unsafe", "unknown"}:
            raise ValueError(
                "Safety status must be safe, unsafe or unknown."
            )

        # Safety restrictions take priority over utility scores.
        if safety_status == "unsafe":
            return {
                "recommendation": "Recycle",
                "reason": (
                    "The device is marked unsafe. "
                    "Do not repair or reuse it. "
                    "Send it to an authorized e-waste recycler."
                ),
                "scores": {}
            }

        if safety_status == "unknown":
            return {
                "recommendation": "Safety Assessment Required",
                "reason": (
                    "Device safety is unknown. "
                    "Assess safety before repair or reuse."
                ),
                "scores": {}
            }

        # Remove options that are not suitable.
        eligible_options = dict(options)

        if repairability < self.repairability_threshold:
            eligible_options.pop("Repair", None)

        if failure_probability >= self.high_risk_threshold:
            eligible_options.pop("Repair", None)

        if not eligible_options:
            return {
                "recommendation": "Recycle",
                "reason": (
                    "No eligible repair or reuse option "
                    "was provided. Consider authorized recycling."
                ),
                "scores": {}
            }

        # Select the option with the highest utility.
        best_option = max(
            eligible_options,
            key=eligible_options.get
        )

        return {
            "recommendation": best_option,
            "reason": (
                f"{best_option} has the highest utility "
                "among the eligible options."
            ),
            "scores": eligible_options
        }
