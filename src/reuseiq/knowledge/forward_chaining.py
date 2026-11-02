"""
ReUseIQ - Forward Chaining Inference Engine

Performs data-driven forward deduction starting from initial device facts,
iteratively evaluating domain rules, resolving variable bindings, and tracking
a complete explanation trace of all rule firings.
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Set, Tuple

from reuseiq.knowledge.predicates import Fact, Predicate, Rule, RuleFiringTrace, unify


@dataclass
class ForwardInferenceResult:
    """Encapsulates the complete outcome of forward chaining inference."""
    device_id: str
    all_facts: Set[Predicate]
    rule_traces: List[RuleFiringTrace]
    eligible_actions: List[str]
    prohibited_actions: List[str]
    mandatory_actions: List[str]
    safety_warnings: List[str]
    explanations: Dict[str, str]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "device_id": self.device_id,
            "eligible_actions": self.eligible_actions,
            "prohibited_actions": self.prohibited_actions,
            "mandatory_actions": self.mandatory_actions,
            "safety_warnings": self.safety_warnings,
            "rule_traces": [t.to_dict() for t in self.rule_traces],
            "total_facts_known": len(self.all_facts),
        }


class ForwardChainingEngine:
    """Forward chaining inference engine with priority scheduling and trace logging."""

    def __init__(self, rules: Optional[List[Rule]] = None):
        from reuseiq.knowledge.rules import get_standard_rules
        self.rules = sorted(
            rules if rules is not None else get_standard_rules(),
            key=lambda r: r.priority,
            reverse=True
        )

    def _match_antecedents(
        self,
        antecedents: List[Predicate],
        facts: Set[Predicate],
        bindings: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Recursively matches a list of antecedent patterns against facts,
        yielding all possible consistent variable binding sets.
        """
        if not antecedents:
            return [bindings]

        first = antecedents[0]
        rest = antecedents[1:]
        results: List[Dict[str, Any]] = []

        if first.is_negated:
            # Negation as failure: substitute existing bindings and check that NO ground fact matches
            subbed = first.substitute(bindings)
            # Check if any fact in knowledge base matches subbed pattern (negation disregarded)
            positive_pattern = Predicate(subbed.name, *subbed.args, is_negated=False)
            has_match = False
            for f in facts:
                if unify(positive_pattern, f, bindings) is not None:
                    has_match = True
                    break
            if not has_match:
                # Negation holds, proceed to remaining antecedents
                results.extend(self._match_antecedents(rest, facts, bindings))
        else:
            for f in facts:
                new_bindings = unify(first, f, bindings)
                if new_bindings is not None:
                    results.extend(self._match_antecedents(rest, facts, new_bindings))

        return results

    def infer(self, initial_facts: List[Fact], device_id: str) -> ForwardInferenceResult:
        """
        Executes forward chaining starting with initial_facts until no new facts are derived.
        """
        known_facts: Set[Predicate] = set(initial_facts)
        rule_traces: List[RuleFiringTrace] = []
        step_counter = 1
        fired_instances: Set[Tuple[str, Tuple[Tuple[str, Any], ...]]] = set()

        changed = True
        max_iterations = 50
        iteration = 0

        while changed and iteration < max_iterations:
            changed = False
            iteration += 1

            for rule in self.rules:
                # Find all valid variable bindings for this rule's antecedents
                binding_solutions = self._match_antecedents(rule.antecedents, known_facts, {})

                for bindings in binding_solutions:
                    # Create signature to prevent duplicate firing of the same rule instance
                    binding_sig = (rule.rule_id, tuple(sorted(bindings.items())))
                    if binding_sig in fired_instances:
                        continue

                    # Instantiate consequents
                    derived = [c.substitute(bindings) for c in rule.consequents]
                    new_derived = [d for d in derived if d not in known_facts]

                    if new_derived:
                        # Record rule firing
                        matched = [
                            a.substitute(bindings)
                            for a in rule.antecedents
                            if not a.is_negated
                        ]

                        trace = RuleFiringTrace(
                            step=step_counter,
                            rule_id=rule.rule_id,
                            rule_name=rule.name,
                            category=rule.category,
                            bindings=bindings,
                            matched_facts=matched,
                            derived_facts=new_derived,
                            explanation=rule.description
                        )
                        rule_traces.append(trace)
                        step_counter += 1

                        # Assert new facts into the knowledge base
                        for d in new_derived:
                            known_facts.add(d)

                        fired_instances.add(binding_sig)
                        changed = True

        # Extract derived results
        eligible: List[str] = []
        prohibited: Set[str] = set()
        mandatory: List[str] = []
        safety_warnings: List[str] = []
        explanations: Dict[str, str] = {}

        for f in known_facts:
            if f.name == "ProhibitAction" and len(f.args) >= 2:
                prohibited.add(str(f.args[1]))
            elif f.name == "MandatoryAction" and len(f.args) >= 2:
                mandatory.append(str(f.args[1]))
            elif f.name in {"SafetyHazardWarning", "SafetyWarning", "DataSecurityWarning"} and len(f.args) >= 2:
                safety_warnings.append(f"{f.name}: {f.args[1]}")
            elif f.name == "FeasibleExplanation" and len(f.args) >= 3:
                explanations[str(f.args[1])] = str(f.args[2])

        for f in known_facts:
            if f.name == "EligibleAction" and len(f.args) >= 2:
                action = str(f.args[1])
                # Safety filtering: Prohibited actions can never be eligible
                if action not in prohibited and action not in eligible:
                    eligible.append(action)

        # If mandatory action exists (e.g. recycle due to safety), enforce it
        if mandatory:
            for m in mandatory:
                if m not in eligible:
                    eligible.append(m)
            # Remove non-mandatory actions if critical hazard
            if any("CRITICAL" in w or "Hazard" in w for w in safety_warnings):
                eligible = [m for m in eligible if m in mandatory]

        return ForwardInferenceResult(
            device_id=device_id,
            all_facts=known_facts,
            rule_traces=rule_traces,
            eligible_actions=eligible,
            prohibited_actions=list(prohibited),
            mandatory_actions=mandatory,
            safety_warnings=safety_warnings,
            explanations=explanations
        )
