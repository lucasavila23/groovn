from pathlib import Path

import duckdb
import pytest

from download_data import check, convert, download

FIXTURES = Path(__file__).parent / "fixtures"


def columns(path: Path) -> list[str]:
    return [row[0] for row in duckdb.sql(f"DESCRIBE SELECT * FROM '{path}'").fetchall()]


def count(path: Path) -> int:
    return duckdb.sql(f"SELECT count(*) FROM '{path}'").fetchone()[0]


def test_convert_writes_three_tables_with_expected_columns(tmp_path):
    convert(FIXTURES, tmp_path)
    assert columns(tmp_path / "ratings.parquet") == [
        "user_id", "item_id", "rating", "ts", "verified_purchase", "helpful_vote"]
    assert columns(tmp_path / "reviews.parquet") == ["user_id", "item_id", "ts", "title", "text"]
    assert columns(tmp_path / "albums.parquet") == [
        "item_id", "title", "store", "categories", "details",
        "average_rating", "rating_number", "image_url"]
    assert count(tmp_path / "ratings.parquet") == 20
    assert count(tmp_path / "albums.parquet") == 20
    check(tmp_path)  # real sample rows pass the sanity checks


def test_convert_turns_millisecond_timestamps_into_datetimes(tmp_path):
    convert(FIXTURES, tmp_path)
    year = duckdb.sql(f"SELECT min(year(ts)) FROM '{tmp_path}/ratings.parquet'").fetchone()[0]
    assert 1995 < year < 2025


def test_convert_handles_album_without_images_or_categories(tmp_path):
    raw = tmp_path / "raw"
    raw.mkdir()
    (raw / "reviews.jsonl").write_bytes((FIXTURES / "reviews.jsonl").read_bytes())
    (raw / "meta.jsonl").write_text(
        '{"parent_asin": "X1", "title": "Bare", "store": null, "categories": [], '
        '"details": {}, "average_rating": 4.0, "rating_number": 3, "images": []}\n')
    convert(raw, tmp_path)
    image_url, categories = duckdb.sql(
        f"SELECT image_url, categories FROM '{tmp_path}/albums.parquet'").fetchone()
    assert image_url is None
    assert categories == []


@pytest.mark.parametrize("row", [
    "('u', 'i', 6)",      # out of range
    "('u', 'i', NULL)",   # missing rating
    "(NULL, 'i', 5)",     # missing user
    "('u', NULL, 5)",     # missing album
])
def test_check_rejects_bad_ratings(tmp_path, row):
    convert(FIXTURES, tmp_path)
    duckdb.sql(f"COPY (SELECT * FROM (VALUES {row}) t(user_id, item_id, rating)) "
               f"TO '{tmp_path}/ratings.parquet'")
    with pytest.raises(ValueError):
        check(tmp_path)


def test_check_rejects_empty_table(tmp_path):
    convert(FIXTURES, tmp_path)
    duckdb.sql(f"COPY (SELECT 'x' AS item_id WHERE false) TO '{tmp_path}/albums.parquet'")
    with pytest.raises(ValueError, match="albums"):
        check(tmp_path)


def test_download_copies_file_and_leaves_no_part_file(tmp_path):
    src = FIXTURES / "meta.jsonl"
    dest = tmp_path / "raw" / "meta.jsonl"
    download(src.as_uri(), dest)
    assert dest.read_bytes() == src.read_bytes()
    assert not list(dest.parent.glob("*.part"))


def test_download_skips_a_finished_file(tmp_path):
    dest = tmp_path / "meta.jsonl"
    dest.write_text("already here")
    download("file:///does/not/exist", dest)
    assert dest.read_text() == "already here"


def test_download_failure_leaves_no_finished_file(tmp_path):
    dest = tmp_path / "meta.jsonl"
    with pytest.raises(OSError):
        download((tmp_path / "missing.jsonl").as_uri(), dest)
    assert not dest.exists()
