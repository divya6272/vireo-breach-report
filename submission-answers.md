# Submission form — draft answers

Fill in the bracketed placeholders with your own details before submitting.
Everything else is ready to use or lightly edit into your own voice.

---

### What did you build, and what business outcome does it move? State the number and the money.

A weekly first-response SLA breach report by agent and shift (as asked),
built on top of a deterministic Python/pandas pipeline that dedupes the
Freshdesk migration overlap, applies the policy's channel-specific breach
targets, and joins each ticket to the resolving agent's roster assignment
at the time.

The outcome it moves: Vireo's breach rate has averaged **25% over the last
12 months** (up from **9%** in the 6 months before), costing roughly
**Rs 1.95 lakh/quarter** in automatic Rs 350 SLA credits versus a prior
run-rate of ~Rs 37,000/quarter. **70.8% of that is attributable to one
structural cause**: the Night shift (22:00–06:00 IST) was eliminated
company-wide on 2025-06-30, and nobody has covered those hours since.
The goal the tool points to isn't "coach agents" — it's "close or
re-price that 8-hour gap," which could plausibly bring breach costs back
toward the ~Rs 37k/quarter pre-reshuffle baseline without adding headcount.

### What does one run cost, and what would a month cost at Vireo's volume (roughly 650 tickets a week)?

**Rs 0 / $0.** The core report (dedup, breach calc, roster join, weekly
rollup) is pure pandas over the provided CSVs — no API calls, no paid
service, at any ticket volume. Run it once a week or once an hour; the
cost doesn't change because there isn't one.

The optional `--summarize` flag adds one Claude API call per run to turn
the already-computed numbers into a short paragraph. At roughly 500 input
+ 300 output tokens per call, that's about **$0.006/run** — running it
weekly all month (4 runs) is about **$0.024/month**, i.e. still
effectively free. This flag is off by default and the report is complete
without it.

### How do you know it works? Sample size, how you checked, error rate, and the kind of case it gets wrong.

- The breach flag was recomputed **independently in plain Python (no
  pandas)** for all **11,200** deduplicated tickets (100% of the dataset,
  not a sample) and diffed against the script's output: **0 mismatches**.
- The roster-to-ticket join was checked for both failure modes directly:
  **0 tickets matched more than one roster row**, **0 tickets matched
  zero roster rows** — 100% clean join, not assumed.
- `output/validation_sample.csv` gives 40 random tickets with raw
  timestamps next to the computed flag for a human spot-check.
- Where it could still be wrong: tickets created within a few hours of an
  agent's roster-transition date (role change) resolve to whichever side
  of that date they were created on — a defensible choice, but a judgment
  call, not a verified one, since the roster doesn't give hour-level
  transition times.

### Did you change, narrow, or push back on the client's ask? What, when, and why.

Yes, in one specific way: Neha's ask was "breach report by agent and
shift" so she could "have the conversation with the right people." I built
that report exactly as asked — but added a prominent caveat on top of it,
because the report on its own points at the wrong people. Morning shift
shows the most breaches; **80% of those are tickets created overnight,
before that shift started**, that nobody could have answered faster. Using
the report for individual coaching without that context would waste a
conversation and not move the number. I didn't refuse or replace the ask —
I delivered it plus the one thing that makes it safe to act on.

### What is wrong with what you are handing us? Be specific: bugs, shortcuts, things you know are off.

- The Rs 350/breach credit cost is **reconstructed from the breach count**,
  not reconciled against an actual SLA-credit ledger line in the P&L —
  Arjun referenced the P&L credit line but no export of it was provided,
  so the Rs 1.95 lakh/quarter figure is a model of the cost, not a verified
  actual.
- Shift attribution uses the ticket's *creation* date to pick the agent's
  roster row; a ticket created right at a roster-transition boundary could
  theoretically land on the wrong side of a role change (no observed cases
  in this data, but not provably impossible).
- `transfers` is blank/0 for pre-migration legacy tickets — not because
  there were no hand-offs, but because the field "exists only in the
  current helpdesk" per the README. Any hand-off analysis would need to be
  scoped to post-migration tickets only; I didn't build that analysis at
  all (see "left out," below), but flagging the gap in case someone does.
- I did not reconcile `assigned_team` (ticket's first-routed team) against
  the resolving agent's roster `team` — they can legitimately differ after
  a transfer, but I didn't check whether mismatches are common enough to
  indicate a routing problem worth its own report.

### What did you deliberately leave out, and why that rather than something else?

- **orders.csv, customers.csv, products.csv** — not touched. They'd
  support a different question (which products/customers drive ticket
  volume or refund cost), and Neha's ask was specifically about
  first-response SLA by agent/shift. Pulling in three more tables to
  answer a question nobody asked would have eaten the time budget for the
  one finding that actually explains most of the breach cost.
- **A dashboard or UI.** The ask was "a breach report," not a product. A
  CSV + a markdown summary is faster to build, easier to verify, and
  exactly as useful for the weekly conversation Neha described.
- **A precise Rs-savings estimate for the two fixes I suggest** (retarget
  overnight SLA, stagger Morning shift start). Both are qualitative
  recommendations on purpose — a specific savings number would require
  assuming future ticket volume and a specific schedule change neither
  Neha nor Arjun has committed to, and a fabricated-precise number would
  be worse than an honest range.

### Anything you built or found that nobody asked for?

- The Morning-shift-inherits-the-blame finding (above) — nobody asked "is
  the shift report misleading," but it would have made the deliverable
  actively harmful to use as-is.
- **616 duplicate tickets** from the Freshdesk→helpdesk migration
  reconciliation, with a specific, verified root cause (legacy rows wrongly
  encode "no CSAT response" as `0` instead of blank). Worth a note back to
  Sameer/IT — any other analysis run against this export without deduping
  will silently double-count roughly 5.5% of tickets.
- The roster shows **3 of the 5 former Night-shift agents left the company
  entirely** in the June reshuffle (not just reassigned) — unrelated to
  the SLA question, but possibly relevant to whatever "cost-neutral"
  analysis Arjun ran on the reshuffle itself.

### What did you use AI for?

[Personalize this with what actually happened for you — a starting draft:]
Used Claude (chat) throughout: exploring the raw CSVs and forming/testing
the night-shift-elimination hypothesis, writing and iterating the
pandas pipeline, independently re-deriving the breach calculation in plain
Python specifically to cross-check the pandas version rather than trust it
by construction, and drafting this memo and documentation. It was most
useful for fast hypothesis testing (e.g., slicing breach rate by hour and
period took one message, not a debugging session) and for generating the
independent-validation code, since writing a second implementation by hand
to check the first is exactly the kind of task worth delegating. It was
least useful/would have wasted time if I'd let it just describe the data
instead of computing from it directly — every claim in the memo traces to
a number actually computed from the CSVs, not inferred from column names
or domain assumptions.
**[Link your screen recording here]**

### Your Public Google Drive Link
**[Add your Drive link here — upload the repo contents, screen recording, and this submission doc]**

### Someone picks this up on Monday and you are unreachable. The three things they need to know.

1. **The weekly agent/shift CSV is correct but dangerous if read alone** —
   Morning shift will look like the problem; 80% of what they're blamed
   for happened overnight before their shift started. Read
   `coverage_gap_summary.txt` first.
2. **The Rs 350/breach credit cost is a reconstruction, not a reconciled
   actual** — if Finance ever shares the real SLA credit ledger line, swap
   it in and re-validate against this estimate rather than assuming either
   number is right.
3. **Re-run `breach_report.py` fresh each time** rather than patching the
   CSVs in `output/` by hand — the dedup and roster-join logic is easy to
   get subtly wrong by hand (616 duplicate rows, point-in-time roster
   matching) and the script already has both independently verified.

### Honest hours spent. One number.
**[Fill in your actual number]**

### Github Repo Link
**[Add your public GitHub repo URL here]**

### Please upload your Github Repo URL (Public)
**[Same as above]**
