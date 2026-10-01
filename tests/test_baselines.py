import numpy as np
import scipy.sparse as sp

from groovn.baselines import ItemKNNRecommender, PopularityRecommender


def test_popularity_ranks_by_total_interactions():
    train = sp.csr_matrix(np.array([[1, 0, 1], [1, 1, 0]], dtype=float))
    model = PopularityRecommender().fit(train)
    assert list(model.scores()) == [2.0, 1.0, 1.0]


def test_item_knn_scores_higher_for_items_similar_to_seen_items():
    # items 0 and 1 are always co-interacted; item 2 is independent.
    train = sp.csr_matrix(np.array([
        [1, 1, 0],
        [1, 1, 0],
        [0, 0, 1],
        [1, 0, 0],
    ], dtype=float))
    model = ItemKNNRecommender(n_neighbors=2).fit(train)
    scores = model.scores().toarray()
    # user 3 (row index 3) has only seen item 0 -> item 1 should score higher than item 2.
    assert scores[3, 1] > scores[3, 2]
