"""Builds the warm-user set and ground-truth lookup every model's evaluation run shares, so
"warm test user" and "what counts as a hit" mean the same thing for every model compared.
"""
import numpy as np
import pandas as pd


def warm_user_rows(test_df: pd.DataFrame, user_index: pd.Index, user_col: str = "user_id") -> np.ndarray:
    """Row indices (into the train matrix) of test users who also appear in train — the only
    users any of these models can score, since a model with no training history for a user
    has nothing to base a recommendation on."""
    warm_users = test_df[user_col][test_df[user_col].isin(user_index)].unique()
    return np.asarray(user_index.get_indexer(warm_users))


def build_ground_truth(
    test_df: pd.DataFrame, user_index: pd.Index, item_index: pd.Index,
    user_col: str = "user_id", item_col: str = "item_id",
) -> dict[int, set[int]]:
    """{user row -> set of item columns they interacted with after the cutoff}, restricted to
    items present in the train catalog (a model can't rank an item it never saw in training)."""
    df = test_df[test_df[user_col].isin(user_index) & test_df[item_col].isin(item_index)]
    user_rows = user_index.get_indexer(df[user_col])
    item_cols = item_index.get_indexer(df[item_col])
    ground_truth: dict[int, set[int]] = {}
    for u, i in zip(user_rows, item_cols):
        ground_truth.setdefault(u, set()).add(i)
    return ground_truth
