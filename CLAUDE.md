# GenAI Inventory

A hand-curated inventory of generative-AI models, hosting options, agent frameworks and
software-engineering agents, published as a static site (GitHub Pages from `docs/`):
https://zeljkoobrenovic.github.io/genai-inventory/

## Layout

- `data/data.json` — labs (`frontier_labs[]`) and their `models[]`; `model_categories` lists the
  allowed `category` values. Model fields: `id`, `name`, `release_date` (`YYYY-MM-DD`, or
  `YYYY-MM` / `YYYY` if unknown), `category`, `modalities[]`, `context_window_tokens`, `access{}`
  (free-form boolean/string flags; only `open_source` / `open_weights` drive site behaviour),
  optional `pricing{input_per_million_tokens, output_per_million_tokens}`, `parameters`,
  `activated_parameters`, `features[]`, `based_on`.
- `data/running.json` — where to run LLMs (managed APIs, clouds, inference clouds, routers,
  GPU clouds, on-prem, engines, local runtimes, edge). `categories[]` + `options[]`.
- `data/agents.json` — agent-building platforms/frameworks/protocols. Same shape.
- `data/software-engineering.json` — coding/SWE agents and tools. Same shape.
- `data/tools-timeline.json` — `milestones[]` with `domain` (`hosting` | `app_agents` |
  `swe_agents`), `category` (must match a category id in the corresponding options file),
  `date`, `name`, `provider`, `summary`, `url`.
- `templates/template.html` — single-page app; `generate-docs.py` injects the JSON into it and
  writes `docs/index.html`. `docs/index.html` is generated — never edit it by hand.
- `docs/assets/` — logos. Labs use the `logo` field in data.json; options and timeline entries
  go through `imageOf(provider, name)` in the template, which maps names to logo files and falls
  back to `logo.png`. Add new mapping lines at the end of `imageOf` (256px favicons from
  `https://www.google.com/s2/favicons?domain=X&sz=256`, fetched with `curl -L`, work well).
  `node scripts/check_logos.js` lists providers on the default logo and broken mappings.
- `scripts/merge_updates.py` — merges research-agent result JSON into the data files (see the
  `update-inventory` skill).
- `scripts/check_logos.js` — logo coverage check (Node; evaluates `imageOf` from the template).
- `main.py` — unrelated podcast-analysis experiment (depends on a missing `speaking_agents`
  package); ignore.
- `LINKEDIN.txt` — draft announcement post for the latest update.

## Conventions

- Every `data/*.json` has a top-level `updated_at`; set it to the update date.
- Model order inside a lab does not matter (the site sorts by `release_date`); insert new
  models at the top to keep diffs small. Do not re-sort existing lists.
- One entry per distinct release. New checkpoints of an existing model (e.g. DeepSeek
  V4 Pro 0813) get their own entry rather than rewriting the original `release_date`.
- Retired models stay in the list; mark them via `access` flags (`legacy`, `eol_date`, …).
  Weights that are only promised go in `open_weights_planned` (date or text), not `open_weights`.
- Missing pre-window models may be backfilled when an official dated source exists.
- The `hosting` timeline also records major model launches on managed APIs (e.g. Claude Opus 5.5).
- `notes` on options are 1–3 sentences: what it is + the latest notable capabilities/releases.
  No rumours or unconfirmed funding talk.
- Only add things verifiable with a dated primary/official source. Never invent models.
- After changing data or template: `python3 generate-docs.py`, then commit data + docs together.
  Commit messages are terse: "new data (<date> update)", "post update", "new logos".
- JSON is written with `indent=4`, `ensure_ascii=False`, trailing newline.
