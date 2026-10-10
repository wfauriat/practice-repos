"""Tests for src/loaders.py — pinning the contract that notebooks rely on."""

from src.loaders import by_day_summary, load_tips


def test_load_tips_columns_lowercased():
    df = load_tips()
    assert all(c.islower() for c in df.columns)
    assert "tip_pct" in df.columns


def test_load_tips_tip_pct_in_range():
    df = load_tips()
    # All tips should be a positive fraction of the total bill, well below 100%.
    assert (df["tip_pct"] > 0).all()
    assert (df["tip_pct"] < 1).all()


def test_by_day_summary_sorted_descending():
    df = load_tips()
    summary = by_day_summary(df)
    pct = summary["mean_tip_pct"].tolist()
    assert pct == sorted(pct, reverse=True)


def test_by_day_summary_columns():
    df = load_tips()
    summary = by_day_summary(df)
    assert set(summary.columns) >= {"day", "n", "mean_tip_pct", "mean_size"}
