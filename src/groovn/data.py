"""Loading and shaping the ratings data into the sparse user-item form every model consumes."""
from pathlib import Path

import pandas as pd
import scipy.sparse as sp

from groovn.split import temporal_split

DATA = Path(__file__).resolve().parents[2] / "data" / "processed"


def load_ratings(columns: list[str] | None = None) -> pd.DataFrame:
    columns = columns or ["user_id", "item_id", "rating", "ts"]
    df = pd.read_parquet(DATA / "ratings.parquet", columns=columns)
    if {"user_id", "item_id", "ts"} <= set(columns):
        df = df.sort_values("ts").drop_duplicates(subset=["user_id", "item_id"], keep="last")
    return df


def load_filtered_split(
    min_user: int = 5, min_item: int = 5, test_frac: float = 0.2,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.Timestamp]:
    """The one prepared train/test split every notebook from 03 onward evaluates against:
    dedup -> k-core filter -> temporal split. Centralized so "warm test user" and "candidate
    catalog" mean the same thing in every notebook.
    """
    ratings = load_ratings()
    filtered = filter_min_interactions(ratings, min_user=min_user, min_item=min_item)
    return temporal_split(filtered, test_frac=test_frac)


def load_filtered_three_way_split(
    min_user: int = 5, min_item: int = 5, val_frac: float = 0.15, test_frac: float = 0.15,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """train / validation / test, split by time: tune hyperparameters against validation,
    report final numbers on test only once, after every tuning decision is already locked in.
    Notebooks 4-6 reused one train/test split throughout model development — fine for
    comparing model families, but picking a hyperparameter (e.g. notebook 5's confidence
    scale) by checking its effect on that same test set is a mild form of test-set leakage:
    the test number stops being an honest estimate of unseen performance once it influenced a
    decision. This three-way split is what notebook 7's tuning uses instead.
    """
    ratings = load_ratings()
    filtered = filter_min_interactions(ratings, min_user=min_user, min_item=min_item)
    rest, test, _ = temporal_split(filtered, test_frac=test_frac)
    train, val, _ = temporal_split(rest, test_frac=val_frac / (1 - test_frac))
    return train, val, test


def filter_min_interactions(
    df: pd.DataFrame, min_user: int = 5, min_item: int = 5,
    user_col: str = "user_id", item_col: str = "item_id",
) -> pd.DataFrame:
    """Iterative k-core filter: drop users/items below the interaction floor, repeat until stable.

    A single pass can push a user below the floor by removing their items (and vice versa),
    so one-shot filtering under-prunes. Needed before kNN/MF: a user or item with a handful of
    ratings gives a similarity/factor estimate that's mostly noise.
    """
    df = df.copy()
    while True:
        user_counts = df[user_col].value_counts()
        item_counts = df[item_col].value_counts()
        keep_users = user_counts[user_counts >= min_user].index
        keep_items = item_counts[item_counts >= min_item].index
        before = len(df)
        df = df[df[user_col].isin(keep_users) & df[item_col].isin(keep_items)]
        if len(df) == before:
            return df


def build_interaction_matrix(
    df: pd.DataFrame, user_col: str = "user_id", item_col: str = "item_id",
    value_col: str | None = None,
) -> tuple[sp.csr_matrix, pd.Index, pd.Index]:
    """Sparse (n_users, n_items) matrix plus the index arrays mapping row/col position back to id.

    `value_col=None` fills with 1.0 (binary implicit signal: did they interact at all).
    """
    user_idx, user_index = pd.factorize(df[user_col])
    item_idx, item_index = pd.factorize(df[item_col])
    values = df[value_col].to_numpy(dtype="float32") if value_col else pd.Series(1.0, index=df.index, dtype="float32").to_numpy()
    matrix = sp.csr_matrix(
        (values, (user_idx, item_idx)),
        shape=(len(user_index), len(item_index)),
    )
    return matrix, user_index, item_index
