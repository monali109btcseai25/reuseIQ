
"""
ReUseIQ - Fuzzy Logic Engine

Estimates how suitable a device is for repair
using damage severity and repair cost.
"""


class FuzzyEngine:

    def triangular_membership(self, x, a, b, c):
        """
        Calculates membership of x in a triangular fuzzy set.

        Returns a value between 0 and 1.
        """

        if x < a or x > c:
            return 0.0

        # Left shoulder
        if a == b:
            if x <= b:
                return 1.0
            return (c - x) / (c - b)

        # Right shoulder
        if b == c:
            if x >= b:
                return 1.0
            return (x - a) / (b - a)

        # Normal triangular membership
        if x == b:
            return 1.0

        if x < b:
            return (x - a) / (b - a)

        return (c - x) / (c - b)

    def get_memberships(self, value):
        """
        Divides a normalized value into:
        Low, Medium and High fuzzy categories.
        """

        return {
            "low": self.triangular_membership(
                value, 0.0, 0.0, 0.5
            ),
            "medium": self.triangular_membership(
                value, 0.0, 0.5, 1.0
            ),
            "high": self.triangular_membership(
                value, 0.5, 1.0, 1.0
            )
        }

    def calculate_repairability(self, damage, repair_cost_ratio):
        """
        Calculates repair suitability from 0 to 100.

        damage:
            0 = No damage
            1 = Very severe damage

        repair_cost_ratio:
            Repair cost / Replacement cost

            0 = Very cheap repair
            1 = Repair costs as much as replacement
        """

        if not 0 <= damage <= 1:
            raise ValueError("Damage must be between 0 and 1.")

        if repair_cost_ratio < 0:
            raise ValueError("Repair cost ratio cannot be negative.")

        # Normalize cost ratio.
        cost = min(repair_cost_ratio, 1.0)

        damage_memberships = self.get_memberships(damage)
        cost_memberships = self.get_memberships(cost)

        # Rule base:
        # (Damage category, Cost category, Repairability score)

        rules = [
            ("low", "low", 95),
            ("low", "medium", 80),
            ("low", "high", 60),

            ("medium", "low", 75),
            ("medium", "medium", 55),
            ("medium", "high", 30),

            ("high", "low", 45),
            ("high", "medium", 25),
            ("high", "high", 10)
        ]

        weighted_score = 0.0
        total_strength = 0.0

        # Apply fuzzy rules.
        for damage_category, cost_category, score in rules:

            damage_strength = damage_memberships[damage_category]
            cost_strength = cost_memberships[cost_category]

            # AND operator: minimum membership.
            rule_strength = min(
                damage_strength,
                cost_strength
            )

            weighted_score += rule_strength * score
            total_strength += rule_strength

        if total_strength == 0:
            return 0.0

        # Weighted average of rule outputs.
        result = weighted_score / total_strength

        return round(result, 2)
