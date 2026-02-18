import pandas as pd
import streamlit as st

st.set_page_config(page_title="Internship Tracker", layout="wide")
st.title("Engineering Internship Tracker")

# Load data
try:
    df = pd.read_csv("jobs.csv")
except FileNotFoundError:
    st.error("jobs.csv not found. Run your scraper first.")
    st.stop()

# Basic cleanup
for col in ["source", "company", "title", "location", "url", "updated_at"]:
    if col not in df.columns:
        st.error(f"Missing column in jobs.csv: {col}")
        st.stop()

df = df.fillna("")

# Sidebar filters
st.sidebar.header("Filters")

source_choice = st.sidebar.multiselect(
    "Source",
    options=sorted(df["source"].unique()),
    default=sorted(df["source"].unique())
)

company_search = st.sidebar.text_input("Company contains", "")
title_search = st.sidebar.text_input("Title contains", "")
location_search = st.sidebar.text_input("Location contains", "")

# Apply filters
filtered = df[df["source"].isin(source_choice)].copy()

if company_search.strip():
    filtered = filtered[filtered["company"].str.contains(company_search, case=False, na=False)]

if title_search.strip():
    filtered = filtered[filtered["title"].str.contains(title_search, case=False, na=False)]

if location_search.strip():
    filtered = filtered[filtered["location"].str.contains(location_search, case=False, na=False)]

st.write(f"Showing **{len(filtered)}** jobs")

# Make URLs clickable
def make_clickable(url):
    return f'<a href="{url}" target="_blank">Apply</a>'

filtered_display = filtered.copy()
filtered_display["apply"] = filtered_display["url"].apply(make_clickable)
filtered_display = filtered_display.drop(columns=["url"])

# Show table
st.dataframe(
    filtered,
    column_config={
        "url": st.column_config.LinkColumn(
            "Apply",
            display_text="Open"
        )
    },
    hide_index=True,
    use_container_width=True
)


# Download button
st.download_button(
    label="Download filtered CSV",
    data=filtered.to_csv(index=False).encode("utf-8"),
    file_name="filtered_jobs.csv",
    mime="text/csv"
)
