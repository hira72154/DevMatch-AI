
import json
from pathlib import Path

import pandas as pd


# PROJECT PATHS

PROJECT_ROOT = Path(__file__).resolve().parent.parent

RAW_DATA_DIR = PROJECT_ROOT / "data" / "raw"
PROCESSED_DATA_DIR = PROJECT_ROOT / "data" / "processed"

REPOSITORIES_FILE = RAW_DATA_DIR / "repositories.json"
LANGUAGES_FILE = RAW_DATA_DIR / "repository_languages.json"
ISSUES_FILE = RAW_DATA_DIR / "issues.json"

REPOSITORIES_OUTPUT = PROCESSED_DATA_DIR / "repositories_clean.csv"
ISSUES_OUTPUT = PROCESSED_DATA_DIR / "issues_clean.csv"
ISSUES_SUMMARY_OUTPUT = PROCESSED_DATA_DIR / "issues_summary.csv"


# LOAD JSON

def load_json(file_path):

    if not file_path.exists() or file_path.stat().st_size == 0:
        raise ValueError(f"File is empty or missing: {file_path}")

    with open(file_path, "r", encoding="utf-8") as file:
        return json.load(file)


# PROCESS REPOSITORIES

def process_repositories(repositories):

    df = pd.DataFrame(repositories)

    required_columns = [
        "id",
        "name",
        "full_name",
        "description",
        "created_at",
        "updated_at",
        "pushed_at",
        "size",
        "stargazers_count",
        "forks_count",
        "language",
        "archived"
    ]

    missing = [
        col for col in required_columns
        if col not in df.columns
    ]

    if missing:
        raise ValueError(f"Missing columns: {missing}")

    df = df[required_columns].copy()

    df["description"] = df["description"].fillna("No description")
    df["language"] = df["language"].fillna("Unknown")

    date_columns = ["created_at", "updated_at", "pushed_at"]

    for column in date_columns:
        df[column] = pd.to_datetime(
            df[column],
            errors="coerce",
            utc=True
        )

    df = df.drop_duplicates(subset="id")

    return df


# PROCESS LANGUAGES

def process_languages(language_data):

    languages_df = pd.DataFrame(language_data)

    if languages_df.empty:
        return pd.DataFrame(columns=["id", "languages"])

    languages_df = languages_df.rename(
        columns={"repository_id": "id"}
    )

    languages_df = languages_df[["id", "languages"]].copy()

    languages_df["languages"] = languages_df["languages"].apply(
        lambda value: json.dumps(
            value if isinstance(value, dict) else {},
            ensure_ascii=False
        )
    )

    return languages_df.drop_duplicates(subset="id")


# PROCESS ISSUES

def process_issues(issues):

    if not issues:
        raise ValueError("No GitHub issue records found!")

    df = pd.DataFrame(issues)

    required_columns = [
        "repository_id",
        "repository_full_name",
        "issue_id",
        "title",
        "html_url",
        "state",
        "created_at",
        "updated_at",
        "comments",
        "labels"
    ]

    missing = [
        col for col in required_columns
        if col not in df.columns
    ]

    if missing:
        raise ValueError(f"Missing issue columns: {missing}")

    df = df[required_columns].copy()

    df["title"] = df["title"].fillna("Untitled issue")
    df["comments"] = pd.to_numeric(
        df["comments"],
        errors="coerce"
    ).fillna(0).astype(int)

    # Extract label names

    def get_label_names(labels):

        if not isinstance(labels, list):
            return []

        return [
            str(label.get("name", "")).lower()
            for label in labels
            if isinstance(label, dict)
        ]

    df["label_names"] = df["labels"].apply(get_label_names)

    # Beginner-friendly classification

    beginner_keywords = [
        "good first issue",
        "help wanted",
        "beginner",
        "easy",
        "first-timers-only"
    ]

    df["is_beginner_friendly"] = df["label_names"].apply(
        lambda labels: any(
            keyword in label
            for label in labels
            for keyword in beginner_keywords
        )
    )

    df["is_good_first_issue"] = df["label_names"].apply(
        lambda labels: any(
            "good first issue" in label
            for label in labels
        )
    )

    df["is_help_wanted"] = df["label_names"].apply(
        lambda labels: any(
            "help wanted" in label
            for label in labels
        )
    )

    # Convert labels list into readable CSV text

    df["labels"] = df["label_names"].apply(
        lambda labels: ", ".join(labels)
    )

    df = df.drop(columns=["label_names"])

    return df


# CREATE REPOSITORY-WISE ISSUE SUMMARY

def create_issue_summary(issues_df):

    summary = issues_df.groupby(
        ["repository_id", "repository_full_name"]
    ).agg(
        total_open_issues=("issue_id", "count"),
        beginner_friendly_issues=("is_beginner_friendly", "sum"),
        good_first_issues=("is_good_first_issue", "sum"),
        help_wanted_issues=("is_help_wanted", "sum")
    ).reset_index()

    summary = summary.rename(
        columns={
            "repository_id": "id",
            "repository_full_name": "full_name"
        }
    )

    return summary


# MAIN TRANSFORMATION PIPELINE

def transform_repositories():

    print("\nStarting Data Transformation...\n")

    repositories = load_json(REPOSITORIES_FILE)
    language_data = load_json(LANGUAGES_FILE)
    issues = load_json(ISSUES_FILE)

    print("Repositories loaded:", len(repositories))
    print("Language records loaded:", len(language_data))
    print("Issue records loaded:", len(issues))

    # Transform repositories and languages

    repositories_df = process_repositories(repositories)
    languages_df = process_languages(language_data)

    final_repositories = repositories_df.merge(
        languages_df,
        on="id",
        how="left"
    )

    final_repositories["languages"] = (
        final_repositories["languages"].fillna("{}")
    )

    # Transform issues separately

    issues_df = process_issues(issues)

    issues_summary = create_issue_summary(issues_df)

    # Save all processed datasets

    PROCESSED_DATA_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    final_repositories.to_csv(
        REPOSITORIES_OUTPUT,
        index=False,
        encoding="utf-8"
    )

    issues_df.to_csv(
        ISSUES_OUTPUT,
        index=False,
        encoding="utf-8"
    )

    issues_summary.to_csv(
        ISSUES_SUMMARY_OUTPUT,
        index=False,
        encoding="utf-8"
    )

    print("\nTransformation Completed Successfully!")
    print("---------------------------------------")

    print("Repositories Shape:", final_repositories.shape)
    print("Repository Columns:", len(final_repositories.columns))

    print("Issues Shape:", issues_df.shape)
    print("Issue Summary Shape:", issues_summary.shape)

    print("Repository Duplicate IDs:",
          final_repositories["id"].duplicated().sum())

    print("Issue Duplicate IDs:",
          issues_df["issue_id"].duplicated().sum())

    print("\nFiles Saved:")
    print(REPOSITORIES_OUTPUT)
    print(ISSUES_OUTPUT)
    print(ISSUES_SUMMARY_OUTPUT)


if __name__ == "__main__":
    transform_repositories()
