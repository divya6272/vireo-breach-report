# Memo: First-Response SLA Breaches — Weekly Report + What's Actually Driving It

**To:** Neha Kulkarni, Support Operations Manager
**Re:** SLA breach report by agent and shift

---

You asked for a weekly breach report by agent and shift so you could have
the right conversations with the right people. It's attached
(`weekly_breach_by_agent_shift.csv`). But before you use it to start those
conversations, there's one thing in the data that changes who those
conversations should be with.

## The number

Over the last 12 months, Vireo's first-response breach rate has averaged
**25%**, costing roughly **Rs 1.95 lakh a quarter** in automatic Rs 350 SLA
credits. In the six months before that, it averaged **9%**, costing about
**Rs 37,000 a quarter**. That's the jump Arjun is seeing in the P&L — and
it isn't a mystery, and it isn't a slow drift. It happened on one specific
date.

## What actually happened

On **30 June 2025**, the Night shift (22:00–06:00 IST) was eliminated —
not reduced, eliminated, company-wide. The roster shows zero Night-shift
agents anywhere after that date. Two of the five agents who'd been on it
moved to a Day shift; the other three left the roster entirely.

The effect is exactly what you'd expect: nobody responds to anything
created between 10pm and 6am until the Morning shift logs on. For chat,
where the target is 15 minutes, every single overnight chat ticket now
breaches — **100% of them**, no exceptions. Social is at 86%. Even email,
with an 8-hour target, breaches half the time overnight.

**70.8% of every breach in the last 12 months is a ticket that was created
during those unstaffed hours.** This isn't 44 agents having a bad year.
It's one scheduling decision, still in effect, that nobody's revisited.

## The trap in the report you asked for

Here's the part that matters most for how you use the attached CSV: read
weekly by shift, **Morning shift** comes out looking like the biggest
problem — they're attached to the most breaches. They are not the cause.
**80% of the breaches credited to Morning shift are tickets that were
already breached before that shift's day even started** — the customer
messaged at 2am, the clock ran out at 2:15am, and the Morning agent who
finally answered at 6:30am inherited a breach they had no way to prevent.
If you coach Morning shift on speed, nothing will move, because speed
isn't the problem on these tickets — staffing hours is.

## On the credit-line disagreement

Arjun's right that the SLA credit line jumped hard — it's gone up roughly
5x, not 3x, but his instinct that something changed is correct, and now
we know what. Priya's "flat month on month" is also right in a narrow
sense — it's been flat *since* the jump, hovering Rs 55k–75k/month for the
last year rather than still climbing. But CSAT hasn't moved to explain
anything: it's sat between 3.27 and 3.51 the entire 18 months, no trend up
or down. The credit line moved because of the schedule change, not because
something else shifted and credits are incidental.

## What I'm not recommending

Finance has headcount frozen through Q4, so "add a Night shift back" isn't
on the table and I'm not proposing it. Two things that don't need new
headcount:

1. **Give overnight tickets a realistic target instead of the current one.**
   Right now the policy promises a 15-minute chat response 24/7 with nobody
   staffed to deliver it 8 hours a day. Either stop auto-crediting Rs 350
   for a gap that was a deliberate staffing call, or set an explicit
   overnight target (e.g., "by 07:00 IST") that reflects reality.
2. **Look at a staggered start** — one or two Morning agents starting at
   4–5am instead of 6am would close most of the worst of the gap without
   adding a single headcount, just a schedule change.

## Bottom line

The weekly agent/shift numbers are attached as asked. Before using them for
individual coaching, it's worth reading `output/coverage_gap_summary.txt`
alongside — it'll save you a conversation with Morning shift that won't
fix the actual problem.
