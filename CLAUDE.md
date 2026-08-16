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
- `docs/assets/` — logos. `imageOf(provider, name)` in the template maps provider/option
  names to logo files; unknown ones fall back to `logo.png`. Add a mapping line there when
  adding a logo (256px PNG favicons from `https://www.google.com/s2/favicons?domain=X&sz=256`
  work well).
- `scripts/merge_updates.py` — merges research-agent result JSON into the data files (see the
  `update-inventory` skill).
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
- `notes` on options are 1–3 sentences: what it is + the latest notable capabilities/releases.
  No rumours or unconfirmed funding talk.
- Only add things verifiable with a dated primary/official source. Never invent models.
- After changing data or template: `python3 generate-docs.py`, then commit data + docs together.
  Commit messages historically are terse ("new data", "new data and logos").
- JSON is written with `indent=4`, `ensure_ascii=False`, trailing newline.
