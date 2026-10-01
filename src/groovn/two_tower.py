"""Two-tower neural recommender: a user embedding tower and an item embedding tower, trained
so a user's vector sits close to the vectors of items they interacted with. With no side
features (genre, text, audio) each tower is just an embedding table, so this reduces to
matrix factorization trained by gradient descent with negative sampling instead of ALS's
closed-form solve. The payoff of this architecture only shows up once a tower takes more than
an id — e.g. a text embedding of the review, or album metadata — which is a natural next step,
not implemented here (kept out: YAGNI until there's a feature to feed it).
"""
import numpy as np
import scipy.sparse as sp
import torch
from torch import nn


class TwoTowerModel(nn.Module):
    def __init__(self, n_users: int, n_items: int, n_factors: int = 64):
        super().__init__()
        self.user_tower = nn.Embedding(n_users, n_factors)
        self.item_tower = nn.Embedding(n_items, n_factors)
        nn.init.normal_(self.user_tower.weight, std=0.1)
        nn.init.normal_(self.item_tower.weight, std=0.1)

    def forward(self, user_idx: torch.Tensor, item_idx: torch.Tensor) -> torch.Tensor:
        return (self.user_tower(user_idx) * self.item_tower(item_idx)).sum(dim=-1)


def pick_device() -> torch.device:
    if torch.backends.mps.is_available():
        return torch.device("mps")
    return torch.device("cpu")


def train_two_tower(
    train_matrix: sp.csr_matrix, n_factors: int = 64, epochs: int = 10, batch_size: int = 4096,
    n_negatives: int = 4, lr: float = 0.01, random_state: int = 42, device: torch.device | None = None,
) -> tuple[TwoTowerModel, list[float]]:
    """One positive (observed interaction) paired with `n_negatives` items sampled uniformly
    at random. At this catalog's sparsity (~0.01% filled) a sampled negative is a true positive
    only by rare chance, which the literature treats as acceptable label noise rather than a
    bug worth the extra bookkeeping to prevent.
    """
    torch.manual_seed(random_state)
    rng = np.random.default_rng(random_state)
    device = device or pick_device()

    n_users, n_items = train_matrix.shape
    users, items = train_matrix.tocoo().row, train_matrix.tocoo().col
    n_pos = len(users)

    model = TwoTowerModel(n_users, n_items, n_factors).to(device)
    optimizer = torch.optim.Adam(model.parameters(), lr=lr)
    loss_fn = nn.BCEWithLogitsLoss()

    losses = []
    for _epoch in range(epochs):
        order = rng.permutation(n_pos)
        epoch_loss, n_batches = 0.0, 0
        for start in range(0, n_pos, batch_size):
            batch_idx = order[start:start + batch_size]
            pos_u, pos_i = users[batch_idx], items[batch_idx]
            neg_u = np.repeat(pos_u, n_negatives)
            neg_i = rng.integers(0, n_items, size=len(neg_u))

            batch_users = np.concatenate([pos_u, neg_u])
            batch_items = np.concatenate([pos_i, neg_i])
            labels = np.concatenate([np.ones(len(pos_u)), np.zeros(len(neg_u))])

            u = torch.as_tensor(batch_users, dtype=torch.long, device=device)
            i = torch.as_tensor(batch_items, dtype=torch.long, device=device)
            y = torch.as_tensor(labels, dtype=torch.float32, device=device)

            optimizer.zero_grad()
            logits = model(u, i)
            loss = loss_fn(logits, y)
            loss.backward()
            optimizer.step()

            epoch_loss += loss.item()
            n_batches += 1
        losses.append(epoch_loss / n_batches)

    return model, losses


def model_scores(model: TwoTowerModel, device: torch.device):
    user_factors = model.user_tower.weight.detach().to("cpu").numpy()
    item_factors = model.item_tower.weight.detach().to("cpu").numpy()
    return lambda batch_rows: user_factors[batch_rows] @ item_factors.T
