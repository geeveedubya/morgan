# Books

Morgan's running records. Two parts: the pending queue (proposals waiting for
Gregg) and the ledgers (approved, booked entries per tax year).

## Pending queue — `pending/queue.yaml`

Every transaction Morgan sees lands here first with `status: pending`, a
proposed category, and one-sentence reasoning. Nothing skips the queue.

Gregg approves or declines in chat ("approve 1, 3; decline 2"). Approved
entries are booked to the month's ledger; declined entries stay in the queue
file with `status: declined` — the audit trail is kept, never deleted.

Entry schema is documented in `agents/transaction-watcher.md` and at the top
of the queue file itself.

## Ledgers — `<tax-year>/<YYYY-MM>.yaml`

One file per calendar month, grouped by UK tax year (6 April – 5 April), e.g.
`2026-27/2026-07.yaml`. April is split across two files at the tax-year
boundary by transaction date.

A booked entry is the queue entry plus:

```yaml
  approved_on: 2026-07-08      # date Gregg approved in chat
  booked_on: 2026-07-08        # date it was written to this ledger
```

Amounts are GBP, recorded gross (Oxford Circus Digital is not VAT-registered).
Non-GBP transactions are only booked after Gregg decides how to record them —
they wait in the queue flagged `non-gbp` until then.

The format is deliberately simple enough to export as CSV for the accountant
(roadmap phase 3).
