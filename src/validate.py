
import pandas as pd
from pathlib import Path
from typing import Optional

from pydantic import BaseModel, ValidationError, ConfigDict


# ==========================================
# 1. PROJECT PATHS
# ==========================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent

PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"

REPOSITORIES_FILE = PROCESSED_DIR / "repositories_clean.csv"
ISSUES_FILE = PROCESSED_DIR / "issues_clean.csv"


# ==========================================
# 2. REPOSITORY VALIDATION MODEL
# ==========================================

class RepositoryModel(BaseModel):

    model_config = ConfigDict(extra="ignore")

    id: int
    name: str
    full_name: str
    description: Optional[str] = None

    created_at: str
    updated_at: str
    pushed_at: str

    size: int
    stargazers_count: int
    forks_count: int

    language: str
    archived: bool
    languages: str


# ==========================================
# 3. ISSUE VALIDATION MODEL
# ==========================================

class IssueModel(BaseModel):

    model_config = ConfigDict(extra="ignore")

    repository_id: int
    repository_full_name: str
    issue_id: int

    title: str
    html_url: str
    state: str

    created_at: str
    updated_at: str

    comments: int

    # Labels may be missing
    labels: Optional[str] = None

    is_beginner_friendly: bool
    is_good_first_issue: bool
    is_help_wanted: bool


# ==========================================
# 4. CLEAN MISSING VALUES
# ==========================================

def clean_record(record):

    data = record.to_dict()

    cleaned_data = {}

    for key, value in data.items():

        # Convert NaN into None
        if pd.isna(value):
            value = None

        # Convert NumPy values into Python values
        elif hasattr(value, "item"):
            value = value.item()

        cleaned_data[key] = value

    return cleaned_data


# ==========================================
# 5. VALIDATE DATASET
# ==========================================

def validate_dataset(df, model, dataset_name):

    valid_records = 0
    invalid_records = 0

    print(f"\nValidating {dataset_name}...")

    for index, record in df.iterrows():

        try:

            data = clean_record(record)

            model.model_validate(data)

            valid_records += 1

        except ValidationError as error:

            invalid_records += 1

            if invalid_records <= 5:

                print(f"\nInvalid record at row {index}:")
                print(error)

    print(f"\n{dataset_name} Validation Results:")
    print(f"Total Records: {len(df)}")
    print(f"Valid Records: {valid_records}")
    print(f"Invalid Records: {invalid_records}")

    return invalid_records == 0


# ==========================================
# 6. MAIN FUNCTION
# ==========================================

def main():

    print("=" * 45)
    print("DEVMatch AI - DATA VALIDATION")
    print("=" * 45)

    # Check repository file
    if not REPOSITORIES_FILE.exists():

        print("\nError: repositories_clean.csv not found!")
        return

    # Check issues file
    if not ISSUES_FILE.exists():

        print("\nError: issues_clean.csv not found!")
        return

    # Load datasets
    repositories_df = pd.read_csv(REPOSITORIES_FILE)

    issues_df = pd.read_csv(ISSUES_FILE)

    print("\nDatasets Loaded Successfully!")

    print(f"Repositories: {repositories_df.shape}")
    print(f"Issues: {issues_df.shape}")

    # ======================================
    # 7. HANDLE ISSUES WITH MISSING TITLES
    # ======================================

    missing_title_count = issues_df["title"].isna().sum()

    print(f"\nIssues with missing titles: {missing_title_count}")

    # Exclude records with missing required titles
    issues_df = issues_df.dropna(subset=["title"]).copy()

    print(f"Issues remaining after cleaning: {len(issues_df)}")

    # ======================================
    # 8. VALIDATE REPOSITORIES
    # ======================================

    repositories_valid = validate_dataset(
        repositories_df,
        RepositoryModel,
        "Repositories"
    )

    # ======================================
    # 9. VALIDATE ISSUES
    # ======================================

    issues_valid = validate_dataset(
        issues_df,
        IssueModel,
        "Issues"
    )

    # ======================================
    # 10. FINAL VALIDATION REPORT
    # ======================================

    print("\n" + "=" * 45)
    print("FINAL VALIDATION REPORT")
    print("=" * 45)

    print(
        "Repositories:",
        "PASSED" if repositories_valid else "FAILED"
    )

    print(
        "Issues:",
        "PASSED" if issues_valid else "FAILED"
    )

    print(f"\nIssues excluded due to missing title: {missing_title_count}")

    if repositories_valid and issues_valid:

        print("\nAll datasets passed Pydantic validation!")

    else:

        print("\nSome records need attention.")


# ==========================================
# 11. PROGRAM ENTRY POINT
# ==========================================

if __name__ == "__main__":
    main()
