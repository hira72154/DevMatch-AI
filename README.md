# DevMatch AI – Smart Open-Source Contribution & Repository Intelligence System

## Project Description

DevMatch AI is a data-driven platform designed to help students and developers discover suitable open-source projects on GitHub based on their programming skills, experience levels, and interests.

## Problem Statement

GitHub hosts millions of open-source repositories, making it difficult for beginners to identify active, reliable, and beginner-friendly projects. Developers often struggle to find suitable contribution opportunities and evaluate repository quality.

## Proposed Solution

DevMatch AI aims to provide an intelligent repository analysis and recommendation system that evaluates GitHub projects based on programming languages, maintenance activity, popularity, and beginner-friendly issues.

The system will generate Repository Health Scores and Contribution Opportunity Scores to help users make informed decisions when selecting open-source projects.

## Data Source and ETL Process

The project uses the free GitHub REST API to extract public repository information, including repository details, programming languages, stars, forks, activity timestamps, and issue details.

The ETL pipeline has been implemented using:

- **Extract:** Fetching repository, language, and issue data through the GitHub REST API.
- **Transform:** Cleaning and preprocessing data using Python and Pandas.
- **Validate:** Validating data records using Pydantic.
- **Load:** Storing cleaned and validated data in an SQLite database, with CSV exports for analysis.

## Exploratory Data Analysis (EDA)

The project will analyze:

- Programming language distributions.
- Repository popularity based on stars and forks.
- Repository maintenance and activity.
- Relationship between stars and forks.
- Beginner-friendly contribution opportunities.

## Key Features (Planned)

An interactive Streamlit dashboard featuring:

1. Beginner-Friendly Open-Source Project Finder
2. Repository Health Score (0–100)
3. Contribution Opportunity Score
4. Skill-Based Repository Recommendation System
5. Interactive EDA Charts and Repository Comparisons

## Expected Outcome

A free, data-driven platform that helps students and developers discover suitable open-source projects and contribution opportunities through explainable, rule-based recommendations and meaningful data analysis.

## Technology Stack

- **Programming Language:** Python
- **Data Extraction:** GitHub REST API
- **Data Processing:** Pandas
- **Data Validation:** Pydantic
- **Database:** SQLite
- **Data Analysis:** Jupyter Notebook
- **Dashboard:** Streamlit (Planned)
