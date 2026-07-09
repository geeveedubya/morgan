#!/usr/bin/env python3
"""Build Morgan's day-book dashboard (briefings/dashboard.html) from the books.

Reads: books/2026-27/*.yaml, books/pending/queue.yaml, books/watching.yaml,
books/hours-snapshot.yaml. Writes a single self-contained HTML page (no external
requests — Artifact CSP-safe). Run from the repo root:  python3 scripts/build_dashboard.py
"""
import yaml, glob, json, html, datetime
from collections import defaultdict

CAT_LABELS = {
    'office_costs_and_software': 'Office & software',
    'equipment': 'Equipment',
    'travel': 'Travel & parking',
    'marketing_and_website': 'Marketing & website',
    'phone_and_internet': 'Phone & internet',
    'bank_and_payment_fees': 'Bank & payment fees',
    'professional_fees': 'Professional fees',
    'sales': 'Sales', 'personal': 'Personal', 'exclude': 'Excluded', '': 'Uncategorised',
}
MONTH_NAMES = {'04': 'Apr', '05': 'May', '06': 'Jun', '07': 'Jul', '08': 'Aug', '09': 'Sep',
               '10': 'Oct', '11': 'Nov', '12': 'Dec', '01': 'Jan', '02': 'Feb', '03': 'Mar'}

def gbp(x):
    return f"£{x:,.2f}"

def load():
    months, cat, clients = [], defaultdict(float), defaultdict(float)
    for f in sorted(glob.glob('books/2026-27/*.yaml')):
        d = yaml.safe_load(open(f))
        months.append({'month': d['month'], 'label': MONTH_NAMES[d['month'][-2:]],
                       'income': d['totals']['income_gbp'], 'expenses': d['totals']['expenses_gbp']})
        for e in d['entries']:
            if e['proposed_category'] == 'sales':
                desc = e['description']
                if 'Craig' in desc or 'Arctic Ape' in desc: clients['Arctic Ape'] += e['amount']
                elif 'Stefan' in desc: clients['Stefan Brozin'] += e['amount']
                else: clients['Other / unnamed'] += e['amount']
            else:
                cat[e['proposed_category']] += e['amount']
    q = yaml.safe_load(open('books/pending/queue.yaml'))['queue']
    status = defaultdict(int); pending = []
    for e in q:
        status[e['status']] += 1
        if e['status'] == 'pending':
            pending.append(e)
    watching = yaml.safe_load(open('books/watching.yaml'))['watching']
    hours = yaml.safe_load(open('books/hours-snapshot.yaml'))
    return months, cat, clients, dict(status), pending, watching, hours

def build():
    months, cat, clients, status, pending, watching, hours = load()
    today = datetime.date.today().isoformat()
    income = round(sum(m['income'] for m in months), 2)
    expenses = round(sum(m['expenses'] for m in months), 2)
    net = round(income - expenses, 2)
    top_client, top_amt = max(clients.items(), key=lambda kv: kv[1])
    share = round(100 * top_amt / income) if income else 0
    hrs = hours.get('tax_year_total_hours', 0)
    rate = round(clients.get('Arctic Ape', 0) / hrs, 2) if hrs else None
    peak = max(months, key=lambda m: m['income'])
    scale = max([max(m['income'], m['expenses']) for m in months] + [1])

    tale = (f"Since 6 April you've invoiced and been paid {gbp(income)}, almost all of it settled "
            f"through Stripe. {html.escape(top_client)} is the backbone — {gbp(top_amt)}, about {share}% of income"
            + (f", earned across {hrs} logged hours (≈ {gbp(rate)}/hour)" if rate else "") + ". "
            f"{peak['label']} was the strongest month at {gbp(peak['income'])}. Spending is lean: "
            f"{gbp(expenses)} booked so far, dominated by the software that runs the business. "
            f"Net position: {gbp(net)} before the items still awaiting exact amounts.")

    def bars():
        out = []
        for m in months:
            hi = max(1, round(140 * m['income'] / scale)); he = max(1, round(140 * m['expenses'] / scale))
            out.append(f'''<div class="bgroup" role="img" aria-label="{m['label']}: income {gbp(m['income'])}, expenses {gbp(m['expenses'])}">
  <div class="bpair"><div class="blabel">{f"{gbp(m['income'])}" if m['income'] else ""}</div>
    <div class="bar inc" style="height:{hi if m['income'] else 2}px" data-tip="{m['label']} income · {gbp(m['income'])}"></div>
    <div class="bar exp" style="height:{he if m['expenses'] else 2}px" data-tip="{m['label']} expenses · {gbp(m['expenses'])}"></div></div>
  <div class="baxis">{m['label']}</div></div>''')
        return '\n'.join(out)

    def catbars():
        total = sum(cat.values()) or 1
        mx = max(cat.values()) if cat else 1
        rows = []
        for k, v in sorted(cat.items(), key=lambda kv: -kv[1]):
            w = max(2, round(100 * v / mx))
            rows.append(f'''<div class="crow" data-tip="{CAT_LABELS.get(k,k)} · {gbp(v)} · {round(100*v/total)}% of expenses">
  <span class="cname">{CAT_LABELS.get(k, k)}</span>
  <span class="ctrack"><span class="cfill" style="width:{w}%"></span></span>
  <span class="cval">{gbp(v)}</span></div>''')
        return '\n'.join(rows)

    def clientrows():
        mx = max(clients.values()) if clients else 1
        rows = []
        for k, v in sorted(clients.items(), key=lambda kv: -kv[1]):
            w = max(2, round(100 * v / mx))
            rows.append(f'''<div class="crow" data-tip="{html.escape(k)} · {gbp(v)}">
  <span class="cname">{html.escape(k)}</span>
  <span class="ctrack"><span class="cfill inc" style="width:{w}%"></span></span>
  <span class="cval">{gbp(v)}</span></div>''')
        return '\n'.join(rows)

    def pipeline():
        order = [('booked', 'Booked'), ('approved', 'Approved · amounts pending'),
                 ('pending', 'Needs your decision'), ('declined', 'Declined (kept)')]
        total = sum(status.values()) or 1
        segs, leg = [], []
        for key, label in order:
            n = status.get(key, 0)
            if n:
                segs.append(f'<span class="seg s-{key}" style="flex:{n}" data-tip="{label}: {n}"></span>')
            leg.append(f'<span class="lg"><span class="dot s-{key}"></span>{label} <b>{n}</b></span>')
        return '<div class="pipe">' + ''.join(segs) + '</div><div class="legend">' + ''.join(leg) + '</div>'

    def pendrows():
        if not pending:
            return '<p class="empty">Queue is clear — nothing needs you.</p>'
        rows = []
        for e in pending:
            amt = gbp(e['amount']) if isinstance(e.get('amount'), (int, float)) else '—'
            if e.get('currency') not in (None, 'GBP') and isinstance(e.get('amount'), (int, float)):
                amt = f"{e['amount']:,.2f} {e['currency']}"
            rows.append(f'''<tr><td class="mono">{str(e['date'])[5:]}</td><td>{html.escape(e['description'])}</td>
<td class="mono num">{amt}</td><td><span class="chip">{CAT_LABELS.get(e['proposed_category'], e['proposed_category'])}</span></td></tr>''')
        return ('<table class="ptable"><thead><tr><th>Date</th><th>Item</th><th>Amount</th><th>Proposed</th></tr></thead><tbody>'
                + '\n'.join(rows) + '</tbody></table>'
                + '<p class="hint">To decide: open your Morgan session and reply, e.g. “approve 1, decline 2”.</p>')

    watch_html = '\n'.join(f'<li>{html.escape(w["item"])} <span class="since">since {str(w["since"])[5:]}</span></li>' for w in watching)
    n_pending = status.get('pending', 0)

    page = f'''<title>Morgan · Oxford Circus Digital day-book</title>
<style>
:root {{
  --paper:#fbfbf9; --card:#ffffff; --ink:#1a1d18; --ink2:#5a6055; --line:#e4e6df;
  --accent:#1e6b4f; --inc:#2a78d6; --exp:#1baf7a; --slot3:#eda100;
  --warn-bg:#fdf3e2; --warn-ink:#7c4a02; --shadow:0 1px 2px rgba(26,29,24,.05);
}}
@media (prefers-color-scheme: dark) {{ :root {{
  --paper:#161815; --card:#1d201c; --ink:#f2f3ef; --ink2:#b9beb2; --line:#2b2e28;
  --accent:#4fae87; --inc:#3987e5; --exp:#199e70; --slot3:#c98500;
  --warn-bg:#33270f; --warn-ink:#eec680; --shadow:none;
}} }}
:root[data-theme="dark"] {{
  --paper:#161815; --card:#1d201c; --ink:#f2f3ef; --ink2:#b9beb2; --line:#2b2e28;
  --accent:#4fae87; --inc:#3987e5; --exp:#199e70; --slot3:#c98500;
  --warn-bg:#33270f; --warn-ink:#eec680; --shadow:none;
}}
:root[data-theme="light"] {{
  --paper:#fbfbf9; --card:#ffffff; --ink:#1a1d18; --ink2:#5a6055; --line:#e4e6df;
  --accent:#1e6b4f; --inc:#2a78d6; --exp:#1baf7a; --slot3:#eda100;
  --warn-bg:#fdf3e2; --warn-ink:#7c4a02; --shadow:0 1px 2px rgba(26,29,24,.05);
}}
* {{ box-sizing:border-box }}
body {{ background:var(--paper); color:var(--ink); margin:0;
  font:15px/1.55 system-ui,-apple-system,"Segoe UI",sans-serif; }}
.mono {{ font-family:ui-monospace,SFMono-Regular,Menlo,Consolas,monospace; font-variant-numeric:tabular-nums; }}
.wrap {{ max-width:1060px; margin:0 auto; padding:28px 20px 60px; }}
header {{ display:flex; justify-content:space-between; align-items:baseline; flex-wrap:wrap; gap:8px;
  border-bottom:3px double var(--line); padding-bottom:14px; }}
.brand {{ font-size:13px; letter-spacing:.14em; text-transform:uppercase; color:var(--accent); font-weight:700; }}
h1 {{ font-size:clamp(22px,3.4vw,30px); margin:2px 0 0; font-weight:750; letter-spacing:-.015em; text-wrap:balance; }}
.asof {{ color:var(--ink2); font-size:13px; }}
.stats {{ display:grid; grid-template-columns:repeat(auto-fit,minmax(170px,1fr)); gap:12px; margin:22px 0; }}
.stat {{ background:var(--card); border:1px solid var(--line); border-radius:6px; padding:14px 16px; box-shadow:var(--shadow); }}
.stat .k {{ font-size:11px; letter-spacing:.1em; text-transform:uppercase; color:var(--ink2); }}
.stat .v {{ font-size:26px; font-weight:700; margin-top:2px; }}
.stat.attn {{ border-color:var(--warn-ink); background:var(--warn-bg); color:var(--warn-ink); }}
.stat.attn .k {{ color:var(--warn-ink); }}
.tale {{ font-size:16.5px; max-width:68ch; color:var(--ink); border-left:3px solid var(--accent);
  padding:2px 0 2px 16px; margin:6px 0 26px; }}
.grid {{ display:grid; grid-template-columns:repeat(auto-fit,minmax(300px,1fr)); gap:14px; }}
.panel {{ background:var(--card); border:1px solid var(--line); border-radius:6px; padding:16px 18px; box-shadow:var(--shadow); }}
.panel h2 {{ font-size:12px; letter-spacing:.1em; text-transform:uppercase; color:var(--ink2); margin:0 0 14px; font-weight:700; }}
.chart {{ display:flex; gap:18px; align-items:flex-end; min-height:190px; padding-top:16px; }}
.bgroup {{ flex:1; display:flex; flex-direction:column; align-items:center; gap:6px; }}
.bpair {{ display:flex; gap:3px; align-items:flex-end; position:relative; }}
.blabel {{ position:absolute; top:-20px; left:50%; transform:translateX(-50%); font-size:11px; color:var(--ink2);
  font-family:ui-monospace,monospace; white-space:nowrap; }}
.bar {{ width:26px; border-radius:4px 4px 0 0; cursor:default; }}
.bar.inc {{ background:var(--inc); }} .bar.exp {{ background:var(--exp); }}
.baxis {{ font-size:12px; color:var(--ink2); border-top:1px solid var(--line); width:100%; text-align:center; padding-top:5px; }}
.legend {{ display:flex; flex-wrap:wrap; gap:14px; margin-top:12px; font-size:12.5px; color:var(--ink2); }}
.lg b {{ color:var(--ink); }}
.dot {{ display:inline-block; width:9px; height:9px; border-radius:2px; margin-right:5px; }}
.dot.inc,.s-booked {{ background:var(--inc); }} .dot.exp {{ background:var(--exp); }}
.crow {{ display:grid; grid-template-columns:minmax(110px,38%) 1fr auto; gap:10px; align-items:center; margin:9px 0; }}
.cname {{ font-size:13.5px; }}
.ctrack {{ background:var(--line); border-radius:3px; height:12px; overflow:hidden; display:block; }}
.cfill {{ display:block; height:100%; background:var(--exp); border-radius:3px; }}
.cfill.inc {{ background:var(--inc); }}
.cval {{ font-size:13px; font-family:ui-monospace,monospace; font-variant-numeric:tabular-nums; color:var(--ink2); }}
.pipe {{ display:flex; gap:2px; height:16px; border-radius:4px; overflow:hidden; }}
.seg {{ display:block; }}
.s-booked {{ background:var(--inc); }} .s-approved {{ background:var(--slot3); }}
.s-pending {{ background:var(--exp); }} .s-declined {{ background:var(--line); }}
.dot.s-declined {{ border:1px solid var(--ink2); }}
.ptable {{ width:100%; border-collapse:collapse; font-size:13.5px; }}
.ptable th {{ text-align:left; font-size:11px; letter-spacing:.08em; text-transform:uppercase; color:var(--ink2);
  border-bottom:1px solid var(--line); padding:4px 8px 6px; }}
.ptable td {{ border-bottom:1px solid var(--line); padding:8px; vertical-align:top; }}
.ptable td.num {{ text-align:right; white-space:nowrap; }}
.chip {{ font-size:11.5px; border:1px solid var(--line); border-radius:10px; padding:1px 8px; color:var(--ink2); white-space:nowrap; }}
.hint,.empty {{ color:var(--ink2); font-size:13px; }}
ul.watch {{ margin:0; padding-left:18px; }} ul.watch li {{ margin:8px 0; font-size:14px; }}
.since {{ color:var(--ink2); font-size:12px; }}
footer {{ margin-top:26px; color:var(--ink2); font-size:12.5px; border-top:1px solid var(--line); padding-top:12px; max-width:75ch; }}
#tip {{ position:fixed; pointer-events:none; background:var(--ink); color:var(--paper); font-size:12px;
  padding:4px 9px; border-radius:4px; opacity:0; transition:opacity .12s; z-index:10; white-space:nowrap; }}
@media (prefers-reduced-motion:reduce) {{ #tip {{ transition:none }} }}
.tablewrap {{ overflow-x:auto; }}
</style>
<div class="wrap">
<header>
  <div><div class="brand">Morgan · Day-book</div>
  <h1>Oxford Circus Digital — tax year 2026/27</h1></div>
  <div class="asof mono">as of {today} · books current to last scan</div>
</header>

<div class="stats">
  <div class="stat"><div class="k">Net position</div><div class="v mono">{gbp(net)}</div></div>
  <div class="stat"><div class="k">Income booked</div><div class="v mono">{gbp(income)}</div></div>
  <div class="stat"><div class="k">Expenses booked</div><div class="v mono">{gbp(expenses)}</div></div>
  <div class="stat{' attn' if n_pending else ''}"><div class="k">Needs your decision</div><div class="v mono">{n_pending}</div></div>
</div>

<p class="tale">{tale}</p>

<div class="grid">
  <div class="panel"><h2>Month by month</h2>
    <div class="chart">{bars()}</div>
    <div class="legend"><span class="lg"><span class="dot inc"></span>Income</span>
    <span class="lg"><span class="dot exp"></span>Expenses</span></div></div>
  <div class="panel"><h2>Where the money goes</h2>{catbars()}</div>
  <div class="panel"><h2>Who pays you</h2>{clientrows()}
    <p class="hint" style="margin-top:12px">{hrs}h logged in Airtable this tax year{f" · ≈ {gbp(rate)}/hour on Arctic Ape work" if rate else ""}</p></div>
  <div class="panel"><h2>The queue — every transaction's journey</h2>{pipeline()}</div>
</div>

<div class="panel" style="margin-top:14px"><h2>Waiting on you ({n_pending})</h2><div class="tablewrap">{pendrows()}</div></div>

<div class="panel" style="margin-top:14px"><h2>Morgan is watching</h2><ul class="watch">{watch_html}</ul></div>

<footer>Every figure traces to a booked entry in <span class="mono">books/2026-27/</span>, approved by Gregg in chat —
nothing here was categorised without him. Pending and declined items live in <span class="mono">books/pending/queue.yaml</span>.
Morgan reads Stripe, Gmail and Airtable; it never moves money, never sends anything, never files with HMRC.</footer>
</div>
<div id="tip" role="status"></div>
<script>
const tip = document.getElementById('tip');
document.querySelectorAll('[data-tip]').forEach(el => {{
  el.addEventListener('mousemove', e => {{
    tip.textContent = el.dataset.tip; tip.style.opacity = 1;
    tip.style.left = Math.min(e.clientX + 12, innerWidth - tip.offsetWidth - 8) + 'px';
    tip.style.top = (e.clientY + 14) + 'px';
  }});
  el.addEventListener('mouseleave', () => tip.style.opacity = 0);
}});
</script>'''
    open('briefings/dashboard.html', 'w').write(page)
    print(f"briefings/dashboard.html written — income {gbp(income)}, expenses {gbp(expenses)}, net {gbp(net)}, pending {n_pending}")

if __name__ == '__main__':
    build()
