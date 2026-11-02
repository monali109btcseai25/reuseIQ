"""
ReUseIQ - SQLite Database Manager

Handles persistence for electronic devices, component breakdowns,
recommendation histories, and analytics.
"""

import json
import os
import sqlite3
from datetime import datetime
from typing import Any, Dict, List, Optional

from reuseiq.data.models import (
    BatteryCondition,
    ComponentInfo,
    DeviceRecord,
    DeviceType,
    OverallCondition,
    PartsAvailability,
)


class DatabaseManager:
    """Manages SQLite database storage for ReUseIQ."""

    def __init__(self, db_path: Optional[str] = None):
        if db_path is None:
            # Default to a local data directory in the project root
            base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
            data_dir = os.path.join(base_dir, "data")
            os.makedirs(data_dir, exist_ok=True)
            self.db_path = os.path.join(data_dir, "reuseiq.db")
        else:
            self.db_path = db_path
            parent = os.path.dirname(self.db_path)
            if parent:
                os.makedirs(parent, exist_ok=True)

        self.init_db()

    def get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON;")
        return conn

    def init_db(self) -> None:
        """Creates the required tables and indexes if they do not exist."""
        with self.get_connection() as conn:
            cursor = conn.cursor()

            # Devices table
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS devices (
                device_id TEXT PRIMARY KEY,
                device_type TEXT NOT NULL,
                age_years REAL NOT NULL,
                overall_condition TEXT NOT NULL,
                damage_severity REAL NOT NULL,
                repair_cost REAL,
                replacement_cost REAL NOT NULL,
                repair_success_probability REAL,
                battery_condition TEXT NOT NULL,
                safety_check_passed INTEGER,
                spare_parts_availability TEXT NOT NULL,
                resale_value REAL NOT NULL,
                personal_data_present INTEGER NOT NULL,
                data_erased INTEGER NOT NULL DEFAULT 0,
                field_metadata TEXT,
                notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            """)

            # Components table (normalized representation)
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS components (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                device_id TEXT NOT NULL,
                name TEXT NOT NULL,
                is_working INTEGER NOT NULL,
                is_reusable INTEGER NOT NULL DEFAULT 1,
                estimated_value REAL DEFAULT 0.0,
                compatibility_notes TEXT,
                remarks TEXT,
                FOREIGN KEY (device_id) REFERENCES devices(device_id) ON DELETE CASCADE
            );
            """)

            # Recommendations / Assessments history table
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS recommendations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                device_id TEXT NOT NULL,
                recommended_action TEXT NOT NULL,
                feasible_options TEXT NOT NULL,
                fuzzy_scores TEXT NOT NULL,
                probability_estimates TEXT NOT NULL,
                utility_scores TEXT NOT NULL,
                safety_warnings TEXT NOT NULL,
                missing_information TEXT NOT NULL,
                rules_fired TEXT NOT NULL,
                explanation TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (device_id) REFERENCES devices(device_id) ON DELETE CASCADE
            );
            """)

            # Indexes
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_devices_type ON devices(device_type);")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_recs_device ON recommendations(device_id);")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_components_device ON components(device_id);")

            conn.commit()

    def save_device(self, device: DeviceRecord) -> bool:
        """Inserts or updates a device record along with its components."""
        errors = device.validate()
        if errors:
            raise ValueError(f"Validation failed: {', '.join(errors)}")

        with self.get_connection() as conn:
            cursor = conn.cursor()

            safety_int = None
            if device.safety_check_passed is not None:
                safety_int = 1 if device.safety_check_passed else 0

            cursor.execute("""
            INSERT INTO devices (
                device_id, device_type, age_years, overall_condition,
                damage_severity, repair_cost, replacement_cost,
                repair_success_probability, battery_condition, safety_check_passed,
                spare_parts_availability, resale_value, personal_data_present,
                data_erased, field_metadata, notes, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
            ON CONFLICT(device_id) DO UPDATE SET
                device_type = excluded.device_type,
                age_years = excluded.age_years,
                overall_condition = excluded.overall_condition,
                damage_severity = excluded.damage_severity,
                repair_cost = excluded.repair_cost,
                replacement_cost = excluded.replacement_cost,
                repair_success_probability = excluded.repair_success_probability,
                battery_condition = excluded.battery_condition,
                safety_check_passed = excluded.safety_check_passed,
                spare_parts_availability = excluded.spare_parts_availability,
                resale_value = excluded.resale_value,
                personal_data_present = excluded.personal_data_present,
                data_erased = excluded.data_erased,
                field_metadata = excluded.field_metadata,
                notes = excluded.notes,
                updated_at = CURRENT_TIMESTAMP;
            """, (
                device.device_id,
                device.device_type,
                device.age_years,
                device.overall_condition,
                device.damage_severity,
                device.repair_cost,
                device.replacement_cost,
                device.repair_success_probability,
                device.battery_condition,
                safety_int,
                device.spare_parts_availability,
                device.resale_value,
                1 if device.personal_data_present else 0,
                1 if device.data_erased else 0,
                json.dumps(device.field_metadata),
                device.notes
            ))

            # Replace components for this device
            cursor.execute("DELETE FROM components WHERE device_id = ?;", (device.device_id,))
            for comp in device.components:
                cursor.execute("""
                INSERT INTO components (
                    device_id, name, is_working, is_reusable, estimated_value,
                    compatibility_notes, remarks
                ) VALUES (?, ?, ?, ?, ?, ?, ?);
                """, (
                    device.device_id,
                    comp.name,
                    1 if comp.is_working else 0,
                    1 if comp.is_reusable else 0,
                    comp.estimated_value,
                    comp.compatibility_notes,
                    comp.remarks
                ))

            conn.commit()
            return True

    def get_device(self, device_id: str) -> Optional[DeviceRecord]:
        """Retrieves a single device by ID with components."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM devices WHERE device_id = ?;", (device_id,))
            row = cursor.fetchone()
            if not row:
                return None

            cursor.execute("SELECT * FROM components WHERE device_id = ?;", (device_id,))
            comp_rows = cursor.fetchall()
            components = [
                ComponentInfo(
                    name=c["name"],
                    is_working=bool(c["is_working"]),
                    is_reusable=bool(c["is_reusable"]),
                    estimated_value=float(c["estimated_value"]),
                    compatibility_notes=c["compatibility_notes"] or "",
                    remarks=c["remarks"] or ""
                )
                for c in comp_rows
            ]

            safety_passed = None
            if row["safety_check_passed"] is not None:
                safety_passed = bool(row["safety_check_passed"])

            field_meta = {}
            if row["field_metadata"]:
                try:
                    field_meta = json.loads(row["field_metadata"])
                except Exception:
                    field_meta = {}

            return DeviceRecord(
                device_id=row["device_id"],
                device_type=row["device_type"],
                age_years=float(row["age_years"]),
                overall_condition=row["overall_condition"],
                damage_severity=float(row["damage_severity"]),
                repair_cost=float(row["repair_cost"]) if row["repair_cost"] is not None else None,
                replacement_cost=float(row["replacement_cost"]),
                repair_success_probability=float(row["repair_success_probability"]) if row["repair_success_probability"] is not None else None,
                battery_condition=row["battery_condition"],
                safety_check_passed=safety_passed,
                spare_parts_availability=row["spare_parts_availability"],
                resale_value=float(row["resale_value"]),
                personal_data_present=bool(row["personal_data_present"]),
                data_erased=bool(row["data_erased"]),
                components=components,
                field_metadata=field_meta,
                notes=row["notes"] or ""
            )

    def list_devices(self, filter_type: Optional[str] = None) -> List[DeviceRecord]:
        """Lists all stored devices, optionally filtered by type."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            if filter_type:
                cursor.execute("SELECT device_id FROM devices WHERE device_type = ? ORDER BY device_id ASC;", (filter_type,))
            else:
                cursor.execute("SELECT device_id FROM devices ORDER BY device_id ASC;")
            rows = cursor.fetchall()

        results = []
        for r in rows:
            dev = self.get_device(r["device_id"])
            if dev:
                results.append(dev)
        return results

    def delete_device(self, device_id: str) -> bool:
        """Deletes a device and cascades to its components and recommendations."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM devices WHERE device_id = ?;", (device_id,))
            conn.commit()
            return cursor.rowcount > 0

    def save_recommendation(self, device_id: str, rec_data: Dict[str, Any]) -> int:
        """Saves an AI recommendation record."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
            INSERT INTO recommendations (
                device_id, recommended_action, feasible_options,
                fuzzy_scores, probability_estimates, utility_scores,
                safety_warnings, missing_information, rules_fired,
                explanation
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
            """, (
                device_id,
                rec_data.get("recommended_action", "unknown"),
                json.dumps(rec_data.get("feasible_options", [])),
                json.dumps(rec_data.get("fuzzy_scores", {})),
                json.dumps(rec_data.get("probability_estimates", {})),
                json.dumps(rec_data.get("expected_utility", rec_data.get("utility_scores", {}))),
                json.dumps(rec_data.get("safety_warnings", [])),
                json.dumps(rec_data.get("missing_information", [])),
                json.dumps(rec_data.get("rules_fired", [])),
                json.dumps(rec_data.get("explanation", []))
            ))
            conn.commit()
            return cursor.lastrowid

    def get_recommendations(self, device_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """Retrieves recommendation records."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            if device_id:
                cursor.execute("""
                SELECT * FROM recommendations WHERE device_id = ? ORDER BY created_at DESC;
                """, (device_id,))
            else:
                cursor.execute("SELECT * FROM recommendations ORDER BY created_at DESC;")
            rows = cursor.fetchall()

        results = []
        for r in rows:
            results.append({
                "id": r["id"],
                "device_id": r["device_id"],
                "recommended_action": r["recommended_action"],
                "feasible_options": json.loads(r["feasible_options"]),
                "fuzzy_scores": json.loads(r["fuzzy_scores"]),
                "probability_estimates": json.loads(r["probability_estimates"]),
                "utility_scores": json.loads(r["utility_scores"]),
                "safety_warnings": json.loads(r["safety_warnings"]),
                "missing_information": json.loads(r["missing_information"]),
                "rules_fired": json.loads(r["rules_fired"]),
                "explanation": json.loads(r["explanation"]),
                "created_at": r["created_at"],
            })
        return results

    def get_analytics_summary(self) -> Dict[str, Any]:
        """Computes summary statistics for dashboard reporting."""
        with self.get_connection() as conn:
            cursor = conn.cursor()

            cursor.execute("SELECT COUNT(*) AS total_devices FROM devices;")
            total_devices = cursor.fetchone()["total_devices"]

            cursor.execute("SELECT device_type, COUNT(*) as count FROM devices GROUP BY device_type;")
            by_type = {row["device_type"]: row["count"] for row in cursor.fetchall()}

            cursor.execute("SELECT recommended_action, COUNT(*) as count FROM recommendations GROUP BY recommended_action;")
            by_action = {row["recommended_action"]: row["count"] for row in cursor.fetchall()}

            cursor.execute("SELECT AVG(damage_severity) as avg_damage, SUM(replacement_cost) as total_val, SUM(repair_cost) as total_repair FROM devices;")
            stats = cursor.fetchone()

            avg_damage = round(stats["avg_damage"], 2) if stats["avg_damage"] is not None else 0.0
            total_replacement = round(stats["total_val"], 2) if stats["total_val"] is not None else 0.0
            total_repair_cost = round(stats["total_repair"], 2) if stats["total_repair"] is not None else 0.0

            cursor.execute("SELECT COUNT(*) as count FROM components WHERE is_working = 1;")
            recovered_components_count = cursor.fetchone()["count"]

            return {
                "total_devices": total_devices,
                "devices_by_type": by_type,
                "recommendations_by_action": by_action,
                "avg_damage_severity": avg_damage,
                "total_replacement_value": total_replacement,
                "total_repair_cost": total_repair_cost,
                "working_components_count": recovered_components_count
            }

    def seed_default_devices(self) -> None:
        """
        Seeds standard test scenarios described in the specification:
        1. LAP104: Illustrative specification example (damaged screen, working RAM/storage, low cost)
        2. DSK201: Working device needing no repair (direct reuse / donation)
        3. MOB305: Straightforward inexpensive repair (cracked glass only)
        4. TAB402: Expensive repair + low success probability (uneconomical, recycle/recovery)
        5. LAP550: Uneconomical repair but high component value (RAM, NVMe SSD, screen working)
        6. MOB611: Battery swollen safety hazard (blocks repair/donation, quarantine/recycle)
        7. PRN708: Working device containing sensitive personal data (requires sanitization)
        8. DEV812: Incomplete/missing repair data
        """
        samples = [
            # 1. LAP104 - Specification illustrative example
            DeviceRecord(
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
                resale_value=12000.0,
                personal_data_present=True,
                data_erased=False,
                components=[
                    ComponentInfo(name="RAM", is_working=True, estimated_value=2500.0, compatibility_notes="DDR4 16GB"),
                    ComponentInfo(name="storage", is_working=True, estimated_value=3000.0, compatibility_notes="512GB NVMe SSD"),
                    ComponentInfo(name="motherboard", is_working=True, estimated_value=8000.0),
                    ComponentInfo(name="screen", is_working=False, estimated_value=0.0, remarks="Cracked display panel"),
                    ComponentInfo(name="keyboard", is_working=True, estimated_value=800.0)
                ],
                notes="Specification benchmark laptop."
            ),
            # 2. DSK201 - Pristine working device
            DeviceRecord(
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
                spare_parts_availability=PartsAvailability.AVAILABLE.value,
                resale_value=28000.0,
                personal_data_present=False,
                data_erased=True,
                components=[
                    ComponentInfo(name="CPU", is_working=True, estimated_value=12000.0),
                    ComponentInfo(name="RAM", is_working=True, estimated_value=4000.0),
                    ComponentInfo(name="storage", is_working=True, estimated_value=3500.0),
                    ComponentInfo(name="power_supply", is_working=True, estimated_value=3000.0),
                    ComponentInfo(name="motherboard", is_working=True, estimated_value=9000.0)
                ],
                notes="Fully functional desktop computer, prime candidate for direct reuse or donation."
            ),
            # 3. MOB305 - Inexpensive repair
            DeviceRecord(
                device_id="MOB305",
                device_type=DeviceType.MOBILE_PHONE.value,
                age_years=1.5,
                damage_severity=25.0,
                repair_cost=1500.0,
                replacement_cost=20000.0,
                repair_success_probability=0.85,
                overall_condition=OverallCondition.GOOD.value,
                battery_condition=BatteryCondition.NORMAL.value,
                safety_check_passed=True,
                spare_parts_availability=PartsAvailability.AVAILABLE.value,
                resale_value=11000.0,
                personal_data_present=True,
                data_erased=False,
                components=[
                    ComponentInfo(name="screen", is_working=False, remarks="Cracked front glass, digitizer functional"),
                    ComponentInfo(name="motherboard", is_working=True, estimated_value=7000.0),
                    ComponentInfo(name="camera", is_working=True, estimated_value=2000.0),
                    ComponentInfo(name="battery", is_working=True, estimated_value=1200.0)
                ],
                notes="Minor screen damage with high repair feasibility and low cost."
            ),
            # 4. TAB402 - Expensive repair + low success probability
            DeviceRecord(
                device_id="TAB402",
                device_type=DeviceType.TABLET.value,
                age_years=6.0,
                damage_severity=85.0,
                repair_cost=14000.0,
                replacement_cost=15000.0,
                repair_success_probability=0.20,
                overall_condition=OverallCondition.BROKEN.value,
                battery_condition=BatteryCondition.DEGRADED.value,
                safety_check_passed=True,
                spare_parts_availability=PartsAvailability.SCARCE.value,
                resale_value=1000.0,
                personal_data_present=False,
                data_erased=True,
                components=[
                    ComponentInfo(name="motherboard", is_working=False, remarks="Severe water corrosion"),
                    ComponentInfo(name="screen", is_working=False, remarks="Shattered"),
                    ComponentInfo(name="battery", is_working=False, remarks="Depleted capacity")
                ],
                notes="Severe damage, parts scarce, repair uneconomical. Recycling recommended."
            ),
            # 5. LAP550 - Uneconomical whole repair, but excellent component recovery
            DeviceRecord(
                device_id="LAP550",
                device_type=DeviceType.LAPTOP.value,
                age_years=5.0,
                damage_severity=65.0,
                repair_cost=22000.0,
                replacement_cost=25000.0,
                repair_success_probability=0.35,
                overall_condition=OverallCondition.POOR.value,
                battery_condition=BatteryCondition.DEGRADED.value,
                safety_check_passed=True,
                spare_parts_availability=PartsAvailability.UNAVAILABLE.value,
                resale_value=4000.0,
                personal_data_present=True,
                data_erased=False,
                components=[
                    ComponentInfo(name="RAM", is_working=True, estimated_value=3000.0, compatibility_notes="32GB DDR4 SO-DIMM"),
                    ComponentInfo(name="storage", is_working=True, estimated_value=4500.0, compatibility_notes="1TB PCIe Gen4 SSD"),
                    ComponentInfo(name="wifi_card", is_working=True, estimated_value=900.0, compatibility_notes="Intel Wi-Fi 6 AX200"),
                    ComponentInfo(name="motherboard", is_working=False, remarks="Blown VRM chips"),
                    ComponentInfo(name="screen", is_working=False, remarks="Shattered hinge and display")
                ],
                notes="Chassis and motherboard unrepairable, but valuable high-grade RAM and SSD for harvesting."
            ),
            # 6. MOB611 - Swollen battery safety hazard
            DeviceRecord(
                device_id="MOB611",
                device_type=DeviceType.MOBILE_PHONE.value,
                age_years=3.0,
                damage_severity=70.0,
                repair_cost=2500.0,
                replacement_cost=18000.0,
                repair_success_probability=0.70,
                overall_condition=OverallCondition.POOR.value,
                battery_condition=BatteryCondition.SWOLLEN.value,
                safety_check_passed=False,
                spare_parts_availability=PartsAvailability.AVAILABLE.value,
                resale_value=5000.0,
                personal_data_present=False,
                data_erased=True,
                components=[
                    ComponentInfo(name="battery", is_working=False, remarks="Hazardously bulging lithium polymer pack"),
                    ComponentInfo(name="motherboard", is_working=True, estimated_value=5000.0),
                    ComponentInfo(name="screen", is_working=True, estimated_value=3000.0)
                ],
                notes="CRITICAL: Swollen battery blocks all reuse/repair until professional hazmat resolution."
            ),
            # 7. PRN708 - Printer with personal data in flash memory
            DeviceRecord(
                device_id="PRN708",
                device_type=DeviceType.PRINTER.value,
                age_years=3.5,
                damage_severity=10.0,
                repair_cost=500.0,
                replacement_cost=12000.0,
                repair_success_probability=0.95,
                overall_condition=OverallCondition.GOOD.value,
                battery_condition=BatteryCondition.NOT_APPLICABLE.value,
                safety_check_passed=True,
                spare_parts_availability=PartsAvailability.AVAILABLE.value,
                resale_value=6000.0,
                personal_data_present=True,
                data_erased=False,
                components=[
                    ComponentInfo(name="printhead", is_working=True, estimated_value=3000.0),
                    ComponentInfo(name="logic_board", is_working=True, estimated_value=2500.0),
                    ComponentInfo(name="feed_rollers", is_working=True, estimated_value=800.0)
                ],
                notes="Functional network printer with stored spool logs and confidential documents."
            ),
            # 8. DEV812 - Missing / unknown repair info
            DeviceRecord(
                device_id="DEV812",
                device_type=DeviceType.OTHER.value,
                age_years=5.0,
                damage_severity=30.0,
                repair_cost=None,  # Unknown
                replacement_cost=10000.0,
                repair_success_probability=None,  # Unknown
                overall_condition=OverallCondition.FAIR.value,
                battery_condition=BatteryCondition.NORMAL.value,
                safety_check_passed=None,  # Uninspected
                spare_parts_availability=PartsAvailability.UNKNOWN.value,
                resale_value=2000.0,
                personal_data_present=False,
                data_erased=False,
                components=[],
                field_metadata={"repair_cost": "unknown", "safety_check": "unknown"},
                notes="Uninspected device with incomplete diagnostic parameters."
            ),
        ]

        for sample in samples:
            self.save_device(sample)
