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
