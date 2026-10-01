import numpy as np
import scipy.sparse as sp

from groovn.ranking import top_k_excluding_seen


def _train_matrix():
    # user 0 has seen item 0; user 1 has seen nothing.
    return sp.csr_matrix(np.array([[1.0, 0.0, 0.0], [0.0, 0.0, 0.0]]))


def test_vector_scores_exclude_seen_items():
    scores = np.array([10.0, 5.0, 1.0])  # item 0 scores highest but user 0 already saw it
    out = top_k_excluding_seen(scores, _train_matrix(), user_rows=np.array([0, 1]), k=2)
    assert list(out[0]) == [1, 2]
    assert list(out[1]) == [0, 1]


def test_callable_scores_batch_lazily():
    def scores_fn(batch_rows):
        return np.tile(np.array([1.0, 2.0, 3.0]), (len(batch_rows), 1))

    out = top_k_excluding_seen(scores_fn, _train_matrix(), user_rows=np.array([0, 1]), k=1)
    assert out[0, 0] == 2  # highest score among items 1,2 (item 0 excluded for user 0)
    assert out[1, 0] == 2  # highest score overall for user 1


def test_pads_with_minus_one_when_fewer_candidates_than_k():
    scores = np.array([1.0, 2.0])
    train = sp.csr_matrix(np.array([[1.0, 1.0]]))  # user 0 has seen both items
    out = top_k_excluding_seen(scores, train, user_rows=np.array([0]), k=3)
    assert list(out[0]) == [-1, -1, -1]
