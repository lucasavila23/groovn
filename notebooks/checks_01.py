"""Answer checks for 01_eda. Spoiler: this file computes the answers. Solve first, peek later."""
import math
from pathlib import Path

import duckdb
import numpy as np
import pandas as pd

DATA = Path(__file__).resolve().parents[1] / "data" / "processed"
DETAIL_KEYS = {"label": "Label", "n_discs": "Number of discs",
               "original_year": "Original Release Date", "first_available": "Date First Available"}


def _sql(sql: str, data: Path) -> duckdb.DuckDBPyRelation:
    return duckdb.sql(sql.format(r=f"'{data / 'ratings.parquet'}'", a=f"'{data / 'albums.parquet'}'"))


def _one(sql: str, data: Path):
    return _sql(sql, data).fetchone()[0]


def _ok(name: str, passed) -> None:
    __tracebackhide__ = True  # IPython: keep the answer-computing lines out of the traceback
    assert bool(passed), f"{name} looks off. Re-read the instructions and check your computation."
    print(f"✓ {name}")


def _close(a, b, tol: float = 1e-6) -> bool:
    return math.isclose(float(a), float(b), rel_tol=tol, abs_tol=tol)


def _rows(data: Path) -> int:
    return _one("SELECT count(*) FROM {r}", data)


# --- 1. Data quality ---------------------------------------------------------

def ex1_loaded(ratings, albums, data: Path = DATA) -> None:
    __tracebackhide__ = True
    r_cols = {"user_id", "item_id", "rating", "ts", "verified_purchase", "helpful_vote", "text_len"}
    a_cols = {"item_id", "title", "store", "categories", "details", "average_rating", "rating_number", "image_url"}
    _ok("ratings", r_cols <= set(ratings.columns) and len(ratings) == _rows(data))
    _ok("albums", a_cols <= set(albums.columns) and len(albums) == _one("SELECT count(*) FROM {a}", data))


def ex3_missing(missing, data: Path = DATA) -> None:
    __tracebackhide__ = True
    cols = ["item_id", "title", "store", "categories", "details", "average_rating", "rating_number", "image_url"]
    want = {col: _one(f"SELECT avg(({col} IS NULL)::DOUBLE) FROM {{a}}", data) for col in cols}
    _ok("missing", set(cols) <= set(missing.index) and all(_close(missing[k], v) for k, v in want.items()))


def ex4_duplicates(dup_rows, data: Path = DATA) -> None:
    __tracebackhide__ = True
    want = _rows(data) - _one("SELECT count(*) FROM (SELECT DISTINCT user_id, item_id FROM {r})", data)
    _ok("dup_rows", dup_rows == want)


def ex5_details_missing(details_missing, data: Path = DATA) -> None:
    __tracebackhide__ = True
    want = {k: _one(f"SELECT avg((details::JSON->>'{key}' IS NULL)::DOUBLE) FROM {{a}}", data)
            for k, key in DETAIL_KEYS.items()}
    _ok("details_missing", set(want) <= set(details_missing.index)
        and all(_close(details_missing[k], v) for k, v in want.items()))


def ex6_clean_artist(clean_artist) -> None:
    __tracebackhide__ = True
    cases = {
        "SWV   Format: Audio CD": "SWV",
        "Shrimp City Slim  (Artist)    Format: Audio CD": "Shrimp City Slim",
        "Nikki Hill   Format: Audio CD": "Nikki Hill",
        "Andres Calamaro   Format: Audio CD": "Andres Calamaro",
    }
    _ok("clean_artist", all(clean_artist(raw) == want for raw, want in cases.items()))


# --- 2. One variable at a time -----------------------------------------------

def ex7_rating_dist(rating_dist, data: Path = DATA) -> None:
    __tracebackhide__ = True
    rows = _sql("SELECT rating, count(*) / sum(count(*)) OVER () FROM {r} GROUP BY rating", data).fetchall()
    got = {int(k): float(v) for k, v in rating_dist.items() if v}
    _ok("rating_dist", got.keys() == {int(k) for k, _ in rows} and all(_close(got[int(k)], v) for k, v in rows))


def ex8_share_helpful(share_helpful, data: Path = DATA) -> None:
    __tracebackhide__ = True
    _ok("share_helpful", _close(share_helpful, _one("SELECT avg((helpful_vote > 0)::DOUBLE) FROM {r}", data)))


def _count_hist(col: str, data: Path) -> dict:
    return dict(_sql(f"SELECT n, count(*) FROM (SELECT count(*) n FROM {{r}} GROUP BY {col}) GROUP BY n",
                     data).fetchall())


def ex9_counts(user_counts, item_counts, data: Path = DATA) -> None:
    __tracebackhide__ = True
    for name, got, col in [("user_counts", user_counts, "user_id"), ("item_counts", item_counts, "item_id")]:
        _ok(name, got.index.is_unique
            and {int(k): int(v) for k, v in got.value_counts().items()} == _count_hist(col, data))


def ex10_gini(gini, data: Path = DATA) -> None:
    __tracebackhide__ = True
    x = np.sort(_sql("SELECT count(*) FROM {r} GROUP BY item_id", data).fetchnumpy()["count_star()"]).astype(float)
    n = len(x)
    want = 2 * np.sum(np.arange(1, n + 1) * x) / (n * x.sum()) - (n + 1) / n
    _ok("gini", _close(gini, want, tol=1e-4))


# --- 3. Time -------------------------------------------------------------------

def ex11_per_year(per_year, data: Path = DATA) -> None:
    __tracebackhide__ = True
    rows = _sql("SELECT year(ts), count(*) FROM {r} GROUP BY 1", data).fetchall()
    _ok("per_year", {int(k): int(v) for k, v in per_year.items()} == dict(rows))


# --- 4. Relationships ------------------------------------------------------------

def _same_frame(got: pd.DataFrame, want: pd.DataFrame, sample: int = 2000) -> bool:
    """got matches want on want's columns, for all rows (length) and a fixed random sample of ids."""
    if not set(want.columns) <= set(got.columns) or len(got) != len(want):
        return False
    ids = want.sample(min(sample, len(want)), random_state=0).index
    if not ids.isin(got.index).all():
        return False
    g, w = got.loc[ids, want.columns].astype(float), want.loc[ids].astype(float)
    return bool(np.allclose(g.to_numpy(), w.to_numpy(), rtol=1e-6, atol=1e-6, equal_nan=True))


def ex12_album_feats(album_feats, data: Path = DATA) -> None:
    __tracebackhide__ = True
    want = _sql("""SELECT item_id, count(*) n_ratings, avg(rating) mean_rating, stddev_samp(rating) std_rating,
                   avg(verified_purchase::DOUBLE) pct_verified, avg(helpful_vote) mean_helpful,
                   avg(text_len) mean_text_len FROM {r} GROUP BY item_id""", data).df().set_index("item_id")
    _ok("album_feats", _same_frame(album_feats, want))


def ex13_user_feats(user_feats, data: Path = DATA) -> None:
    __tracebackhide__ = True
    want = _sql("""SELECT user_id, count(*) n_ratings, avg(rating) mean_rating, stddev_samp(rating) std_rating,
                   avg(verified_purchase::DOUBLE) pct_verified, avg(text_len) mean_text_len,
                   epoch(max(ts) - min(ts)) / 86400 days_active FROM {r} GROUP BY user_id""", data).df()
    _ok("user_feats", _same_frame(user_feats, want.set_index("user_id")))


def ex14_corr(album_feats_10, corr_spearman, data: Path = DATA, min_ratings: int = 10) -> None:
    __tracebackhide__ = True
    want = _sql(f"""SELECT count(*) n, avg(rating) m FROM {{r}} GROUP BY item_id
                    HAVING count(*) >= {min_ratings}""", data).df()
    _ok("album_feats_10", len(album_feats_10) == len(want))
    _ok("corr_spearman", _close(corr_spearman.loc["n_ratings", "mean_rating"], want.n.corr(want.m, method="spearman")))


# --- 5. PCA ----------------------------------------------------------------------

def ex16_pca(X_std, pca) -> None:
    __tracebackhide__ = True
    x = np.asarray(X_std, dtype=float)
    standardized = (not np.isnan(x).any() and np.allclose(x.mean(0), 0, atol=1e-6)
                    and np.allclose(x.std(0), 1, atol=1e-2))
    _ok("X_std", standardized)
    eig = np.sort(np.linalg.eigvalsh(np.cov(x.T)))[::-1]
    evr = np.asarray(pca.explained_variance_ratio_)
    _ok("pca", pca.n_features_in_ == x.shape[1] and np.allclose(evr, (eig / eig.sum())[:len(evr)], atol=1e-6))


def ex17_matrix(R, data: Path = DATA, min_user: int = 5, min_item: int = 20) -> None:
    __tracebackhide__ = True
    users, items, pairs = _sql(f"""
        WITH kept AS (SELECT DISTINCT user_id, item_id FROM {{r}}
            WHERE user_id IN (SELECT user_id FROM {{r}} GROUP BY 1 HAVING count(*) >= {min_user})
              AND item_id IN (SELECT item_id FROM {{r}} GROUP BY 1 HAVING count(*) >= {min_item}))
        SELECT count(DISTINCT user_id), count(DISTINCT item_id), count(*) FROM kept""", data).fetchone()
    R = R.tocsr()
    _ok("R", R.shape == (users, items) and R.nnz == pairs and R.max() == 1)
