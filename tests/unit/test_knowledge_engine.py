import unittest

from reuseiq.data.models import (
    BatteryCondition,
    ComponentInfo,
    DeviceRecord,
    DeviceType,
    OverallCondition,
    PartsAvailability,
)
from reuseiq.knowledge.backward_chaining import BackwardChainingEngine
from reuseiq.knowledge.forward_chaining import ForwardChainingEngine
from reuseiq.knowledge.predicates import Fact, Predicate
from reuseiq.knowledge.rules import device_to_facts, get_standard_rules


class TestKnowledgeEngine(unittest.TestCase):

    def setUp(self):
        self.forward_engine = ForwardChainingEngine()
        self.backward_engine = BackwardChainingEngine()

    def test_lap104_forward_inference(self):
        # Illustrative device from Section 5
        lap104 = DeviceRecord(
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
            spare_parts_availability=PartsAvailability.AVAILABLE.value,
            personal_data_present=True,
            data_erased=False,
            components=[
                ComponentInfo(name="RAM", is_working=True),
                ComponentInfo(name="storage", is_working=True),
                ComponentInfo(name="screen", is_working=False)
            ]
        )

        facts = device_to_facts(lap104)
        result = self.forward_engine.infer(facts, lap104.device_id)

        # In LAP104:
        # Repair is economical (2000/30000 = 0.067 <= 0.6) and parts available -> repair is eligible
        self.assertIn("repair", result.eligible_actions)
        # Refurbish is eligible
        self.assertIn("refurbish", result.eligible_actions)
        # Recycle is eligible
        self.assertIn("recycle", result.eligible_actions)
        # Direct reuse is PROHIBITED because data is not erased!
        self.assertIn("donate_reuse", result.prohibited_actions)
        self.assertNotIn("donate_reuse", result.eligible_actions)

        # Rule firing trace should contain entries
        self.assertGreater(len(result.rule_traces), 0)
        rule_ids = [t.rule_id for t in result.rule_traces]
        self.assertIn("R_DATA_SECURITY_UNSANITIZED", rule_ids)
        self.assertIn("R_FEASIBLE_REPAIR", rule_ids)

    def test_swollen_battery_blocks_repair_and_reuse(self):
        # Swollen battery scenario (Safety rule R_SAFETY_SWOLLEN_BATTERY)
        hazard_dev = DeviceRecord(
            device_id="MOB611",
            device_type=DeviceType.MOBILE_PHONE.value,
            age_years=2.0,
            damage_severity=30.0,
            repair_cost=1000.0,
            replacement_cost=15000.0,
            battery_condition=BatteryCondition.SWOLLEN.value,
            safety_check_passed=False,
            components=[ComponentInfo(name="battery", is_working=False)]
        )

        facts = device_to_facts(hazard_dev)
        result = self.forward_engine.infer(facts, hazard_dev.device_id)

        # Swollen battery MUST prohibit repair, refurbish, reuse, component recovery
        self.assertIn("repair", result.prohibited_actions)
        self.assertIn("donate_reuse", result.prohibited_actions)
        self.assertIn("refurbish", result.prohibited_actions)
        self.assertIn("recycle", result.mandatory_actions)
        # Only recycle should be feasible/mandatory
        self.assertEqual(result.eligible_actions, ["recycle"])

    def test_backward_chaining_proof(self):
        lap104 = DeviceRecord(
            device_id="LAP104",
            device_type=DeviceType.LAPTOP.value,
            age_years=4.0,
            damage_severity=40.0,
            repair_cost=2000.0,
            replacement_cost=30000.0,
            battery_condition=BatteryCondition.NORMAL.value,
            safety_check_passed=True,
            spare_parts_availability=PartsAvailability.AVAILABLE.value,
            components=[ComponentInfo(name="screen", is_working=False)]
        )
        facts = set(device_to_facts(lap104))

        # Test proving why repair is eligible
        goal = Predicate("EligibleAction", "LAP104", "repair")
        proof = self.backward_engine.prove(goal, facts)
        self.assertTrue(proof.is_proved)
        self.assertEqual(proof.rule_used.rule_id, "R_FEASIBLE_REPAIR")

        # Test proving prohibition on swollen battery
        hazard_dev = DeviceRecord(
            device_id="MOB611",
            device_type=DeviceType.MOBILE_PHONE.value,
            age_years=2.0,
            damage_severity=30.0,
            repair_cost=1000.0,
            replacement_cost=15000.0,
            battery_condition=BatteryCondition.SWOLLEN.value,
            safety_check_passed=False,
            components=[]
        )
        hazard_facts = set(device_to_facts(hazard_dev))
        prohibit_goal = Predicate("ProhibitAction", "MOB611", "repair")
        proof_prohibit = self.backward_engine.prove(prohibit_goal, hazard_facts)
        self.assertTrue(proof_prohibit.is_proved)
        self.assertEqual(proof_prohibit.rule_used.rule_id, "R_SAFETY_SWOLLEN_BATTERY")


if __name__ == "__main__":
    unittest.main()
