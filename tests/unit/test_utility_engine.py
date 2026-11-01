
import unittest

from reuseiq.reasoning.utility_engine import UtilityEngine


class TestUtilityEngine(unittest.TestCase):

    def setUp(self):
        self.engine = UtilityEngine()

    def test_utility_calculation(self):
        result = self.engine.calculate_utility(
            economic_score=80,
            environmental_score=90,
            life_extension_score=75
        )

        self.assertEqual(result, 82.25)

    def test_compare_options(self):
        options = {
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

        result = self.engine.compare_options(options)

        self.assertEqual(
            list(result.keys())[0],
            "Repair"
        )

    def test_invalid_score(self):
        with self.assertRaises(ValueError):
            self.engine.calculate_utility(
                economic_score=120,
                environmental_score=80,
                life_extension_score=70
            )


if __name__ == "__main__":
    unittest.main()
