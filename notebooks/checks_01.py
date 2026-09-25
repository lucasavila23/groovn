"""Answer checks for 01_eda. Spoiler: this file computes the answers. Solve first, peek later."""
import math
from pathlib import Path

import duckdb

DATA = Path(__file__).resolve().parents[1] / "data" / "processed"


def _one(sql: str, data: Path):
    return duckdb.sql(sql.format(r=f"'{data / 'ratings.parquet'}'",
                                 a=f"'{data / 'albums.parquet'}'")).fetchone()[0]


def _ok(name: str, passed: bool) -> None:
    assert passed, f"{name} looks off. Re-read the instructions and check your computation."
    print(f"✓ {name}")


def _close(a: float, b: float) -> bool:
    return math.isclose(a, b, rel_tol=1e-6)


def ex1_loaded(ratings, data: Path = DATA) -> None:
    need = {"user_id", "item_id", "rating"}
    _ok("ratings", need <= set(ratings.columns) and len(ratings) == _one("SELECT count(*) FROM {r}", data))


def ex2_sizes(n_users, n_items, density, data: Path = DATA) -> None:
    rows = _one("SELECT count(*) FROM {r}", data)
    _ok("n_users", n_users == _one("SELECT count(DISTINCT user_id) FROM {r}", data))
    _ok("n_items", n_items == _one("SELECT count(DISTINCT item_id) FROM {r}", data))
    _ok("density", _close(density, rows / (n_users * n_items)))


def ex3_duplicates(dup_rows, data: Path = DATA) -> None:
    want = _one("SELECT count(*) - (SELECT count(*) FROM (SELECT DISTINCT user_id, item_id FROM {r})) FROM {r}", data)
    _ok("dup_rows", dup_rows == want)


def ex4_user_counts(user_counts, data: Path = DATA) -> None:
    n_users = _one("SELECT count(DISTINCT user_id) FROM {r}", data)
    top = _one("SELECT max(n) FROM (SELECT count(*) n FROM {r} GROUP BY user_id)", data)
    _ok("user_counts", len(user_counts) == n_users and user_counts.max() == top
        and user_counts.sum() == _one("SELECT count(*) FROM {r}", data))


def ex5_top1_share(top1_share, data: Path = DATA) -> None:
    want = _one("""WITH c AS (SELECT count(*) n FROM {r} GROUP BY item_id),
                   ranked AS (SELECT n, row_number() OVER (ORDER BY n DESC) rn,
                                     ceil(count(*) OVER () / 100.0) k FROM c)
                   SELECT sum(n) FILTER (WHERE rn <= k) / sum(n) FROM ranked""", data)
    _ok("top1_share", _close(top1_share, want))


def ex6_rating_dist(rating_dist, data: Path = DATA) -> None:
    rows = duckdb.sql(f"SELECT rating, count(*) / sum(count(*)) OVER () FROM '{data / 'ratings.parquet'}' "
                      "GROUP BY rating").fetchall()
    got = {int(k): float(v) for k, v in rating_dist.items() if v}
    _ok("rating_dist", got.keys() == {int(k) for k, _ in rows}
        and all(_close(got[int(k)], v) for k, v in rows))


def ex7_per_year(per_year, data: Path = DATA) -> None:
    rows = duckdb.sql(f"SELECT year(ts), count(*) FROM '{data / 'ratings.parquet'}' GROUP BY 1").fetchall()
    _ok("per_year", {int(k): int(v) for k, v in per_year.items()} == dict(rows))


def ex8_meta_coverage(meta_coverage, data: Path = DATA) -> None:
    want = _one("SELECT count(*) FILTER (WHERE item_id IN (SELECT item_id FROM {a})) / count(*) "
                "FROM (SELECT DISTINCT item_id FROM {r})", data)
    _ok("meta_coverage", _close(meta_coverage, want))


def ex9_clean_artist(clean_artist) -> None:
    cases = {
        "SWV   Format: Audio CD": "SWV",
        "Shrimp City Slim  (Artist)    Format: Audio CD": "Shrimp City Slim",
        "Nikki Hill   Format: Audio CD": "Nikki Hill",
        "Andres Calamaro   Format: Audio CD": "Andres Calamaro",
    }
    _ok("clean_artist", all(clean_artist(raw) == want for raw, want in cases.items()))


def ex10_users_ge5(users_ge5, data: Path = DATA) -> None:
    want = _one("SELECT count(*) FROM (SELECT user_id FROM {r} GROUP BY 1 HAVING count(*) >= 5)", data)
    _ok("users_ge5", users_ge5 == want)
