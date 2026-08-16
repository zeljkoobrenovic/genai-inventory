#!/usr/bin/env python3
"""Merge research-agent result files into the inventory JSON data files.

Usage:
    python3 scripts/merge_updates.py <results_dir> [YYYY-MM-DD]

<results_dir> holds one JSON file per research agent:
  * per-lab model files (any name except running.json / agents_swe.json):
      {"lab": "<name as in data.json>", "additions": [model...], "updates":
       [{"id":..., "changes": {...}, "reason":...}], "removals": [...], ...}
  * running.json:
      {"option_updates": [{"name":..., "notes":...}], "option_additions": [option...],
       "option_removals": [...], "timeline_additions": [milestone...]}
  * agents_swe.json:
      {"agents": {option_updates/additions/removals}, "software_engineering": {...},
       "timeline_additions": [milestone...]}

Rules: additions are inserted at the top of the lab's model list (the site sorts by
release_date itself); duplicates by id/name are skipped; dict fields in updates are merged,
scalars overwritten; removals are only logged, never applied; null fields are dropped;
timeline milestones are de-duplicated by (name, date). Safe to re-run.
"""
import glob
import json
import os
import sys
import datetime

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REPO = os.path.join(ROOT, 'data') + '/'
CATS = {'frontier_omni', 'reasoning', 'agentic_coding', 'media_generation',
        'embeddings_retrieval', 'small_edge', 'open_weight_foundation'}


def load(p):
    return json.load(open(p))


def save(p, d):
    with open(p, 'w') as f:
        json.dump(d, f, indent=4, ensure_ascii=False)
        f.write('\n')


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    res = sys.argv[1].rstrip('/') + '/'
    today = sys.argv[2] if len(sys.argv) > 2 else datetime.date.today().isoformat()
    log = []

    # ---------- data.json ----------
    data = load(REPO + 'data.json')
    labs = {l['name']: l for l in data['frontier_labs']}
    for f in sorted(glob.glob(res + '*.json')):
        base = os.path.basename(f)
        if base in ('running.json', 'agents_swe.json'):
            continue
        r = load(f)
        lab = labs.get(r.get('lab'))
        if lab is None:
            log.append(f'!! unknown lab {r.get("lab")} in {base}')
            continue
        ids = {m['id']: m for m in lab['models']}
        for m in r.get('additions') or []:
            if m['id'] in ids:
                log.append(f'  skip dup {lab["name"]}: {m["id"]}')
                continue
            assert m['category'] in CATS, (base, m['id'], m['category'])
            for k in ('id', 'name', 'release_date', 'modalities', 'access'):
                assert k in m, (base, m.get('id'), k)
            m = {k: v for k, v in m.items() if v is not None}
            lab['models'].insert(0, m)
            ids[m['id']] = m
            log.append(f'  + {lab["name"]}: {m["name"]} ({m["release_date"]})')
        for u in r.get('updates') or []:
            m = ids.get(u['id'])
            if not m:
                log.append(f'!! update for unknown id {u["id"]} in {base}')
                continue
            for k, v in u['changes'].items():
                if isinstance(v, dict) and isinstance(m.get(k), dict):
                    m[k].update(v)
                else:
                    m[k] = v
            log.append(f'  ~ {lab["name"]}: {u["id"]} {list(u["changes"])} -- {u.get("reason", "")}')
        for rm in r.get('removals') or []:
            rid = rm['id'] if isinstance(rm, dict) else rm
            log.append(f'  ? removal requested {lab["name"]}: {rid} (NOT applied automatically)')
    data['updated_at'] = today
    save(REPO + 'data.json', data)

    # ---------- option files ----------
    def apply_options(path, r):
        d = load(path)
        byname = {o['name']: o for o in d['options']}
        for u in r.get('option_updates') or []:
            o = byname.get(u['name'])
            if not o:
                log.append(f'!! {os.path.basename(path)}: unknown option {u["name"]}')
                continue
            o['notes'] = u['notes']
            log.append(f'  ~ {os.path.basename(path)}: {u["name"]}')
        for a in r.get('option_additions') or []:
            if a['name'] in byname:
                log.append(f'  skip dup option {a["name"]}')
                continue
            a.pop('sources', None)
            d['options'].append(a)
            byname[a['name']] = a
            log.append(f'  + {os.path.basename(path)}: {a["name"]} [{a["category"]}]')
        for rm in r.get('option_removals') or []:
            log.append(f'  ? removal requested {os.path.basename(path)}: {rm} (NOT applied)')
        d['updated_at'] = today
        save(path, d)

    tl_add = []
    if os.path.exists(res + 'running.json'):
        r = load(res + 'running.json')
        apply_options(REPO + 'running.json', r)
        tl_add += r.get('timeline_additions') or []
    if os.path.exists(res + 'agents_swe.json'):
        r = load(res + 'agents_swe.json')
        apply_options(REPO + 'agents.json', r.get('agents', {}))
        apply_options(REPO + 'software-engineering.json', r.get('software_engineering', {}))
        tl_add += r.get('timeline_additions') or []

    # ---------- timeline ----------
    tl = load(REPO + 'tools-timeline.json')
    existing = {(m['name'], m['date']) for m in tl['milestones']}
    for m in tl_add:
        if (m['name'], m['date']) in existing:
            continue
        tl['milestones'].append(m)
        existing.add((m['name'], m['date']))
        log.append(f'  + timeline: {m["date"]} {m["name"]} [{m["domain"]}/{m["category"]}]')
    tl['updated_at'] = today
    save(REPO + 'tools-timeline.json', tl)

    print('\n'.join(log))


if __name__ == '__main__':
    main()
