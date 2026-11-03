"""
ReUseIQ - Backward Chaining Inference Engine

Provides goal-directed reasoning to answer diagnostic queries such as:
- "Why was Repair recommended / feasible?"
- "Why was Reuse prohibited?"
- "Is device X safe for donation?"
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Set, Tuple

from reuseiq.knowledge.predicates import Fact, Predicate, Rule, unify


@dataclass
class ProofNode:
    """Represents a node in a backward-chaining proof tree."""
    goal: Predicate
    is_proved: bool
    rule_used: Optional[Rule] = None
    supporting_facts: List[Predicate] = field(default_factory=list)
    subproofs: List["ProofNode"] = field(default_factory=list)
    explanation: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "goal": str(self.goal),
            "proved": self.is_proved,
            "rule": self.rule_used.rule_id if self.rule_used else None,
            "supporting_facts": [str(f) for f in self.supporting_facts],
            "explanation": self.explanation,
            "subproofs": [s.to_dict() for s in self.subproofs]
        }

    def format_tree(self, indent: int = 0) -> str:
        prefix = "  " * indent
        status = "✓ PROVED" if self.is_proved else "✗ FAILED"
        rule_str = f" [via {self.rule_used.rule_id}]" if self.rule_used else ""
        lines = [f"{prefix}{status}: {self.goal}{rule_str}"]
        if self.explanation:
            lines.append(f"{prefix}  Detail: {self.explanation}")
        for s in self.subproofs:
            lines.append(s.format_tree(indent + 1))
        return "\n".join(lines)


class BackwardChainingEngine:
    """Goal-directed theorem prover with proof tree generation."""

    def __init__(self, rules: Optional[List[Rule]] = None):
        from reuseiq.knowledge.rules import get_standard_rules
        self.rules = rules if rules is not None else get_standard_rules()

    def prove(
        self,
        goal: Predicate,
        facts: Set[Predicate],
        visited_goals: Optional[Set[Predicate]] = None
    ) -> ProofNode:
        """
        Attempts to prove a goal predicate from known facts and rules.
        Returns a ProofNode detailing the proof tree.
        """
        if visited_goals is None:
            visited_goals = set()

        # Check for cyclic goal loops
        if goal in visited_goals:
            return ProofNode(
                goal=goal,
                is_proved=False,
                explanation="Cycle detected in goal resolution."
            )

        new_visited = visited_goals | {goal}

        # 1. Base case: Goal is directly asserted as a known fact
        for f in facts:
            bindings = unify(goal, f, {})
            if bindings is not None:
                return ProofNode(
                    goal=goal,
                    is_proved=True,
                    supporting_facts=[f],
                    explanation=f"Directly asserted in knowledge base: {f}"
                )

        # 2. Check if any rule consequents unify with the goal
        for rule in self.rules:
            for consequent in rule.consequents:
                bindings = unify(consequent, goal, {})
                if bindings is None:
                    continue

                # Rule might conclude the goal. Attempt to prove all antecedents.
                all_proved = True
                subproofs: List[ProofNode] = []

                for ant in rule.antecedents:
                    instantiated_ant = ant.substitute(bindings)

                    if instantiated_ant.is_negated:
                        # Negation as failure: Subproof must FAIL to prove positive counterpart
                        positive_goal = Predicate(
                            instantiated_ant.name,
                            *instantiated_ant.args,
                            is_negated=False
                        )
                        neg_sub = self.prove(positive_goal, facts, new_visited)
                        if neg_sub.is_proved:
                            all_proved = False
                            subproofs.append(ProofNode(
                                goal=instantiated_ant,
                                is_proved=False,
                                explanation=f"Negation failed because {positive_goal} holds."
                            ))
                            break
                        else:
                            subproofs.append(ProofNode(
                                goal=instantiated_ant,
                                is_proved=True,
                                explanation=f"Negation satisfied: {positive_goal} cannot be proved."
                            ))
                    else:
                        sub = self.prove(instantiated_ant, facts, new_visited)
                        subproofs.append(sub)
                        if not sub.is_proved:
                            all_proved = False
                            break

                if all_proved:
                    return ProofNode(
                        goal=goal,
                        is_proved=True,
                        rule_used=rule,
                        subproofs=subproofs,
                        explanation=f"Proved by rule {rule.rule_id} ({rule.name}): {rule.description}"
                    )

        # 3. Could not prove goal
        return ProofNode(
            goal=goal,
            is_proved=False,
            explanation=f"No applicable rule or fact proved {goal}."
        )

    def explain_query(self, goal: Predicate, facts: Set[Predicate]) -> str:
        """Returns human-readable text explaining the query resolution."""
        node = self.prove(goal, facts)
        return node.format_tree()
