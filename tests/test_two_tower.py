import numpy as np
import scipy.sparse as sp

from groovn.two_tower import model_scores, train_two_tower


def _toy_matrix():
    rng = np.random.default_rng(0)
    mat = (rng.random((30, 15)) < 0.2).astype(float)
    return sp.csr_matrix(mat)


def test_train_two_tower_loss_decreases():
    model, losses = train_two_tower(
        _toy_matrix(), n_factors=8, epochs=5, batch_size=64, n_negatives=2,
        random_state=42, device=None,
    )
    assert losses[-1] < losses[0]


def test_model_scores_shape_matches_catalog():
    train = _toy_matrix()
    model, _ = train_two_tower(train, n_factors=8, epochs=1, batch_size=64, random_state=42)
    scores_fn = model_scores(model, device=next(model.parameters()).device)
    batch = scores_fn(np.array([0, 1, 2]))
    assert batch.shape == (3, 15)
