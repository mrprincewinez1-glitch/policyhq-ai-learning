"""
PolicyHQ Confidence & Human-Approval Thresholds
------------------------------------------------
Input:   an automated decision's confidence score (0-1) and its risk_tier
         -- e.g. Lapse Shield's commission-figure extraction, or the
         Gemini renewal bot's read of a client's WhatsApp reply
Output:  one of AUTO_APPROVE / NEEDS_HUMAN_REVIEW / AUTO_REJECT, with the
         exact threshold rule that produced it
Benefit: stops PolicyHQ's automation from silently acting on a shaky AI
         guess (wrong commission figure, misread client intent) while
         still letting confidently-correct, low-stakes actions go
         through without waiting on an agent.

Mirrors CS50AI's Uncertainty unit: a system that reasons under
uncertainty is only as good as the threshold it uses for "confident
enough to act alone" -- and that threshold should get stricter as the
cost of being wrong goes up.
"""

from dataclasses import dataclass
from enum import Enum


class RiskTier(Enum):
    LOW = "low"        # e.g. drafting a WhatsApp reply, tagging a lead
    MEDIUM = "medium"  # e.g. extracted commission figure, quote estimate
    HIGH = "high"      # e.g. cancelling a policy, changing a payout amount


class Decision(Enum):
    AUTO_APPROVE = "auto_approve"
    NEEDS_HUMAN_REVIEW = "needs_human_review"
    AUTO_REJECT = "auto_reject"


# (auto_approve_at, auto_reject_below) per risk tier.
# HIGH's approve threshold is set above 1.0 -- deliberately unreachable,
# because a high-stakes action should never fire without a human, no
# matter how confident the model claims to be.
THRESHOLDS = {
    RiskTier.LOW:    (0.75, 0.30),
    RiskTier.MEDIUM: (0.90, 0.50),
    RiskTier.HIGH:   (1.01, 0.50),
}


@dataclass
class Verdict:
    decision: Decision
    reason: str


def evaluate(confidence: float, risk_tier: RiskTier) -> Verdict:
    if not 0.0 <= confidence <= 1.0:
        raise ValueError(f"confidence must be between 0 and 1, got {confidence}")

    approve_at, reject_below = THRESHOLDS[risk_tier]

    if confidence >= approve_at:
        return Verdict(
            Decision.AUTO_APPROVE,
            f"{risk_tier.value}-risk action, confidence {confidence:.2f} >= "
            f"auto-approve threshold {approve_at:.2f}"
        )
    if confidence < reject_below:
        return Verdict(
            Decision.AUTO_REJECT,
            f"{risk_tier.value}-risk action, confidence {confidence:.2f} < "
            f"minimum threshold {reject_below:.2f} -- too unreliable to act on"
        )
    return Verdict(
        Decision.NEEDS_HUMAN_REVIEW,
        f"{risk_tier.value}-risk action, confidence {confidence:.2f} is between "
        f"{reject_below:.2f} and {approve_at:.2f} -- an agent must confirm"
    )


def print_verdict(label: str, confidence: float, risk_tier: RiskTier):
    v = evaluate(confidence, risk_tier)
    print(label)
    print(f"  -> {v.decision.value}")
    print(f"     because {v.reason}\n")


if __name__ == "__main__":
    print_verdict("Lapse Shield: commission figure extracted from statement",
                  confidence=0.95, risk_tier=RiskTier.MEDIUM)

    print_verdict("Gemini renewal bot: client said 'yes renew me' (clear reply)",
                  confidence=0.88, risk_tier=RiskTier.LOW)

    print_verdict("Gemini renewal bot: ambiguous client reply ('maybe later?')",
                  confidence=0.55, risk_tier=RiskTier.MEDIUM)

    print_verdict("Auto-cancel policy after 3 missed payments (high stakes)",
                  confidence=0.97, risk_tier=RiskTier.HIGH)

    print_verdict("OCR misread commission statement, garbled text",
                  confidence=0.20, risk_tier=RiskTier.MEDIUM)
