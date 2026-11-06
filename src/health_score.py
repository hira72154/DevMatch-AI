
import numpy as np
import pandas as pd
from pathlib import Path


def calculate_health_score(repositories_df):
    """
    Calculate repository health scores between 0 and 100.

    Factors:
    1. Recent Activity: 50%
    2. Popularity (Stars): 25%
    3. Community Engagement (Forks): 25%
    """

    df = repositories_df.copy()

    # Required columns
    required_columns = [
        "stargazers_count",
        "forks_count"
    ]

    missing_columns = [
        col for col in required_columns
        if col not in df.columns
    ]

    if missing_columns:
        raise ValueError(
            f"Missing required columns: {missing_columns}"
        )

    # Calculate days since last push if not available
    if "days_since_last_push" not in df.columns:

        if "pushed_at" not in df.columns:
            raise ValueError(
                "Both days_since_last_push and pushed_at are missing."
            )

        pushed_dates = pd.to_datetime(
            df["pushed_at"],
            errors="coerce",
            utc=True
        )

        reference_date = pd.Timestamp.now(tz="UTC")

        df["days_since_last_push"] = (
            reference_date - pushed_dates
        ).dt.total_seconds() / 86400

    # Convert numerical columns
    numerical_columns = [
        "days_since_last_push",
        "stargazers_count",
        "forks_count"
    ]

    for col in numerical_columns:
        df[col] = pd.to_numeric(
            df[col],
            errors="coerce"
        )

    # Handle invalid and missing values
    df["days_since_last_push"] = (
        df["days_since_last_push"].clip(lower=0)
    )

    df["stargazers_count"] = (
        df["stargazers_count"].clip(lower=0)
    )

    df["forks_count"] = (
        df["forks_count"].clip(lower=0)
    )

    # 1. Activity Score (50%)
    # Recent updates receive higher scores
    df["activity_score"] = (
        100 * np.exp(
            -df["days_since_last_push"] / 365
        )
    )

    # Unknown activity should not receive a perfect score
    df.loc[
        df["days_since_last_push"].isna(),
        "activity_score"
    ] = 0

    # 2. Popularity Score (25%)
    # Log scaling reduces the effect of extremely popular repositories
    log_stars = np.log1p(df["stargazers_count"])
    max_stars = log_stars.max()

    if pd.isna(max_stars) or max_stars == 0:
        df["popularity_score"] = 0
    else:
        df["popularity_score"] = (
            log_stars / max_stars
        ) * 100

    df.loc[
        df["stargazers_count"].isna(),
        "popularity_score"
    ] = 0

    # 3. Community Engagement Score (25%)
    log_forks = np.log1p(df["forks_count"])
    max_forks = log_forks.max()

    if pd.isna(max_forks) or max_forks == 0:
        df["engagement_score"] = 0
    else:
        df["engagement_score"] = (
            log_forks / max_forks
        ) * 100

    df.loc[
        df["forks_count"].isna(),
        "engagement_score"
    ] = 0

    # 4. Final Weighted Health Score
    df["health_score"] = (
        df["activity_score"] * 0.50
        + df["popularity_score"] * 0.25
        + df["engagement_score"] * 0.25
    ).round(2)

    # Keep score within 0-100
    df["health_score"] = df["health_score"].clip(
        lower=0,
        upper=100
    )

    # 5. Health Status
    def get_health_status(score):

        if score >= 75:
            return "Healthy"

        elif score >= 50:
            return "Moderate"

        else:
            return "Needs Attention"

    df["health_status"] = (
        df["health_score"].apply(get_health_status)
    )

    return df


# Main execution
if __name__ == "__main__":

    # Project directory
    PROJECT_ROOT = Path(__file__).resolve().parent.parent

    # Input file
    DATA_PATH = (
        PROJECT_ROOT
        / "data"
        / "processed"
        / "repositories_clean.csv"
    )

    # Output file
    OUTPUT_PATH = (
        PROJECT_ROOT
        / "data"
        / "processed"
        / "repositories_health_scores.csv"
    )

    # Load repository dataset
    repositories = pd.read_csv(DATA_PATH)

    # Calculate health scores
    result = calculate_health_score(repositories)

    # Save results
    result.to_csv(
        OUTPUT_PATH,
        index=False
    )

    # Display results
    display_columns = [
        col for col in [
            "full_name",
            "activity_score",
            "popularity_score",
            "engagement_score",
            "health_score",
            "health_status"
        ]
        if col in result.columns
    ]

    print("\nRepository Health Scores Generated!")
    print("=" * 60)

    print(
        result[display_columns]
        .head(10)
        .to_string(index=False)
    )

    print("\nHealth Status Distribution:")
    print(
        result["health_status"]
        .value_counts()
        .to_string()
    )

    print("\nTotal Repositories:", len(result))

    print("\nOutput saved at:")
    print(OUTPUT_PATH)
