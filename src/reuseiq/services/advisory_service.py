"""
ReUseIQ - Advisory Service (Core Integration Orchestrator)

Integrates Person 2's Knowledge Base, Predicate Logic, and Forward/Backward Chaining
with Person 1's Fuzzy, Probability, Utility, and Decision Engines to deliver
comprehensive, explainable e-waste decisions.
"""

from typing import Any, Dict, List, Optional, Tuple

from reuseiq.data.database import DatabaseManager
from reuseiq.data.models import (
    BatteryCondition,
    DeviceRecord,
    PartsAvailability,
    SafetyStatus,
)
from reuseiq.knowledge.backward_chaining import BackwardChainingEngine
from reuseiq.knowledge.forward_chaining import ForwardChainingEngine, ForwardInferenceResult
from reuseiq.knowledge.predicates import Predicate
from reuseiq.knowledge.rules import device_to_facts
from reuseiq.reasoning.decision_engine import DecisionEngine
from reuseiq.reasoning.explanation import ExplanationEngine
from reuseiq.reasoning.fuzzy_engine import FuzzyEngine
from reuseiq.reasoning.probability_engine import ProbabilityEngine
from reuseiq.reasoning.utility_engine import UtilityEngine


class AdvisoryService:
    """End-to-end advisor combining symbolic rules with uncertainty and utility reasoning."""

    def __init__(self, db_manager: Optional[DatabaseManager] = None):
        self.db = db_manager if db_manager is not None else DatabaseManager()
        self.forward_engine = ForwardChainingEngine()
        self.backward_engine = BackwardChainingEngine()

        # Person 1 reasoning components
        self.fuzzy_engine = FuzzyEngine()
        self.prob_engine = ProbabilityEngine()
        self.utility_engine = UtilityEngine()
        self.decision_engine = DecisionEngine()
        self.explanation_engine = ExplanationEngine()

    def evaluate_device(
        self,
        device: DeviceRecord,
        save_result: bool = True
    ) -> Dict[str, Any]:
        """
        Executes the full symbolic reasoning and decision evaluation pipeline for a device.
        Returns a structured result conforming to Section 6 of the project specification.
        """
        # Step 1: Extract ground predicate logic facts
        facts = device_to_facts(device)

        # Step 2: Execute forward chaining inference
        inference: ForwardInferenceResult = self.forward_engine.infer(
            initial_facts=facts,
            device_id=device.device_id
        )

        # Step 3: Identify missing information
        missing_info = device.get_missing_information()

        # Step 4: Fuzzy Logic Reasoning
        norm_damage = min(max(device.damage_severity / 100.0, 0.0), 1.0)
        cost_ratio = device.repair_cost_ratio
        ratio_is_estimated = False
        if cost_ratio is None:
            # Fallback estimate when repair cost is unknown
            cost_ratio = 0.50
            ratio_is_estimated = True

        fuzzy_repairability = self.fuzzy_engine.calculate_repairability(
            damage=norm_damage,
            repair_cost_ratio=cost_ratio
        )
        damage_memberships = self.fuzzy_engine.get_memberships(norm_damage)
        cost_memberships = self.fuzzy_engine.get_memberships(min(cost_ratio, 1.0))

        fuzzy_scores = {
            "repairability": fuzzy_repairability,
            "damage_membership": {k: round(v, 3) for k, v in damage_memberships.items()},
            "cost_ratio_membership": {k: round(v, 3) for k, v in cost_memberships.items()},
            "cost_ratio_used": round(cost_ratio, 4),
            "ratio_is_estimated": ratio_is_estimated
        }

        # Step 5: Probabilistic Reasoning (Bayesian & Risk)
        if device.repair_success_probability is not None:
            # If repair_success_probability is explicitly given, the failure prob is 1 - P(success)
            failure_prob = round(1.0 - device.repair_success_probability, 4)
            prob_is_estimated = False
        else:
            # Illustrative fallback estimate
            failure_prob = 0.35
            prob_is_estimated = True

        risk_category = self.prob_engine.classify_risk(failure_prob)
        prob_estimates = {
            "failure_probability": round(failure_prob, 4),
            "success_probability": round(1.0 - failure_prob, 4),
            "risk_classification": risk_category,
            "is_estimated_fallback": prob_is_estimated
        }

        # Step 6: Multi-Criteria Utility Calculation for Candidate Actions
        # Calculate scores for all domain options: repair, refurbish, component_recovery, donate_reuse, recycle
        candidate_scores = self._calculate_option_scores(
            device=device,
            repairability=fuzzy_repairability,
            failure_prob=failure_prob
        )

        # Calculate weighted utility for each option using Person 1's UtilityEngine
        utility_scores = self.utility_engine.compare_options(candidate_scores)

        # Step 7: Apply Safety Constraints and Decision Theory
        safety_status = device.safety_status_str
        feasible_options = inference.eligible_actions
        safety_warnings = list(inference.safety_warnings)

        if device.battery_condition == BatteryCondition.SWOLLEN.value:
            safety_warnings.append("CRITICAL: Swollen battery detected. Device quarantined.")

        # Filter utility scores only to feasible options
        feasible_utilities = {
            opt: utility_scores[opt]
            for opt in feasible_options
            if opt in utility_scores
        }

        # Determine recommended action
        if safety_status == SafetyStatus.UNSAFE.value:
            recommended_action = "recycle"
            selection_reason = (
                "Safety constraints take absolute priority: The device is marked unsafe "
                "(safety hazard detected). Ordinary repair and reuse pathways are prohibited. "
                "Immediate routing to an authorized hazardous e-waste recycler is required."
            )
        elif safety_status == SafetyStatus.UNKNOWN.value and not feasible_utilities:
            recommended_action = "safety_assessment_required"
            selection_reason = (
                "Safety status is unknown and uninspected. "
                "Qualified safety testing is required before repair, donation, or refurbishment can proceed."
            )
        elif feasible_utilities:
            # Sort feasible options by utility descending
            sorted_feasible = sorted(
                feasible_utilities.items(),
                key=lambda x: x[1],
                reverse=True
            )
            recommended_action = sorted_feasible[0][0]
            top_score = sorted_feasible[0][1]
            selection_reason = (
                f"{recommended_action.replace('_', ' ').title()} achieved the highest expected utility "
                f"({top_score}/100) among all safe and legally eligible options."
            )
        else:
            recommended_action = "recycle"
            selection_reason = "No alternative repair or reuse options met eligibility thresholds. Safe recycling selected as default."

        # Step 8: Build Detailed Structured Explanation
        explanation_paragraphs = self._build_explanation(
            device=device,
            recommended_action=recommended_action,
            feasible_options=feasible_options,
            prohibited_actions=inference.prohibited_actions,
            selection_reason=selection_reason,
            fuzzy_repairability=fuzzy_repairability,
            failure_prob=failure_prob,
            utility_scores=feasible_utilities,
            safety_warnings=safety_warnings,
            missing_info=missing_info,
            rules_fired=inference.rule_traces
        )

        # Build final structured output according to Section 6 format
        result: Dict[str, Any] = {
            "device_id": device.device_id,
            "recommended_action": recommended_action,
            "feasible_options": feasible_options,
            "fuzzy_scores": fuzzy_scores,
            "probability_estimates": prob_estimates,
            "expected_utility": feasible_utilities,
            "all_option_utilities": utility_scores,
            "safety_warnings": safety_warnings,
            "missing_information": missing_info,
            "rules_fired": [t.to_dict() for t in inference.rule_traces],
            "explanation": explanation_paragraphs
        }

        # Step 9: Persist recommendation to database if requested
        if save_result:
            try:
                self.db.save_recommendation(device.device_id, result)
            except Exception:
                pass

        return result

    def _calculate_option_scores(
        self,
        device: DeviceRecord,
        repairability: float,
        failure_prob: float
    ) -> Dict[str, Dict[str, float]]:
        """
        Calculates normalized economic, environmental, and life-extension scores (0-100)
        for each possible action according to domain facts and calculations.
        """
        # Economic score for repair: higher when repair cost is small fraction of replacement
        ratio = device.repair_cost_ratio or 0.5
        repair_economic = max(0.0, min(100.0, (1.0 - ratio) * 100.0))
        # Environmental score for repair: keeps device out of landfill
        repair_env = max(0.0, min(100.0, 95.0 - (device.damage_severity * 0.2)))
        # Life extension for repair
        repair_life = max(0.0, min(100.0, (1.0 - failure_prob) * 100.0))

        # Refurbish - higher process overhead than simple component repair
        refurb_economic = max(0.0, min(100.0, repair_economic * 0.75))
        refurb_env = 82.0
        refurb_life = max(0.0, min(100.0, (1.0 - failure_prob) * 92.0))

        # Component Recovery
        # Value depends on working harvestable components
        working_val = sum(c.estimated_value for c in device.components if c.is_working and c.is_reusable)
        comp_economic = min(100.0, max(20.0, (working_val / max(device.replacement_cost * 0.5, 1000.0)) * 100.0))
        comp_env = 75.0  # Spares manufactured components from landfill
        comp_life = 50.0

        # Donate / Direct Reuse
        resale_ratio = device.resale_value / max(device.replacement_cost, 1000.0)
        reuse_economic = min(100.0, max(30.0, resale_ratio * 100.0))
        reuse_env = 95.0  # Maximum circular economy benefit
        reuse_life = max(20.0, min(95.0, (10.0 - min(device.age_years, 8.0)) * 10.0))

        # Recycle
        recycle_economic = 40.0  # Raw material scrap value
        recycle_env = 80.0       # Material recovery prevents toxic leaching
        recycle_life = 20.0      # End of life for this unit

        return {
            "repair": {
                "economic": round(repair_economic, 1),
                "environmental": round(repair_env, 1),
                "life_extension": round(repair_life, 1)
            },
            "refurbish": {
                "economic": round(refurb_economic, 1),
                "environmental": round(refurb_env, 1),
                "life_extension": round(refurb_life, 1)
            },
            "component_recovery": {
                "economic": round(comp_economic, 1),
                "environmental": round(comp_env, 1),
                "life_extension": round(comp_life, 1)
            },
            "donate_reuse": {
                "economic": round(reuse_economic, 1),
                "environmental": round(reuse_env, 1),
                "life_extension": round(reuse_life, 1)
            },
            "recycle": {
                "economic": round(recycle_economic, 1),
                "environmental": round(recycle_env, 1),
                "life_extension": round(recycle_life, 1)
            }
        }

    def _build_explanation(
        self,
        device: DeviceRecord,
        recommended_action: str,
        feasible_options: List[str],
        prohibited_actions: List[str],
        selection_reason: str,
        fuzzy_repairability: float,
        failure_prob: float,
        utility_scores: Dict[str, float],
        safety_warnings: List[str],
        missing_info: List[str],
        rules_fired: List[Any]
    ) -> List[str]:
        """Builds an understandable, transparent audit trail explanation."""
        lines: List[str] = []

        action_name = recommended_action.replace("_", " ").title()
        lines.append(f"**Recommended Action**: {action_name}. {selection_reason}")

        # Core logic highlights
        lines.append(
            f"**Fuzzy Repairability Score**: {fuzzy_repairability}/100. "
            f"(Evaluated using damage severity of {device.damage_severity}/100 and repair cost ratio of {device.repair_cost_ratio or 'N/A'})."
        )

        lines.append(
            f"**Probabilistic Risk**: Estimated failure probability after repair is {failure_prob * 100:.1f}%. "
            f"(Implies an estimated { (1.0 - failure_prob) * 100:.1f}% probability of successful operation)."
        )

        # Expected utility rankings
        if utility_scores:
            ranking_parts = [f"{opt.replace('_', ' ').title()}: {score}/100" for opt, score in utility_scores.items()]
            lines.append(f"**Expected Utility Ranking**: {', '.join(ranking_parts)}.")

        # Feasible vs rejected options
        if feasible_options:
            alt_options = [o.replace('_', ' ').title() for o in feasible_options if o != recommended_action]
            if alt_options:
                lines.append(f"**Feasible Alternatives**: {', '.join(alt_options)} are viable under current constraints but scored lower in overall expected utility.")

        if prohibited_actions:
            prohib_names = [p.replace('_', ' ').title() for p in prohibited_actions]
            lines.append(f"**Prohibited / Disqualified Options**: {', '.join(prohib_names)} were blocked by domain rules prior to ranking.")

        # Safety & warnings
        if safety_warnings:
            lines.append(f"**Safety Warnings**: {'; '.join(safety_warnings)}.")

        # Missing information alert
        if missing_info:
            lines.append(f"**Missing Information Alert**: {'; '.join(missing_info)}. Note: Missing parameters used illustrative fallback estimates and should be confirmed.")

        # Explain why specific rules fired
        fired_summary = [f"{r.rule_id} ({r.rule_name})" for r in rules_fired[:4]]
        if fired_summary:
            lines.append(f"**Key Symbolic Rules Triggered**: {', '.join(fired_summary)}.")

        return lines
