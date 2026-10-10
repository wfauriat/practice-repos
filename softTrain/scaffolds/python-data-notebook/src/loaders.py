"""Data loading and light cleaning. Reusable across notebooks; testable on its own."""

import pandas as pd
import seaborn as sns


def load_tips() -> pd.DataFrame:
    """Load seaborn's `tips` dataset and apply some light cleaning.

    Returns a DataFrame with normalised column names and an explicit `tip_pct` derived column.
    """
    df = sns.load_dataset("tips").copy()
    df.columns = [c.lower() for c in df.columns]
    df["tip_pct"] = df["tip"] / df["total_bill"]
    return df


def by_day_summary(df: pd.DataFrame) -> pd.DataFrame:
    """Mean tip percentage and party size by day, sorted by tip_pct descending."""
    summary = (
        df.groupby("day", observed=True)
        .agg(
            n=("tip", "size"),
            mean_tip_pct=("tip_pct", "mean"),
            mean_size=("size", "mean"),
        )
        .reset_index()
        .sort_values("mean_tip_pct", ascending=False)
    )
    return summary
