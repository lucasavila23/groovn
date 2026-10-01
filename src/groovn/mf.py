"""Matrix factorization for implicit feedback (Hu, Koren & Volinsky, 2008): learn a low-rank
user-factor and item-factor matrix whose dot product approximates confidence, instead of
hand-building a similarity graph like item-kNN.
"""
import numpy as np
import scipy.sparse as sp


def als_numpy(
    confidence: sp.csr_matrix, n_factors: int = 10, regularization: float = 0.1,
    iterations: int = 10, random_state: int = 42,
) -> tuple[np.ndarray, np.ndarray]:
    """Textbook alternating least squares, written out in full so the update rule is visible:
    fix item factors, solve the user factors in closed form (and vice versa), repeat.

    Deliberately O(n_users * n_items * n_factors) per iteration via dense sub-arrays — only
    meant to run on a small sample to show the math. The `implicit` library (ALSRecommender
    below) implements the same update with sparse linear algebra for the real dataset.
    """
    rng = np.random.default_rng(random_state)
    n_users, n_items = confidence.shape
    conf = confidence.toarray() if sp.issparse(confidence) else np.asarray(confidence)
    preference = (conf > 0).astype(np.float64)

    user_factors = rng.normal(scale=0.1, size=(n_users, n_factors))
    item_factors = rng.normal(scale=0.1, size=(n_items, n_factors))
    reg_eye = regularization * np.eye(n_factors)

    for _ in range(iterations):
        for u in range(n_users):
            c_u = conf[u]
            a = item_factors.T @ (item_factors * c_u[:, None]) + reg_eye
            b = item_factors.T @ (c_u * preference[u])
            user_factors[u] = np.linalg.solve(a, b)
        for i in range(n_items):
            c_i = conf[:, i]
            a = user_factors.T @ (user_factors * c_i[:, None]) + reg_eye
            b = user_factors.T @ (c_i * preference[:, i])
            item_factors[i] = np.linalg.solve(a, b)

    return user_factors, item_factors


class ALSRecommender:
    """Wraps the `implicit` library's Cython ALS so it runs on the full filtered catalog."""

    def __init__(self, factors: int = 64, regularization: float = 0.05, iterations: int = 15, random_state: int = 42):
        self.factors = factors
        self.regularization = regularization
        self.iterations = iterations
        self.random_state = random_state

    def fit(self, confidence: sp.csr_matrix) -> "ALSRecommender":
        from implicit.als import AlternatingLeastSquares

        model = AlternatingLeastSquares(
            factors=self.factors, regularization=self.regularization,
            iterations=self.iterations, random_state=self.random_state,
        )
        model.fit(confidence)
        self.model_ = model
        return self

    def scores(self):
        user_factors = self.model_.user_factors.astype(np.float32)
        item_factors = self.model_.item_factors.astype(np.float32)
        return lambda batch_rows: user_factors[batch_rows] @ item_factors.T
