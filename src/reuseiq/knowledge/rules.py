"""
ReUseIQ - Knowledge Base Rules & Fact Extractor

Translates device records into first-order logic ground facts and provides
the declarative domain rule set for symbolic inference.
"""

from typing import List, Set
from reuseiq.data.models import (
    BatteryCondition,
    DeviceRecord,
    PartsAvailability,
    SafetyStatus,
)
from reuseiq.knowledge.predicates import Fact, Predicate, Rule


def device_to_facts(device: DeviceRecord) -> List[Fact]:
    """
    Transforms a DeviceRecord into a comprehensive set of ground First-Order Logic facts.
    """
    facts: List[Fact] = []
    dev_id = device.device_id

    # Core device assertions
    facts.append(Fact("Device", dev_id))
    facts.append(Fact("DeviceType", dev_id, device.device_type))
    facts.append(Fact("AgeYears", dev_id, device.age_years))
    facts.append(Fact("DamageSeverity", dev_id, device.damage_severity))

    # Damage category mapping
    if device.damage_severity < 20.0:
        facts.append(Fact("DamageLow", dev_id))
    elif device.damage_severity <= 60.0:
        facts.append(Fact("DamageModerate", dev_id))
    else:
        facts.append(Fact("DamageHigh", dev_id))

    # Overall condition
    facts.append(Fact("OverallCondition", dev_id, device.overall_condition))
    if device.overall_condition in {"excellent", "good"} and device.damage_severity < 20.0:
        facts.append(Fact("Functional", dev_id))

    # Safety checks
    if device.battery_condition == BatteryCondition.SWOLLEN.value:
        facts.append(Fact("SwollenBattery", dev_id))
        facts.append(Fact("SafetyHazard", dev_id, "SwollenBatteryHazard"))

    if device.safety_check_passed is True:
        facts.append(Fact("SafetyCheckPassed", dev_id))
    elif device.safety_check_passed is False:
        facts.append(Fact("SafetyCheckFailed", dev_id))
        facts.append(Fact("SafetyHazard", dev_id, "InspectionFailedHazard"))
    else:
        facts.append(Fact("SafetyCheckUnknown", dev_id))

    # Personal data presence
    if device.personal_data_present:
        facts.append(Fact("ContainsPersonalData", dev_id))
        if device.data_erased:
            facts.append(Fact("DataErased", dev_id))
        else:
            facts.append(Fact("DataNotErased", dev_id))

    # Spare parts availability
    facts.append(Fact("SparePartsStatus", dev_id, device.spare_parts_availability))
    if device.spare_parts_availability == PartsAvailability.AVAILABLE.value:
        facts.append(Fact("SparePartsAvailable", dev_id))
    elif device.spare_parts_availability == PartsAvailability.SCARCE.value:
        facts.append(Fact("SparePartsScarce", dev_id))
    elif device.spare_parts_availability == PartsAvailability.UNAVAILABLE.value:
        facts.append(Fact("SparePartsUnavailable", dev_id))

    # Cost and economics
    if device.repair_cost is not None:
        facts.append(Fact("RepairCostKnown", dev_id))
        ratio = device.repair_cost_ratio
        if ratio is not None:
            facts.append(Fact("RepairCostRatio", dev_id, ratio))
            # Standard economic threshold: repair is economical if <= 60% of replacement cost
            if ratio <= 0.60 and device.spare_parts_availability != PartsAvailability.UNAVAILABLE.value:
                facts.append(Fact("EconomicalToRepair", dev_id))
            else:
                facts.append(Fact("UneconomicalToRepair", dev_id))
    else:
        facts.append(Fact("RepairCostUnknown", dev_id))

    # Repair success probability
    if device.repair_success_probability is not None:
        facts.append(Fact("RepairSuccessProbKnown", dev_id))
        facts.append(Fact("RepairSuccessProb", dev_id, device.repair_success_probability))
        if device.repair_success_probability >= 0.60:
            facts.append(Fact("HighProbabilitySuccess", dev_id))
        else:
            facts.append(Fact("LowProbabilitySuccess", dev_id))
    else:
        facts.append(Fact("RepairSuccessProbUnknown", dev_id))

    # Component assertions
    working_count = 0
    for comp in device.components:
        facts.append(Fact("HasComponent", dev_id, comp.name))
        if comp.is_working:
            facts.append(Fact("Working", comp.name))
            working_count += 1
            if comp.is_reusable:
                facts.append(Fact("Harvestable", dev_id, comp.name))
        else:
            facts.append(Fact("Damaged", comp.name))

    if working_count > 0:
        facts.append(Fact("HasWorkingComponents", dev_id))
    if any(c.is_working and c.is_reusable for c in device.components):
        facts.append(Fact("HasHarvestableComponent", dev_id))

    # Refurbishment suitability condition
    # Moderate damage, working core components, economical
    if (device.damage_severity <= 60.0 and working_count >= 1 and
            device.spare_parts_availability != PartsAvailability.UNAVAILABLE.value):
        facts.append(Fact("RefurbishmentViable", dev_id))

    return facts


def get_standard_rules() -> List[Rule]:
    """
    Returns the comprehensive domain rule set for electronic waste reasoning.
    Ordered by priority (Safety 100 -> Data 80 -> Feasibility 50 -> Default 20).
    """
    rules: List[Rule] = [
        # --- Safety Rules (Priority 100) ---
        Rule(
            rule_id="R_SAFETY_SWOLLEN_BATTERY",
            name="Swollen Battery Severe Hazard Block",
            priority=100,
            category="safety",
            description="A swollen or physically compromised lithium battery poses fire and chemical hazards. Ordinary repair, reuse, and donation must be blocked until professionally remediated.",
            antecedents=[
                Predicate("SwollenBattery", "?dev")
            ],
            consequents=[
                Predicate("ProhibitAction", "?dev", "repair"),
                Predicate("ProhibitAction", "?dev", "donate_reuse"),
                Predicate("ProhibitAction", "?dev", "refurbish"),
                Predicate("ProhibitAction", "?dev", "component_recovery"),
                Predicate("SafetyHazardWarning", "?dev", "CRITICAL_SWOLLEN_BATTERY"),
                Predicate("RequireSafetyQuarantine", "?dev")
            ]
        ),
        Rule(
            rule_id="R_SAFETY_INSPECTION_FAILED",
            name="Failed Safety Check Block",
            priority=95,
            category="safety",
            description="If a device failed its electrical or physical safety inspection, prohibit reuse, repair, and donation.",
            antecedents=[
                Predicate("SafetyCheckFailed", "?dev")
            ],
            consequents=[
                Predicate("ProhibitAction", "?dev", "repair"),
                Predicate("ProhibitAction", "?dev", "donate_reuse"),
                Predicate("ProhibitAction", "?dev", "refurbish"),
                Predicate("SafetyHazardWarning", "?dev", "FAILED_SAFETY_INSPECTION")
            ]
        ),
        Rule(
            rule_id="R_SAFETY_INSPECTION_UNKNOWN",
            name="Unverified Safety Status Precaution",
            priority=90,
            category="safety",
            description="If safety status is unknown or unverified, block direct donation or reuse until inspected.",
            antecedents=[
                Predicate("SafetyCheckUnknown", "?dev")
            ],
            consequents=[
                Predicate("ProhibitAction", "?dev", "donate_reuse"),
                Predicate("SafetyWarning", "?dev", "UNVERIFIED_SAFETY_INSPECTION_REQUIRED")
            ]
        ),

        # --- Data Security Rules (Priority 80) ---
        Rule(
            rule_id="R_DATA_SECURITY_UNSANITIZED",
            name="Personal Data Erasure Required",
            priority=80,
            category="data_security",
            description="Devices containing unerased personal data cannot be donated or reused without certified sanitization.",
            antecedents=[
                Predicate("ContainsPersonalData", "?dev"),
                Predicate("DataNotErased", "?dev")
            ],
            consequents=[
                Predicate("ProhibitAction", "?dev", "donate_reuse"),
                Predicate("RequiresDataSanitization", "?dev"),
                Predicate("DataSecurityWarning", "?dev", "PERSONAL_DATA_PRESENT_UNSANITIZED")
            ]
        ),
        Rule(
            rule_id="R_DATA_SECURITY_SANITIZED",
            name="Personal Data Sanitization Cleared",
            priority=80,
            category="data_security",
            description="Device personal data has been certified erased.",
            antecedents=[
                Predicate("ContainsPersonalData", "?dev"),
                Predicate("DataErased", "?dev")
            ],
            consequents=[
                Predicate("DataSanitizationCompleted", "?dev")
            ]
        ),

        # --- Feasibility & Action Rules (Priority 50) ---
        Rule(
            rule_id="R_FEASIBLE_DIRECT_REUSE",
            name="Direct Reuse and Donation Feasibility",
            priority=50,
            category="feasibility",
            description="Functional devices with low damage that passed safety inspection are feasible for continued use or donation.",
            antecedents=[
                Predicate("Device", "?dev"),
                Predicate("Functional", "?dev"),
                Predicate("SafetyCheckPassed", "?dev"),
                Predicate("DamageLow", "?dev"),
                Predicate("ProhibitAction", "?dev", "donate_reuse", is_negated=True)
            ],
            consequents=[
                Predicate("EligibleAction", "?dev", "donate_reuse"),
                Predicate("FeasibleExplanation", "?dev", "donate_reuse", "Device is fully functional with minimal damage and passed safety check.")
            ]
        ),
        Rule(
            rule_id="R_FEASIBLE_REPAIR",
            name="Repair Feasibility",
            priority=50,
            category="feasibility",
            description="Devices that are economical to repair, have spare parts available, and are not safety prohibited are feasible for repair.",
            antecedents=[
                Predicate("Device", "?dev"),
                Predicate("EconomicalToRepair", "?dev"),
                Predicate("SparePartsAvailable", "?dev"),
                Predicate("ProhibitAction", "?dev", "repair", is_negated=True)
            ],
            consequents=[
                Predicate("EligibleAction", "?dev", "repair"),
                Predicate("FeasibleExplanation", "?dev", "repair", "Repair cost is reasonable relative to replacement value and spare parts are available.")
            ]
        ),
        Rule(
            rule_id="R_FEASIBLE_REFURBISH",
            name="Refurbishment Feasibility",
            priority=45,
            category="feasibility",
            description="Devices with moderate damage, working components, and parts availability can be refurbished.",
            antecedents=[
                Predicate("Device", "?dev"),
                Predicate("RefurbishmentViable", "?dev"),
                Predicate("ProhibitAction", "?dev", "refurbish", is_negated=True)
            ],
            consequents=[
                Predicate("EligibleAction", "?dev", "refurbish"),
                Predicate("FeasibleExplanation", "?dev", "refurbish", "Device has working components and is suitable for certified refurbishment.")
            ]
        ),
        Rule(
            rule_id="R_FEASIBLE_COMPONENT_RECOVERY_UNECONOMICAL",
            name="Component Recovery for Uneconomical Repairs",
            priority=40,
            category="feasibility",
            description="If a whole-device repair is uneconomical but reusable working components exist, recover and harvest those components.",
            antecedents=[
                Predicate("Device", "?dev"),
                Predicate("UneconomicalToRepair", "?dev"),
                Predicate("HasHarvestableComponent", "?dev"),
                Predicate("ProhibitAction", "?dev", "component_recovery", is_negated=True)
            ],
            consequents=[
                Predicate("EligibleAction", "?dev", "component_recovery"),
                Predicate("FeasibleExplanation", "?dev", "component_recovery", "Whole device repair is uneconomical, but functional working components can be harvested for spare parts.")
            ]
        ),
        Rule(
            rule_id="R_FEASIBLE_COMPONENT_RECOVERY_HIGH_DAMAGE",
            name="Component Recovery for High Damage",
            priority=40,
            category="feasibility",
            description="If a device has high structural/chassis damage but valuable working components exist, salvage those parts.",
            antecedents=[
                Predicate("Device", "?dev"),
                Predicate("DamageHigh", "?dev"),
                Predicate("HasHarvestableComponent", "?dev"),
                Predicate("ProhibitAction", "?dev", "component_recovery", is_negated=True)
            ],
            consequents=[
                Predicate("EligibleAction", "?dev", "component_recovery"),
                Predicate("FeasibleExplanation", "?dev", "component_recovery", "Chassis has severe damage but valuable internal components remain functional.")
            ]
        ),
        Rule(
            rule_id="R_FEASIBLE_RECYCLE_DEFAULT",
            name="Authorized E-Waste Recycling Route",
            priority=20,
            category="feasibility",
            description="Every electronic device can be sent to an authorized e-waste recycler for material recovery.",
            antecedents=[
                Predicate("Device", "?dev")
            ],
            consequents=[
                Predicate("EligibleAction", "?dev", "recycle"),
                Predicate("FeasibleExplanation", "?dev", "recycle", "Safe material recovery through authorized e-waste recycling facilities is always a valid baseline.")
            ]
        ),
        Rule(
            rule_id="R_MANDATORY_RECYCLE_UNSAFE",
            name="Mandatory Recycling for Hazardous / Unsafe Devices",
            priority=99,
            category="safety",
            description="Unsafe devices must follow regulated e-waste hazard disposal.",
            antecedents=[
                Predicate("Device", "?dev"),
                Predicate("SafetyHazard", "?dev", "?hazard")
            ],
            consequents=[
                Predicate("MandatoryAction", "?dev", "recycle"),
                Predicate("RecyclingPriority", "?dev", "hazardous_waste_facility")
            ]
        )
    ]
    return rules
