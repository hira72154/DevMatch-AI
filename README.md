# DevMatch AI – Smart Open-Source Contribution & Repository Intelligence System

**Discover the right open-source projects based on your skills.**

## 📌 Project Overview

DevMatch AI is a data-driven platform that helps students and developers discover suitable open-source projects on GitHub based on their programming skills and interests.

It analyzes repository activity, popularity, maintenance status, and beginner-friendly issues to generate meaningful repository insights and recommendations.

## 🎯 Problem Statement

GitHub contains millions of open-source repositories, making it difficult for beginners to identify active, reliable, and beginner-friendly projects. Developers also face challenges in finding relevant contribution opportunities and evaluating repository health.

## 💡 Proposed Solution

DevMatch AI provides an intelligent repository analysis and recommendation system that:

- Evaluates repository health and maintenance activity.
- Identifies beginner-friendly contribution opportunities.
- Recommends repositories based on programming skills.
- Presents insights through an interactive dashboard.

## ⚙️ ETL Pipeline

The project uses the **GitHub REST API** to collect public repository, programming language, and issue-related data.

The ETL pipeline consists of four stages:

1. **Extract:** Fetches repository details, languages, stars, forks, activity timestamps, and issues using the GitHub API.
2. **Transform:** Cleans and preprocesses collected data using Python and Pandas.
3. **Validate:** Validates data records using Pydantic.
4. **Load:** Stores processed data in an SQLite database and exports CSV files for further analysis.

## 📊 Exploratory Data Analysis (EDA)

EDA is performed using Jupyter Notebook to understand the collected dataset through:

- Programming language distribution.
- Repository popularity based on stars and forks.
- Repository maintenance and activity analysis.
- Correlation between stars and forks.
- Beginner-friendly issue distribution.
- Data quality checks and missing-value analysis.

## ✨ Key Features

1. **Beginner-Friendly Project Finder** – Helps users identify repositories with contribution opportunities.
2. **Repository Health Score (0–100)** – Evaluates repository activity, popularity, and engagement.
3. **Contribution Opportunity Score** – Measures available beginner-friendly issues and contribution opportunities.
4. **Skill-Based Recommendation System** – Recommends repositories based on users' programming languages and skills.
5. **Interactive Streamlit Dashboard** – Displays repository insights, charts, filters, scores, and recommendations.

## 🧮 Scoring Methodology

| Component | Evaluation Criteria |
|---|---|
| Repository Health | Activity (50%), Popularity (25%), Engagement (25%) |
| Contribution Opportunity | Beginner-Friendly Issues (40%), Good First Issues (30%), Help Wanted (20%), Activity (10%) |
| Skill Recommendation | Skill Match (60%), Repository Health (20%), Contribution Opportunity (20%) |

The system uses explainable, rule-based scoring rather than a trained machine learning model.

## 🛠️ Technology Stack

- **Programming Language:** Python
- **Data Extraction:** GitHub REST API
- **Data Processing:** Pandas, NumPy
- **Data Validation:** Pydantic
- **Database:** SQLite
- **Data Analysis:** Jupyter Notebook
- **Dashboard:** Streamlit
- **Visualization:** Altair
- **Version Control:** Git & GitHub

## 📁 Project Structure

```text
DevMatch-AI/
│
├── data/
│   ├── raw/
│   └── processed/
│
├── database/
│   └── devmatch.db
│
├── notebook/
│   ├── 01_data_quality_checks.ipynb
│   └── 02_exploratory_data_analysis.ipynb
│
├── src/
│   ├── extract.py
│   ├── transform.py
│   ├── validate.py
│   ├── load.py
│   ├── health_score.py
│   ├── contribution_score.py
│   └── recommendation.py
│
├── .streamlit/
│   └── config.toml
│
├── app.py
└── README.md
```

## 🚀 Installation & Setup

**1. Clone the repository**

```bash
git clone <YOUR_GITHUB_REPOSITORY_URL>
cd DevMatch-AI
```

**2. Activate your virtual environment**

```bash
# Windows PowerShell
.\.venv\Scripts\Activate.ps1
```

**3. Install dependencies**

```bash
pip install pandas numpy streamlit altair jupyter pydantic requests
```

**4. Run the Streamlit dashboard**

```bash
streamlit run app.py
```

Open the local URL displayed in your terminal to access the dashboard.

## 📈 Expected Outcome

DevMatch AI provides a free and data-driven way for students and developers to explore open-source repositories, understand repository health, discover contribution opportunities, and find projects that match their programming skills.

## ⚠️ Limitations

- Recommendations currently use exact programming language matching.
- Scoring is rule-based and depends on the available GitHub data.
- Stars and forks indicate popularity and engagement, not guaranteed code quality.
- Repository scores are indicators to support decisions, not definitive quality ratings.

## 👥 Contributors

Developed as an academic project focused on data engineering, exploratory data analysis, repository intelligence, and recommendation systems.

---

**DevMatch AI – Making Open-Source Contributions Easier and Smarter.**