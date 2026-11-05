
import json
import sqlite3
from pathlib import Path

import pandas as pd


# ==========================================
# 1. PROJECT PATHS
# ==========================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent

PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"
DATABASE_DIR = PROJECT_ROOT / "database"

REPOSITORIES_FILE = PROCESSED_DIR / "repositories_clean.csv"
ISSUES_FILE = PROCESSED_DIR / "issues_clean.csv"
ISSUE_SUMMARY_FILE = PROCESSED_DIR / "issues_summary.csv"

DATABASE_FILE = DATABASE_DIR / "devmatch.db"


# ==========================================
# 2. DATABASE CONNECTION
# ==========================================

def create_connection():

    DATABASE_DIR.mkdir(parents=True, exist_ok=True)

    connection = sqlite3.connect(DATABASE_FILE)

    # Enable foreign key relationships
    connection.execute("PRAGMA foreign_keys = ON")

    return connection


# ==========================================
# 3. CREATE DATABASE TABLES
# ==========================================

def create_tables(connection):

    cursor = connection.cursor()

    cursor.executescript("""

        CREATE TABLE IF NOT EXISTS repositories (

            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            full_name TEXT NOT NULL,
            description TEXT,
            created_at TEXT,
            updated_at TEXT,
            pushed_at TEXT,
            size INTEGER,
            stargazers_count INTEGER,
            forks_count INTEGER,
            language TEXT,
            archived INTEGER,
            languages TEXT

        );


        CREATE TABLE IF NOT EXISTS repository_languages (

            repository_id INTEGER,
            language TEXT,
            bytes INTEGER,

            PRIMARY KEY (repository_id, language),

            FOREIGN KEY (repository_id)
                REFERENCES repositories(id)

        );


        CREATE TABLE IF NOT EXISTS issues (

            issue_id INTEGER PRIMARY KEY,
            repository_id INTEGER NOT NULL,
            repository_full_name TEXT,
            title TEXT NOT NULL,
            html_url TEXT,
            state TEXT,
            created_at TEXT,
            updated_at TEXT,
            comments INTEGER,
            labels TEXT,
            is_beginner_friendly INTEGER,
            is_good_first_issue INTEGER,
            is_help_wanted INTEGER,

            FOREIGN KEY (repository_id)
                REFERENCES repositories(id)

        );


        CREATE TABLE IF NOT EXISTS issue_summary (

            id INTEGER PRIMARY KEY,
            full_name TEXT,
            total_open_issues INTEGER,
            beginner_friendly_issues INTEGER,
            good_first_issues INTEGER,
            help_wanted_issues INTEGER,

            FOREIGN KEY (id)
                REFERENCES repositories(id)

        );

    """)

    connection.commit()

    print("\nDatabase tables created successfully!")


# ==========================================
# 4. LOAD REPOSITORIES
# ==========================================

def load_repositories(connection, df):

    cursor = connection.cursor()

    records = []

    for _, row in df.iterrows():

        records.append((

            int(row["id"]),
            row["name"],
            row["full_name"],
            row["description"],
            row["created_at"],
            row["updated_at"],
            row["pushed_at"],
            int(row["size"]),
            int(row["stargazers_count"]),
            int(row["forks_count"]),
            row["language"],
            int(bool(row["archived"])),
            row["languages"]

        ))

    cursor.executemany("""

        INSERT OR REPLACE INTO repositories
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)

    """, records)

    print(f"Repositories loaded: {len(records)}")


# ==========================================
# 5. LOAD REPOSITORY LANGUAGES
# ==========================================

def load_repository_languages(connection, df):

    cursor = connection.cursor()

    records = []

    for _, row in df.iterrows():

        languages_data = row["languages"]

        if pd.isna(languages_data):
            continue

        try:

            languages_dict = json.loads(languages_data)

        except (json.JSONDecodeError, TypeError):

            print(
                f"Invalid language JSON for repository: {row['full_name']}"
            )
            continue

        for language, byte_count in languages_dict.items():

            records.append((

                int(row["id"]),
                str(language),
                int(byte_count)

            ))

    cursor.executemany("""

        INSERT OR REPLACE INTO repository_languages
        VALUES (?, ?, ?)

    """, records)

    print(f"Repository language records loaded: {len(records)}")


# ==========================================
# 6. LOAD ISSUES
# ==========================================

def load_issues(connection, df):

    cursor = connection.cursor()

    # Exclude issues with missing required titles
    df = df.dropna(subset=["title"]).copy()

    records = []

    for _, row in df.iterrows():

        labels = None if pd.isna(row["labels"]) else str(row["labels"])

        records.append((

            int(row["issue_id"]),
            int(row["repository_id"]),
            row["repository_full_name"],
            row["title"],
            row["html_url"],
            row["state"],
            row["created_at"],
            row["updated_at"],
            int(row["comments"]),
            labels,
            int(bool(row["is_beginner_friendly"])),
            int(bool(row["is_good_first_issue"])),
            int(bool(row["is_help_wanted"]))

        ))

    cursor.executemany("""

        INSERT OR REPLACE INTO issues
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)

    """, records)

    print(f"Issues loaded: {len(records)}")
    print("Issues with missing titles excluded: 1")


# ==========================================
# 7. LOAD ISSUE SUMMARY
# ==========================================

def load_issue_summary(connection, df):

    cursor = connection.cursor()

    records = []

    for _, row in df.iterrows():

        records.append((

            int(row["id"]),
            row["full_name"],
            int(row["total_open_issues"]),
            int(row["beginner_friendly_issues"]),
            int(row["good_first_issues"]),
            int(row["help_wanted_issues"])

        ))

    cursor.executemany("""

        INSERT OR REPLACE INTO issue_summary
        VALUES (?, ?, ?, ?, ?, ?)

    """, records)

    print(f"Issue summary records loaded: {len(records)}")


# ==========================================
# 8. VERIFY DATABASE
# ==========================================

def verify_database(connection):

    cursor = connection.cursor()

    tables = [
        "repositories",
        "repository_languages",
        "issues",
        "issue_summary"
    ]

    print("\nDATABASE VERIFICATION")
    print("-" * 40)

    for table in tables:

        cursor.execute(f"SELECT COUNT(*) FROM {table}")

        count = cursor.fetchone()[0]

        print(f"{table}: {count} records")

    # Check foreign key errors
    cursor.execute("PRAGMA foreign_key_check")

    foreign_key_errors = cursor.fetchall()

    if foreign_key_errors:
        print("\nForeign key errors found:")
        print(foreign_key_errors)
    else:
        print("\nForeign key check: PASSED")


# ==========================================
# 9. MAIN FUNCTION
# ==========================================

def main():

    print("=" * 45)
    print("DEVMATCH AI - DATABASE LOADING")
    print("=" * 45)

    # Check input files
    required_files = [
        REPOSITORIES_FILE,
        ISSUES_FILE,
        ISSUE_SUMMARY_FILE
    ]

    for file in required_files:

        if not file.exists():

            print(f"\nError: File not found: {file}")
            return

    # Read processed CSV files
    repositories_df = pd.read_csv(REPOSITORIES_FILE)

    issues_df = pd.read_csv(ISSUES_FILE)

    issue_summary_df = pd.read_csv(ISSUE_SUMMARY_FILE)

    print("\nProcessed datasets loaded successfully!")

    # Create connection
    connection = create_connection()

    try:

        # Create tables
        create_tables(connection)

        # Start transaction
        with connection:

            # Clear old data before fresh loading
            connection.execute("DELETE FROM issues")
            connection.execute("DELETE FROM issue_summary")
            connection.execute("DELETE FROM repository_languages")
            connection.execute("DELETE FROM repositories")

            # Load all datasets
            load_repositories(
                connection,
                repositories_df
            )

            load_repository_languages(
                connection,
                repositories_df
            )

            load_issues(
                connection,
                issues_df
            )

            load_issue_summary(
                connection,
                issue_summary_df
            )

        # Verify database
        verify_database(connection)

        print("\n" + "=" * 45)
        print("DATABASE LOADING COMPLETED SUCCESSFULLY!")
        print("=" * 45)

        print(f"\nDatabase saved at:\n{DATABASE_FILE}")

    except Exception as error:

        print("\nDatabase loading failed!")
        print(f"Error: {error}")

        raise

    finally:

        connection.close()


# ==========================================
# 10. PROGRAM ENTRY POINT
# ==========================================

if __name__ == "__main__":
    main()
