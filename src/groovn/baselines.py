"""Non-personalized and neighborhood baselines. Every later model has to beat these to
justify its extra complexity.
"""
import numpy as np
import scipy.sparse as sp
from sklearn.neighbors import NearestNeighbors


class PopularityRecommender:
    """Recommends whatever is most-interacted-with overall, same list for every user minus
    what they've already seen. The floor every personalized model must clear."""

    def fit(self, train_matrix: sp.csr_matrix) -> "PopularityRecommender":
        self.popularity_ = np.asarray(train_matrix.sum(axis=0)).ravel()
        return self

    def scores(self) -> np.ndarray:
        return self.popularity_


class ItemKNNRecommender:
    """Scores item i for user u by summing the similarity between i and everything u already
    interacted with. Similarity is cosine over item co-occurrence columns, truncated to each
    item's n_neighbors nearest items so the similarity matrix stays sparse — a dense
    (n_items x n_items) matrix at this catalog size wouldn't fit in memory.
    """

    def __init__(self, n_neighbors: int = 50):
        self.n_neighbors = n_neighbors

    def fit(self, train_matrix: sp.csr_matrix) -> "ItemKNNRecommender":
        item_vectors = train_matrix.T.tocsr()
        n_items = item_vectors.shape[0]
        k = min(self.n_neighbors + 1, n_items)  # +1: self is always the closest neighbor
        nn = NearestNeighbors(n_neighbors=k, metric="cosine", algorithm="brute")
        nn.fit(item_vectors)
        distances, indices = nn.kneighbors(item_vectors)

        rows = np.repeat(np.arange(n_items), k)
        cols = indices.ravel()
        vals = 1.0 - distances.ravel()
        keep = cols != rows
        self.similarity_ = sp.csr_matrix((vals[keep], (rows[keep], cols[keep])), shape=(n_items, n_items))
        self.train_matrix_ = train_matrix
        return self

    def scores(self) -> sp.csr_matrix:
        return (self.train_matrix_ @ self.similarity_.T).tocsr()
