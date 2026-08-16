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
"flag pre-window models missing from the list". Agents can exhaust WebSearch budget — tell them
to fall back to WebFetch of official blogs/changelogs/Hugging Face.

## 3. Merge

```
python3 scripts/merge_updates.py <scratch>/results <today>
git diff --stat
```
Review the log and `git diff` for: `!!` lines (unknown lab/id/option), rewritten
`release_date`s of existing entries (turn into separate checkpoint entries instead), rumours in
notes, over-long notes, and speculative additions. Fix by editing the result JSON and
re-running (the script is idempotent) or by small post-edits. Do not apply removals blindly.

Sanity checks: dates match `^\d{4}(-\d{2}(-\d{2})?)?$`, no duplicate ids, timeline categories
exist in the matching options file.

## 4. Regenerate, logos, commit

- `python3 generate-docs.py`
- New providers without a logo: fetch a 256px favicon into `docs/assets/<slug>.png`, add an
  `imageOf` mapping in `templates/template.html`, regenerate.
- Commit data + docs (+ template/assets) together, e.g. `new data (<date> update)`; push only
  if asked.

## 5. Optional: LinkedIn post

If asked, write `LINKEDIN.txt`: title with date, 1-line framing, a Models bullet block, a
Tools bullet block, 1-2 take-aways, links to the site and repo, hashtags. Keep it short
(~130 words unless told otherwise).
