"""Download Amazon Reviews 2023 (CDs & Vinyl) and convert it to Parquet.

Usage: .venv/bin/python scripts/download_data.py

Finished downloads are skipped on rerun; Parquet files are rebuilt.
No cleaning happens here: deduplication and filtering are analysis decisions.
"""
import urllib.request
from pathlib import Path

import duckdb

BASE = "https://huggingface.co/datasets/McAuley-Lab/Amazon-Reviews-2023/resolve/main/raw"
SOURCES = {
    "reviews.jsonl": f"{BASE}/review_categories/CDs_and_Vinyl.jsonl",
    "meta.jsonl": f"{BASE}/meta_categories/meta_CDs_and_Vinyl.jsonl",
}
ROOT = Path(__file__).resolve().parents[1]

REVIEW_COLS = """{user_id: 'VARCHAR', parent_asin: 'VARCHAR', rating: 'DOUBLE',
    timestamp: 'BIGINT', verified_purchase: 'BOOLEAN', helpful_vote: 'INTEGER',
    title: 'VARCHAR', text: 'VARCHAR'}"""
META_COLS = """{parent_asin: 'VARCHAR', title: 'VARCHAR', store: 'VARCHAR',
    categories: 'VARCHAR[]', details: 'JSON', average_rating: 'DOUBLE',
    rating_number: 'BIGINT', images: 'STRUCT(large VARCHAR)[]'}"""


def download(url: str, dest: Path) -> None:
    """Stream url to dest. A finished file is skipped; an interrupted one never looks finished."""
    if dest.exists():
        print(f"skip {dest.name} (already downloaded)")
        return
    dest.parent.mkdir(parents=True, exist_ok=True)
    part = dest.with_name(dest.name + ".part")
    # ponytail: an interrupted download restarts from zero; add HTTP Range resume if that bites
    with urllib.request.urlopen(url) as resp, open(part, "wb") as out:
        expected = int(resp.headers.get("Content-Length") or 0)
        done = 0
        while chunk := resp.read(8 << 20):
            out.write(chunk)
            done += len(chunk)
            print(f"\r{dest.name}: {done >> 20:,} MB", end="", flush=True)
    print()
    if expected and done != expected:
        part.unlink()
        raise RuntimeError(f"{dest.name}: got {done} bytes, expected {expected}")
    part.rename(dest)


def convert(raw: Path, out: Path) -> None:
    out.mkdir(parents=True, exist_ok=True)
    con = duckdb.connect()
    con.execute("SET memory_limit = '4GB'")
    reviews = f"read_json('{raw / 'reviews.jsonl'}', format='newline_delimited', columns={REVIEW_COLS})"
    meta = f"read_json('{raw / 'meta.jsonl'}', format='newline_delimited', columns={META_COLS})"
    ts = "make_timestamp(timestamp * 1000)"  # raw timestamps are epoch milliseconds
    con.execute(f"""COPY (SELECT user_id, parent_asin AS item_id, rating::TINYINT AS rating,
        {ts} AS ts, verified_purchase, helpful_vote FROM {reviews})
        TO '{out / 'ratings.parquet'}'""")
    con.execute(f"""COPY (SELECT user_id, parent_asin AS item_id, {ts} AS ts, title, text
        FROM {reviews}) TO '{out / 'reviews.parquet'}'""")
    con.execute(f"""COPY (SELECT parent_asin AS item_id, title, store, categories,
        details::VARCHAR AS details, average_rating, rating_number, images[1].large AS image_url
        FROM {meta}) TO '{out / 'albums.parquet'}'""")


def check(out: Path) -> None:
    con = duckdb.connect()

    def one(sql: str) -> int:
        return con.sql(sql).fetchone()[0]

    for name in ("ratings", "reviews", "albums"):
        if one(f"SELECT count(*) FROM '{out / name}.parquet'") == 0:
            raise ValueError(f"{name}.parquet is empty")
    ratings = out / "ratings.parquet"
    if n := one(f"SELECT count(*) FROM '{ratings}' WHERE user_id IS NULL OR item_id IS NULL"):
        raise ValueError(f"ratings.parquet: {n} rows with a null user_id or item_id")
    if n := one(f"SELECT count(*) FROM '{ratings}' WHERE rating IS NULL OR rating NOT BETWEEN 1 AND 5"):
        raise ValueError(f"ratings.parquet: {n} rows with a rating outside 1-5")
    if n := one(f"SELECT count(*) FROM '{out / 'albums.parquet'}' WHERE item_id IS NULL"):
        raise ValueError(f"albums.parquet: {n} rows with a null item_id")


def main() -> None:
    raw, out = ROOT / "data" / "raw", ROOT / "data" / "processed"
    for name, url in SOURCES.items():
        download(url, raw / name)
    convert(raw, out)
    check(out)
    for p in sorted(out.glob("*.parquet")):
        print(f"ok {p.name}: {p.stat().st_size >> 20:,} MB")


if __name__ == "__main__":
    main()
