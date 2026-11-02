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


class TestDatabaseManager(unittest.TestCase):

    def setUp(self):
        self.temp_db = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
        self.temp_db.close()
        self.db = DatabaseManager(db_path=self.temp_db.name)

    def tearDown(self):
        if os.path.exists(self.temp_db.name):
            try:
                os.remove(self.temp_db.name)
            except Exception:
                pass

    def test_save_and_get_device(self):
        device = DeviceRecord(
            device_id="TEST01",
            device_type=DeviceType.LAPTOP.value,
            age_years=3.0,
            damage_severity=35.0,
            repair_cost=1500.0,
            replacement_cost=25000.0,
            repair_success_probability=0.8,
            overall_condition=OverallCondition.GOOD.value,
            battery_condition=BatteryCondition.NORMAL.value,
            safety_check_passed=True,
            spare_parts_availability=PartsAvailability.AVAILABLE.value,
            resale_value=8000.0,
            personal_data_present=True,
            data_erased=False,
            components=[
                ComponentInfo(name="RAM", is_working=True, estimated_value=2000.0),
                ComponentInfo(name="screen", is_working=False, remarks="Scratched")
            ],
            notes="Testing unit device"
        )

        saved = self.db.save_device(device)
        self.assertTrue(saved)

        retrieved = self.db.get_device("TEST01")
        self.assertIsNotNone(retrieved)
        self.assertEqual(retrieved.device_id, "TEST01")
        self.assertEqual(len(retrieved.components), 2)
        self.assertEqual(retrieved.working_components, ["RAM"])
        self.assertEqual(retrieved.damaged_components, ["screen"])
        self.assertEqual(retrieved.safety_status_str, "safe")
        self.assertEqual(retrieved.repair_cost_ratio, 0.06)

    def test_missing_information_detection(self):
        device = DeviceRecord(
            device_id="TEST02",
            device_type=DeviceType.MOBILE_PHONE.value,
            age_years=2.0,
            damage_severity=50.0,
            repair_cost=None,
            replacement_cost=15000.0,
            repair_success_probability=None,
            safety_check_passed=None,
            spare_parts_availability=PartsAvailability.UNKNOWN.value,
            components=[]
        )
        missing = device.get_missing_information()
        self.assertTrue(len(missing) >= 4)
        self.assertTrue(any("Repair cost" in m for m in missing))
        self.assertTrue(any("Safety inspection" in m for m in missing))

    def test_seed_default_devices(self):
        self.db.seed_default_devices()
        devices = self.db.list_devices()
        self.assertGreaterEqual(len(devices), 8)

        lap104 = self.db.get_device("LAP104")
        self.assertIsNotNone(lap104)
        self.assertEqual(lap104.repair_cost, 2000.0)
        self.assertEqual(lap104.replacement_cost, 30000.0)
        self.assertIn("RAM", lap104.working_components)

        summary = self.db.get_analytics_summary()
        self.assertGreaterEqual(summary["total_devices"], 8)
        self.assertGreater(summary["working_components_count"], 5)


if __name__ == "__main__":
    unittest.main()
