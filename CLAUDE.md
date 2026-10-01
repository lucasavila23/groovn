# Groovn — Instructions for Claude Code

## What this project is

Groovn is "Letterboxd for music": rate and review albums, get recommendations.
Started as a 2024 IE university project (Next.js prototype, then a Tkinter + MySQL
app, preserved at git tag `v0-tkinter`). Now being rebuilt as an **ML portfolio
project**. It will not be launched.

The centerpiece is an album recommender trained and validated on the
**Amazon Reviews 2023 — CDs & Vinyl** dataset (real users, 1–5 album ratings,
review text, timestamps). A small FastAPI service and web UI come last.

## Build mode — read this first

Lucas was learning recommender systems by writing the notebooks himself with
Claude as tutor. As of 2026-10-01 he's handed the implementation to Claude:
Claude now writes the EDA, analysis, training, testing and validation code
directly in `notebooks/` and `src/groovn/`, with heavy explanatory markdown
(why each step is done, not just what it does) so Lucas can still follow and
learn from reading it.

| Claude writes | Lucas writes |
|---|---|
| Everything: notebooks, `src/groovn/`, tests, data pipeline | Review comments, steering decisions |

Rules:
- Explain the *why* in markdown cells: the concept, why this approach over
  alternatives, what would go wrong otherwise (leakage, wrong metric, etc.).
- Use fixed random seeds everywhere (splits, model init) for reproducibility.
- Correctness first (no leakage, right metric for the problem, no off-by-one
  in ranking), then clarity.
- Run notebooks end-to-end (e.g. `jupyter nbconvert --execute`) before calling
  a step done — a notebook with no real output isn't finished.
- Graduate reusable logic (splits, metrics, models) into `src/groovn/` with
  pytest coverage; notebooks import from there rather than redefining it.

### Notebook format

`notebooks/NN_topic.ipynb`: why this step matters for Groovn, the concept/math
primer with a small worked example, the implementation with results actually
run and plotted, then a short reflection on what the results show.

## Learning path

1. EDA (canonical): data quality + missingness (MCAR/MAR/MNAR), distributions, Lorenz/Gini, time, feature tables + correlations, PCA, truncated SVD preview
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
