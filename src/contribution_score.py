
import numpy as np
import pandas as pd
from pathlib import Path


def normalize_counts(series):
    """
    Convert issue counts into a normalized score (0-100).
    Log scaling reduces the effect of very large counts.
    """

    values = pd.to_numeric(series, errors="coerce").fillna(0)
    values = values.clip(lower=0)

    log_values = np.log1p(values)
    max_value = log_values.max()

    if max_value == 0:
        return pd.Series(0.0, index=series.index)

    return (log_values / max_value) * 100


def calculate_contribution_score(
    repositories_df,
    issues_summary_df
):
    """
    Calculate contribution opportunity scores (0-100).

    Factors:
    Beginner-friendly issues: 40%
    Good First Issues: 30%
    Help Wanted Issues: 20%
    Repository activity: 10%
    """

    repositories = repositories_df.copy()
    issues = issues_summary_df.copy()

    # Check required columns
    required_repo_columns = [
        "full_name",
        "pushed_at"
    ]

    required_issue_columns = [
        "full_name",
        "beginner_friendly_issues",
        "good_first_issues",
        "help_wanted_issues"
    ]

    for col in required_repo_columns:
        if col not in repositories.columns:
            raise ValueError(
                f"Missing repository column: {col}"
            )

    for col in required_issue_columns:
        if col not in issues.columns:
            raise ValueError(
                f"Missing issue summary column: {col}"
            )

    # Keep only required issue columns
    issues = issues[[
        "full_name",
        "beginner_friendly_issues",
        "good_first_issues",
        "help_wanted_issues"
    ]]

    # Merge issue data with all repositories
    df = repositories.merge(
        issues,
        on="full_name",
        how="left"
    )

    # Missing issue counts are treated as zero
    issue_columns = [
        "beginner_friendly_issues",
        "good_first_issues",
        "help_wanted_issues"
    ]

    for col in issue_columns:
        df[col] = pd.to_numeric(
            df[col],
            errors="coerce"
        ).fillna(0).clip(lower=0)

    # 1. Beginner-Friendly Issues Score (40%)
    df["beginner_score"] = normalize_counts(
        df["beginner_friendly_issues"]
    )

    # 2. Good First Issues Score (30%)
    df["good_first_score"] = normalize_counts(
        df["good_first_issues"]
    )

    # 3. Help Wanted Issues Score (20%)
    df["help_wanted_score"] = normalize_counts(
        df["help_wanted_issues"]
    )

    # 4. Repository Activity Score (10%)
    pushed_dates = pd.to_datetime(
        df["pushed_at"],
        errors="coerce",
        utc=True
    )

    reference_date = pd.Timestamp.now(tz="UTC")

    df["days_since_last_push"] = (
        reference_date - pushed_dates
    ).dt.total_seconds() / 86400

    df["activity_score"] = (
        100 * np.exp(
            -df["days_since_last_push"].clip(lower=0) / 365
        )
    )

    # Unknown activity receives zero
    df.loc[
        df["days_since_last_push"].isna(),
        "activity_score"
    ] = 0

    # Final weighted score
    df["contribution_score"] = (
        df["beginner_score"] * 0.40
        + df["good_first_score"] * 0.30
        + df["help_wanted_score"] * 0.20
        + df["activity_score"] * 0.10
    ).round(2)

    df["contribution_score"] = (
        df["contribution_score"].clip(0, 100)
    )

    # Contribution opportunity classification
    def classify_opportunity(score):

        if score >= 75:
            return "High Opportunity"

        elif score >= 40:
            return "Moderate Opportunity"

        else:
            return "Low Opportunity"

    df["contribution_status"] = (
        df["contribution_score"].apply(
            classify_opportunity
        )
    )

    return df


if __name__ == "__main__":

    # Project root directory
    PROJECT_ROOT = Path(__file__).resolve().parent.parent

    # Input files
    REPOSITORIES_PATH = (
        PROJECT_ROOT
        / "data"
        / "processed"
        / "repositories_clean.csv"
    )

    ISSUES_PATH = (
        PROJECT_ROOT
        / "data"
        / "processed"
        / "issues_summary.csv"
    )

    # Output file
    OUTPUT_PATH = (
        PROJECT_ROOT
        / "data"
        / "processed"
        / "repositories_contribution_scores.csv"
    )

    # Load datasets
    repositories_df = pd.read_csv(REPOSITORIES_PATH)
    issues_summary_df = pd.read_csv(ISSUES_PATH)

    # Calculate contribution scores
    result = calculate_contribution_score(
        repositories_df,
        issues_summary_df
    )

    # Save results
    result.to_csv(
        OUTPUT_PATH,
        index=False
    )

    # Display results
    display_columns = [
        "full_name",
        "beginner_friendly_issues",
        "good_first_issues",
        "help_wanted_issues",
        "contribution_score",
        "contribution_status"
    ]

    print("\nContribution Opportunity Scores Generated!")
    print("=" * 65)

    print(
        result[display_columns]
        .sort_values(
            by="contribution_score",
            ascending=False
        )
        .head(10)
        .to_string(index=False)
    )

    print("\nContribution Opportunity Distribution:")
    print(
        result["contribution_status"]
        .value_counts()
        .to_string()
    )

    print("\nTotal Repositories:", len(result))

    print("\nOutput saved at:")
    print(OUTPUT_PATH)
