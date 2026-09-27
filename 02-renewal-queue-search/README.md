# PolicyHQ Renewal Queue - Search & Priority Model

**What it does:** turns a flat list of policies into an ordered call queue,
with a plain-English reason for every rank.

## Run it
```bash
python3 renewal_queue.py
```
No dependencies beyond the standard library.

## Review it
- Each `Policy` is a node; `priority_score()` is that node's cost.
- `build_call_queue()` is a greedy best-first search: a min-heap
  (`heapq`) always expands (pops) the lowest-cost node next.
- Ranking is tiered:
  1. Urgency tier (7-day windows) always wins.
  2. Within the same tier, higher premium is called first.
  3. Still tied, fewer prior contact attempts goes first.

## Wiring into PolicyHQ
This should sit behind the agent's "Today's Renewals" view: feed it the
day's due policies from Supabase, render the output as the ordered list,
and show `explain_score()`'s text as the "why this order" tooltip.
