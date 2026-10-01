import pandas as pd

from groovn.data import build_interaction_matrix, filter_min_interactions


def test_filter_min_interactions_drops_sparse_users_and_items_iteratively():
    # user "c" only has 1 rating; removing it then drops item "z" below the item floor too.
    df = pd.DataFrame({
        "user_id": ["a", "a", "b", "b", "c"],
        "item_id": ["x", "y", "x", "y", "z"],
    })
    filtered = filter_min_interactions(df, min_user=2, min_item=2)
    assert set(filtered["user_id"]) == {"a", "b"}
    assert set(filtered["item_id"]) == {"x", "y"}


def test_build_interaction_matrix_shapes_and_values():
    df = pd.DataFrame({"user_id": ["a", "a", "b"], "item_id": ["x", "y", "x"], "rating": [5.0, 3.0, 1.0]})
    matrix, user_index, item_index = build_interaction_matrix(df, value_col="rating")
    assert matrix.shape == (2, 2)
    a_row = user_index.get_loc("a")
    x_col = item_index.get_loc("x")
    assert matrix[a_row, x_col] == 5.0


def test_build_interaction_matrix_binary_default():
    df = pd.DataFrame({"user_id": ["a", "b"], "item_id": ["x", "x"]})  # b never touches item y
    df = pd.concat([df, pd.DataFrame({"user_id": ["a"], "item_id": ["y"]})], ignore_index=True)
    matrix, *_ = build_interaction_matrix(df)
    assert set(matrix.toarray().ravel()) == {0.0, 1.0}
