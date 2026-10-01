import math

from groovn.metrics import coverage_at_k, evaluate_rankings, ndcg_at_k, recall_at_k


def test_recall_at_k_counts_hits_within_k():
    assert recall_at_k(["a", "b", "c"], {"a", "z"}, k=2) == 0.5
    assert recall_at_k(["a", "b", "c"], {"a", "b"}, k=3) == 1.0


def test_recall_at_k_empty_relevant_is_nan():
    assert math.isnan(recall_at_k(["a"], set(), k=1))


def test_ndcg_rewards_earlier_hits():
    relevant = {"a"}
    hit_first = ndcg_at_k(["a", "b"], relevant, k=2)
    hit_second = ndcg_at_k(["b", "a"], relevant, k=2)
    assert hit_first == 1.0
    assert 0 < hit_second < hit_first


def test_coverage_counts_distinct_recommended_items():
    assert coverage_at_k([["a", "b"], ["b", "c"]], catalog_size=10, k=2) == 0.3


def test_evaluate_rankings_aggregates_and_skips_no_ground_truth():
    rankings = {1: ["a", "b"], 2: ["c", "d"]}
    ground_truth = {1: {"a"}, 2: set()}
    result = evaluate_rankings(rankings, ground_truth, k=2, catalog_size=4)
    assert result["n_users_evaluated"] == 1
    assert result["recall@2"] == 1.0
