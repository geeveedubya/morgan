# Connector status — honest report

Last checked: 7 July 2026, during the first real transaction-watcher run.
Nothing below is assumed; every "verified" was a real call in a session.

| Source | Connected (OAuth) | Live read verified | Notes |
|---|---|---|---|
| Gmail | yes | **yes** | Whole-mailbox receipt/invoice searches and full receipt bodies read across the tax year to date. |
| Stripe | yes | **yes** | Account "Oxford Circus Digital" (acct_1QUZ3kAnusPN3mWR), live mode. Full charge history read; 12 transactions in tax year 2026/27. |
| Airtable | yes | **yes** | Billable-hours base identified and read: "Automated workflow timesheets" (appHbwQcjxL6zDcO4), Timesheet table, 128 records. IDs recorded in config/sources.yaml. |
| Google Drive | yes | not yet | Connected, awaiting its first approved read. Read-only regardless; any Drive *write* is a separate roadmap gate. |

## Remaining before fully unattended runs

- Stripe and Airtable calls raise a per-call approval prompt; Gregg approved
  them interactively on 7 July. Whether the scheduled headless run can read
  them without Gregg present is unknown until the first firing — see the
  scheduled-run caveats below.
- Gmail calls run without prompting (proven twice, interactively).

## Caveats found during the sample pull

- Stripe access is **live mode** on the real account — reads only, but treat
  every run as touching production data.
- The Stripe connector's write tool exists in the workspace. Morgan's rules
  (CLAUDE.md hard rule 1) forbid ever calling it.

## Scheduled-run caveats (honest, as of 7 Jul 2026)

The daily Routine fires a **fresh headless session** each morning. Two things
only the first firing can prove:

1. **Connector reach.** Interactively-authenticated connectors (Stripe,
   Airtable, Gmail, Drive) may be absent or approval-gated in headless runs.
   If the morning run can't reach a source, it says so in that day's digest
   ("couldn't reach Stripe — run me interactively") rather than guessing, and
   the full scan happens next time Gregg opens a session.
2. **Notifications.** Push needs the Claude app with notifications enabled;
   the email summary is the fallback. Both come from the Claude platform —
   Morgan itself never sends email.

The run time is pinned in UTC (06:26), i.e. 7:26am UK in summer time and
6:26am in winter — Gregg can ask Morgan to re-pin it when clocks change.

## Questions resolved by Gregg (7 Jul 2026)

The three observations from the sample digest, answered in chat:

1. Same-day Lovable/Anthropic receipts on 6 July — **separate, planned
   charges**, not duplicates. Rule noted in categorisation-rules.yaml.
2. trAIned — **a trading name of the same business; include its income in
   these books.** Recorded in CLAUDE.md and the income indicators.
3. The $19 USD May "subscription creation" charge — **a test event**, to be
   excluded from the books. A test-payment exclusion rule now exists.
