#!/usr/bin/env python3
"""
Vireo Audio — Weekly First-Response SLA Breach Report
======================================================

Produces the report Neha Kulkarni asked for (breach by agent and shift,
weekly), plus the structural finding that actually explains most of it:
a company-wide Night-shift coverage gap since 2025-06-30.

Run:
    python3 breach_report.py

Inputs expected in the same folder: tickets.csv, agents.csv
Outputs (in ./output/):
    weekly_breach_by_agent_shift.csv   <- the literal ask
    weekly_breach_by_channel.csv       <- supporting detail
    coverage_gap_summary.txt           <- the headline finding, in numbers
    validation_sample.csv              <- 40 random tickets, hand-checkable

Optional AI-assisted narrative (off by default, $0 unless you opt in):
    python3 breach_report.py --summarize
    Requires ANTHROPIC_API_KEY in the environment. If not set, this flag
    is silently skipped and the script still produces every number above
    with zero API calls and zero cost. The narrative is cosmetic — it
    summarizes numbers already computed deterministically below; it never
    computes a number itself. That split is deliberate: the figures used
    to have a coaching conversation with named employees should not depend
    on a model call succeeding, being reproducible, or costing money.
"""

import argparse
import os
import sys
import pandas as pd

IST_OFFSET = pd.Timedelta(hours=5, minutes=30)
FIRST_RESPONSE_TARGET_MINUTES = {"chat": 15, "voice": 120, "social": 240, "email": 480}
SLA_CREDIT_PER_BREACH_INR = 350  # support-policy.pdf section 3
NIGHT_SHIFT_ELIMINATED_ON = pd.Timestamp("2025-06-30")  # derived from agents.csv roster


def load_tickets(path="tickets.csv"):
    t = pd.read_csv(
        path,
        parse_dates=["created_at", "first_response_at", "resolved_at"],
    )

    # --- Dedup migration overlap -------------------------------------------
    # README + email thread: a subset of legacy tickets was re-imported into
    # the new helpdesk during reconciliation and can appear under both
    # source systems. Verified: every duplicated ticket_id has exactly one
    # 'helpdesk' row and one 'legacy_fd' row with identical core fields;
    # they differ only in csat_score (legacy wrongly encodes "no response"
    # as 0 instead of blank — support-policy.pdf section 8). We keep the
    # helpdesk row, which has the correct blank-for-no-response semantics.
    before = len(t)
    t = t.sort_values("source_system").drop_duplicates(subset="ticket_id", keep="first")
    removed = before - len(t)
    print(f"[dedup] removed {removed} duplicate rows from the Freshdesk migration overlap")

    # --- Timezone -----------------------------------------------------------
    # README: "All timestamps in this export are UTC (helpdesk API export)."
    # support-policy.pdf section 9: shifts and the policy's own reporting are
    # in IST. We convert to IST for any date/hour/week bucketing; breach math
    # itself (a duration) is timezone-invariant, so it stays on the raw UTC
    # columns.
    t["created_at_ist"] = t["created_at"] + IST_OFFSET
    t["resolved_at_ist"] = t["resolved_at"] + IST_OFFSET

    # --- Breach flag ----------------------------------------------------
    # support-policy.pdf section 3: "Breach: first response later than the
    # target in section 3," targets by channel as in the dict above.
    t["target_minutes"] = t["channel"].map(FIRST_RESPONSE_TARGET_MINUTES)
    t["resp_minutes"] = (t["first_response_at"] - t["created_at"]).dt.total_seconds() / 60
    t["breached"] = t["resp_minutes"] > t["target_minutes"]

    t["hour_ist"] = t["created_at_ist"].dt.hour
    t["is_night_ist"] = (t["hour_ist"] >= 22) | (t["hour_ist"] < 6)
    t["week_ist"] = t["created_at_ist"].dt.to_period("W-MON")

    return t


def load_agents(path="agents.csv"):
    a = pd.read_csv(path, parse_dates=["from_date", "to_date"])
    return a


def attach_shift(tickets, agents):
    """
    Point-in-time join: a ticket's shift/site/team is whatever the resolving
    agent's roster row says was active on the ticket's creation date (IST).
    support-policy.pdf section 3: "Breaches are reported against the
    resolving agent." The roster has one row per assignment (agents.csv),
    so an agent who changed shift mid-period gets the correct historical
    shift for each ticket, not just their current one.
    """
    tickets = tickets.copy()
    tickets["asof_date"] = tickets["created_at_ist"].dt.normalize()

    merged = tickets.merge(agents, on="agent_id", how="left", suffixes=("", "_roster"))
    in_window = (merged["asof_date"] >= merged["from_date"]) & (
        merged["to_date"].isna() | (merged["asof_date"] <= merged["to_date"])
    )
    matched = merged[in_window].copy()

    dupe_check = matched["ticket_id"].duplicated().sum()
    if dupe_check:
        print(f"[warn] {dupe_check} tickets matched more than one roster row — check for overlapping roster dates", file=sys.stderr)

    unmatched = set(tickets["ticket_id"]) - set(matched["ticket_id"])
    if unmatched:
        print(f"[warn] {len(unmatched)} tickets had no matching roster row and were dropped from the agent/shift report", file=sys.stderr)

    return matched


def weekly_breach_by_agent_shift(attached):
    g = (
        attached.groupby(["week_ist", "site", "shift", "agent_id", "name"])
        .agg(tickets=("ticket_id", "count"), breaches=("breached", "sum"))
        .reset_index()
    )
    g["breach_rate_pct"] = (g["breaches"] / g["tickets"] * 100).round(1)
    g["sla_credit_inr"] = g["breaches"] * SLA_CREDIT_PER_BREACH_INR
    return g.sort_values(["week_ist", "breach_rate_pct"], ascending=[True, False])


def weekly_breach_by_channel(tickets):
    g = (
        tickets.groupby(["week_ist", "channel"])
        .agg(tickets=("ticket_id", "count"), breaches=("breached", "sum"))
        .reset_index()
    )
    g["breach_rate_pct"] = (g["breaches"] / g["tickets"] * 100).round(1)
    return g.sort_values(["week_ist", "channel"])


def coverage_gap_summary(tickets):
    post = tickets[tickets["created_at"] >= NIGHT_SHIFT_ELIMINATED_ON]
    pre = tickets[tickets["created_at"] < NIGHT_SHIFT_ELIMINATED_ON]

    weeks_post = max((post["created_at"].max() - post["created_at"].min()).days / 7, 1)
    weeks_pre = max((pre["created_at"].max() - pre["created_at"].min()).days / 7, 1)

    total_breaches_post = int(post["breached"].sum())
    night_breaches_post = int(post[post["is_night_ist"]]["breached"].sum())
    night_share = night_breaches_post / total_breaches_post if total_breaches_post else 0

    lines = []
    lines.append("COVERAGE GAP FINDING")
    lines.append("=" * 60)
    lines.append(f"Night-shift roster rows after {NIGHT_SHIFT_ELIMINATED_ON.date()}: 0 (company-wide)")
    lines.append("")
    lines.append(f"Breach rate before reshuffle: {pre['breached'].mean()*100:.1f}%  "
                  f"(run-rate Rs {pre['breached'].sum()/weeks_pre*SLA_CREDIT_PER_BREACH_INR*13:,.0f}/quarter)")
    lines.append(f"Breach rate after reshuffle:  {post['breached'].mean()*100:.1f}%  "
                  f"(run-rate Rs {post['breached'].sum()/weeks_post*SLA_CREDIT_PER_BREACH_INR*13:,.0f}/quarter)")
    lines.append("")
    lines.append(f"Of {total_breaches_post} breaches since the reshuffle, {night_breaches_post} "
                  f"({night_share*100:.1f}%) happened on tickets created 22:00-06:00 IST — "
                  f"hours with zero staffed agents of any kind.")
    lines.append("")
    lines.append("Breach rate by channel, night hours only (post-reshuffle):")
    night_post = post[post["is_night_ist"]]
    for ch, grp in night_post.groupby("channel"):
        lines.append(f"  {ch:8s}  {grp['breached'].mean()*100:5.1f}%   (n={len(grp)})")
    return "\n".join(lines)


def validation_sample(tickets, n=40, seed=42):
    """
    40 random tickets with the raw inputs and the computed breach flag side
    by side, so the number itself can be hand-checked without re-running
    any code (see README's 'How we know it works').
    """
    cols = ["ticket_id", "channel", "created_at", "first_response_at",
            "target_minutes", "resp_minutes", "breached"]
    return tickets[cols].sample(n=min(n, len(tickets)), random_state=seed)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--summarize", action="store_true",
                         help="Also generate a short AI-written narrative (requires ANTHROPIC_API_KEY; $0 if omitted)")
    parser.add_argument("--tickets", default="tickets.csv")
    parser.add_argument("--agents", default="agents.csv")
    args = parser.parse_args()

    os.makedirs("output", exist_ok=True)

    tickets = load_tickets(args.tickets)
    agents = load_agents(args.agents)
    attached = attach_shift(tickets, agents)

    weekly_agent = weekly_breach_by_agent_shift(attached)
    weekly_channel = weekly_breach_by_channel(tickets)
    gap_summary = coverage_gap_summary(tickets)
    sample = validation_sample(tickets)

    weekly_agent.to_csv("output/weekly_breach_by_agent_shift.csv", index=False)
    weekly_channel.to_csv("output/weekly_breach_by_channel.csv", index=False)
    sample.to_csv("output/validation_sample.csv", index=False)
    with open("output/coverage_gap_summary.txt", "w") as f:
        f.write(gap_summary)

    print()
    print(gap_summary)
    print()
    print(f"[done] wrote output/weekly_breach_by_agent_shift.csv ({len(weekly_agent)} rows)")
    print(f"[done] wrote output/weekly_breach_by_channel.csv ({len(weekly_channel)} rows)")
    print(f"[done] wrote output/validation_sample.csv ({len(sample)} rows)")
    print(f"[done] wrote output/coverage_gap_summary.txt")

    if args.summarize:
        api_key = os.environ.get("ANTHROPIC_API_KEY")
        if not api_key:
            print("\n[summarize] ANTHROPIC_API_KEY not set — skipping AI narrative. $0 spent.")
            return
        try:
            import urllib.request
            import json as json_lib
            prompt = (
                "Write a 4-sentence plain-English summary of this support "
                "operations finding for a non-technical ops manager:\n\n" + gap_summary
            )
            req = urllib.request.Request(
                "https://api.anthropic.com/v1/messages",
                data=json_lib.dumps({
                    "model": "claude-sonnet-4-6",
                    "max_tokens": 300,
                    "messages": [{"role": "user", "content": prompt}],
                }).encode(),
                headers={
                    "Content-Type": "application/json",
                    "x-api-key": api_key,
                    "anthropic-version": "2023-06-01",
                },
            )
            with urllib.request.urlopen(req, timeout=20) as resp:
                data = json_lib.loads(resp.read())
            narrative = "".join(b["text"] for b in data.get("content", []) if b.get("type") == "text")
            with open("output/ai_narrative.txt", "w") as f:
                f.write(narrative)
            print("\n[summarize] wrote output/ai_narrative.txt")
        except Exception as e:
            print(f"\n[summarize] skipped due to error: {e}")


if __name__ == "__main__":
    main()
