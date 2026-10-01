"""Turn a score source into a top-k item list per user, with items the user already saw in
train removed. Every recommender (popularity, item-kNN, ALS, two-tower) needs exactly this,
just fed a different score source, so it lives in one place instead of once per model.
"""
import numpy as np
import scipy.sparse as sp


def top_k_excluding_seen(scores, train_matrix: sp.csr_matrix, user_rows: np.ndarray, k: int, batch_size: int = 1000) -> np.ndarray:
    """scores is one of:
    - 1D ndarray (n_items,): same vector for every user (e.g. popularity counts)
    - sparse (n_train_users, n_items) matrix aligned to train_matrix rows (e.g. item-kNN scores)
    - callable(batch_row_indices) -> dense (len(batch), n_items) ndarray, computed lazily per
      batch so a full (n_users, n_items) dense matrix never has to fit in memory (e.g. ALS/
      two-tower factor dot products).

    Returns (len(user_rows), k) int array of item column indices, -1 padded if fewer than k
    candidates remain.
    """
    n_users = len(user_rows)
    out = np.full((n_users, k), -1, dtype=np.int64)

    if isinstance(scores, np.ndarray) and scores.ndim == 1:
        for i, u in enumerate(user_rows):
            row = scores.copy()
            row[train_matrix[u].indices] = -np.inf
            out[i] = _top_k_row(row, k)
        return out

    for start in range(0, n_users, batch_size):
        batch = user_rows[start:start + batch_size]
        if callable(scores):
            dense = np.array(scores(batch))  # copy: about to mutate for masking
        elif sp.issparse(scores):
            dense = scores[batch].toarray()
        else:
            dense = np.array(scores[batch])
        for i, u in enumerate(batch):
            dense[i, train_matrix[u].indices] = -np.inf
        for i in range(len(batch)):
            out[start + i] = _top_k_row(dense[i], k)
    return out


def _top_k_row(row: np.ndarray, k: int) -> np.ndarray:
    k_eff = min(k, row.shape[0])
    top = np.argpartition(-row, k_eff - 1)[:k_eff]
    top = top[np.argsort(-row[top])]
    top = top[row[top] > -np.inf]  # drop seen/absent candidates pulled in when too few remain
    if len(top) < k:
        top = np.pad(top, (0, k - len(top)), constant_values=-1)
    return top
