import pandas as pd

from groovn.split import temporal_split


def test_temporal_split_keeps_everything_before_cutoff_in_train():
    df = pd.DataFrame({
        "ts": pd.to_datetime([f"2020-01-{d:02d}" for d in range(1, 11)]),
        "rating": range(10),
    })
    train, test, cutoff = temporal_split(df, test_frac=0.2)
    assert len(train) + len(test) == len(df)
    assert (train["ts"] <= cutoff).all()
    assert (test["ts"] > cutoff).all()
    assert len(test) == 2
