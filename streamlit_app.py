import streamlit as st
import pandas as pd
import altair as alt

# --------------------------------------------------
# Page config
# --------------------------------------------------
st.set_page_config(
    page_title="GenAI Adoption Impact Dashboard",
    layout="wide",
    page_icon="🤖",
)

# --------------------------------------------------
# Load data
# --------------------------------------------------
@st.cache_data
def load_data():
    df = pd.read_csv("Enterprise_GenAI_Adoption_Impact.csv")

    df = df.rename(
        columns={
            "Company Name": "Company_Name",
            "GenAI Tool": "GenAI_Tool",
            "Number of Employees Impacted": "Employees_Impacted",
            "New Roles Created": "New_Roles_Created",
            "Training Hours Provided": "Training_Hours",
            "Productivity Change (%)": "Productivity_Change",
            "Employee Sentiment": "Employee_Sentiment",
        }
    )
    return df

df = load_data()

# --------------------------------------------------
# Sidebar filters
# --------------------------------------------------
st.sidebar.title("Filters")

industries = st.sidebar.multiselect(
    "Industry",
    sorted(df["Industry"].unique()),
    default=sorted(df["Industry"].unique()),
)

countries = st.sidebar.multiselect(
    "Country",
    sorted(df["Country"].unique()),
    default=sorted(df["Country"].unique()),
)

tools = st.sidebar.multiselect(
    "GenAI Tool",
    sorted(df["GenAI_Tool"].unique()),
    default=sorted(df["GenAI_Tool"].unique()),
)

min_year = int(df["Adoption Year"].min())
max_year = int(df["Adoption Year"].max())
year_range = st.sidebar.slider(
    "Adoption Year Range",
    min_value=min_year,
    max_value=max_year,
    value=(min_year, max_year),
)

filtered_df = df[
    (df["Industry"].isin(industries)) &
    (df["Country"].isin(countries)) &
    (df["GenAI_Tool"].isin(tools)) &
    (df["Adoption Year"] >= year_range[0]) &
    (df["Adoption Year"] <= year_range[1])
]

if filtered_df.empty:
    st.warning("No data matches your filters. Try relaxing one of the filters.")
    st.stop()

# --------------------------------------------------
# Title & intro
# --------------------------------------------------
st.title("🤖 GenAI Adoption Impact Dashboard")
st.write(
    "Use the filters in the sidebar to explore how enterprise GenAI adoption "
    "impacts productivity, training, and employees across industries."
)

# --------------------------------------------------
# KPI metrics
# --------------------------------------------------
c1, c2, c3 = st.columns(3)

with c1:
    st.metric("Companies", filtered_df["Company_Name"].nunique())

with c2:
    st.metric(
        "Avg Productivity Change (%)",
        f"{filtered_df['Productivity_Change'].mean():.1f}"
    )

with c3:
    st.metric(
        "Avg Training Hours",
        f"{filtered_df['Training_Hours'].mean():.0f}"
    )

st.markdown("---")

# --------------------------------------------------
# Chart 1 — Companies by GenAI Tool
# --------------------------------------------------
st.subheader("Companies Using Each GenAI Tool")

tool_counts = (
    filtered_df
    .groupby("GenAI_Tool")
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
    .properties(
        title="Companies Using Each GenAI Tool"   # <-- This forces a visible title
    )
)

st.altair_chart(chart_tools, use_container_width=True)


# --------------------------------------------------
# Chart 2 — Average productivity change by GenAI tool
# --------------------------------------------------
st.subheader("Average Productivity Change by GenAI Tool")

tool_productivity = (
    filtered_df
    .groupby("GenAI_Tool")["Productivity_Change"]
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
            alt.Tooltip("Productivity_Change:Q", format=".1f")
        ],
    )
)

st.altair_chart(chart_tool_productivity, use_container_width=True)

# --------------------------------------------------
# Chart 3 — Company-level Training Hours vs Productivity Change
# --------------------------------------------------
st.subheader("Company-level Training Hours vs Productivity Change")

scatter = (
    alt.Chart(filtered_df)
    .mark_circle(size=70, opacity=0.7)
    .encode(
        x=alt.X("Training_Hours:Q", title="Training Hours Provided"),
        y=alt.Y("Productivity_Change:Q", title="Productivity Change (%)"),
        color=alt.Color("GenAI_Tool:N", title="GenAI Tool"),
        tooltip=[
            "Company_Name",
            "Industry",
            "Country",
            "GenAI_Tool",
            "Training_Hours",
            "Productivity_Change",
        ],
    )
    .interactive()
)

st.altair_chart(scatter, use_container_width=True)

# --------------------------------------------------
# Raw data view
# --------------------------------------------------
with st.expander("Show raw data"):
    st.write(filtered_df)
