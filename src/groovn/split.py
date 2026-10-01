"""Temporal train/test split: the only split that doesn't leak the future into training.

A random split puts some of a user's 2023 ratings in train and their 2015 ratings in test,
so the model would effectively predict the past from the future — something no deployed
recommender can do. Splitting on a single global timestamp cutoff keeps every train row
before it and every test row after it, matching how the model will actually be used.
No randomness involved, so there's no random_state here.
"""
import pandas as pd


def temporal_split(
    df: pd.DataFrame, test_frac: float = 0.2, ts_col: str = "ts",
) -> tuple[pd.DataFrame, pd.DataFrame, pd.Timestamp]:
    cutoff = df[ts_col].quantile(1 - test_frac)
    train = df[df[ts_col] <= cutoff]
    test = df[df[ts_col] > cutoff]
    return train, test, cutoff
