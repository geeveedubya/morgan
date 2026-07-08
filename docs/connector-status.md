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

## Scheduled-run status — FAILED FIRST FIRING, now disabled (8 Jul 2026)

The caveat below came true on the first firing, for a concrete reason worth
recording.

**What happened.** The 8 Jul 06:26 run started in an empty container: no repo
cloned (nothing to read or write) and all four connectors toggled off (no scan
possible). It reported this honestly and wrote/faked nothing.

**Root cause.** The Routine was created with the MCP `create_trigger` tool,
whose config carries only `allowed_tools` — it has no way to attach a repo
`source` or enable `mcp_connections`. Compared against the account's working
`fleet-daily-cycle` trigger (created via the web UI / http_api), which does
carry `session_context.sources` (its git repo) and `mcp_connections` (its
connectors), the difference is exactly those two missing pieces.

**Fix.** Re-create the schedule as a **web-UI scheduled task** with:
- source = `geeveedubya/morgan`, branch `claude/morgan-bookkeeper-foundation-1z2849`
- connectors enabled: Stripe, Gmail, Airtable, Google Drive

Connector UUIDs (for reference): Gmail `cbead29c-af1e-4977-b8c2-1488769adb7b`,
Stripe `8baf69c7-824a-4501-b828-53da53a84b45`, Airtable
`d6820e65-b508-4a59-ad8a-725a7448dace`, Google Drive
`0a947318-5062-496a-9eee-c669e70dbab9`.

The broken MCP-created trigger (`trig_01PmYT8Ki3DzC7HqJMen6orA`) is **disabled**
so it stops firing daily false alarms. It can be deleted once a working
web-UI schedule replaces it.

**Notifications** (unchanged): push needs the Claude app with notifications on;
email is the fallback. Both come from the Claude platform — Morgan never sends
email. Run time is pinned in UTC (06:26 = 7:26am UK summer, 6:26am winter).

Until a proper schedule exists, Morgan runs **when Gregg opens a session** —
the repo and connectors are always present interactively (proven 7 Jul).

## Questions resolved by Gregg (7 Jul 2026)

The three observations from the sample digest, answered in chat:

1. Same-day Lovable/Anthropic receipts on 6 July — **separate, planned
   charges**, not duplicates. Rule noted in categorisation-rules.yaml.
2. trAIned — **a trading name of the same business; include its income in
   these books.** Recorded in CLAUDE.md and the income indicators.
3. The $19 USD May "subscription creation" charge — **a test event**, to be
   excluded from the books. A test-payment exclusion rule now exists.
