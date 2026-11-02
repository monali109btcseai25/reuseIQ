"""
ReUseIQ - Data Models for Electronic Devices and Components.

Defines structured data representations with explicit distinction
between known, estimated, and unknown values.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Any
import json


class DeviceType(str, Enum):
    LAPTOP = "laptop"
    MOBILE_PHONE = "mobile_phone"
    DESKTOP_COMPUTER = "desktop_computer"
    TABLET = "tablet"
    PRINTER = "printer"
    OTHER = "other"


class OverallCondition(str, Enum):
    EXCELLENT = "excellent"
    GOOD = "good"
    FAIR = "fair"
    POOR = "poor"
    BROKEN = "broken"


class BatteryCondition(str, Enum):
    NORMAL = "normal"
    DEGRADED = "degraded"
    SWOLLEN = "swollen"
    MISSING = "missing"
    NOT_APPLICABLE = "not_applicable"


class SafetyStatus(str, Enum):
    SAFE = "safe"
    UNSAFE = "unsafe"
    UNKNOWN = "unknown"


class PartsAvailability(str, Enum):
    AVAILABLE = "available"
    SCARCE = "scarce"
    UNAVAILABLE = "unavailable"
    UNKNOWN = "unknown"


class ActionOption(str, Enum):
    REPAIR = "repair"
    REFURBISH = "refurbish"
    COMPONENT_RECOVERY = "component_recovery"
    DONATE_REUSE = "donate_reuse"
    RECYCLE = "recycle"


@dataclass
class ComponentInfo:
    """Represents a component within an electronic device."""
    name: str
    is_working: bool
    is_reusable: bool = True
    estimated_value: float = 0.0
    compatibility_notes: str = ""
    remarks: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "is_working": self.is_working,
            "is_reusable": self.is_reusable,
            "estimated_value": self.estimated_value,
            "compatibility_notes": self.compatibility_notes,
            "remarks": self.remarks,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ComponentInfo":
        return cls(
            name=data["name"],
            is_working=bool(data.get("is_working", False)),
            is_reusable=bool(data.get("is_reusable", True)),
            estimated_value=float(data.get("estimated_value", 0.0)),
            compatibility_notes=data.get("compatibility_notes", ""),
            remarks=data.get("remarks", "")
        )


@dataclass
class DeviceRecord:
    """
    Complete domain representation of an electronic device.
    Distinguishes known, estimated, and unknown attributes.
    """
    device_id: str
    device_type: str
    age_years: float
    damage_severity: float  # 0 to 100 scale
    repair_cost: Optional[float]
    replacement_cost: float
    overall_condition: str = OverallCondition.FAIR.value
    battery_condition: str = BatteryCondition.NORMAL.value
    safety_check_passed: Optional[bool] = None  # None indicates unknown / not yet tested
    spare_parts_availability: str = PartsAvailability.AVAILABLE.value
    resale_value: float = 0.0
    personal_data_present: bool = False
    data_erased: bool = False
    repair_success_probability: Optional[float] = None  # None indicates unknown
    components: List[ComponentInfo] = field(default_factory=list)
    field_metadata: Dict[str, str] = field(default_factory=dict)  # "known", "estimated", "unknown"
    notes: str = ""

    def validate(self) -> List[str]:
        """Validates device record and returns list of validation errors."""
        errors = []
        if not self.device_id or not self.device_id.strip():
            errors.append("Device ID cannot be empty.")
        if self.age_years < 0:
            errors.append("Age cannot be negative.")
        if not (0.0 <= self.damage_severity <= 100.0):
            errors.append("Damage severity must be between 0 and 100.")
        if self.repair_cost is not None and self.repair_cost < 0:
            errors.append("Repair cost cannot be negative.")
        if self.replacement_cost <= 0:
            errors.append("Replacement cost must be greater than 0.")
        if self.repair_success_probability is not None:
            if not (0.0 <= self.repair_success_probability <= 1.0):
                errors.append("Repair success probability must be between 0.0 and 1.0.")
        return errors

    @property
    def working_components(self) -> List[str]:
        return [c.name for c in self.components if c.is_working]

    @property
    def damaged_components(self) -> List[str]:
        return [c.name for c in self.components if not c.is_working]

    @property
    def repair_cost_ratio(self) -> Optional[float]:
        if self.repair_cost is None or self.replacement_cost <= 0:
            return None
        return round(self.repair_cost / self.replacement_cost, 4)

    @property
    def safety_status_str(self) -> str:
        if self.battery_condition == BatteryCondition.SWOLLEN.value:
            return SafetyStatus.UNSAFE.value
        if self.safety_check_passed is True:
            return SafetyStatus.SAFE.value
        elif self.safety_check_passed is False:
            return SafetyStatus.UNSAFE.value
        return SafetyStatus.UNKNOWN.value

    def get_missing_information(self) -> List[str]:
        """Identifies missing or unknown information that could affect reasoning."""
        missing = []
        if self.repair_cost is None:
            missing.append("Repair cost is missing or unknown.")
        if self.repair_success_probability is None:
            missing.append("Repair success probability estimate is unknown.")
        if self.safety_check_passed is None:
            missing.append("Safety inspection status has not been verified (pending/unknown).")
        if self.spare_parts_availability == PartsAvailability.UNKNOWN.value:
            missing.append("Spare parts availability is unknown.")
        if not self.components:
            missing.append("No component-level diagnostic data provided.")
        return missing

    def to_dict(self) -> Dict[str, Any]:
        return {
            "device_id": self.device_id,
            "device_type": self.device_type,
            "age_years": self.age_years,
            "overall_condition": self.overall_condition,
            "damage_severity": self.damage_severity,
            "repair_cost": self.repair_cost,
            "replacement_cost": self.replacement_cost,
            "repair_success_probability": self.repair_success_probability,
            "battery_condition": self.battery_condition,
            "safety_check_passed": self.safety_check_passed,
            "spare_parts_availability": self.spare_parts_availability,
            "resale_value": self.resale_value,
            "personal_data_present": self.personal_data_present,
            "data_erased": self.data_erased,
            "components": [c.to_dict() for c in self.components],
            "field_metadata": self.field_metadata,
            "notes": self.notes,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "DeviceRecord":
        components = [
            ComponentInfo.from_dict(c) if isinstance(c, dict) else ComponentInfo(name=str(c), is_working=True)
            for c in data.get("components", [])
        ]
        # Support shorthand working_components / damaged_components if present
        if not components and ("working_components" in data or "damaged_components" in data):
            for wc in data.get("working_components", []):
                components.append(ComponentInfo(name=wc, is_working=True))
            for dc in data.get("damaged_components", []):
                components.append(ComponentInfo(name=dc, is_working=False))

        return cls(
            device_id=data["device_id"],
            device_type=data.get("device_type", DeviceType.LAPTOP.value),
            age_years=float(data.get("age_years", 1.0)),
            overall_condition=data.get("overall_condition", OverallCondition.FAIR.value),
            damage_severity=float(data.get("damage_severity", 0.0)),
            repair_cost=float(data["repair_cost"]) if data.get("repair_cost") is not None else None,
            replacement_cost=float(data.get("replacement_cost", 1000.0)),
            repair_success_probability=float(data["repair_success_probability"]) if data.get("repair_success_probability") is not None else None,
            battery_condition=data.get("battery_condition", BatteryCondition.NORMAL.value),
            safety_check_passed=data.get("safety_check_passed"),
            spare_parts_availability=data.get("spare_parts_availability", PartsAvailability.AVAILABLE.value),
            resale_value=float(data.get("resale_value", 0.0)),
            personal_data_present=bool(data.get("personal_data_present", False)),
            data_erased=bool(data.get("data_erased", False)),
            components=components,
            field_metadata=data.get("field_metadata", {}),
            notes=data.get("notes", "")
        )
