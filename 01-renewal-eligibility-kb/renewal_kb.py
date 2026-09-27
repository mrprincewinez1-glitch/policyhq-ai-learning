"""
PolicyHQ Renewal & Eligibility Knowledge Base
----------------------------------------------
Input:   a policy record (days_until_expiry, premium_paid, contact_valid)
Output:  the set of derived facts (e.g. "eligible_for_reminder", "urgent_renewal")
         PLUS a human-readable explanation trace showing which rule fired,
         from which facts, and why.
Benefit: agents (and support staff) can see WHY a policy was or wasn't
         flagged for renewal outreach, instead of trusting a black-box flag.

This is a small forward-chaining propositional rule engine, in the spirit
of CS50AI's "Knowledge" project (facts + rules -> new knowledge), applied
to a real PolicyHQ decision: who gets a renewal reminder.
"""

from dataclasses import dataclass
from typing import Set, Dict, List


@dataclass
class Rule:
    name: str
    requires: Set[str]                 # facts that must all be true
    forbids: Set[str]                  # facts that must all be false
    conclusion: str                    # fact added if the rule fires
    why: str                           # human-readable explanation template


class KnowledgeBase:
    def __init__(self, rules: List[Rule]):
        self.rules = rules

    def infer(self, facts: Set[str]) -> Dict[str, List[str]]:
        """
        Forward-chain to a fixpoint. Returns {derived_fact: [explanation, ...]}
        so every conclusion carries the reasoning that produced it.
        """
        known = set(facts)
        explanations: Dict[str, List[str]] = {}
        changed = True

        while changed:
            changed = False
            for rule in self.rules:
                if rule.conclusion in known:
                    continue
                if rule.requires <= known and not (rule.forbids & known):
                    known.add(rule.conclusion)
                    trace = f"{rule.name}: {rule.why}"
                    explanations.setdefault(rule.conclusion, []).append(trace)
                    changed = True

        return explanations


def build_input_facts(days_until_expiry: int, premium_paid: bool, contact_valid: bool) -> Set[str]:
    facts = set()
    if days_until_expiry <= 30:
        facts.add("in_renewal_window")
    if days_until_expiry <= 7:
        facts.add("within_7_days")
    if premium_paid:
        facts.add("premium_paid")
    if contact_valid:
        facts.add("contact_valid")
    return facts


RULES = [
    Rule(
        name="R1_renewal_pending",
        requires={"in_renewal_window"},
        forbids={"premium_paid"},
        conclusion="renewal_pending",
        why="policy is within its 30-day renewal window and premium is unpaid",
    ),
    Rule(
        name="R2_eligible_for_reminder",
        requires={"renewal_pending", "contact_valid"},
        forbids=set(),
        conclusion="eligible_for_reminder",
        why="renewal is pending and the client's contact details are valid",
    ),
    Rule(
        name="R3_flagged_missing_contact",
        requires={"renewal_pending"},
        forbids={"contact_valid"},
        conclusion="flagged_missing_contact",
        why="renewal is pending but no valid contact channel is on file",
    ),
    Rule(
        name="R4_urgent_renewal",
        requires={"renewal_pending", "within_7_days"},
        forbids=set(),
        conclusion="urgent_renewal",
        why="renewal is pending and expiry is 7 days away or less",
    ),
]


def explain_policy(policy_id: str, days_until_expiry: int, premium_paid: bool, contact_valid: bool):
    kb = KnowledgeBase(RULES)
    facts = build_input_facts(days_until_expiry, premium_paid, contact_valid)
    derived = kb.infer(facts)

    print(f"\nPolicy {policy_id}")
    print(f"  input facts: {sorted(facts) or '(none)'}")
    if not derived:
        print("  derived: (no rules fired -- policy is not in the renewal window, "
              "or premium is already paid)")
        return derived

    for fact, reasons in derived.items():
        print(f"  -> {fact}")
        for r in reasons:
            print(f"       because {r}")
    return derived


if __name__ == "__main__":
    explain_policy("MOT-2201", days_until_expiry=5, premium_paid=False, contact_valid=True)
    explain_policy("LIFE-0087", days_until_expiry=20, premium_paid=False, contact_valid=False)
    explain_policy("MOT-1190", days_until_expiry=12, premium_paid=True, contact_valid=True)
