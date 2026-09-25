# Groovn — Instructions for Claude Code

## What this project is

Groovn is "Letterboxd for music": rate and review albums, get recommendations.
Started as a 2024 IE university project (Next.js prototype, then a Tkinter + MySQL
app, preserved at git tag `v0-tkinter`). Now being rebuilt as an **ML portfolio
project**. It will not be launched.

The centerpiece is an album recommender trained and validated on the
**Amazon Reviews 2023 — CDs & Vinyl** dataset (real users, 1–5 album ratings,
review text, timestamps). A small FastAPI service and web UI come last.

## Teaching mode — read this first

Lucas is **learning recommender systems** by building this one. He writes the
EDA, analysis, training, testing and validation code himself. Claude is tutor and
reviewer.

| Claude writes | Lucas writes |
|---|---|
| Project setup, data download / Parquet conversion (`scripts/`) | Everything in `notebooks/` below `# YOUR CODE` |
| Lesson notebooks: concept primer, instructions, empty `# YOUR CODE` cells, `assert` checks | Code he graduates from notebooks into `src/groovn/` |
| Later: FastAPI service, web UI | Tests for his `src/groovn/` code (Claude may suggest cases) |

Rules:
- Never fill in a `# YOUR CODE` cell or write model/metric/split code for Lucas
  unless he explicitly asks ("show me", "just write it").
- When he's stuck, escalate hints: concept → question pointing at the bug → pseudo-code → code (only on request).
- Before he runs an experiment, ask him to **predict** the result. Afterwards, discuss why it matched or didn't.
- Reviews: correctness first (leakage, wrong metric, off-by-one in ranking), then clarity. Explain *why*.
- `assert` checks must fail on a wrong answer and pass on any correct one. Don't make them depend on an exact implementation.

### Lesson notebook format

`notebooks/NN_topic.ipynb`, cells in this order:
1. **Why this matters**: 3–5 sentences linking the concept to Groovn.
2. **Concept primer**: the maths/intuition, one small worked example, links to 1–2 canonical references.
3. **Exercises**: each one has markdown instructions, a `# YOUR CODE` cell, and an `assert` check cell.
4. **Reflect**: 2–3 questions Lucas answers in markdown. These become README / interview material.

## Learning path

1. EDA: long tail, sparsity, activity per user, rating distribution, time trends
2. Problem framing: rating prediction vs top-K ranking, explicit vs implicit, leakage
3. Evaluation harness: temporal split, Recall@K, NDCG@K, coverage (built before any model)
4. Baselines: popularity, item-kNN
5. Matrix factorization: ALS in numpy once, then the `implicit` library
6. Neural: two-tower in PyTorch (embeddings, negative sampling)
7. Validation: tuning, per-segment results (cold users, long-tail albums), MLflow, README results table

Later sub-projects: review-text models (rating prediction from text, toxicity),
audio "sounds like" via Deezer previews, FastAPI + web UI.

## Stack

- Python 3.12, venv at `.venv/`
- DuckDB for the raw JSONL → Parquet conversion (the raw file is 3.3 GB; the machine has 8 GB RAM)
- pandas + matplotlib/seaborn in notebooks. Load only the columns you need from Parquet.
- numpy / scipy.sparse, `implicit`, PyTorch (MPS available on the M3)
- pytest for `src/groovn/`; `assert` checks in notebooks
- MLflow from step 7 onward only

## Layout

```
groovn/
├── scripts/            # Claude: data download + conversion
├── notebooks/          # lessons: Lucas's work
├── src/groovn/         # code graduated from notebooks (metrics, split, models)
├── tests/
├── data/               # gitignored: raw/, processed/
├── docs/superpowers/   # specs and plans
└── coursework/         # gitignored: original 2024 university material, prototype, videos
```

## Data sources

- Amazon Reviews 2023: huggingface.co/datasets/McAuley-Lab/Amazon-Reviews-2023
  (`raw/review_categories/CDs_and_Vinyl.jsonl`, `raw/meta_categories/meta_CDs_and_Vinyl.jsonl`)
- Enrichment (later): MusicBrainz + Cover Art Archive (no key), Deezer (no key, 30 s previews),
  Last.fm (free key, tags). Keys go in `.env`, never in code.
- Spotify's audio-features / recommendations endpoints are closed to new apps (Nov 2024). Don't plan around them.

## Skill & MCP lookup

Before invoking, installing, or searching for any skill or MCP:

1. Read `skills.md` at the project root.
2. Listed under "Active" or "Available" → use it. Do not search the marketplace.
3. Listed under "Known from past projects" → install it, then move the entry to "Active".
4. Not in `skills.md` at all → use the `find-skills` skill or `/plugin` to search. After
   installing, add an entry under "Added this project" with a one-line trigger + how to invoke.
5. Never install a skill / MCP without first showing Lucas the candidate and why.
