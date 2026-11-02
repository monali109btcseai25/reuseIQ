import os
import tempfile
import unittest

from reuseiq.data.database import DatabaseManager
from reuseiq.data.models import (
    BatteryCondition,
    ComponentInfo,
    DeviceRecord,
    DeviceType,
    OverallCondition,
    PartsAvailability,
)
from reuseiq.services.advisory_service import AdvisoryService


class TestAdvisoryScenarios(unittest.TestCase):

    def setUp(self):
        self.temp_db = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
        self.temp_db.close()
        self.db = DatabaseManager(db_path=self.temp_db.name)
        self.advisor = AdvisoryService(db_manager=self.db)

    def tearDown(self):
        if os.path.exists(self.temp_db.name):
            try:
                os.remove(self.temp_db.name)
            except Exception:
                pass

    def test_scenario_1_pristine_working_device(self):
        """Scenario 1: Working device requiring no repair (donate / direct reuse)."""
        dsk = DeviceRecord(
            device_id="DSK201",
            device_type=DeviceType.DESKTOP_COMPUTER.value,
            age_years=2.0,
            damage_severity=5.0,
            repair_cost=0.0,
            replacement_cost=45000.0,
            repair_success_probability=0.98,
            overall_condition=OverallCondition.EXCELLENT.value,
            battery_condition=BatteryCondition.NOT_APPLICABLE.value,
            safety_check_passed=True,
            resale_value=28000.0,
            personal_data_present=False,
            data_erased=True,
            components=[ComponentInfo(name="CPU", is_working=True)]
        )
        res = self.advisor.evaluate_device(dsk)
        self.assertIn("donate_reuse", res["feasible_options"])
        self.assertEqual(res["recommended_action"], "donate_reuse")

    def test_scenario_2_inexpensive_straightforward_repair(self):
        """Scenario 2: LAP104 benchmark example from Section 5."""
        lap = DeviceRecord(
            device_id="LAP104",
            device_type=DeviceType.LAPTOP.value,
            age_years=4.0,
            damage_severity=40.0,
            repair_cost=2000.0,
            replacement_cost=30000.0,
            repair_success_probability=0.75,
            overall_condition=OverallCondition.FAIR.value,
            battery_condition=BatteryCondition.NORMAL.value,
            safety_check_passed=True,
            personal_data_present=True,
            data_erased=False,
            components=[
                ComponentInfo(name="RAM", is_working=True),
                ComponentInfo(name="storage", is_working=True),
                ComponentInfo(name="screen", is_working=False)
            ]
        )
        res = self.advisor.evaluate_device(lap)
        self.assertEqual(res["recommended_action"], "repair")
        self.assertIn("repair", res["feasible_options"])
        self.assertIn("refurbish", res["feasible_options"])
        self.assertIn("recycle", res["feasible_options"])
        # Direct reuse is prohibited because personal data not erased
        self.assertNotIn("donate_reuse", res["feasible_options"])
        self.assertGreater(res["fuzzy_scores"]["repairability"], 60.0)

    def test_scenario_3_expensive_repair_low_success(self):
        """Scenario 3: Severe damage, expensive repair, low probability of success."""
        tab = DeviceRecord(
            device_id="TAB402",
            device_type=DeviceType.TABLET.value,
            age_years=6.0,
            damage_severity=85.0,
            repair_cost=14000.0,
            replacement_cost=15000.0,
            repair_success_probability=0.20,
            battery_condition=BatteryCondition.DEGRADED.value,
            safety_check_passed=True,
            spare_parts_availability=PartsAvailability.SCARCE.value,
            components=[ComponentInfo(name="screen", is_working=False)]
        )
        res = self.advisor.evaluate_device(tab)
        # Should recommend recycle
        self.assertEqual(res["recommended_action"], "recycle")

    def test_scenario_4_uneconomical_repair_with_valuable_components(self):
        """Scenario 4: Uneconomical repair but high component recovery value."""
        lap550 = DeviceRecord(
            device_id="LAP550",
            device_type=DeviceType.LAPTOP.value,
            age_years=5.0,
            damage_severity=65.0,
            repair_cost=22000.0,
            replacement_cost=25000.0,
            repair_success_probability=0.35,
            battery_condition=BatteryCondition.DEGRADED.value,
            safety_check_passed=True,
            spare_parts_availability=PartsAvailability.UNAVAILABLE.value,
            components=[
                ComponentInfo(name="RAM", is_working=True, estimated_value=4000.0),
                ComponentInfo(name="storage", is_working=True, estimated_value=5000.0),
                ComponentInfo(name="motherboard", is_working=False)
            ]
        )
        res = self.advisor.evaluate_device(lap550)
        self.assertIn("component_recovery", res["feasible_options"])
        self.assertIn(res["recommended_action"], ["component_recovery", "recycle"])

    def test_scenario_5_safety_hazard_swollen_battery(self):
        """Scenario 5: Serious battery hazard blocks repair, reuse, and refurbish."""
        mob = DeviceRecord(
            device_id="MOB611",
            device_type=DeviceType.MOBILE_PHONE.value,
            age_years=3.0,
            damage_severity=70.0,
            repair_cost=1500.0,
            replacement_cost=20000.0,
            battery_condition=BatteryCondition.SWOLLEN.value,
            safety_check_passed=False,
            components=[ComponentInfo(name="battery", is_working=False)]
        )
        res = self.advisor.evaluate_device(mob)
        self.assertEqual(res["recommended_action"], "recycle")
        self.assertEqual(res["feasible_options"], ["recycle"])
        self.assertTrue(any("Swollen" in w or "SWOLLEN" in w for w in res["safety_warnings"]))

    def test_scenario_6_missing_information_detection(self):
        """Scenario 6: Missing repair cost and safety check."""
        dev = DeviceRecord(
            device_id="DEV812",
            device_type=DeviceType.OTHER.value,
            age_years=4.0,
            damage_severity=30.0,
            repair_cost=None,
            replacement_cost=10000.0,
            repair_success_probability=None,
            safety_check_passed=None,
            components=[]
        )
        res = self.advisor.evaluate_device(dev)
        self.assertGreaterEqual(len(res["missing_information"]), 3)
        self.assertTrue(res["fuzzy_scores"]["ratio_is_estimated"])
        self.assertTrue(res["probability_estimates"]["is_estimated_fallback"])

    def test_scenario_7_probability_sensitivity(self):
        """Scenario 7: Recommendation sensitivity when repair-success probability changes."""
        base_kwargs = dict(
            device_id="SENS01",
            device_type=DeviceType.LAPTOP.value,
            age_years=3.0,
            damage_severity=40.0,
            repair_cost=5000.0,
            replacement_cost=20000.0,
            safety_check_passed=True,
            components=[ComponentInfo(name="screen", is_working=False)]
        )

        # High probability of success -> Repair
        dev_high = DeviceRecord(**base_kwargs, repair_success_probability=0.90)
        res_high = self.advisor.evaluate_device(dev_high)

        # Very low probability of success -> Higher failure risk
        dev_low = DeviceRecord(**base_kwargs, repair_success_probability=0.10)
        res_low = self.advisor.evaluate_device(dev_low)

        self.assertGreater(
            res_high["probability_estimates"]["success_probability"],
            res_low["probability_estimates"]["success_probability"]
        )
        self.assertNotEqual(
            res_high["probability_estimates"]["risk_classification"],
            res_low["probability_estimates"]["risk_classification"]
        )


if __name__ == "__main__":
    unittest.main()
