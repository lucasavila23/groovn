English | [Español](README.es.md)

# Groovn

Letterboxd for music: rate and review albums, and get recommendations that learn your taste.

## Status

Being rebuilt (2026) as a machine-learning project. The core is an album recommender
trained and validated on real users' album ratings (Amazon Reviews 2023, CDs & Vinyl),
compared step by step from popularity baselines to matrix factorization and a neural
two-tower model.

The earlier Tkinter + MySQL version is preserved at the [`v0-tkinter`](../../tree/v0-tkinter) tag.

## Results

Top-10 ranking quality on a held-out, time-based test split never used for tuning (see
`notebooks/07_validation.ipynb`). ALS and Item-kNN were both tuned on a separate validation
split first.

| Model      | Recall@10 | NDCG@10 | Coverage@10 |
|:-----------|----------:|--------:|------------:|
| Popularity |    0.0014 |  0.0011 |      0.0002 |
| Item-kNN   |    0.0085 |  0.0060 |      0.7514 |
| ALS        |    0.0098 |  0.0066 |      0.0607 |
| Two-Tower  |    0.0035 |  0.0024 |      0.1961 |

Tuned ALS edges out Item-kNN on overall recall/NDCG, but that hides a large gap: **ALS never
once recommends a long-tail album that a user actually went on to interact with
(Recall@10 = 0.0 on the long-tail-item segment)**, while Item-kNN keeps meaningful recall
there and covers ~75% of the catalog across all users vs. ALS's ~6%. Which model is "better"
depends on whether the product goal is matching mainstream taste or surfacing the long tail —
see the notebook for the full per-segment breakdown (cold vs. warm users, head vs. long-tail
items) and why it matters more than the overall average.

## Author

Lucas Avila Manotas · [LinkedIn](https://www.linkedin.com/in/lucas-avila23)
