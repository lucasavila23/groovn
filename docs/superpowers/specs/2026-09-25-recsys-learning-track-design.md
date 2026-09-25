# Groovn recommender: learning track (design)

Date: 2026-09-25 · Status: draft, awaiting Lucas's review

## Intent

**What Lucas said.** Rebuild Groovn (Letterboxd for music) as an ML portfolio piece, not
a launch. The focus is recommendation engines and neural networks, not LLMs. He has
never built a recommender and wants to **learn by doing**: he writes the EDA, analysis,
training, testing and validation himself, and Claude teaches and reviews. Format: guided
notebooks (concept primer + `# YOUR CODE` cells + `assert` checks). Keep the name
Groovn and the GitHub repo `lucasavila23/groovn`.

**Assumptions (correct if wrong).**
- Success means Lucas can explain and defend every modelling choice in an interview,
  and the README carries an honest results table. It does not mean hitting a
  particular score.
- Pace is one lesson at a time, with no deadline.
- Everything runs locally on an Apple M3 with 8 GB RAM. No cloud GPUs.

## Scope

In scope: data foundation plus lessons 1–7 (EDA through validation).
Out of scope, each getting its own spec later: review-text models (rating from text,
toxicity), audio "sounds like" (Deezer previews), FastAPI + web UI rebrand.

## Data

**Source:** Amazon Reviews 2023, CDs & Vinyl (McAuley Lab, Hugging Face).
- `raw/review_categories/CDs_and_Vinyl.jsonl`: 3.3 GB, about 4.8 M ratings
- `raw/meta_categories/meta_CDs_and_Vinyl.jsonl`: 0.95 GB of album metadata
- `benchmark/5core/timestamp_w_his/`: the authors' own filtered, time-split files.
  Used **only** in lesson 7, to check Lucas's own split and filtering for sanity.

**Known limitation to state in the README:** Amazon buyers of physical media are not
typical streaming listeners. The dataset records purchases and ratings, not listening.

## Components

### 1. Project setup (Claude)
- `.venv` plus `requirements.txt`. Dependencies are added when a lesson first needs
  them. Initial set: `duckdb pandas pyarrow matplotlib seaborn jupyterlab pytest`.
- `src/groovn/__init__.py` and an empty `tests/`, so graduated code has a home.

### 2. `scripts/download_data.py` (Claude)
- Streams both raw files into `data/raw/` with the standard library (`urllib`),
  skipping files already present at the right size. Rerunning it is safe.
- Converts with DuckDB (`memory_limit='4GB'`) into three column-based Parquet files
  in `data/processed/`:

| File | Columns | Why separate |
|---|---|---|
| `ratings.parquet` | `user_id, item_id, rating, ts, verified_purchase, helpful_vote` | The only table the recommender needs. Small enough for pandas. |
| `reviews.parquet` | `user_id, item_id, ts, title, text` | Review text is most of the bytes. Load it only for the text lessons. |
| `albums.parquet` | `item_id, title, store, categories, details, average_rating, rating_number, image_url` | Metadata for EDA and, later, the UI. |

- `item_id` is Amazon's `parent_asin`, which groups the editions of a product.
- **No cleaning, filtering or deduplication in the script.** Those are analysis
  decisions and belong to Lucas's lessons.
- The script ends with sanity checks: every table is non-empty, `user_id` and
  `item_id` are never null, and `rating` is between 1 and 5. It stops with an error
  if any check fails.

### 3. Lesson notebooks (Claude scaffolds, Lucas solves)

Each lesson is scaffolded **only after the previous one is done**, so it can build on
what Lucas actually found. Format is defined in `CLAUDE.md`.

| # | Notebook | Lucas builds | Key concepts |
|---|---|---|---|
| 1 | `01_eda` | Distributions of ratings per user and per album, the long tail, sparsity, rating distribution, activity over time, duplicate ratings | Popularity bias, sparsity, why the average rating misleads |
| 2 | `02_framing` | Choosing the task and the filtering (k-core), turning ratings into "liked" signals | Rating prediction vs top-K ranking, explicit vs implicit, what counts as a positive |
| 3 | `03_evaluation` | Temporal split, Recall@K, NDCG@K, catalogue coverage → `src/groovn/{split,metrics}.py` plus pytest | Leakage, why random splits cheat, ranking metrics |
| 4 | `04_baselines` | Popularity, item-kNN (cosine similarity on the sparse matrix) | Baselines are hard to beat, similarity measures |
| 5 | `05_matrix_factorization` | ALS by hand in numpy on a small sample, then `implicit` on the full data | Latent factors, regularisation, confidence weighting |
| 6 | `06_two_tower` | A PyTorch two-tower model with sampled negatives, trained on MPS | Embeddings, negative sampling, softmax vs BPR loss |
| 7 | `07_validation` | Tuning, results by segment (cold users, rarely rated albums), MLflow tracking, final results table, sanity check against the McAuley benchmark | Overfitting to the validation set, fairness across segments, reporting results honestly |

### 4. Review loop
After each lesson: Lucas says it's done → Claude runs the notebook top to bottom →
reviews it (correctness first: leakage, metric bugs, off-by-one errors in ranking) →
Lucas answers the Reflect questions → work-unit commit. Code that graduates into
`src/groovn/` gets pytest tests written by Lucas and a `/code-review` pass.

## Error handling
- Download: the script stops with a clear message on a network error or a size
  mismatch. It never leaves a partial file that looks complete (it downloads to
  `.part`, then renames).
- Conversion: the sanity checks above. Anything odd in the *content* is an EDA
  finding, not a script error.

## Testing
- Script: one pytest that runs the conversion on a 20-line fixture JSONL and checks the
  output schemas and the sanity checks.
- Lessons: `assert` cells. Graduated code: Lucas's pytest suites.

## Git
- Local folder linked to `origin` = `lucasavila23/groovn`. The Tkinter version is kept
  at tag `v0-tkinter` and removed from the working tree. `coursework/` and `data/` are
  gitignored.
- Nothing is pushed without Lucas's go-ahead.

## Resolved questions
- Package manager: plain `venv` + `pip` (`uv` is not installed; switching later is trivial).
- Lessons live only as notebooks; the primers are markdown cells, not separate docs.
