# How to review Morgan's pending transactions

Morgan proposes; you decide. Nothing is booked as business until you approve it.

## The daily flow

1. Morgan's run writes a numbered digest to `briefings/daily/YYYY-MM-DD.md`
   and (once scheduling is live) notifies you by push/email.
2. You read the digest and reply **in chat, in any Morgan session**:

   ```
   approve 1, 3-5; decline 2 — that one's personal
   ```

   Anything goes: "approve all the Lovable ones", "hold 7 until I check",
   "6 is actually travel, approve as travel". Morgan applies it, tells you
   what it did, and asks only when genuinely unsure.
3. Morgan updates `books/pending/queue.yaml` statuses and books approved
   entries to `books/2026-27/<YYYY-MM>.yaml` with `approved_on`/`booked_on`.
   Declined entries stay in the queue file with `status: declined` — the
   audit trail is never deleted.

Digest numbers map to queue entry ids (the digest shows both).

## Fallback — no chat session needed

Edit `books/pending/queue.yaml` directly: change an entry's `status: pending`
to `approved` or `declined` (optionally add a `note:`), commit and push.
Morgan's next run books whatever you've marked. Same effect, just slower.

## What the statuses mean

| status | meaning |
|---|---|
| `pending`  | waiting for you — not in the books |
| `approved` | you said yes — will be booked to the monthly ledger |
| `declined` | you said no — kept for the audit trail, never booked |
| `booked`   | approved and written to `books/<tax-year>/<YYYY-MM>.yaml` |

## Scheduled runs

The daily run and its notifications are configured in
`config/review-cadence.yaml` (see `scheduling:` there for the live routine's
details). You own the schedule: tell Morgan to change or stop it any time.
Note: the run time is set in UTC, so it shifts by an hour when UK clocks
change — say the word and Morgan re-pins it.
