from pathlib import Path

import pandas as pd


def load_and_merge_logs(folder_path: Path) -> pd.DataFrame:
    """Read all CSV log files from a folder and combine them into one DataFrame."""
    csv_files = sorted(folder_path.glob("*.csv"))
    if not csv_files:
        raise FileNotFoundError(f"No CSV files found in '{folder_path}'.")

    dataframes = [pd.read_csv(file) for file in csv_files]
    return pd.concat(dataframes, ignore_index=True)


def clean_logs(df: pd.DataFrame) -> pd.DataFrame:
    """Standardize text fields, remove duplicate jobs, and handle missing values."""
    # Clean whitespace and standardize client names
    df["client_name"] = (
        df["client_name"].fillna("Unknown Client").str.strip().str.title()
    )
    df["doc_type"] = df["doc_type"].fillna("General").str.strip().str.title()

    # Remove duplicate job IDs across merged shift logs
    df = df.drop_duplicates(subset=["job_id"], keep="first").copy()

    # Flag jobs missing a valid line count before filling with 0
    df["is_missing_lines"] = df["line_count"].isna() | (df["line_count"] <= 0)

    # Fill missing numeric values safely
    df["line_count"] = df["line_count"].fillna(0).astype(int)
    df["rate_per_line"] = df["rate_per_line"].fillna(0.0)
    df["error_count"] = df["error_count"].fillna(0).astype(int)

    # Calculate earnings and QA accuracy per job
    df["total_charge"] = (df["line_count"] * df["rate_per_line"]).round(2)
    df["accuracy_pct"] = df.apply(
        lambda row: (
            round(
                ((row["line_count"] - row["error_count"]) / row["line_count"]) * 100, 2
            )
            if row["line_count"] > 0
            else None
        ),
        axis=1,
    )
    return df


def build_client_summary(df: pd.DataFrame) -> pd.DataFrame:
    """Group cleaned job records by client to generate totals and weighted accuracy."""
    summary = df.groupby("client_name", as_index=False).agg(
        total_jobs=("job_id", "count"),
        missing_line_jobs=("is_missing_lines", "sum"),
        total_lines=("line_count", "sum"),
        total_errors=("error_count", "sum"),
        total_billed=("total_charge", "sum"),
    )

    # Compute true line-weighted accuracy per client
    summary["weighted_accuracy_pct"] = summary.apply(
        lambda row: (
            round(
                ((row["total_lines"] - row["total_errors"]) / row["total_lines"]) * 100,
                2,
            )
            if row["total_lines"] > 0
            else 0.0
        ),
        axis=1,
    )
    summary["total_billed"] = summary["total_billed"].round(2)

    # Reorder columns cleanly
    return summary[
        [
            "client_name",
            "total_jobs",
            "missing_line_jobs",
            "total_lines",
            "total_errors",
            "weighted_accuracy_pct",
            "total_billed",
        ]
    ]


def main() -> None:
    logs_folder = Path("sample_logs")
    cleaned_output = Path("merged_cleaned_jobs.csv")
    summary_output = Path("client_billing_summary.csv")

    raw_df = load_and_merge_logs(logs_folder)
    cleaned_df = clean_logs(raw_df)
    summary_df = build_client_summary(cleaned_df)

    cleaned_df.to_csv(cleaned_output, index=False)
    summary_df.to_csv(summary_output, index=False)

    print(f"Processed {len(cleaned_df)} unique jobs.")
    print(f"Saved cleaned log to '{cleaned_output}'.")
    print(f"Saved client summary to '{summary_output}'.\n")
    print(summary_df.to_string(index=False))


if __name__ == "__main__":
    main()
