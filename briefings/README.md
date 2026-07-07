# Briefings

Morgan's plain-English output for Gregg. Two kinds, per
`config/review-cadence.yaml`:

## Daily digest — `daily/YYYY-MM-DD.md`

Everything pending review, numbered, each with amount, date, merchant, proposed
category, and one sentence of reasoning. Written so Gregg can reply in chat:

> approve 1 and 3, decline 2 — that one is personal

Flagged items (non-GBP, over £250, no rule matched) are called out explicitly.

## Weekly summary — `weekly/YYYY-Www.md`

The wider view: totals by category (booked and pending), approvals vs declines,
anomalies (possible duplicates, unmatched Stripe payouts, unusual amounts), and
anything sitting too long in the pending queue.

Both are written for a human: no jargon, explicit numbers, short.
