"""
ReUseIQ - First-Order Predicate Logic Representation

Provides explicit logical primitives:
- Predicate: Logical relation with symbol and terms (constants or variables)
- Fact: Ground predicate (terms are concrete constants)
- Rule: Logical IF-THEN implication with antecedents and consequents
- Unification and variable substitution for symbolic inference
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple, Set, Union


def is_variable(term: str) -> bool:
    """Variables in predicate patterns start with '?' e.g. '?dev', '?comp'."""
    return isinstance(term, str) and term.startswith("?")


@dataclass(frozen=True)
class Predicate:
    """
    First-order logical predicate, e.g.
    Device(?dev), HasComponent(?dev, RAM), Working(?comp), SafetyCheckPassed(?dev).
    """
    name: str
    args: Tuple[Any, ...] = field(default_factory=tuple)
    is_negated: bool = False

    def __init__(self, name: str, *args: Any, is_negated: bool = False):
        object.__setattr__(self, "name", name)
        # Convert any list/set args to tuple for hashability
        cleaned_args = tuple(str(a) if not isinstance(a, (int, float, bool, str)) else a for a in args)
        object.__setattr__(self, "args", cleaned_args)
        object.__setattr__(self, "is_negated", is_negated)

    def is_ground(self) -> bool:
        """Returns True if none of the arguments are pattern variables."""
        return not any(is_variable(arg) for arg in self.args)

    def substitute(self, bindings: Dict[str, Any]) -> "Predicate":
        """Applies variable substitutions to produce a new predicate."""
        new_args = []
        for arg in self.args:
            if is_variable(arg) and arg in bindings:
                new_args.append(bindings[arg])
            else:
                new_args.append(arg)
        return Predicate(self.name, *new_args, is_negated=self.is_negated)

    def __repr__(self) -> str:
        prefix = "NOT " if self.is_negated else ""
        args_str = ", ".join(str(a) for a in self.args)
        return f"{prefix}{self.name}({args_str})"


class Fact(Predicate):
    """A ground logical fact whose truth is asserted in the Knowledge Base."""
    def __init__(self, name: str, *args: Any, is_negated: bool = False):
        super().__init__(name, *args, is_negated=is_negated)
        if not self.is_ground():
            raise ValueError(f"Fact must be ground (no variables permitted): {self}")


def unify(pattern: Predicate, target: Predicate, bindings: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """
    Unifies a predicate pattern containing variables with a target predicate.
    Returns an updated bindings dictionary, or None if unification fails.
    """
    if pattern.name != target.name:
        return None
    if pattern.is_negated != target.is_negated:
        return None
    if len(pattern.args) != len(target.args):
        return None

    new_bindings = dict(bindings)

    for p_arg, t_arg in zip(pattern.args, target.args):
        if is_variable(p_arg):
            if p_arg in new_bindings:
                if new_bindings[p_arg] != t_arg:
                    return None
            else:
                new_bindings[p_arg] = t_arg
        else:
            # Constant matching
            if p_arg != t_arg:
                return None

    return new_bindings


@dataclass
class Rule:
    """
    Logical IF-THEN implication rule.
    IF antecedents (all hold) THEN consequents (are derived).
    """
    rule_id: str
    name: str
    antecedents: List[Predicate]
    consequents: List[Predicate]
    priority: int = 10  # Higher priority rules evaluated first (e.g. safety = 100)
    category: str = "general"
    description: str = ""

    def __repr__(self) -> str:
        antecedents_str = " AND ".join(str(a) for a in self.antecedents)
        consequents_str = " AND ".join(str(c) for c in self.consequents)
        return f"[{self.rule_id}] IF {antecedents_str} THEN {consequents_str}"


@dataclass
class RuleFiringTrace:
    """Records one execution of a rule during inference."""
    step: int
    rule_id: str
    rule_name: str
    category: str
    bindings: Dict[str, Any]
    matched_facts: List[Predicate]
    derived_facts: List[Predicate]
    explanation: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "step": self.step,
            "rule_id": self.rule_id,
            "rule_name": self.rule_name,
            "category": self.category,
            "bindings": self.bindings,
            "matched_facts": [str(f) for f in self.matched_facts],
            "derived_facts": [str(f) for f in self.derived_facts],
            "explanation": self.explanation
        }
