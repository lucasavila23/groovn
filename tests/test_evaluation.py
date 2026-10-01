import pandas as pd

from groovn.evaluation import build_ground_truth, warm_user_rows


def test_warm_user_rows_excludes_users_absent_from_train():
    user_index = pd.Index(["a", "b", "c"])
    test_df = pd.DataFrame({"user_id": ["a", "a", "z"]})  # "z" never appeared in train
    rows = warm_user_rows(test_df, user_index)
    assert sorted(rows) == [0]


def test_build_ground_truth_restricts_to_train_catalog_and_groups_by_user():
    user_index = pd.Index(["a", "b"])
    item_index = pd.Index(["x", "y"])
    test_df = pd.DataFrame({
        "user_id": ["a", "a", "b", "z"],
        "item_id": ["x", "y", "unseen_item", "x"],
    })
    gt = build_ground_truth(test_df, user_index, item_index)
    assert gt == {0: {0, 1}}  # user b's only test item isn't in the train catalog -> dropped
