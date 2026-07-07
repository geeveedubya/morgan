# Morgan roadmap

The foundation (this repo skeleton, config, transaction-watcher) came first.
What follows, in order — each phase is gated on Gregg, and every new write
capability is staged and asked for before it's ever used.

## Phase 1 — Books builder
Turn approvals into books. When Gregg approves entries in chat, book them to
the monthly ledger (`books/<tax-year>/<YYYY-MM>.yaml`), keep running totals per
category, and show the month-to-date position in the weekly summary.

## Phase 2 — Month-end reconciliation
A month-end agent that cross-checks three views of the same month: Stripe
payouts vs booked income vs Airtable billable hours per client. Produces a
plain-English discrepancy report — unpaid invoiced work, unbilled hours,
unmatched payouts — plus the use-of-home flat-rate entry for the month.

## Phase 3 — Accountant handoff pack
At tax-year end (or on request): export the year's ledgers to CSV, write a
summary (income, expenses by category, net profit) an accountant can work from
directly. Filing the pack to Google Drive is Morgan's **first external write**
— it happens only after Gregg explicitly approves the destination folder and
the write itself.

## Phase 4 — Cloud scheduling (partially delivered, 7 Jul 2026)
The **daily** run is live: a Routine Gregg approved on 7 July fires a fresh
session each morning (~7:26am UK) that runs the transaction watcher and
notifies him by push + email — details in `config/review-cadence.yaml`,
caveats in `docs/connector-status.md`. Still to come: the **weekly summary**
routine, and confirming the headless run can actually reach Stripe/Airtable
(first firing is the test). One batched run per cadence, nothing in between.

## Phase 5 — Rule learning
Morgan studies Gregg's approve/decline history and proposes concrete edits to
`config/categorisation-rules.yaml` ("you've approved GitHub as
office_costs_and_software 6 times — add it to examples?"). Gregg accepts or
rejects each suggestion; Morgan never edits the rules file unilaterally.

## Standing constraints (never change with phases)
- Read-only against Stripe, Gmail, Airtable, banks — always.
- No money movement, no sending, no HMRC filing — ever.
- Every categorisation passes through Gregg's approval.
- Any write beyond this repo is staged and asked for, never assumed.
