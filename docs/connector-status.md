# Connector status — honest report

Last checked: 7 July 2026, during the foundation build session. Nothing below
is assumed; every "verified" was a real call in this session.

| Source | Connected (OAuth) | Live read verified | Notes |
|---|---|---|---|
| Gmail | yes | **yes** | Labels listed; receipt/invoice search returned real results (Lovable, Anthropic receipts; Stripe tax invoices; client invoice threads). |
| Stripe | yes | **yes** | Account confirmed: "Oxford Circus Digital" (acct_1QUZ3kAnusPN3mWR), live mode. Last 10 charges read successfully. |
| Airtable | yes | not yet | Connector present and org-connected. First read blocked in plan mode by the per-call approval prompt; no call attempted after. Needs one approved call to identify the billable-hours base. |
| Google Drive | yes | not yet | Same situation as Airtable — connected, awaiting a first approved read. Read-only regardless; any Drive *write* is a separate roadmap gate. |

## What Gregg needs to do before the first real run

1. **Nothing to install or authorise** — all four connectors are already
   OAuth-connected to the workspace.
2. **Approve the prompts**: Stripe, Airtable, and Drive tool calls raise a
   per-call approval prompt in the session. Approving them when Morgan runs is
   the only remaining step. (Gmail calls run without prompting.)
3. **Point Morgan at the Airtable base**: on the first Airtable read, confirm
   which base/table holds billable hours per client.

## Caveats found during the sample pull

- Stripe access is **live mode** on the real account — reads only, but treat
  every run as touching production data.
- The Stripe connector's write tool exists in the workspace. Morgan's rules
  (CLAUDE.md hard rule 1) forbid ever calling it.

## Questions resolved by Gregg (7 Jul 2026)

The three observations from the sample digest, answered in chat:

1. Same-day Lovable/Anthropic receipts on 6 July — **separate, planned
   charges**, not duplicates. Rule noted in categorisation-rules.yaml.
2. trAIned — **a trading name of the same business; include its income in
   these books.** Recorded in CLAUDE.md and the income indicators.
3. The $19 USD May "subscription creation" charge — **a test event**, to be
   excluded from the books. A test-payment exclusion rule now exists.
