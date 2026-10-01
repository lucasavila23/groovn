"""Top-K ranking metrics. Rating prediction (RMSE/MAE) scores how close a number is;
these score whether the right items landed near the top of a list, which is what a
recommender actually has to do, so they're what the eval harness optimizes against.
"""
import math

import numpy as np


def recall_at_k(ranked_items: list, relevant: set, k: int) -> float:
    """Fraction of the user's relevant items that made it into the top k. Undefined (nan) if
    the user has no relevant items — don't let an empty ground truth masquerade as a miss."""
    if not relevant:
        return math.nan
    hits = len(set(ranked_items[:k]) & relevant)
    return hits / len(relevant)


def ndcg_at_k(ranked_items: list, relevant: set, k: int) -> float:
    """Normalized Discounted Cumulative Gain: like recall, but a hit at rank 1 counts more than
    a hit at rank k, and dividing by the ideal DCG makes scores comparable across users with
    different numbers of relevant items."""
    if not relevant:
        return math.nan
    dcg = sum(1.0 / math.log2(rank + 2) for rank, item in enumerate(ranked_items[:k]) if item in relevant)
    ideal_hits = min(len(relevant), k)
    idcg = sum(1.0 / math.log2(rank + 2) for rank in range(ideal_hits))
    return dcg / idcg if idcg > 0 else math.nan


def coverage_at_k(all_ranked_items: list[list], catalog_size: int, k: int) -> float:
    """Share of the catalog that ever appears in anyone's top-k. A model that always recommends
    the same 20 popular albums gets great recall but near-zero coverage — this catches that."""
    recommended = set()
    for ranked_items in all_ranked_items:
        recommended.update(ranked_items[:k])
    return len(recommended) / catalog_size


def evaluate_rankings(
    rankings: dict, ground_truth: dict, k: int, catalog_size: int,
) -> dict[str, float]:
    """Mean recall@k / ndcg@k over users with ground truth, plus coverage@k over all rankings."""
    recalls, ndcgs = [], []
    for user, relevant in ground_truth.items():
        ranked = rankings.get(user, [])
        r = recall_at_k(ranked, relevant, k)
        n = ndcg_at_k(ranked, relevant, k)
        if not math.isnan(r):
            recalls.append(r)
            ndcgs.append(n)
    return {
        f"recall@{k}": float(np.mean(recalls)) if recalls else math.nan,
        f"ndcg@{k}": float(np.mean(ndcgs)) if ndcgs else math.nan,
        f"coverage@{k}": coverage_at_k(list(rankings.values()), catalog_size, k),
        "n_users_evaluated": len(recalls),
    }
