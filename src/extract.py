
import os
import json
import time
from pathlib import Path

import requests
from dotenv import load_dotenv


# --------------------------------------------------
# PROJECT PATHS
# --------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parent.parent

load_dotenv(PROJECT_ROOT / ".env")

RAW_DATA_DIR = PROJECT_ROOT / "data" / "raw"

REPOSITORIES_FILE = RAW_DATA_DIR / "repositories.json"
LANGUAGES_FILE = RAW_DATA_DIR / "repository_languages.json"
ISSUES_FILE = RAW_DATA_DIR / "issues.json"


# --------------------------------------------------
# GITHUB API
# --------------------------------------------------

API_BASE_URL = "https://api.github.com"
SEARCH_URL = f"{API_BASE_URL}/search/repositories"

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")

HEADERS = {
    "Accept": "application/vnd.github+json"
}

if GITHUB_TOKEN:
    HEADERS["Authorization"] = f"Bearer {GITHUB_TOKEN}"
else:
    print("Warning: GitHub token not found. Using unauthenticated requests.")


# --------------------------------------------------
# TARGET LANGUAGES
# --------------------------------------------------

TARGET_LANGUAGES = [
    "Python",
    "C",
    "C++",
    "Java",
    "JavaScript",
    "HTML",
    "CSS"
]

REPOSITORIES_PER_LANGUAGE = 10


# --------------------------------------------------
# STEP 1: EXTRACT REPOSITORIES
# --------------------------------------------------

def get_repositories():
    """Fetch repositories for each selected language."""

    all_repositories = {}

    for language in TARGET_LANGUAGES:

        print(f"\nSearching {language} repositories...")

        params = {
            "q": f"stars:>10 language:{language}",
            "sort": "stars",
            "order": "desc",
            "per_page": REPOSITORIES_PER_LANGUAGE,
            "page": 1
        }

        response = requests.get(
            SEARCH_URL,
            headers=HEADERS,
            params=params,
            timeout=30
        )

        response.raise_for_status()

        repositories = response.json().get("items", [])

        for repository in repositories:
            repo_id = repository["id"]
            all_repositories[repo_id] = repository

        print(
            f"{language}: {len(repositories)} repositories fetched."
        )

        time.sleep(1)

    return list(all_repositories.values())


# --------------------------------------------------
# STEP 2: EXTRACT REPOSITORY LANGUAGES
# --------------------------------------------------

def get_repository_languages(repositories):
    """Fetch actual language breakdown of every repository."""

    language_data = []

    for index, repository in enumerate(repositories, start=1):

        full_name = repository["full_name"]

        print(
            f"Fetching languages ({index}/{len(repositories)}): "
            f"{full_name}"
        )

        url = f"{API_BASE_URL}/repos/{full_name}/languages"

        try:
            response = requests.get(
                url,
                headers=HEADERS,
                timeout=30
            )

            response.raise_for_status()

            language_breakdown = response.json()

            language_data.append({
                "repository_id": repository["id"],
                "full_name": full_name,
                "languages": language_breakdown
            })

        except requests.exceptions.HTTPError as error:

            print(f"Could not fetch languages for {full_name}: {error}")

            language_data.append({
                "repository_id": repository["id"],
                "full_name": full_name,
                "languages": {},
                "error": str(error)
            })

            if response.status_code == 403:
                print("GitHub rate limit may have been reached.")
                print("Check your token and remaining API quota.")
                break

        except requests.exceptions.RequestException as error:

            print(f"Request failed for {full_name}: {error}")

            language_data.append({
                "repository_id": repository["id"],
                "full_name": full_name,
                "languages": {},
                "error": str(error)
            })

        time.sleep(0.5)

    return language_data


# --------------------------------------------------
# STEP 3: EXTRACT GITHUB ISSUES
# --------------------------------------------------

def get_repository_issues(repositories):
    """Fetch open issues and their labels from every repository."""

    all_issues = []

    for index, repository in enumerate(repositories, start=1):

        full_name = repository["full_name"]
        repository_id = repository["id"]

        print(
            f"Fetching issues ({index}/{len(repositories)}): "
            f"{full_name}"
        )

        url = f"{API_BASE_URL}/repos/{full_name}/issues"

        params = {
            "state": "open",
            "per_page": 100,
            "page": 1,
            "sort": "created",
            "direction": "desc"
        }

        try:
            response = requests.get(
                url,
                headers=HEADERS,
                params=params,
                timeout=30
            )

            response.raise_for_status()

            issues = response.json()

            for issue in issues:

                # Exclude pull requests
                if "pull_request" in issue:
                    continue

                labels = [
                    {
                        "name": label.get("name", "")
                    }
                    for label in issue.get("labels", [])
                ]

                issue_record = {
                    "repository_id": repository_id,
                    "repository_full_name": full_name,
                    "issue_id": issue.get("id"),
                    "title": issue.get("title"),
                    "html_url": issue.get("html_url"),
                    "state": issue.get("state"),
                    "created_at": issue.get("created_at"),
                    "updated_at": issue.get("updated_at"),
                    "comments": issue.get("comments", 0),
                    "labels": labels
                }

                all_issues.append(issue_record)

            print(
                f"Fetched {len(issues)} API records for {full_name}."
            )

        except requests.exceptions.HTTPError as error:

            print(f"HTTP error for {full_name}: {error}")

            if response.status_code == 403:
                print("GitHub API rate limit reached. Stopping issue extraction.")
                break

        except requests.exceptions.RequestException as error:

            print(f"Request failed for {full_name}: {error}")

        time.sleep(0.5)

    return all_issues


# --------------------------------------------------
# SAVE JSON DATA
# --------------------------------------------------

def save_json(data, output_file):
    """Save extracted data as JSON."""

    output_file.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    with open(output_file, "w", encoding="utf-8") as file:

        json.dump(
            data,
            file,
            indent=4,
            ensure_ascii=False
        )


# --------------------------------------------------
# MAIN EXTRACTION PIPELINE
# --------------------------------------------------

def extract_repositories():

    try:

        print("\nStarting GitHub Data Extraction...\n")

        if GITHUB_TOKEN:
            print("GitHub token detected. Authenticated requests enabled.")

        # Step 1: Repositories
        repositories = get_repositories()

        print(f"\nTotal unique repositories: {len(repositories)}")

        # Step 2: Languages
        language_data = get_repository_languages(repositories)

        # Step 3: Issues
        issue_data = get_repository_issues(repositories)

        # Save all raw datasets
        save_json(repositories, REPOSITORIES_FILE)
        save_json(language_data, LANGUAGES_FILE)
        save_json(issue_data, ISSUES_FILE)

        successful_languages = sum(
            1 for item in language_data
            if "error" not in item
        )

        failed_languages = len(language_data) - successful_languages

        # Final report
        print("\nExtraction Completed!")
        print("----------------------------------")

        print(f"Repositories extracted: {len(repositories)}")
        print(f"Language records extracted: {len(language_data)}")
        print(f"Successful language records: {successful_languages}")
        print(f"Failed language records: {failed_languages}")
        print(f"Total issues extracted: {len(issue_data)}")

        print(f"\nRepositories saved: {REPOSITORIES_FILE}")
        print(f"Languages saved: {LANGUAGES_FILE}")
        print(f"Issues saved: {ISSUES_FILE}")

    except requests.exceptions.HTTPError as error:

        print(f"\nGitHub API HTTP error: {error}")

    except requests.exceptions.RequestException as error:

        print(f"\nNetwork/API request error: {error}")

    except (ValueError, KeyError, OSError) as error:

        print(f"\nData processing or file error: {error}")


if __name__ == "__main__":
    extract_repositories()
