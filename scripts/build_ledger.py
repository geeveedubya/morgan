#!/usr/bin/env python3
"""Build Morgan's line-by-line ledger (briefings/ledger.html) from the books.

Reads books/2026-27/*.yaml (booked entries) and books/pending/queue.yaml
(approved-but-awaiting-amount items). Writes a self-contained, print-friendly
HTML ledger — every booked transaction, grouped by month, income and expenses
in separate columns with running totals, plus an appendix of items approved but
awaiting an exact amount. Run from repo root: python3 scripts/build_ledger.py
"""
import yaml, glob, html, datetime
from collections import defaultdict

CAT = {
 'sales':'Sales','office_costs_and_software':'Office & software','equipment':'Equipment',
 'travel':'Travel & parking','marketing_and_website':'Marketing & website',
 'phone_and_internet':'Phone & internet','bank_and_payment_fees':'Bank & payment fees',
 'professional_fees':'Professional fees','staff_costs':'Staff costs','use_of_home':'Use of home',
 'training_and_courses':'Training','exclude':'Excluded','': 'Uncategorised',
}
MON = {'04':'April','05':'May','06':'June','07':'July','08':'August','09':'September',
       '10':'October','11':'November','12':'December','01':'January','02':'February','03':'March'}

def gbp(x): return f"£{x:,.2f}"

def build():
    months=[]
    for f in sorted(glob.glob('books/2026-27/*.yaml')):
        d=yaml.safe_load(open(f)); months.append(d)
    q=yaml.safe_load(open('books/pending/queue.yaml'))['queue']
    awaiting=[e for e in q if e['status']=='approved']

    tot_in=tot_out=0
    sections=[]
    for d in months:
        m=d['month']; label=f"{MON[m[-2:]]} {m[:4]}"
        rows=[]; m_in=m_out=0
        for e in sorted(d['entries'], key=lambda x:(str(x['date']),x['id'])):
            amt=e['amount'] or 0
            is_inc = e['proposed_category']=='sales'
            if is_inc: m_in+=amt
            else: m_out+=amt
            inc = gbp(amt) if is_inc else ''
            out = gbp(amt) if not is_inc else ''
            note = e.get('note','')
            rows.append(f'''<tr>
  <td class="mono">{str(e['date'])[5:]}</td>
  <td>{html.escape(e['description'])}{f'<span class="note">{html.escape(note)}</span>' if note else ''}</td>
  <td><span class="chip">{CAT.get(e['proposed_category'],e['proposed_category'])}</span></td>
  <td class="mono num in">{inc}</td>
  <td class="mono num out">{out}</td>
</tr>''')
        tot_in+=m_in; tot_out+=m_out
        sections.append(f'''<section class="month">
  <div class="mhead"><h2>{label}</h2>
    <div class="msum mono">in {gbp(m_in)} · out {gbp(m_out)} · net {gbp(m_in-m_out)}</div></div>
  <div class="tablewrap"><table>
    <thead><tr><th>Date</th><th>Description</th><th>Category</th><th class="num">Income</th><th class="num">Expense</th></tr></thead>
    <tbody>{''.join(rows)}</tbody>
  </table></div>
</section>''')

    # appendix: approved awaiting amounts
    ap_rows=''.join(f'''<tr><td class="mono">{str(e['date'])[5:]}</td><td>{html.escape(e['description'])}</td>
      <td><span class="chip">{CAT.get(e['proposed_category'],e['proposed_category'] or '—')}</span></td>
      <td>{e.get('note','')and html.escape(e['note'])}</td></tr>''' for e in awaiting)
    appendix=f'''<section class="month appendix">
  <div class="mhead"><h2>Approved · awaiting exact amount ({len(awaiting)})</h2>
    <div class="msum mono">not yet in the totals</div></div>
  <div class="tablewrap"><table><thead><tr><th>Date</th><th>Item</th><th>Category</th><th>How it pins</th></tr></thead>
    <tbody>{ap_rows}</tbody></table></div>
</section>''' if awaiting else ''

    today=datetime.date.today().isoformat()
    page=f'''<title>Morgan · Ledger 2026/27</title>
<style>
:root {{ --paper:#fbfbf9; --card:#fff; --ink:#1a1d18; --ink2:#5a6055; --line:#e4e6df;
  --accent:#1e6b4f; --in:#1e6b4f; --out:#7c4a02; --chip:#eef1ea; }}
@media (prefers-color-scheme:dark){{:root{{ --paper:#161815; --card:#1d201c; --ink:#f2f3ef; --ink2:#b9beb2;
  --line:#2b2e28; --accent:#4fae87; --in:#4fae87; --out:#eec680; --chip:#23271f; }}}}
:root[data-theme="dark"]{{ --paper:#161815; --card:#1d201c; --ink:#f2f3ef; --ink2:#b9beb2; --line:#2b2e28;
  --accent:#4fae87; --in:#4fae87; --out:#eec680; --chip:#23271f; }}
:root[data-theme="light"]{{ --paper:#fbfbf9; --card:#fff; --ink:#1a1d18; --ink2:#5a6055; --line:#e4e6df;
  --accent:#1e6b4f; --in:#1e6b4f; --out:#7c4a02; --chip:#eef1ea; }}
*{{box-sizing:border-box}}
body{{background:var(--paper);color:var(--ink);margin:0;font:14px/1.5 system-ui,-apple-system,"Segoe UI",sans-serif}}
.mono{{font-family:ui-monospace,SFMono-Regular,Menlo,Consolas,monospace;font-variant-numeric:tabular-nums}}
.wrap{{max-width:960px;margin:0 auto;padding:26px 18px 60px}}
header{{border-bottom:3px double var(--line);padding-bottom:14px;margin-bottom:8px}}
.brand{{font-size:12px;letter-spacing:.14em;text-transform:uppercase;color:var(--accent);font-weight:700}}
h1{{font-size:clamp(20px,3vw,27px);margin:2px 0 0;font-weight:750;letter-spacing:-.01em}}
.asof{{color:var(--ink2);font-size:12.5px;margin-top:4px}}
.totbar{{display:flex;flex-wrap:wrap;gap:20px;margin:18px 0 8px;padding:14px 16px;background:var(--card);
  border:1px solid var(--line);border-radius:6px}}
.totbar div{{display:flex;flex-direction:column}}
.totbar .k{{font-size:11px;letter-spacing:.09em;text-transform:uppercase;color:var(--ink2)}}
.totbar .v{{font-size:22px;font-weight:700;margin-top:1px}}
.month{{margin-top:26px}}
.mhead{{display:flex;justify-content:space-between;align-items:baseline;gap:10px;flex-wrap:wrap;
  border-bottom:2px solid var(--line);padding-bottom:5px;margin-bottom:2px}}
.mhead h2{{font-size:16px;margin:0;font-weight:700}}
.msum{{font-size:12.5px;color:var(--ink2)}}
.tablewrap{{overflow-x:auto}}
table{{width:100%;border-collapse:collapse;font-size:13px}}
th{{text-align:left;font-size:10.5px;letter-spacing:.07em;text-transform:uppercase;color:var(--ink2);
  padding:7px 8px 5px;border-bottom:1px solid var(--line);white-space:nowrap}}
td{{padding:7px 8px;border-bottom:1px solid var(--line);vertical-align:top}}
td.num,th.num{{text-align:right;white-space:nowrap}}
td.in{{color:var(--in)}} td.out{{color:var(--out)}}
.note{{display:block;font-size:11.5px;color:var(--ink2);margin-top:2px;max-width:60ch}}
.chip{{font-size:11px;background:var(--chip);border-radius:10px;padding:1px 8px;color:var(--ink2);white-space:nowrap}}
.appendix{{opacity:.92}}
footer{{margin-top:30px;color:var(--ink2);font-size:12px;border-top:1px solid var(--line);padding-top:12px;max-width:78ch}}
@media print{{ body{{background:#fff}} .totbar,table,section{{break-inside:avoid}} }}
</style>
<div class="wrap">
<header>
  <div class="brand">Morgan · Ledger</div>
  <h1>Oxford Circus Digital — tax year 2026/27</h1>
  <div class="asof mono">booked entries only · 6 Apr 2026 – 5 Apr 2027 · generated {today}</div>
</header>
<div class="totbar">
  <div><span class="k">Income</span><span class="v mono">{gbp(tot_in)}</span></div>
  <div><span class="k">Expenses</span><span class="v mono">{gbp(tot_out)}</span></div>
  <div><span class="k">Net</span><span class="v mono">{gbp(tot_in-tot_out)}</span></div>
</div>
{''.join(sections)}
{appendix}
<footer>Every line here was approved by Gregg in chat before being booked. Declined and pending items are
kept in <span class="mono">books/pending/queue.yaml</span>; the full audit trail and monthly YAML ledgers
live in the repository. Amounts are GBP, recorded gross (not VAT-registered). This is a prepared record for
the accountant — Morgan never files with HMRC.</footer>
</div>'''
    open('briefings/ledger.html','w').write(page)
    print(f"briefings/ledger.html — income {gbp(tot_in)}, expenses {gbp(tot_out)}, net {gbp(tot_in-tot_out)}, {len(awaiting)} awaiting")

if __name__=='__main__':
    build()
