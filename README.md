# Vireo Audio — First-Response SLA Breach Report

Neha asked for: *"a breach report: which agents and which shift are
breaching most, weekly."* This tool produces exactly that — plus the one
finding that explains most of it, which a literal agent/shift report would
otherwise bury.

## Run it (clean machine)
```bash
pip install pandas
python3 breach_report.py
```
That's it — no API key required for the core report. Outputs land in `./output/`:

- `weekly_breach_by_agent_shift.csv` — the literal ask: one row per
  agent × shift × week, with ticket count, breach count, breach rate, and
  the Rs cost in SLA credits.
- `weekly_breach_by_channel.csv` — same, by channel, for context.
- `coverage_gap_summary.txt` — the headline finding (below).
- `validation_sample.csv` — 40 random tickets with raw timestamps and the
  computed breach flag side by side, so the logic can be hand-checked
  without re-running anything.

Optional, costs money only if you turn it on:
```bash
ANTHROPIC_API_KEY=sk-... python3 breach_report.py --summarize
```
Adds a short AI-written plain-English paragraph on top of the already-computed
numbers (`output/ai_narrative.txt`). Without a key set, this flag is a no-op —
the core report is 100% deterministic and free either way.

## The headline finding
Something structural is driving most of the breach increase, and it isn't
agent performance:

- **The Night shift (22:00–06:00 IST) was eliminated company-wide on
  2025-06-30.** Not reduced — eliminated. `agents.csv` has zero Night-shift
  roster rows after that date, at either site.
- Overall breach rate: **9.2% before → 25.0% after** that date.
- **70.8%** of all breaches since then are on tickets *created* during
  those unstaffed hours — chat tickets created overnight breach **100%** of
  the time (nobody picks them up until 06:00 IST; the chat target is 15
  minutes).
- The weekly agent/shift report will show **Morning shift** with the most
  breaches. **80.1% of those are tickets created overnight**, before the
  Morning agent's shift even started. Read literally, the report points at
  the wrong people.

See `memo-to-neha.md` for the full writeup, or `output/coverage_gap_summary.txt`
for the numbers on their own.

## How the numbers are built (for whoever picks this up)
1. **Dedup**: 616 tickets appear twice (Freshdesk→helpdesk migration overlap,
   confirmed in `email-thread.txt`). Kept the `helpdesk` row of each pair —
   it has the correct blank-for-no-response CSAT encoding (legacy wrongly
   uses `0`; policy §8 says blank = no response, not zero).
2. **Timezone**: `tickets.csv` timestamps are UTC (README says so; policy
   reports and shift definitions are IST), so everything is converted +5:30
   before any date/hour/week bucketing. Breach math itself (a duration) is
   timezone-invariant.
3. **Breach**: `first_response_at - created_at` vs. the channel's target in
   policy §3 (chat 15m, voice 2h, social 4h, email 8h).
4. **Shift attribution**: policy §3 says breaches are reported against the
   *resolving* agent. `agents.csv` is one row per roster assignment (an
   agent can change shift and keep the same `agent_id`), so each ticket is
   joined to whichever roster row covers that agent on the ticket's
   creation date (IST) — not just the agent's current shift.

## Validation
- The breach flag was independently recomputed in plain Python (no pandas)
  for all 11,200 deduplicated tickets. **0 mismatches** against the script's
  output.
- The roster join matched **100%** of tickets to exactly one roster row (no
  duplicates, no misses) — checked explicitly, not assumed.
- `output/validation_sample.csv` gives 40 random tickets for an independent
  human spot-check.
- Known soft spot: a handful of legacy tickets have `transfers` blank (field
  "exists only in the current helpdesk" per README) — doesn't affect breach
  math, just means hand-off counts aren't comparable pre/post migration.

## What this doesn't try to do
- It doesn't recommend headcount changes (Finance has frozen headcount
  through Q4 — see `email-thread.txt`).
- It doesn't touch refund amounts (`refund_amount_inr`) — those are a
  separate rupee flow (DOA/lost-in-transit/etc. refunds) and don't include
  the automatic Rs 350 SLA credit, which isn't broken out anywhere in the
  export and had to be reconstructed from the breach count.
