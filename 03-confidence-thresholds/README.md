# PolicyHQ Confidence & Human-Approval Thresholds

**What it does:** takes an automated decision's confidence score and how
risky the action is, and returns `auto_approve`, `needs_human_review`, or
`auto_reject` -- with the exact threshold rule that produced it.

## Run it
```bash
python3 confidence_thresholds.py
```
No dependencies beyond the standard library.

## Review it
- `THRESHOLDS` maps each `RiskTier` to `(auto_approve_at, auto_reject_below)`.
- `evaluate()` is the whole decision: above the top threshold, approve;
  below the bottom, reject; in between, send to a human.
- **HIGH-risk actions can never auto-approve** -- their approve threshold
  (1.01) is set above the maximum possible confidence (1.0) on purpose.
  This is deliberate policy, not a bug: something like auto-cancelling a
  policy should always get a human's eyes on it, no matter how confident
  the model claims to be.
- To change where a tier's line sits, edit `THRESHOLDS` -- no other code
  changes needed.

## Wiring into PolicyHQ
This is the gate that should sit in front of every AI-driven action:
Lapse Shield's commission-figure extraction (MEDIUM), the Gemini
WhatsApp/Telegram renewal bot reading client replies (LOW/MEDIUM), and
any future auto-cancel, refund, or payout-adjustment logic (HIGH).
Each call site passes its own confidence score and risk tier into
`evaluate()` instead of inventing its own ad-hoc "good enough?" check.
