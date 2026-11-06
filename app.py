
import sqlite3
from pathlib import Path

import altair as alt
import pandas as pd
import streamlit as st


# =====================================================
# PAGE CONFIGURATION
# =====================================================

st.set_page_config(
    page_title="DevMatch AI | Dashboard",
    layout="wide",
    initial_sidebar_state="expanded"
)

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "database" / "devmatch.db"
PROCESSED = BASE_DIR / "data" / "processed"

HEALTH_PATH = PROCESSED / "repositories_health_scores.csv"
CONTRIBUTION_PATH = PROCESSED / "repositories_contribution_scores.csv"


# =====================================================
# PROFESSIONAL LIGHT THEME + TYPOGRAPHY
# =====================================================

st.markdown("""
<style>

/* Main Application */
.stApp {
    background: #FFFFFF;
    color: #263445;
    font-family: "Inter", "Segoe UI", Arial, sans-serif;
}

html, body, [class*="css"] {
    font-family: "Inter", "Segoe UI", Arial, sans-serif;
    font-size: 16px;
}

.block-container {
    padding-top: 2rem;
    padding-bottom: 2rem;
    max-width: 1450px;
}

/* Sidebar */
section[data-testid="stSidebar"] {
    background: #F1F5F9;
    border-right: 1px solid #E1E8F0;
}

section[data-testid="stSidebar"] * {
    color: #263445 !important;
    font-size: 15px;
}

section[data-testid="stSidebar"] h2 {
    font-size: 24px !important;
    font-weight: 800 !important;
}

section[data-testid="stSidebar"] p {
    font-size: 14px !important;
}

/* Main Headings */
h1 {
    color: #263F5C !important;
    font-size: 30px !important;
    font-weight: 800 !important;
    letter-spacing: -0.7px;
}

h2 {
    color: #263F5C !important;
    font-size: 25px !important;
    font-weight: 750 !important;
}

h3 {
    color: #263F5C !important;
    font-size: 21px !important;
    font-weight: 700 !important;
}

h4 {
    color: #263F5C !important;
    font-size: 18px !important;
    font-weight: 700 !important;
}

/* Normal Text */
p, label, li {
    color: #46566A;
    font-size: 16px;
    line-height: 1.65;
}

/* KPI Cards */
div[data-testid="stMetric"] {
    background: #FFFFFF;
    border: 1px solid #E3EAF2;
    border-top: 4px solid #477DB5;
    border-radius: 12px;
    padding: 19px;
    box-shadow: 0 3px 12px rgba(35, 55, 80, 0.06);
}

div[data-testid="stMetricLabel"] {
    color: #65758A !important;
    font-size: 15px !important;
    font-weight: 650 !important;
}

div[data-testid="stMetricValue"] {
    color: #263F5C !important;
    font-size: 32px !important;
    font-weight: 800 !important;
}

div[data-testid="stMetricDelta"] {
    font-size: 14px !important;
    font-weight: 600 !important;
}

/* Different KPI Card Accents */
div[data-testid="stHorizontalBlock"] > div:nth-child(1)
div[data-testid="stMetric"] {
    border-top-color: #477DB5;
}

div[data-testid="stHorizontalBlock"] > div:nth-child(2)
div[data-testid="stMetric"] {
    border-top-color: #399B78;
}

div[data-testid="stHorizontalBlock"] > div:nth-child(3)
div[data-testid="stMetric"] {
    border-top-color: #D69B35;
}

div[data-testid="stHorizontalBlock"] > div:nth-child(4)
div[data-testid="stMetric"] {
    border-top-color: #9273B9;
}

/* Buttons */
.stButton > button {
    background: #477DB5;
    color: white;
    border: none;
    border-radius: 7px;
    font-size: 15px;
    font-weight: 650;
    padding: 8px 18px;
}

.stButton > button:hover {
    background: #345F8D;
    color: white;
}

/* Inputs and Select Boxes */
.stTextInput label,
.stSelectbox label,
.stMultiSelect label,
.stSlider label {
    font-size: 15px !important;
    font-weight: 650 !important;
    color: #263F5C !important;
}

.stTextInput input {
    font-size: 16px !important;
}

/* Data Tables */
div[data-testid="stDataFrame"] {
    border: 1px solid #E3EAF2;
    border-radius: 9px;
    font-size: 15px;
}

/* Chart Containers */
div[data-testid="stVegaLiteChart"] {
    background: #FFFFFF;
    border: 1px solid #E7ECF2;
    border-radius: 11px;
    padding: 12px;
}

/* Dashboard Header */
.dashboard-header {
    background: #F4F7FB;
    border: 1px solid #E3EAF2;
    border-left: 5px solid #477DB5;
    border-radius: 12px;
    padding: 24px 27px;
    margin-bottom: 24px;
}

.dashboard-header h1 {
    color: #263F5C !important;
    font-size: 32px !important;
    font-weight: 800 !important;
    margin-bottom: 8px;
}

.dashboard-header p {
    color: #65758A;
    font-size: 16px;
    margin-bottom: 0;
}

/* Recommendation Cards */
.recommendation-card {
    background: #FFFFFF;
    border: 1px solid #E3EAF2;
    border-left: 4px solid #399B78;
    border-radius: 9px;
    padding: 17px 19px;
    margin-bottom: 12px;
}

.recommendation-card h4 {
    color: #263F5C !important;
    font-size: 18px !important;
    font-weight: 750 !important;
    margin: 0 0 8px 0;
}

.recommendation-card p {
    color: #65758A;
    margin: 0;
    font-size: 15px;
    font-weight: 500;
}

/* Section Descriptions */
.section-description {
    color: #65758A;
    font-size: 16px;
    font-weight: 500;
    line-height: 1.6;
    margin-top: -10px;
    margin-bottom: 22px;
}

/* Captions */
.stCaption,
[data-testid="stCaptionContainer"] {
    color: #718096 !important;
    font-size: 14px !important;
}

/* Divider */
hr {
    border-color: #E5EAF0;
}

</style>
""", unsafe_allow_html=True)


# =====================================================
# CHART THEME AND COLOURS
# =====================================================

COLORS = [
    "#477DB5",  # Blue
    "#399B78",  # Green
    "#D69B35",  # Yellow
    "#D66A6A",  # Red
    "#9273B9",  # Purple
    "#399DAD",  # Teal
    "#8196AA"   # Slate
]


def chart_style(chart):
    return (
        chart
        .configure_view(strokeOpacity=0)
        .configure_axis(
            labelColor="#46566A",
            titleColor="#263F5C",
            gridColor="#E8EDF3",
            domainColor="#D9E1EA",
            labelFont="Inter",
            titleFont="Inter",
            labelFontSize=13,
            titleFontSize=15,
            titleFontWeight="bold"
        )
        .configure_legend(
            labelFont="Inter",
            titleFont="Inter",
            labelFontSize=13,
            titleFontSize=14,
            titleFontWeight="bold"
        )
        .configure_title(
            color="#263F5C",
            font="Inter",
            fontSize=18,
            fontWeight="bold",
            anchor="start"
        )
    )


def find_col(df, names):
    for name in names:
        if name in df.columns:
            return name
    return None


def score_col(df, keywords):
    for col in df.columns:
        if "score" in col.lower() and any(
            word in col.lower() for word in keywords
        ):
            return col
    return None


def numeric(series):
    return pd.to_numeric(series, errors="coerce").fillna(0)


def heading(title, description):
    st.title(title)
    st.markdown(
        f'<p class="section-description">{description}</p>',
        unsafe_allow_html=True
    )


# =====================================================
# LOAD DATA
# =====================================================

@st.cache_data
def load_data():

    if not DB_PATH.exists():
        raise FileNotFoundError("database/devmatch.db not found")

    con = sqlite3.connect(DB_PATH)

    try:
        repos = pd.read_sql_query(
            "SELECT * FROM repositories", con
        )

        issues = pd.read_sql_query(
            "SELECT * FROM issues", con
        )

        summary = pd.read_sql_query(
            "SELECT * FROM issue_summary", con
        )

    finally:
        con.close()

    health = (
        pd.read_csv(HEALTH_PATH)
        if HEALTH_PATH.exists()
        else pd.DataFrame()
    )

    contribution = (
        pd.read_csv(CONTRIBUTION_PATH)
        if CONTRIBUTION_PATH.exists()
        else pd.DataFrame()
    )

    # Avoid duplicate issue-summary columns.
    summary_columns = [
        "total_open_issues",
        "beginner_friendly_issues",
        "good_first_issues",
        "help_wanted_issues"
    ]

    contribution = contribution.drop(
        columns=[
            c for c in summary_columns
            if c in contribution.columns
        ],
        errors="ignore"
    )

    if not health.empty and "full_name" in health.columns:
        repos = repos.merge(
            health,
            on="full_name",
            how="left",
            suffixes=("", "_health")
        )

    if not contribution.empty and "full_name" in contribution.columns:
        repos = repos.merge(
            contribution,
            on="full_name",
            how="left",
            suffixes=("", "_contribution")
        )

    if "full_name" in summary.columns:
        repos = repos.merge(
            summary,
            on="full_name",
            how="left",
            suffixes=("", "_summary")
        )

    return repos, issues, summary


try:
    repos, issues, issue_summary = load_data()

except Exception as error:
    st.error(f"Unable to load project data: {error}")
    st.stop()


if repos.empty:
    st.warning("No repository data found.")
    st.stop()


language_col = find_col(repos, ["language"])
name_col = find_col(repos, ["full_name", "name"])

health_score = score_col(repos, ["health"])

contribution_score = score_col(
    repos, ["contribution", "opportunity"]
)

health_status = find_col(
    repos, ["health_status", "status"]
)

repos["_repo_name"] = (
    repos[name_col].fillna("Unknown")
    if name_col else "Unknown"
)


# =====================================================
# SIDEBAR
# =====================================================

with st.sidebar:

    st.markdown("""
    <div style="padding:15px 5px 22px 5px;">
        <h2 style="color:#263F5C !important;">
            DEVMATCH AI
        </h2>
        <p style="color:#718096;">
            Repository Intelligence Platform
        </p>
    </div>
    """, unsafe_allow_html=True)

    st.divider()

    page = st.radio(
        "Navigation",
        [
            "Overview",
            "Repository Explorer",
            "Health Analysis",
            "Contribution Opportunities",
            "Skill Recommendations"
        ]
    )

    st.divider()

    st.caption("Project Analytics Dashboard")


# =====================================================
# OVERVIEW
# =====================================================

if page == "Overview":

    st.markdown("""
    <div class="dashboard-header">
        <h1>Dashboard Overview</h1>
        <p>
            Explore repository statistics, programming languages,
            project health and contribution opportunities.
        </p>
    </div>
    """, unsafe_allow_html=True)

    total_repos = len(repos)
    total_issues = len(issues)

    total_languages = (
        repos[language_col].nunique()
        if language_col else 0
    )

    total_stars = (
        numeric(repos["stargazers_count"]).sum()
        if "stargazers_count" in repos.columns else 0
    )

    c1, c2, c3, c4 = st.columns(4)

    c1.metric("Total Repositories", f"{total_repos:,}")
    c2.metric("Total Issues", f"{total_issues:,}")
    c3.metric("Programming Languages", f"{total_languages:,}")
    c4.metric("Total Stars", f"{total_stars:,.0f}")

    st.divider()

    left, right = st.columns(2)

    with left:

        st.subheader("Programming Language Distribution")

        if language_col:

            lang_data = (
                repos[language_col]
                .fillna("Unknown")
                .value_counts()
                .reset_index()
            )

            lang_data.columns = ["Language", "Repositories"]

            donut = (
                alt.Chart(lang_data)
                .mark_arc(
                    innerRadius=65,
                    outerRadius=115,
                    stroke="white",
                    strokeWidth=2
                )
                .encode(
                    theta="Repositories:Q",
                    color=alt.Color(
                        "Language:N",
                        scale=alt.Scale(range=COLORS)
                    ),
                    tooltip=["Language", "Repositories"]
                )
                .properties(height=320)
            )

            st.altair_chart(
                chart_style(donut),
                use_container_width=True
            )

    with right:

        st.subheader("Top Repositories by Stars")

        if "stargazers_count" in repos.columns:

            top = repos.nlargest(
                10, "stargazers_count"
            )[["_repo_name", "stargazers_count"]]

            top = top.rename(
                columns={
                    "_repo_name": "Repository",
                    "stargazers_count": "Stars"
                }
            )

            bar = (
                alt.Chart(top)
                .mark_bar(
                    color="#477DB5",
                    cornerRadiusEnd=5
                )
                .encode(
                    x=alt.X("Stars:Q", title="Stars"),
                    y=alt.Y(
                        "Repository:N",
                        sort="-x",
                        title=None
                    ),
                    tooltip=["Repository", "Stars"]
                )
                .properties(height=320)
            )

            st.altair_chart(
                chart_style(bar),
                use_container_width=True
            )

    st.divider()

    st.subheader("Repository Activity Timeline")

    if "pushed_at" in repos.columns:

        activity = repos[["pushed_at"]].copy()

        activity["pushed_at"] = pd.to_datetime(
            activity["pushed_at"],
            errors="coerce",
            utc=True
        )

        activity = activity.dropna()

        if not activity.empty:

            activity["Month"] = (
                activity["pushed_at"]
                .dt.strftime("%Y-%m")
            )

            monthly = (
                activity.groupby("Month")
                .size()
                .reset_index(name="Repositories")
            )

            wave = (
                alt.Chart(monthly)
                .mark_area(
                    interpolate="monotone",
                    color="#B8D4EC",
                    line={
                        "color": "#477DB5",
                        "strokeWidth": 2.5
                    },
                    opacity=0.8
                )
                .encode(
                    x=alt.X("Month:N", sort=None),
                    y=alt.Y(
                        "Repositories:Q",
                        title="Repository Updates"
                    ),
                    tooltip=["Month", "Repositories"]
                )
                .properties(height=300)
            )

            st.altair_chart(
                chart_style(wave),
                use_container_width=True
            )

    st.divider()

    st.subheader("Repository Dataset")

    st.dataframe(
        repos.drop(columns=["_repo_name"], errors="ignore"),
        use_container_width=True,
        hide_index=True
    )


# =====================================================
# REPOSITORY EXPLORER
# =====================================================

elif page == "Repository Explorer":

    heading(
        "Repository Explorer",
        "Search and filter open-source repositories."
    )

    search = st.text_input(
        "Search repository",
        placeholder="Enter repository name..."
    )

    filtered = repos.copy()

    if language_col:

        languages = sorted(
            filtered[language_col].dropna().unique()
        )

        selected_language = st.selectbox(
            "Programming Language",
            ["All Languages"] + languages
        )

        if selected_language != "All Languages":
            filtered = filtered[
                filtered[language_col] == selected_language
            ]

    if search:
        filtered = filtered[
            filtered["_repo_name"].str.contains(
                search,
                case=False,
                na=False
            )
        ]

    st.metric("Repositories Found", len(filtered))

    st.dataframe(
        filtered.drop(columns=["_repo_name"], errors="ignore"),
        use_container_width=True,
        hide_index=True
    )


# =====================================================
# HEALTH ANALYSIS
# =====================================================

elif page == "Health Analysis":

    heading(
        "Repository Health Analysis",
        "Understand repository activity, popularity and engagement."
    )

    if not health_score:

        st.warning("Health score column was not found.")

    else:

        data = repos.copy()
        data[health_score] = numeric(data[health_score])

        c1, c2, c3 = st.columns(3)

        c1.metric(
            "Average Health Score",
            f"{data[health_score].mean():.2f}"
        )

        c2.metric(
            "Highest Score",
            f"{data[health_score].max():.2f}"
        )

        c3.metric(
            "Lowest Score",
            f"{data[health_score].min():.2f}"
        )

        st.divider()

        left, right = st.columns(2)

        with left:

            st.subheader("Health Score Distribution")

            hist = (
                alt.Chart(data)
                .mark_bar(
                    color="#399B78",
                    cornerRadiusEnd=3
                )
                .encode(
                    x=alt.X(
                        health_score + ":Q",
                        bin=alt.Bin(maxbins=12),
                        title="Health Score"
                    ),
                    y=alt.Y(
                        "count():Q",
                        title="Repositories"
                    ),
                    tooltip=["count()"]
                )
                .properties(height=310)
            )

            st.altair_chart(
                chart_style(hist),
                use_container_width=True
            )

        with right:

            st.subheader("Health Status")

            if health_status:

                status_data = (
                    data[health_status]
                    .fillna("Unknown")
                    .value_counts()
                    .reset_index()
                )

                status_data.columns = [
                    "Status",
                    "Repositories"
                ]

                donut = (
                    alt.Chart(status_data)
                    .mark_arc(
                        innerRadius=65,
                        outerRadius=110
                    )
                    .encode(
                        theta="Repositories:Q",
                        color=alt.Color(
                            "Status:N",
                            scale=alt.Scale(
                                range=[
                                    "#399B78",
                                    "#D69B35",
                                    "#D66A6A"
                                ]
                            )
                        ),
                        tooltip=["Status", "Repositories"]
                    )
                    .properties(height=310)
                )

                st.altair_chart(
                    chart_style(donut),
                    use_container_width=True
                )

        st.divider()

        st.subheader("Top Repository Health Scores")

        top = data.nlargest(
            15, health_score
        )[["_repo_name", health_score]]

        top = top.rename(
            columns={
                "_repo_name": "Repository",
                health_score: "Health Score"
            }
        )

        bar = (
            alt.Chart(top)
            .mark_bar(
                color="#399B78",
                cornerRadiusEnd=5
            )
            .encode(
                x=alt.X(
                    "Health Score:Q",
                    scale=alt.Scale(domain=[0, 100])
                ),
                y=alt.Y(
                    "Repository:N",
                    sort="-x"
                ),
                tooltip=["Repository", "Health Score"]
            )
            .properties(height=400)
        )

        st.altair_chart(
            chart_style(bar),
            use_container_width=True
        )

        st.dataframe(
            data.drop(columns=["_repo_name"], errors="ignore"),
            use_container_width=True,
            hide_index=True
        )


# =====================================================
# CONTRIBUTION OPPORTUNITIES
# =====================================================

elif page == "Contribution Opportunities":

    heading(
        "Contribution Opportunities",
        "Find repositories with beginner-friendly issues and opportunities."
    )

    if not contribution_score:

        st.warning("Contribution score column was not found.")

    else:

        data = repos.copy()

        data[contribution_score] = numeric(
            data[contribution_score]
        )

        beginner = find_col(
            data, ["beginner_friendly_issues"]
        )

        good_first = find_col(
            data, ["good_first_issues"]
        )

        help_wanted = find_col(
            data, ["help_wanted_issues"]
        )

        c1, c2, c3 = st.columns(3)

        for col, label, container in [
            (beginner, "Beginner Friendly Issues", c1),
            (good_first, "Good First Issues", c2),
            (help_wanted, "Help Wanted Issues", c3)
        ]:

            with container:

                value = (
                    numeric(data[col]).sum()
                    if col else 0
                )

                st.metric(label, f"{value:,.0f}")

        st.divider()

        st.subheader("Contribution Opportunity Scores")

        top = data.nlargest(
            15, contribution_score
        )[["_repo_name", contribution_score]]

        top = top.rename(
            columns={
                "_repo_name": "Repository",
                contribution_score: "Opportunity Score"
            }
        )

        bar = (
            alt.Chart(top)
            .mark_bar(
                color="#D69B35",
                cornerRadiusEnd=5
            )
            .encode(
                x=alt.X(
                    "Opportunity Score:Q",
                    scale=alt.Scale(domain=[0, 100])
                ),
                y=alt.Y(
                    "Repository:N",
                    sort="-x"
                ),
                tooltip=["Repository", "Opportunity Score"]
            )
            .properties(height=400)
        )

        st.altair_chart(
            chart_style(bar),
            use_container_width=True
        )

        st.divider()

        st.subheader("Contribution Dataset")

        st.dataframe(
            data.drop(columns=["_repo_name"], errors="ignore"),
            use_container_width=True,
            hide_index=True
        )

        st.caption(
            "Opportunity scores reflect collected issue labels "
            "and repository activity, not overall repository quality."
        )


# =====================================================
# SKILL RECOMMENDATIONS
# =====================================================

elif page == "Skill Recommendations":

    heading(
        "Skill-Based Recommendations",
        "Discover repositories based on your programming language skills."
    )

    if not language_col:

        st.warning("Programming language column is missing.")

    else:

        skills = sorted(
            repos[language_col].dropna().unique().tolist()
        )

        selected_skills = st.multiselect(
            "Select your programming skills",
            skills,
            placeholder="Choose Python, Java, C++, etc."
        )

        top_n = st.slider(
            "Number of recommendations",
            1, 20, 10
        )

        if selected_skills:

            results = repos[
                repos[language_col].isin(selected_skills)
            ].copy()

            if results.empty:

                st.info("No matching repositories found.")

            else:

                results["Skill Match"] = 100

                results["Health Score"] = (
                    numeric(results[health_score])
                    if health_score else 0
                )

                results["Opportunity Score"] = (
                    numeric(results[contribution_score])
                    if contribution_score else 0
                )

                results["Recommendation Score"] = (
                    results["Skill Match"] * 0.60
                    + results["Health Score"] * 0.20
                    + results["Opportunity Score"] * 0.20
                )

                results = results.sort_values(
                    "Recommendation Score",
                    ascending=False
                ).head(top_n)

                st.divider()

                st.metric(
                    "Matching Repositories",
                    len(results)
                )

                st.subheader("Recommended Repositories")

                for _, row in results.iterrows():

                    st.markdown(
                        f"""
                        <div class="recommendation-card">
                            <h4>{row['_repo_name']}</h4>
                            <p>
                                Language: {row[language_col]}
                                &nbsp; | &nbsp;
                                Recommendation Score:
                                {row['Recommendation Score']:.2f}/100
                            </p>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )

                st.divider()

                st.subheader("Score Comparison")

                chart_data = results[
                    [
                        "_repo_name",
                        "Skill Match",
                        "Health Score",
                        "Opportunity Score"
                    ]
                ].rename(
                    columns={"_repo_name": "Repository"}
                )

                melted = chart_data.melt(
                    id_vars="Repository",
                    var_name="Score Type",
                    value_name="Score"
                )

                comparison = (
                    alt.Chart(melted)
                    .mark_bar(
                        cornerRadiusEnd=3
                    )
                    .encode(
                        x=alt.X(
                            "Score:Q",
                            scale=alt.Scale(domain=[0, 100])
                        ),
                        y=alt.Y(
                            "Repository:N",
                            sort="-x"
                        ),
                        color=alt.Color(
                            "Score Type:N",
                            scale=alt.Scale(
                                domain=[
                                    "Skill Match",
                                    "Health Score",
                                    "Opportunity Score"
                                ],
                                range=[
                                    "#477DB5",
                                    "#399B78",
                                    "#D69B35"
                                ]
                            )
                        ),
                        tooltip=[
                            "Repository",
                            "Score Type",
                            "Score"
                        ]
                    )
                    .properties(height=400)
                )

                st.altair_chart(
                    chart_style(comparison),
                    use_container_width=True
                )

                st.subheader("Recommendation Details")

                st.dataframe(
                    results[
                        [
                            "_repo_name",
                            "Skill Match",
                            "Health Score",
                            "Opportunity Score",
                            "Recommendation Score"
                        ]
                    ].rename(
                        columns={"_repo_name": "Repository"}
                    ),
                    use_container_width=True,
                    hide_index=True
                )

                st.caption(
                    "Formula: Skill Match 60% + Health Score 20% "
                    "+ Opportunity Score 20%. Exact language matching."
                )

        else:

            st.info(
                "Select at least one programming skill "
                "to see recommendations."
            )


# =====================================================
# FOOTER
# =====================================================

st.divider()

st.markdown(
    """
    <p style="
        text-align:center;
        color:#8492A3;
        font-size:14px;
        font-weight:600;
    ">
        DevMatch AI | Repository Intelligence Platform
    </p>
    """,
    unsafe_allow_html=True
)
