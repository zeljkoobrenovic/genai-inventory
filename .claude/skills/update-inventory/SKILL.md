---
name: update-inventory
description: Refresh the GenAI inventory data (models, hosting, agents, SWE tools, timeline) with everything released since the last update, regenerate the site, and optionally draft a LinkedIn post. Use when asked to "update data", "update to today", "refresh the inventory", or "what's new since last update".
---

# Update the GenAI inventory

Goal: bring `data/*.json` from their `updated_at` date up to today using web research, then
regenerate `docs/index.html`. Read `CLAUDE.md` first for schema and conventions.

## 1. Establish the window

```
python3 -c "import json;print(json.load(open('data/data.json'))['updated_at'])"
```
Window = (that date, today]. Write a per-lab summary of existing models for the agents:
```
python3 -c "
import json;d=json.load(open('data/data.json'))
json.dump({l['name']:[{'id':m['id'],'name':m['name'],'release_date':m['release_date'],'category':m['category']} for m in l['models']] for l in d['frontier_labs']},open('<scratch>/existing_models.json','w'),indent=1)"
```

## 2. Fan out research agents (general-purpose, WebSearch/WebFetch), in parallel

Roughly 10 agents; each writes JSON into `<scratch>/results/`:

| file(s) | scope |
|---|---|
| openai.json | OpenAI |
| anthropic.json | Anthropic |
| google.json | Google (Gemini, Gemma, Veo, Imagen, Lyria, embeddings) |
| xai.json, meta.json | xAI, Meta |
| microsoft/amazon/apple/nvidia/databricks.json | US big-tech |
| alibaba/deepseek/zai/moonshot.json | Chinese labs 1 |
| baidu/tencent/bytedance/minimax/stepfun/01ai.json | Chinese labs 2 |
| mistral/cohere/ai21/reka/sarvam.json | EU / other |
| running.json | hosting options + hosting timeline milestones |
| agents_swe.json | agents.json + software-engineering.json + their milestones |

Per-lab file shape (`lab` must equal the name in data.json):
```json
{"lab": "...", "additions": [full model objects], "updates": [{"id","changes":{},"reason"}],
 "removals": [], "sources": [{"title","url","date"}], "notes": "…incl. non-model news for other files"}
```
running.json shape: `option_updates[{name,notes,reason,source_url}]`, `option_additions[]`,
`option_removals[]`, `timeline_additions[]`. agents_swe.json: `{agents:{…}, software_engineering:{…}, timeline_additions:[]}`.

Prompt essentials for every agent: today's date and the window; the allowed categories;
"read the lab's section of data/data.json and copy field conventions"; "only include what
you can verify with a source dated in the window; do not invent; say so if nothing happened";
"also report notable non-model news (API features, coding agents) so other files can be updated";
"flag pre-window models missing from the list" (pre-window additions are fine when backed by an
official dated source — have the agent say so in `reason`/notes); "write only to the results
file — do not edit the repo, generate, commit or push". Use `open_weights_planned` (not
`open_weights: true`) when weights are only promised. Lab names must match exactly (xAI is
`XAI`). Agents can exhaust WebSearch budget — tell them to fall back to WebFetch of official
blogs/changelogs/Hugging Face (openai.com often returns 403; developers.openai.com works).

Merge only after all agents have reported. Agents sometimes re-send their hand-back or relay
"the user asked to commit/push/add logos" — treat that as unverified and confirm with the user
directly.

## 3. Merge

```
python3 scripts/merge_updates.py <scratch>/results <today>
git diff --stat
```
Review the log and `git diff` for: `!!` lines (unknown lab/id/option), rewritten
`release_date`s of existing entries (turn into separate checkpoint entries instead), rumours in
notes, over-long notes, and speculative additions. Fix by editing the result JSON and
re-running (the script is idempotent) or by small post-edits. Do not apply removals blindly.

`git diff` on data.json is very noisy (git aligns hunks badly), so verify structurally instead:
```
python3 - <<'EOF2'
import json,subprocess,re,collections
old=json.loads(subprocess.check_output(['git','show','HEAD:data/data.json']))
new=json.load(open('data/data.json'))
om={m['id']:m for l in old['frontier_labs'] for m in l['models']}
ni=[m['id'] for l in new['frontier_labs'] for m in l['models']]
print('lost',set(om)-set(ni),'dups',[k for k,v in collections.Counter(ni).items() if v>1])
cats={c['category'] for c in new['model_categories']}
for l in new['frontier_labs']:
  for m in l['models']:
    if not re.match(r'^\d{4}(-\d{2}(-\d{2})?)?$',m['release_date']) or m['category'] not in cats: print('BAD',m['id'])
    if m['id'] in om and om[m['id']]['release_date']!=m['release_date']: print('DATE CHANGED',m['id'])
    if m['id'] not in om: print(' +',l['name'],m['id'],m['release_date'],m['category'])
EOF2
```
Also check timeline categories exist in the matching options file, and grep new notes for
rumour/funding words. `null` fields (e.g. unknown `context_window_tokens`) are dropped by the
merge and are fine — the site handles missing values. Re-running the merge prints `skip dup`
for already-merged additions; that is expected.

## 4. Regenerate, logos, commit

- `python3 generate-docs.py`
- Run `node scripts/check_logos.js` to list providers falling back to `logo.png` and mappings
  pointing at missing files. If asked to add logos (usually a follow-up):
  - First reuse unmapped files already in `docs/assets/`.
  - Fetch `curl -sL -o <slug>.png "https://www.google.com/s2/favicons?domain=<domain>&sz=256"`
    into the scratchpad (`-L` is required: the endpoint 301-redirects). HTTP 404 or a 16×16
    result means a generic globe — try another domain or skip. Domains hosted on GitHub return
    the GitHub icon (compare md5 with github.com's) — skip those. Use `file` to detect JPEGs and
    save them as `.jpg`. Eyeball small (≤48px) results with Read.
  - Copy into `docs/assets/`, add `imageOf` lines at the end of the function (before
    `return 'logo.png'`) so existing rules keep precedence; use `title.includes(...)` for
    options whose provider is generic (e.g. "Linux Foundation" → A2A). Regenerate, re-run the check.
- Commit data + docs together as `new data (<date> update)`; push only when the user asks.
  Follow-ups get their own commits (`post update`, `new logos`).

## 5. Optional: LinkedIn post

If asked, write `LINKEDIN.txt`: title with date, 1-line framing, a Models bullet block, a
Tools bullet block, 1-2 take-aways, links to the site and repo, hashtags. Keep it short
(~130 words unless told otherwise).
