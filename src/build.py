"""Build the static case study from evidence; no hand-entered aggregate numbers."""
import csv, html, json, re, zipfile, shutil
from collections import Counter
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
LABELS={'ready':'Build now','conditional':'With conditions','blocked':'Blocked','unknown':'Investigate'}

def auth_groups(values):
    out=set()
    for value in values:
        s=value.lower()
        if 'oauth1' in s or 'oauth 1' in s: out.add('OAuth1')
        elif 'oauth2' in s or 'oauth 2' in s: out.add('OAuth2')
        elif 'oauth' in s: out.add('OAuth (unspecified)')
        elif 'basic' in s: out.add('Basic')
        elif 'api' in s and 'key' in s: out.add('API key')
        elif any(x in s for x in ('token','pat','jwt','bearer')): out.add('Token')
        elif s in ('none','no auth','no authentication'): out.add('None')
        elif 'unknown' in s or 'unverified' in s: out.add('Unknown')
        else: out.add('Other')
    return sorted(out)

def gate_group(value):
    s=value.lower()
    if s in ('self_serve','self-serve','free','free_trial','open_source','none','account','trial','self_hosted','self_host_or_trial','trial_then_usage','trial_then_paid','plan_limits','permissions_and_scale'): return 'Self-serve / trial'
    if any(x in s for x in ('unknown','unverified','unresolved','unclear')): return 'Unresolved'
    if any(x in s for x in ('partner','sales','contact')): return 'Outreach'
    if any(x in s for x in ('review','approval','distribution','public_app','verification')): return 'Review / approval'
    if 'paid' in s or 'plan' in s or 'subscription' in s: return 'Paid / admin'
    if 'admin' in s: return 'Paid / admin'
    return 'Other conditions'

def build():
    from research import read, sample
    rows=read(ROOT/'data/research.json')
    for r in rows:
        r['auth_groups']=auth_groups(r['auth'])
        r['gate_group']=gate_group(r['access']['gate'])
    audit=read(ROOT/'data/verification.json') if (ROOT/'data/verification.json').exists() else {'checks':[],'method':'Agent audit pending'}
    links=read(ROOT/'data/link-checks.json') if (ROOT/'data/link-checks.json').exists() else []
    verdicts=Counter(r['verdict'] for r in rows)
    auth=Counter(a for r in rows for a in r['auth_groups'])
    gates=Counter(r['gate_group'] for r in rows)
    conditional_gates=Counter(r['gate_group'] for r in rows if r['verdict']=='conditional')
    categories=[]
    for cat in dict.fromkeys(r['category'] for r in rows):
        group=[r for r in rows if r['category']==cat]
        categories.append({'name':cat,'total':len(group),'verdicts':dict(Counter(r['verdict'] for r in group))})
    summary={'total':len(rows),'categories':len(categories),'verdicts':dict(verdicts),'auth':dict(auth),'gates':dict(gates),'conditional_gates':dict(conditional_gates),'official_mcp':sum(r['mcp']['status']=='official' for r in rows),'sources':len({c['url'] for r in rows for c in r['claims']}),'human_reviewed':0}
    data={'as_of':'2026-11-23','rows':rows,'summary':summary,'categories':categories,'verification':audit,'links':links,'sample_ids':[r['id'] for r in sample(rows)]}
    esc=html.escape
    table=[]
    for r in rows:
        first=next(iter(r['claims']),None)
        source=f'<a href="{esc(first["url"],quote=True)}" target="_blank" rel="noreferrer">Docs</a>' if first else 'Unresolved'
        table.append(f'''<tr data-id="{r['id']}"><th scope="row"><button class="app-name" data-open="{r['id']}">{esc(r['name'])}</button><span class="row-description">{esc(r['description'])}</span></th><td>{esc(', '.join(r['auth_groups']))}</td><td><b>{esc(r['gate_group'])}</b><span class="row-description">{esc(r['access']['sandbox'])}</span></td><td>{esc(' / '.join(r['api']['style']))}<span class="row-description">MCP: {esc(r['mcp']['status'].replace('_',' '))}</span></td><td><span class="pill {r['verdict']}">{LABELS[r['verdict']]}</span><span class="row-description">{esc(r['blocker'])}</span></td><td>{source}<button class="evidence-button" data-open="{r['id']}">Evidence ({len(r['claims'])})</button></td></tr>''')
    template=(ROOT/'src/template.html').read_text(encoding='utf-8')
    payload=json.dumps(data,ensure_ascii=False).replace('<','\\u003c').replace('&','\\u0026')
    page=template.replace('@@DATA@@',payload).replace('@@TABLE@@','\n'.join(table))
    dist=ROOT/'dist'; dist.mkdir(exist_ok=True)
    (dist/'index.html').write_text(page,encoding='utf-8')
    (dist/'research.json').write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf-8')
    (dist/'verification.json').write_text(json.dumps(audit,ensure_ascii=False,indent=2),encoding='utf-8')
    with (dist/'research.csv').open('w',encoding='utf-8-sig',newline='') as f:
        w=csv.writer(f); w.writerow(['id','app','category','description','auth','prototype_access','production_access','gate','api','api_breadth','mcp','verdict','blocker','confidence','evidence_urls'])
        for r in rows:
            w.writerow([r['id'],r['name'],r['category'],r['description'],'; '.join(r['auth']),r['access']['sandbox'],r['access']['production'],r['gate_group'],'; '.join(r['api']['style']),r['api']['breadth'],r['mcp']['status'],r['verdict'],r['blocker'],r['confidence'],'; '.join(dict.fromkeys(c['url'] for c in r['claims']))])
    (dist/'summary.json').write_text(json.dumps(summary,indent=2),encoding='utf-8')
    shutil.copy2(ROOT/'README.md',dist/'README.md')
    with zipfile.ZipFile(dist/'source.zip','w',zipfile.ZIP_DEFLATED) as archive:
        for name in ['research.py','README.md','.gitignore']:
            archive.write(ROOT/name,name)
        for folder in ['data','src','tests']:
            for path in sorted((ROOT/folder).rglob('*')):
                if path.is_file() and '__pycache__' not in path.parts:
                    archive.write(path,path.relative_to(ROOT))
    return data

if __name__=='__main__':
    import sys
    sys.path.insert(0,str(ROOT)); build()
