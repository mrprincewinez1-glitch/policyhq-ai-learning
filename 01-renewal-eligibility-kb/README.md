# PolicyHQ Renewal & Eligibility Knowledge Base

**What it does:** takes a policy's expiry countdown, payment status, and
contact-validity, and derives whether it's eligible for a renewal reminder
-- with a plain-English reason attached to every conclusion.

## Run it
```bash
python3 renewal_kb.py
```
No dependencies beyond the standard library.

## Review it
- `Rule` = one `IF requires AND NOT forbids THEN conclusion` statement.
- `KnowledgeBase.infer()` forward-chains until no new facts can be derived,
  and records which rule fired for each derived fact -- that trace is the
  "explainable" part; nothing is a hidden score or black-box flag.
- To add a new eligibility rule, add a `Rule(...)` to the `RULES` list --
  no other code changes needed.

## Wiring into PolicyHQ
This mirrors the logic that should sit in front of the `send-renewal-reminders`
Supabase Edge Function: instead of the function deciding silently, it can
call this same explain-then-act pattern so a support view can show *why*
a policy was or wasn't messaged.
