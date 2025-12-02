import streamlit as st
import pandas as pd
import altair as alt

# --------------------------------------------------
# Page configuration
# --------------------------------------------------
st.set_page_config(
    page_title="GenAI Adoption Impact Dashboard",
    layout="wide",
)

# --------------------------------------------------
# Load data
# --------------------------------------------------
@st.cache_data
def load_data():
    df = pd.read_csv("Enterprise_GenAI_Adoption_Impact.csv")

# --------------------------------------------------
# Sidebar filters
# --------------------------------------------------
st.sidebar.title("Filters")

industries = st.sidebar.multiselect(
    "Industry",
    options=sorted(df["Industry"].unique()),
    default=sorted(df["Industry"].unique()),
)

countries = st.sidebar.multiselect(
    "Country",
    options=sorted(df["Country"].unique()),
    default=sorted(df["Country"].unique()),
)

tools = st.sidebar.multiselect(
    "GenAI Tool",
    options=sorted(df["GenAI_Tool"].unique()),
    default=sorted(df["GenAI_Tool"].unique()),
)

min_year = int(df["Adoption Year"].min())
max_year = int(df["Adoption Year"].max())

year_range = st.sidebar.slider(
    "Adoption Year Range",
    min_value=min_year,
    max_value=max_year,
    value=(min_year, max_year),
    step=1,
)

# Apply filters
filtered_df = df[
    (df["Industry"].isin(industries))
    & (df["Country"].isin(countries))
    & (df["GenAI_Tool"].isin(tools))
    & (df["Adoption Year"] >= year_range[0])
    & (df["Adoption Year"] <= year_range[1])
]

if filtered_df.empty:
    st.warning("No data matches your filters. Try relaxing one or more filters.")
    st.stop()

# --------------------------------------------------
# Title & KPIs
# --------------------------------------------------
st.title(" GenAI Adoption Impact Dashboard")

st.write(
    "Use the filters in the sidebar to explore how enterprise GenAI adoption "
    "impacts productivity, training, and employees across industries."
)

col_kpi1, col_kpi2, col_kpi3 = st.columns(3)

with col_kpi1:
    st.metric("Number of Records", len(filtered_df))

with col_kpi2:
    st.metric(
        "Avg Productivity Change (%)",
        f"{filtered_df['Productivity_Change'].mean():.1f}",
    )

with col_kpi3:
    st.metric(
        "Avg Training Hours",
        f"{filtered_df['Training_Hours'].mean():.0f}",
    )

st.markdown("---")

# --------------------------------------------------
# Recommendation section 
# --------------------------------------------------
st.subheader(" Data-Driven Recommendation Based on Your Selections")

rec_col1, rec_col2 = st.columns(2)

with rec_col1:
    rec_industry = st.selectbox(
        "Industry for recommendation",
        options=["(All industries)"] + sorted(df["Industry"].unique()),
    )

with rec_col2:
    rec_country = st.selectbox(
        "Country for recommendation",
        options=["(All countries)"] + sorted(df["Country"].unique()),
    )

rec_df = filtered_df.copy()

if rec_industry != "(All industries)":
    rec_df = rec_df[rec_df["Industry"] == rec_industry]

if rec_country != "(All countries)":
    rec_df = rec_df[rec_df["Country"] == rec_country]

if rec_df.empty:
    st.info(
        "No records for that industry / country combination under the current filters."
    )
else:
    # Best tool by average productivity in this slice
    by_tool = (
        rec_df.groupby("GenAI_Tool")["Productivity_Change"]
        .mean()
        .reset_index()
        .sort_values("Productivity_Change", ascending=False)
    )

    top_row = by_tool.iloc[0]
    top_tool = top_row["GenAI_Tool"]
    top_prod = top_row["Productivity_Change"]
    n_recs = rec_df[rec_df["GenAI_Tool"] == top_tool].shape[0]

    st.success(
        f"Based on your selections, **{top_tool}** has the highest average "
        f"productivity change at **{top_prod:.1f}%** across **{n_recs} records** "
        f"in this subset."
    )

    # Planned training hours slider
    min_train = int(rec_df["Training_Hours"].min())
    max_train = int(rec_df["Training_Hours"].max())
    median_train = int(rec_df["Training_Hours"].median())

    planned_hours = st.slider(
        "Planned training hours per employee",
        min_value=min_train,
        max_value=max_train,
        value=median_train,
    )

    # Companies with similar training hours (±10% of range, at least 50 hours)
    train_range = max_train - min_train
    window = max(50, int(0.1 * train_range))

    close_df = rec_df[
        (rec_df["Training_Hours"] >= planned_hours - window)
        & (rec_df["Training_Hours"] <= planned_hours + window)
    ]

    if close_df.empty:
        expected_prod = rec_df["Productivity_Change"].mean()
        st.write(
            f"There are no companies with training hours very close to **{planned_hours}**. "
            f"Across this subset in general, average productivity change is about "
            f"**{expected_prod:.1f}%**."
        )
    else:
        expected_prod = close_df["Productivity_Change"].mean()
        st.write(
            f"For companies with **≈ {planned_hours}** training hours in this subset, "
            f"average productivity change has been about **{expected_prod:.1f}%**."
        )

st.markdown("---")

# --------------------------------------------------
# Chart 1 — Companies by GenAI Tool
# --------------------------------------------------
st.subheader("Companies Using Each GenAI Tool")

tool_counts = (
    filtered_df.groupby("GenAI_Tool")
    .size()
    .reset_index(name="Companies")
)

chart_tools = (
    alt.Chart(tool_counts)
    .mark_bar()
    .encode(
        x=alt.X("GenAI_Tool:N", title="GenAI Tool"),
        y=alt.Y("Companies:Q", title="Number of Companies"),
        tooltip=["GenAI_Tool", "Companies"],
    )
    .properties(title="Companies Using Each GenAI Tool")
)

st.altair_chart(chart_tools, use_container_width=True)

# --------------------------------------------------
# Chart 2 — Average productivity change by tool
# --------------------------------------------------
st.subheader("Average Productivity Change by GenAI Tool")

tool_productivity = (
    filtered_df.groupby("GenAI_Tool")["Productivity_Change"]
    .mean()
    .reset_index()
)

chart_tool_productivity = (
    alt.Chart(tool_productivity)
    .mark_bar()
    .encode(
        x=alt.X("GenAI_Tool:N", title="GenAI Tool"),
        y=alt.Y("Productivity_Change:Q", title="Avg Productivity Change (%)"),
        tooltip=[
            "GenAI_Tool",
            alt.Tooltip("Productivity_Change:Q", format=".1f"),
        ],
    )
    .properties(title="Average Productivity Change by GenAI Tool")
)

st.altair_chart(chart_tool_productivity, use_container_width=True)



# --------------------------------------------------
# Raw data
# --------------------------------------------------
with st.expander("Show raw filtered data"):
    st.write(
        filtered_df[
            [
                "Company_Name",
                "Industry",
                "Country",
                "GenAI_Tool",
                "Adoption Year",
                "Employees_Impacted",
                "New_Roles_Created",
                "Training_Hours",
                "Productivity_Change",
                "Employee_Sentiment",
            ]
        ]
    )
