# Data foundation + Lesson 01 (EDA) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Lucas can open `notebooks/01_eda.ipynb` and start the first lesson on real data: the Amazon CDs & Vinyl dataset downloaded, converted to Parquet and sanity-checked.

**Architecture:** One script (`scripts/download_data.py`) downloads two raw JSONL files and uses DuckDB to convert them into three Parquet tables, with no cleaning. The lesson notebook contains a concept primer and `# YOUR CODE` exercises. Each exercise is verified by a function in `notebooks/checks_01.py`, which computes the correct answer independently with DuckDB and never prints it.

**Tech Stack:** Python 3.12 (venv from `/opt/anaconda3/bin/python3`), DuckDB, pandas, pyarrow, matplotlib, seaborn, JupyterLab, pytest, nbformat (ships with JupyterLab).

**Spec:** `docs/superpowers/specs/2026-09-25-recsys-learning-track-design.md`

## Global Constraints

- Machine: Apple M3, 8 GB RAM. DuckDB runs with `SET memory_limit = '4GB'`.
- The script does **no cleaning, filtering or deduplication**. Those are Lucas's analysis decisions.
- Teaching mode: never fill a `# YOUR CODE` cell. Check functions must never reveal the correct value in their messages.
- Check functions locate data via `__file__`, never the current working directory.
- Nothing is pushed to GitHub without Lucas's go-ahead. He gave it on 2026-09-25 ("ok lets do it"); Task 4 pushes.

## Review Focus

1. **Interrupted download** (Ctrl-C or network drop halfway through 3.3 GB). Expect no file that looks finished; a rerun starts that file again. → Task 2, `test_download_failure_leaves_no_finished_file`.
2. **Bad rows in the raw data** (null rating, rating outside 1–5, null ids). Expect the script to fail loudly and name the problem. → Task 2, `test_check_rejects_bad_ratings`.
3. **Metadata rows with no images, categories or details.** Expect null columns, not a crash. → Task 2, `test_convert_handles_album_without_images_or_categories`.
4. **A check message that leaks the answer.** Expect a generic "looks off" message. → Task 3, `test_failed_check_does_not_leak_answer`.
5. **Notebook run from a different working directory** (VS Code runs from the repo root, Jupyter from `notebooks/`). Expect checks to still find the data. → Task 3, checks resolve `DATA` from `__file__`, and the tests pass explicit `data=` dirs.

---

### Task 1: Python project setup

**Files:**
- Create: `pyproject.toml`
- Create: `src/groovn/__init__.py` (empty)
- Create: `tests/fixtures/reviews.jsonl`, `tests/fixtures/meta.jsonl`. **Already staged:** the first 20 real lines of each raw file.

**Interfaces:**
- Produces: a `.venv` with `import groovn`, `import duckdb` and `pytest` working. pytest puts `scripts/` and `notebooks/` on `sys.path`, so tests can `import download_data` and `import checks_01`.

- [ ] **Step 1: Write `pyproject.toml`**

```toml
[build-system]
requires = ["setuptools>=68"]
build-backend = "setuptools.build_meta"

[project]
name = "groovn"
version = "0.1.0"
requires-python = ">=3.12"
dependencies = [
    "duckdb",
    "pandas",
    "pyarrow",
    "matplotlib",
    "seaborn",
    "jupyterlab",
    "pytest",
]

[tool.setuptools.packages.find]
where = ["src"]

[tool.pytest.ini_options]
pythonpath = ["scripts", "notebooks"]
testpaths = ["tests"]
```

- [ ] **Step 2: Create the package and venv**

```bash
mkdir -p src/groovn scripts notebooks && touch src/groovn/__init__.py
/opt/anaconda3/bin/python3 -m venv .venv
.venv/bin/pip install -q -e .
```

- [ ] **Step 3: Verify**

Run: `.venv/bin/python -c "import groovn, duckdb, pandas; print('ok')" && .venv/bin/pytest -q`
Expected: `ok`, then pytest reports `no tests ran` (exit code 5 is fine here).

- [ ] **Step 4: Commit**

```bash
git add pyproject.toml src/groovn/__init__.py tests/fixtures
git commit -m "chore: python project setup and dataset fixtures"
```

---

### Task 2: `scripts/download_data.py`

**Files:**
- Create: `scripts/download_data.py`
- Test: `tests/test_download_data.py`

**Interfaces:**
- Produces:
  - `download(url: str, dest: Path) -> None`: skips if `dest` exists; downloads to `dest.name + ".part"`, then renames; raises `RuntimeError` on a size mismatch and `OSError`/`URLError` on network failure.
  - `convert(raw: Path, out: Path) -> None`: reads `raw/reviews.jsonl` and `raw/meta.jsonl`; writes `out/{ratings,reviews,albums}.parquet`.
  - `check(out: Path) -> None`: raises `ValueError` naming the problem.
  - Parquet schemas (used by Task 3 and Lucas):
    - `ratings`: `user_id VARCHAR, item_id VARCHAR, rating TINYINT, ts TIMESTAMP, verified_purchase BOOLEAN, helpful_vote INTEGER`
    - `reviews`: `user_id, item_id, ts, title, text`
    - `albums`: `item_id, title, store, categories VARCHAR[], details VARCHAR (JSON text), average_rating DOUBLE, rating_number BIGINT, image_url VARCHAR`

- [ ] **Step 1: Write the failing tests** in `tests/test_download_data.py`

```python
from pathlib import Path

import duckdb
import pytest

from download_data import check, convert, download

FIXTURES = Path(__file__).parent / "fixtures"


def columns(path: Path) -> list[str]:
    return [row[0] for row in duckdb.sql(f"DESCRIBE SELECT * FROM '{path}'").fetchall()]


def count(path: Path) -> int:
    return duckdb.sql(f"SELECT count(*) FROM '{path}'").fetchone()[0]


def test_convert_writes_three_tables_with_expected_columns(tmp_path):
    convert(FIXTURES, tmp_path)
    assert columns(tmp_path / "ratings.parquet") == [
        "user_id", "item_id", "rating", "ts", "verified_purchase", "helpful_vote"]
    assert columns(tmp_path / "reviews.parquet") == ["user_id", "item_id", "ts", "title", "text"]
    assert columns(tmp_path / "albums.parquet") == [
        "item_id", "title", "store", "categories", "details",
        "average_rating", "rating_number", "image_url"]
    assert count(tmp_path / "ratings.parquet") == 20
    assert count(tmp_path / "albums.parquet") == 20
    check(tmp_path)  # real sample rows pass the sanity checks


def test_convert_turns_millisecond_timestamps_into_datetimes(tmp_path):
    convert(FIXTURES, tmp_path)
    year = duckdb.sql(f"SELECT min(year(ts)) FROM '{tmp_path}/ratings.parquet'").fetchone()[0]
    assert 1995 < year < 2025


def test_convert_handles_album_without_images_or_categories(tmp_path):
    raw = tmp_path / "raw"
    raw.mkdir()
    (raw / "reviews.jsonl").write_bytes((FIXTURES / "reviews.jsonl").read_bytes())
    (raw / "meta.jsonl").write_text(
        '{"parent_asin": "X1", "title": "Bare", "store": null, "categories": [], '
        '"details": {}, "average_rating": 4.0, "rating_number": 3, "images": []}\n')
    convert(raw, tmp_path)
    image_url, categories = duckdb.sql(
        f"SELECT image_url, categories FROM '{tmp_path}/albums.parquet'").fetchone()
    assert image_url is None
    assert categories == []


@pytest.mark.parametrize("row", [
    "('u', 'i', 6)",      # out of range
    "('u', 'i', NULL)",   # missing rating
    "(NULL, 'i', 5)",     # missing user
    "('u', NULL, 5)",     # missing album
])
def test_check_rejects_bad_ratings(tmp_path, row):
    convert(FIXTURES, tmp_path)
    duckdb.sql(f"COPY (SELECT * FROM (VALUES {row}) t(user_id, item_id, rating)) "
               f"TO '{tmp_path}/ratings.parquet'")
    with pytest.raises(ValueError):
        check(tmp_path)


def test_check_rejects_empty_table(tmp_path):
    convert(FIXTURES, tmp_path)
    duckdb.sql(f"COPY (SELECT 'x' AS item_id WHERE false) TO '{tmp_path}/albums.parquet'")
    with pytest.raises(ValueError, match="albums"):
        check(tmp_path)


def test_download_copies_file_and_leaves_no_part_file(tmp_path):
    src = FIXTURES / "meta.jsonl"
    dest = tmp_path / "raw" / "meta.jsonl"
    download(src.as_uri(), dest)
    assert dest.read_bytes() == src.read_bytes()
    assert not list(dest.parent.glob("*.part"))


def test_download_skips_a_finished_file(tmp_path):
    dest = tmp_path / "meta.jsonl"
    dest.write_text("already here")
    download("file:///does/not/exist", dest)
    assert dest.read_text() == "already here"


def test_download_failure_leaves_no_finished_file(tmp_path):
    dest = tmp_path / "meta.jsonl"
    with pytest.raises(OSError):
        download((tmp_path / "missing.jsonl").as_uri(), dest)
    assert not dest.exists()
```

- [ ] **Step 2: Run the tests to verify they fail**

Run: `.venv/bin/pytest tests/test_download_data.py -q`
Expected: collection error `ModuleNotFoundError: No module named 'download_data'`

- [ ] **Step 3: Write `scripts/download_data.py`**

```python
"""Download Amazon Reviews 2023 (CDs & Vinyl) and convert it to Parquet.

Usage: .venv/bin/python scripts/download_data.py

Finished downloads are skipped on rerun; Parquet files are rebuilt.
No cleaning happens here: deduplication and filtering are analysis decisions.
"""
import urllib.request
from pathlib import Path

import duckdb

BASE = "https://huggingface.co/datasets/McAuley-Lab/Amazon-Reviews-2023/resolve/main/raw"
SOURCES = {
    "reviews.jsonl": f"{BASE}/review_categories/CDs_and_Vinyl.jsonl",
    "meta.jsonl": f"{BASE}/meta_categories/meta_CDs_and_Vinyl.jsonl",
}
ROOT = Path(__file__).resolve().parents[1]

REVIEW_COLS = """{user_id: 'VARCHAR', parent_asin: 'VARCHAR', rating: 'DOUBLE',
    timestamp: 'BIGINT', verified_purchase: 'BOOLEAN', helpful_vote: 'INTEGER',
    title: 'VARCHAR', text: 'VARCHAR'}"""
META_COLS = """{parent_asin: 'VARCHAR', title: 'VARCHAR', store: 'VARCHAR',
    categories: 'VARCHAR[]', details: 'JSON', average_rating: 'DOUBLE',
    rating_number: 'BIGINT', images: 'STRUCT(large VARCHAR)[]'}"""


def download(url: str, dest: Path) -> None:
    """Stream url to dest. A finished file is skipped; an interrupted one never looks finished."""
    if dest.exists():
        print(f"skip {dest.name} (already downloaded)")
        return
    dest.parent.mkdir(parents=True, exist_ok=True)
    part = dest.with_name(dest.name + ".part")
    # ponytail: an interrupted download restarts from zero; add HTTP Range resume if that bites
    with urllib.request.urlopen(url) as resp, open(part, "wb") as out:
        expected = int(resp.headers.get("Content-Length") or 0)
        done = 0
        while chunk := resp.read(8 << 20):
            out.write(chunk)
            done += len(chunk)
            print(f"\r{dest.name}: {done >> 20:,} MB", end="", flush=True)
    print()
    if expected and done != expected:
        part.unlink()
        raise RuntimeError(f"{dest.name}: got {done} bytes, expected {expected}")
    part.rename(dest)


def convert(raw: Path, out: Path) -> None:
    out.mkdir(parents=True, exist_ok=True)
    con = duckdb.connect()
    con.execute("SET memory_limit = '4GB'")
    reviews = f"read_json('{raw / 'reviews.jsonl'}', format='newline_delimited', columns={REVIEW_COLS})"
    meta = f"read_json('{raw / 'meta.jsonl'}', format='newline_delimited', columns={META_COLS})"
    ts = "make_timestamp(timestamp * 1000)"  # raw timestamps are epoch milliseconds
    con.execute(f"""COPY (SELECT user_id, parent_asin AS item_id, rating::TINYINT AS rating,
        {ts} AS ts, verified_purchase, helpful_vote FROM {reviews})
        TO '{out / 'ratings.parquet'}'""")
    con.execute(f"""COPY (SELECT user_id, parent_asin AS item_id, {ts} AS ts, title, text
        FROM {reviews}) TO '{out / 'reviews.parquet'}'""")
    con.execute(f"""COPY (SELECT parent_asin AS item_id, title, store, categories,
        details::VARCHAR AS details, average_rating, rating_number, images[1].large AS image_url
        FROM {meta}) TO '{out / 'albums.parquet'}'""")


def check(out: Path) -> None:
    con = duckdb.connect()

    def one(sql: str) -> int:
        return con.sql(sql).fetchone()[0]

    for name in ("ratings", "reviews", "albums"):
        if one(f"SELECT count(*) FROM '{out / name}.parquet'") == 0:
            raise ValueError(f"{name}.parquet is empty")
    ratings = out / "ratings.parquet"
    if n := one(f"SELECT count(*) FROM '{ratings}' WHERE user_id IS NULL OR item_id IS NULL"):
        raise ValueError(f"ratings.parquet: {n} rows with a null user_id or item_id")
    if n := one(f"SELECT count(*) FROM '{ratings}' WHERE rating IS NULL OR rating NOT BETWEEN 1 AND 5"):
        raise ValueError(f"ratings.parquet: {n} rows with a rating outside 1-5")
    if n := one(f"SELECT count(*) FROM '{out / 'albums.parquet'}' WHERE item_id IS NULL"):
        raise ValueError(f"albums.parquet: {n} rows with a null item_id")


def main() -> None:
    raw, out = ROOT / "data" / "raw", ROOT / "data" / "processed"
    for name, url in SOURCES.items():
        download(url, raw / name)
    convert(raw, out)
    check(out)
    for p in sorted(out.glob("*.parquet")):
        print(f"ok {p.name}: {p.stat().st_size >> 20:,} MB")


if __name__ == "__main__":
    main()
```

- [ ] **Step 4: Run the tests to verify they pass**

Run: `.venv/bin/pytest tests/test_download_data.py -q`
Expected: `11 passed`

- [ ] **Step 5: Commit**

```bash
git add scripts/download_data.py tests/test_download_data.py
git commit -m "feat: download and convert Amazon CDs & Vinyl to Parquet"
```

---

### Task 3: Lesson 01 (EDA) notebook and its checks

**Files:**
- Create: `notebooks/checks_01.py`
- Create: `notebooks/01_eda.ipynb` (generated once by a throwaway nbformat script in the scratchpad; the script is not committed)
- Test: `tests/test_checks_01.py`

**Interfaces:**
- Consumes: the Parquet schemas from Task 2.
- Produces: check functions, each with an optional `data: Path = DATA` argument. Each raises `AssertionError("<name> looks off …")` on a wrong answer and prints `✓ <name>` on a correct one:
  `ex1_loaded(ratings)`, `ex2_sizes(n_users, n_items, density)`, `ex3_duplicates(dup_rows)`,
  `ex4_user_counts(user_counts)`, `ex5_top1_share(top1_share)`, `ex6_rating_dist(rating_dist)`,
  `ex7_per_year(per_year)`, `ex8_meta_coverage(meta_coverage)`, `ex9_clean_artist(clean_artist)`,
  `ex10_users_ge5(users_ge5)`.

- [ ] **Step 1: Write the failing tests** in `tests/test_checks_01.py`

A tiny dataset whose answers are worked out by hand:

```python
import math

import duckdb
import pandas as pd
import pytest

import checks_01 as c

# user, item, rating, year: u1 rated 'a' twice (1 duplicate row)
ROWS = [("u1", "a", 5, 2019), ("u1", "b", 4, 2020), ("u1", "a", 5, 2020),
        ("u2", "a", 3, 2020), ("u3", "c", 1, 2021)]


@pytest.fixture
def data(tmp_path):
    values = ", ".join(f"('{u}', '{i}', {r}, make_timestamp({y}, 6, 1, 0, 0, 0))"
                       for u, i, r, y in ROWS)
    duckdb.sql(f"COPY (SELECT * FROM (VALUES {values}) t(user_id, item_id, rating, ts)) "
               f"TO '{tmp_path}/ratings.parquet'")
    duckdb.sql(f"COPY (SELECT * FROM (VALUES ('a'), ('b'), ('z')) t(item_id)) "
               f"TO '{tmp_path}/albums.parquet'")
    return tmp_path


def ratings_df():
    return pd.DataFrame(ROWS, columns=["user_id", "item_id", "rating", "year"])


def test_correct_answers_pass(data):
    df = ratings_df()
    c.ex1_loaded(df, data=data)
    c.ex2_sizes(3, 3, 5 / 9, data=data)
    c.ex3_duplicates(1, data=data)
    c.ex4_user_counts(df.user_id.value_counts(), data=data)
    c.ex5_top1_share(3 / 5, data=data)  # k = ceil(3/100) = 1 album ('a', 3 ratings)
    c.ex6_rating_dist(pd.Series({1: .2, 3: .2, 4: .2, 5: .4}), data=data)
    c.ex7_per_year(pd.Series({2019: 1, 2020: 3, 2021: 1}), data=data)
    c.ex8_meta_coverage(2 / 3, data=data)  # rated a, b, c; metadata for a, b
    c.ex10_users_ge5(0, data=data)


@pytest.mark.parametrize("call", [
    lambda d: c.ex1_loaded(ratings_df().head(4), data=d),
    lambda d: c.ex2_sizes(3, 3, 4 / 9, data=d),
    lambda d: c.ex3_duplicates(0, data=d),
    lambda d: c.ex4_user_counts(pd.Series({"u1": 2, "u2": 1, "u3": 1}), data=d),
    lambda d: c.ex5_top1_share(0.5, data=d),
    lambda d: c.ex6_rating_dist(pd.Series({1: 1, 3: 1, 4: 1, 5: 2}), data=d),
    lambda d: c.ex7_per_year(pd.Series({2019: 2, 2020: 2, 2021: 1}), data=d),
    lambda d: c.ex8_meta_coverage(2 / 2, data=d),
    lambda d: c.ex10_users_ge5(1, data=d),
])
def test_wrong_answers_fail(data, call):
    with pytest.raises(AssertionError):
        call(data)


def test_clean_artist():
    c.ex9_clean_artist(lambda s: s.split("(")[0].split("Format:")[0].strip())
    with pytest.raises(AssertionError):
        c.ex9_clean_artist(lambda s: s.strip())


def test_failed_check_does_not_leak_answer(data):
    with pytest.raises(AssertionError) as err:
        c.ex2_sizes(3, 3, 0.1, data=data)
    assert "0.55" not in str(err.value) and "5/9" not in str(err.value)
```

- [ ] **Step 2: Run the tests to verify they fail**

Run: `.venv/bin/pytest tests/test_checks_01.py -q`
Expected: collection error `ModuleNotFoundError: No module named 'checks_01'`

- [ ] **Step 3: Write `notebooks/checks_01.py`**

```python
"""Answer checks for 01_eda. Spoiler: this file computes the answers. Solve first, peek later."""
import math
from pathlib import Path

import duckdb

DATA = Path(__file__).resolve().parents[1] / "data" / "processed"


def _one(sql: str, data: Path):
    return duckdb.sql(sql.format(r=f"'{data / 'ratings.parquet'}'",
                                 a=f"'{data / 'albums.parquet'}'")).fetchone()[0]


def _ok(name: str, passed: bool) -> None:
    assert passed, f"{name} looks off. Re-read the instructions and check your computation."
    print(f"✓ {name}")


def _close(a: float, b: float) -> bool:
    return math.isclose(a, b, rel_tol=1e-6)


def ex1_loaded(ratings, data: Path = DATA) -> None:
    need = {"user_id", "item_id", "rating"}
    _ok("ratings", need <= set(ratings.columns) and len(ratings) == _one("SELECT count(*) FROM {r}", data))


def ex2_sizes(n_users, n_items, density, data: Path = DATA) -> None:
    rows = _one("SELECT count(*) FROM {r}", data)
    _ok("n_users", n_users == _one("SELECT count(DISTINCT user_id) FROM {r}", data))
    _ok("n_items", n_items == _one("SELECT count(DISTINCT item_id) FROM {r}", data))
    _ok("density", _close(density, rows / (n_users * n_items)))


def ex3_duplicates(dup_rows, data: Path = DATA) -> None:
    want = _one("SELECT count(*) - (SELECT count(*) FROM (SELECT DISTINCT user_id, item_id FROM {r})) FROM {r}", data)
    _ok("dup_rows", dup_rows == want)


def ex4_user_counts(user_counts, data: Path = DATA) -> None:
    n_users = _one("SELECT count(DISTINCT user_id) FROM {r}", data)
    top = _one("SELECT max(n) FROM (SELECT count(*) n FROM {r} GROUP BY user_id)", data)
    _ok("user_counts", len(user_counts) == n_users and user_counts.max() == top
        and user_counts.sum() == _one("SELECT count(*) FROM {r}", data))


def ex5_top1_share(top1_share, data: Path = DATA) -> None:
    want = _one("""WITH c AS (SELECT count(*) n FROM {r} GROUP BY item_id),
                   ranked AS (SELECT n, row_number() OVER (ORDER BY n DESC) rn,
                                     ceil(count(*) OVER () / 100.0) k FROM c)
                   SELECT sum(n) FILTER (WHERE rn <= k) / sum(n) FROM ranked""", data)
    _ok("top1_share", _close(top1_share, want))


def ex6_rating_dist(rating_dist, data: Path = DATA) -> None:
    rows = duckdb.sql(f"SELECT rating, count(*) / sum(count(*)) OVER () FROM '{data / 'ratings.parquet'}' "
                      "GROUP BY rating").fetchall()
    got = {int(k): float(v) for k, v in rating_dist.items() if v}
    _ok("rating_dist", got.keys() == {int(k) for k, _ in rows}
        and all(_close(got[int(k)], v) for k, v in rows))


def ex7_per_year(per_year, data: Path = DATA) -> None:
    rows = duckdb.sql(f"SELECT year(ts), count(*) FROM '{data / 'ratings.parquet'}' GROUP BY 1").fetchall()
    _ok("per_year", {int(k): int(v) for k, v in per_year.items()} == dict(rows))


def ex8_meta_coverage(meta_coverage, data: Path = DATA) -> None:
    want = _one("SELECT count(*) FILTER (WHERE item_id IN (SELECT item_id FROM {a})) / count(*) "
                "FROM (SELECT DISTINCT item_id FROM {r})", data)
    _ok("meta_coverage", _close(meta_coverage, want))


def ex9_clean_artist(clean_artist) -> None:
    cases = {
        "SWV   Format: Audio CD": "SWV",
        "Shrimp City Slim  (Artist)    Format: Audio CD": "Shrimp City Slim",
        "Nikki Hill   Format: Audio CD": "Nikki Hill",
        "Andres Calamaro   Format: Audio CD": "Andres Calamaro",
    }
    _ok("clean_artist", all(clean_artist(raw) == want for raw, want in cases.items()))


def ex10_users_ge5(users_ge5, data: Path = DATA) -> None:
    want = _one("SELECT count(*) FROM (SELECT user_id FROM {r} GROUP BY 1 HAVING count(*) >= 5)", data)
    _ok("users_ge5", users_ge5 == want)
```

- [ ] **Step 4: Run the tests to verify they pass**

Run: `.venv/bin/pytest tests/test_checks_01.py -q`
Expected: `12 passed`

- [ ] **Step 5: Generate `notebooks/01_eda.ipynb`** with a throwaway nbformat script (`nbformat.v4.new_markdown_cell` / `new_code_cell`, in this order):

**Cell 1 (md): title + why this matters**
> # Lesson 01: Exploring the data
> A recommender is only as good as its understanding of the data. Before any model, you need three numbers in your head: how **sparse** the ratings matrix is, how **skewed** popularity is (the long tail), and how **positive** people are when they rate. Each of these later decides something concrete: which metric to use, which baseline is hard to beat, and whether to treat ratings as scores or as "liked it" signals.

**Cell 2 (md): concept primer**
> ## Primer
> **The ratings matrix.** Picture a table with one row per user and one column per album; a cell holds a rating if that user rated that album. *Density* = filled cells / all cells = `n_ratings / (n_users × n_items)`. Real recommender data is usually below 0.01% dense. Collaborative filtering exists to fill that empty space.
>
> **The long tail.** A few albums get most of the ratings; most albums get almost none. A recommender that only suggests hits looks accurate but is useless for discovery. Measure it by the share of ratings that go to the top 1% of albums.
>
> **Rating skew.** On Amazon (as on Letterboxd), people mostly rate what they chose and liked, so 5★ dominates. That's *selection bias*: a missing rating isn't a random "unknown", it's usually "never chose it".
>
> **Users' activity.** Most users rate once or twice. Collaborative filtering can't learn anything about a user with one rating, which is why datasets are often filtered to users and items with at least *k* ratings (the *k-core*). You'll make that call in lesson 02.
>
> **Memory tip (8 GB machine):** `pd.read_parquet(path, columns=[...])` loads only what you need. Leave `reviews.parquet` alone this lesson because it holds the text.
>
> References: Aggarwal, *Recommender Systems: The Textbook*, ch. 1; Hou et al. 2024, *Bridging Language and Items for Retrieval and Recommendation* (the paper introducing this dataset).

**Cell 3 (code): setup (given)**
```python
import math
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
import checks_01 as check

DATA = check.DATA
sns.set_theme(style="whitegrid")
```

Then for each exercise: a markdown cell with instructions, a code cell containing only `# YOUR CODE`, and a code cell with the check call.

| # | Instructions (markdown) | Check cell |
|---|---|---|
| 1 | Load `ratings.parquet` into `ratings` with columns `user_id, item_id, rating, ts`. Print its shape and `ratings.memory_usage(deep=True).sum() / 1e6` MB. | `check.ex1_loaded(ratings)` |
| 2 | Compute `n_users`, `n_items` and `density` (use rows as they are; duplicates come next). Before running: *predict the order of magnitude of density.* | `check.ex2_sizes(n_users, n_items, density)` |
| 3 | Some users rated the same album more than once. `dup_rows` = how many rows would disappear if you kept one row per (user, album) pair. Look at a few examples: same rating? same day? | `check.ex3_duplicates(dup_rows)` |
| 4 | `user_counts` = number of ratings per user (a Series indexed by `user_id`). Plot its distribution on log-log axes. What's the median? | `check.ex4_user_counts(user_counts)` |
| 5 | Long tail: `top1_share` = the share of all rating rows that go to the top 1% most-rated albums, with k = `math.ceil(n_items / 100)` albums. Plot ratings per album, sorted, on a log y-axis. | `check.ex5_top1_share(top1_share)` |
| 6 | `rating_dist` = the fraction of rows per star value (a Series indexed by star, summing to 1). Bar-plot it. | `check.ex6_rating_dist(rating_dist)` |
| 7 | `per_year` = the number of ratings per calendar year (a Series indexed by int year). Plot it. Where would you put a train/test cut-off, and why not in 2023? | `check.ex7_per_year(per_year)` |
| 8 | Load `albums.parquet` (columns `item_id, title, store, categories`) into `albums`. `meta_coverage` = the fraction of *distinct rated* albums that have a metadata row. Then list the 15 most common genres (`categories[1]`). | `check.ex8_meta_coverage(meta_coverage)` |
| 9 | `store` holds the artist plus noise (`"SWV   Format: Audio CD"`, `"Shrimp City Slim  (Artist)    Format: Audio CD"`). Write `clean_artist(s: str) -> str`, apply it, and show the top 15 artists by ratings. | `check.ex9_clean_artist(clean_artist)` |
| 10 | `users_ge5` = the number of users with at least 5 ratings. What share of users and of ratings survive that filter? | `check.ex10_users_ge5(users_ge5)` |

**Final cell (md): Reflect** (Lucas answers in markdown)
> ## Reflect
> 1. In one sentence each: how sparse, how long-tailed, how positive is this data? Give the numbers.
> 2. Given the rating distribution, would you rather predict the *star value* or predict *whether someone rates an album at all*? Why?
> 3. What would a "recommend the top 10 most popular albums to everyone" model get right, and what would it get wrong?

- [ ] **Step 6: Verify the notebook is valid and has the expected number of cells**

Run: `.venv/bin/python -c "import nbformat; nb = nbformat.read('notebooks/01_eda.ipynb', 4); nbformat.validate(nb); print(len(nb.cells))"`
Expected: `34` (3 opening cells + 10 × 3 exercise cells + 1 reflect cell).

- [ ] **Step 7: Commit**

```bash
git add notebooks/checks_01.py notebooks/01_eda.ipynb tests/test_checks_01.py
git commit -m "feat: lesson 01 EDA notebook and answer checks"
```

---

### Task 4: Real data run, end-to-end check, push

**Files:** none new. Produces `data/raw/*.jsonl` (about 4.2 GB) and `data/processed/*.parquet` (gitignored).

- [ ] **Step 1: Run the download (long: about 4.2 GB). Run it in the background.**

Run: `.venv/bin/python scripts/download_data.py`
Expected: progress lines for both files, then three `ok <name>.parquet: N MB` lines, and exit code 0.

- [ ] **Step 2: Verify the check functions run against the real data** by calling each check with a deliberately wrong value, so the answers stay hidden from Claude's side too:

```bash
.venv/bin/python -c "
import sys; sys.path.insert(0, 'notebooks'); import checks_01 as c
try: c.ex10_users_ge5(-1)
except AssertionError as e: print('check ran on real data:', e)"
```
Expected: `check ran on real data: users_ge5 looks off. …`

- [ ] **Step 3: Run the full suite**

Run: `.venv/bin/pytest -q`
Expected: `23 passed`

- [ ] **Step 4: Push to GitHub, including the tag**

```bash
git push origin main && git push origin v0-tkinter
```
