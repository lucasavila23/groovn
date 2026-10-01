import numpy as np
import scipy.sparse as sp

from groovn.mf import ALSRecommender, als_numpy


def _toy_confidence():
    # two user "types": {0,1} like items {0,1}; {2,3} like items {2,3}.
    rng = np.random.default_rng(0)
    mat = np.zeros((20, 10))
    for u in range(20):
        liked = range(0, 5) if u % 2 == 0 else range(5, 10)
        for i in liked:
            if rng.random() < 0.7:
                mat[u, i] = 1 + rng.integers(0, 3)
    return sp.csr_matrix(mat)


def test_als_numpy_is_deterministic_given_random_state():
    conf = _toy_confidence()
    u1, v1 = als_numpy(conf, n_factors=4, iterations=3, random_state=42)
    u2, v2 = als_numpy(conf, n_factors=4, iterations=3, random_state=42)
    np.testing.assert_array_equal(u1, u2)
    np.testing.assert_array_equal(v1, v2)


def test_als_numpy_recovers_the_two_item_clusters():
    conf = _toy_confidence()
    user_factors, item_factors = als_numpy(conf, n_factors=4, iterations=15, regularization=0.05, random_state=0)
    scores = user_factors @ item_factors.T
    # users of type "even" should score the 0-4 item block higher than the 5-9 block.
    even_users_scores = scores[0::2]
    assert even_users_scores[:, :5].mean() > even_users_scores[:, 5:].mean()


def test_als_recommender_wraps_implicit_and_produces_scores_callable():
    conf = _toy_confidence()
    model = ALSRecommender(factors=4, iterations=2, random_state=42).fit(conf)
    scores_fn = model.scores()
    batch = scores_fn(np.array([0, 1]))
    assert batch.shape == (2, 10)
