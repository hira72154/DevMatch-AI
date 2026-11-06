
from pathlib import Path
import pandas as pd


# Project paths
PROJECT_ROOT = Path(__file__).resolve().parent.parent
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"

REPOSITORIES_FILE = PROCESSED_DIR / "repositories_clean.csv"
HEALTH_FILE = PROCESSED_DIR / "repositories_health_scores.csv"
CONTRIBUTION_FILE = PROCESSED_DIR / "repositories_contribution_scores.csv"


def recommend_repositories(student_skills, top_n=10):
    """
    Recommend GitHub repositories based on student skills.

    Final Score:
        60% Skill Match
        20% Repository Health
        20% Contribution Opportunity
    """

    # Load datasets
    repositories = pd.read_csv(REPOSITORIES_FILE)
    health = pd.read_csv(HEALTH_FILE)
    contribution = pd.read_csv(CONTRIBUTION_FILE)

    # Validate student input
    if isinstance(student_skills, str):
        student_skills = student_skills.split(",")

    skills = {
        skill.strip().lower()
        for skill in student_skills
        if skill.strip()
    }

    if not skills:
        raise ValueError("Please enter at least one skill.")

    # Merge all datasets
    df = repositories.merge(
        health,
        on="full_name",
        how="left"
    )

    df = df.merge(
        contribution,
        on="full_name",
        how="left"
    )

    # Match student skills with repository language
    df["language_normalized"] = (
        df["language"].fillna("").str.strip().str.lower()
    )

    df["skill_match"] = df["language_normalized"].apply(
        lambda language: language in skills
    )

    # Keep only repositories matching student skills
    recommendations = df[df["skill_match"]].copy()

    if recommendations.empty:
        print("No repositories found for the entered skills.")
        print("Available skills: Python, C, C++, Java, JavaScript, HTML, CSS")
        return recommendations

    # Fill missing score values
    recommendations["health_score"] = (
        recommendations["health_score"].fillna(0)
    )

    recommendations["contribution_score"] = (
        recommendations["contribution_score"].fillna(0)
    )

    # Calculate final recommendation score
    recommendations["recommendation_score"] = (
        recommendations["health_score"] * 0.20
        + recommendations["contribution_score"] * 0.20
        + 100 * 0.60
    )

    # Sort highest score first
    recommendations = recommendations.sort_values(
        by="recommendation_score",
        ascending=False
    )

    # Select useful output columns
    output_columns = [
        "full_name",
        "language",
        "stargazers_count",
        "health_score",
        "contribution_score",
        "recommendation_score"
    ]

    return recommendations[output_columns].head(top_n)


if __name__ == "__main__":

    print("\n===== DevMatch AI Recommendation System =====")
    print("Available Skills: Python, C, C++, Java, JavaScript, HTML, CSS")

    student_input = input(
        "\nEnter your skills (comma-separated): "
    )

    result = recommend_repositories(student_input, top_n=10)

    if not result.empty:
        print("\nRecommended Repositories:\n")

        print(
            result.to_string(
                index=False,
                formatters={
                    "health_score": "{:.2f}".format,
                    "contribution_score": "{:.2f}".format,
                    "recommendation_score": "{:.2f}".format
                }
            )
        )
