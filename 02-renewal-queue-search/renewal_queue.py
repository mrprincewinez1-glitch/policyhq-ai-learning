"""
PolicyHQ Renewal Queue - search & priority problem
----------------------------------------------------
Input:   a list of policies (id, days_until_expiry, premium_value in GHS,
          contact_attempts already made)
Output:  the order an agent should call them in, each with a priority
          score and a plain-English reason for its rank
Benefit: agents stop guessing who to call next; the queue protects the
          most renewal revenue per hour worked and avoids re-hounding
          clients who already didn't pick up.

This models the call queue the way CS50AI's Search project models a
frontier: each policy is a "node", the priority score is that node's
cost, and a min-heap priority queue always expands the lowest-cost node
next - a greedy best-first search over "who to call next".
"""

import heapq
from dataclasses import dataclass
from typing import List, Tuple

URGENCY_TIER_DAYS = 7
TIER_WEIGHT = 1_000_000


@dataclass
class Policy:
    policy_id: str
    days_until_expiry: int
    premium_value: float
    contact_attempts: int = 0


def urgency_tier(p: Policy) -> int:
    return max(p.days_until_expiry, 0) // URGENCY_TIER_DAYS


def priority_score(p: Policy) -> float:
    return (urgency_tier(p) * TIER_WEIGHT
            - p.premium_value
            + p.contact_attempts * 50)


def explain_score(p: Policy) -> str:
    tier = urgency_tier(p)
    window_start, window_end = tier * URGENCY_TIER_DAYS, tier * URGENCY_TIER_DAYS + 6
    return (f"tier {tier} ({window_start}-{window_end} days out), "
            f"GHS {p.premium_value:.0f} premium, "
            f"{p.contact_attempts} prior attempts")


def build_call_queue(policies: List[Policy]) -> List[Tuple[float, Policy]]:
    frontier = []
    for p in policies:
        heapq.heappush(frontier, (priority_score(p), p.policy_id, p))

    ordered = []
    while frontier:
        score, _, p = heapq.heappop(frontier)
        ordered.append((score, p))
    return ordered


def print_call_queue(policies: List[Policy]):
    queue = build_call_queue(policies)
    print("\nCall queue (highest priority first):")
    for rank, (score, p) in enumerate(queue, start=1):
        print(f"  {rank}. {p.policy_id:<10} -> {explain_score(p)}")
    return queue


if __name__ == "__main__":
    policies = [
        Policy("MOT-2201",  days_until_expiry=5,  premium_value=1200, contact_attempts=0),
        Policy("LIFE-0087", days_until_expiry=20, premium_value=4000, contact_attempts=1),
        Policy("MOT-1190",  days_until_expiry=12, premium_value=600,  contact_attempts=3),
        Policy("HEALTH-33", days_until_expiry=3,  premium_value=300,  contact_attempts=0),
        Policy("MOT-0456",  days_until_expiry=28, premium_value=9000, contact_attempts=0),
    ]
    print_call_queue(policies)
