import json

import duckdb
import numpy as np
import pandas as pd
import pytest
import scipy.sparse as sp
from sklearn.decomposition import PCA

import checks_01 as c

# user, item, rating, year, verified, helpful_vote, text_len. u1 rated 'a' twice (1 duplicate row).
ROWS = [("u1", "a", 5, 2019, True, 0, 10), ("u1", "b", 4, 2020, False, 2, 20),
        ("u1", "a", 5, 2020, True, 0, 30), ("u2", "a", 3, 2020, True, 1, 0),
        ("u3", "c", 1, 2021, False, 0, 5)]
ALBUMS = [  # item_id, store, details (JSON text), image_url
    ("a", "SWV   Format: Audio CD", {"Label": "L1", "Number of discs": "1"}, "http://x/a.jpg"),
    ("b", None, {}, "http://x/b.jpg"),
    ("z", "Nikki Hill   Format: Audio CD", {"Label": None, "Original Release Date": "1999"}, None),
]
R_COLS = ["user_id", "item_id", "rating", "year", "verified_purchase", "helpful_vote", "text_len"]


@pytest.fixture
def data(tmp_path):
    values = ", ".join(
        f"('{u}', '{i}', {r}::DOUBLE, make_timestamp({y}, 6, 1, 0, 0, 0) + INTERVAL ({n}) DAY, {v}, {h}, {t})"
        for n, (u, i, r, y, v, h, t) in enumerate(ROWS))
    duckdb.sql(f"COPY (SELECT * FROM (VALUES {values}) t(user_id, item_id, rating, ts, "
               f"verified_purchase, helpful_vote, text_len)) TO '{tmp_path}/ratings.parquet'")
    albums = ", ".join(
        f"('{i}', 'T', {repr(s) if s else 'NULL'}, ['CDs & Vinyl', 'Pop'], '{json.dumps(d)}', 4.0, 3, "
        f"{repr(u) if u else 'NULL'})" for i, s, d, u in ALBUMS)
    duckdb.sql(f"COPY (SELECT * FROM (VALUES {albums}) t(item_id, title, store, categories, details, "
               f"average_rating, rating_number, image_url)) TO '{tmp_path}/albums.parquet'")
    return tmp_path


def ratings_df(data):
    return pd.read_parquet(data / "ratings.parquet")


def albums_df(data):
    return pd.read_parquet(data / "albums.parquet")


def album_feats(df):  # the obvious pandas answer, independent of the checks' SQL
    return df.groupby("item_id").agg(
        n_ratings=("rating", "size"), mean_rating=("rating", "mean"), std_rating=("rating", "std"),
        pct_verified=("verified_purchase", "mean"), mean_helpful=("helpful_vote", "mean"),
        mean_text_len=("text_len", "mean"))


def user_feats(df):
    f = df.groupby("user_id").agg(
        n_ratings=("rating", "size"), mean_rating=("rating", "mean"), std_rating=("rating", "std"),
        pct_verified=("verified_purchase", "mean"), mean_text_len=("text_len", "mean"),
        first=("ts", "min"), last=("ts", "max"))
    f["days_active"] = (f["last"] - f["first"]).dt.total_seconds() / 86400
    return f.drop(columns=["first", "last"])


def test_correct_answers_pass(data):
    df, al = ratings_df(data), albums_df(data)
    c.ex1_loaded(df, al, data=data)
    c.ex3_missing(al.isna().mean(), data=data)
    c.ex4_duplicates(1, data=data)
    c.ex5_details_missing(pd.Series({"label": 2 / 3, "n_discs": 2 / 3, "original_year": 2 / 3,
                                     "first_available": 1.0}), data=data)
    c.ex7_rating_dist(df.rating.value_counts(normalize=True), data=data)
    c.ex8_share_helpful(2 / 5, data=data)
    c.ex9_counts(df.user_id.value_counts(), df.item_id.value_counts(), data=data)
    c.ex10_gini(4 / 15, data=data)  # item counts [1, 1, 3]
    c.ex11_per_year(df.ts.dt.year.value_counts(), data=data)
    feats = album_feats(df)
    c.ex12_album_feats(feats, data=data)
    c.ex13_user_feats(user_feats(df), data=data)
    c.ex14_corr(feats, feats.corr(method="spearman"), data=data, min_ratings=1)
    c.ex17_matrix(sp.csr_matrix(np.ones((2, 1))), data=data, min_user=1, min_item=2)


@pytest.mark.parametrize("call", [
    lambda d: c.ex1_loaded(ratings_df(d).head(4), albums_df(d), data=d),
    lambda d: c.ex1_loaded(ratings_df(d).drop(columns="ts"), albums_df(d), data=d),
    lambda d: c.ex3_missing(albums_df(d).isna().sum(), data=d),
    lambda d: c.ex4_duplicates(0, data=d),
    lambda d: c.ex5_details_missing(pd.Series({"label": 1 / 3, "n_discs": 2 / 3, "original_year": 2 / 3,
                                               "first_available": 1.0}), data=d),
    lambda d: c.ex7_rating_dist(ratings_df(d).rating.value_counts(), data=d),
    lambda d: c.ex8_share_helpful(3 / 5, data=d),
    lambda d: c.ex9_counts(pd.Series({"u1": 2, "u2": 2, "u3": 1}), ratings_df(d).item_id.value_counts(), data=d),
    lambda d: c.ex10_gini(0.5, data=d),
    lambda d: c.ex11_per_year(pd.Series({2019: 2, 2020: 2, 2021: 1}), data=d),
    lambda d: c.ex12_album_feats(album_feats(ratings_df(d)).assign(mean_rating=4.0), data=d),
    lambda d: c.ex13_user_feats(user_feats(ratings_df(d)).assign(days_active=0.0), data=d),
    lambda d: c.ex14_corr(album_feats(ratings_df(d)), album_feats(ratings_df(d)).corr(), data=d, min_ratings=1),
    lambda d: c.ex17_matrix(sp.csr_matrix(np.array([[2.0], [1.0]])), data=d, min_user=1, min_item=2),
    lambda d: c.ex17_matrix(sp.csr_matrix(np.ones((3, 1))), data=d, min_user=1, min_item=2),
])
def test_wrong_answers_fail(data, call):
    with pytest.raises(AssertionError):
        call(data)


def test_clean_artist():
    c.ex6_clean_artist(lambda s: s.split("(")[0].split("Format:")[0].strip())
    with pytest.raises(AssertionError):
        c.ex6_clean_artist(lambda s: s.strip())


def test_pca_check():
    rng = np.random.default_rng(0)
    raw = rng.normal(size=(500, 4)) @ rng.normal(size=(4, 4)) + 10
    x_std = (raw - raw.mean(0)) / raw.std(0)
    c.ex16_pca(x_std, PCA().fit(x_std))
    with pytest.raises(AssertionError):
        c.ex16_pca(raw, PCA().fit(raw))  # not standardized
    with pytest.raises(AssertionError):
        c.ex16_pca(x_std, PCA().fit(raw))  # fitted on different data


def test_failed_check_does_not_leak_answer(data):
    with pytest.raises(AssertionError) as err:
        c.ex8_share_helpful(0.9, data=data)
    assert "0.4" not in str(err.value) and "2/5" not in str(err.value)
