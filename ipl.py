import streamlit as st
st.set_page_config(page_title="IPL Super Dashboard", layout="wide")

import pandas as pd
import plotly.express as px
import warnings
warnings.filterwarnings('ignore')
from imports import *


MATCHES_FILE = "matches.csv"
DELIVERIES_FILE = "deliveries.csv"


@st.cache_data
def load_data():
    matches = pd.read_csv(MATCHES_FILE)
    deliveries = pd.read_csv(DELIVERIES_FILE)
    return matches, deliveries

matches, deliveries = load_data()


st.title(" IPL Cricket Data Visualization ")
seasons = sorted(matches["season"].dropna().unique())
teams = sorted(set(matches["team1"].dropna().unique()) | set(matches["team2"].dropna().unique()))
venues = sorted(matches["venue"].dropna().unique())
cities = sorted(matches["city"].dropna().unique())

selected_season = st.sidebar.selectbox("Select Season", seasons)
selected_team = st.sidebar.selectbox("Select Team", ["All"] + teams)
selected_city = st.sidebar.selectbox("Select City", ["All"] + cities)
selected_venue = st.sidebar.selectbox("Select Venue", ["All"] + venues)


filtered_matches = matches[matches["season"] == selected_season]
if selected_team != "All":
    filtered_matches = filtered_matches[
        (filtered_matches["team1"] == selected_team) | (filtered_matches["team2"] == selected_team)
    ]
if selected_city != "All":
    filtered_matches = filtered_matches[filtered_matches["city"] == selected_city]
if selected_venue != "All":
    filtered_matches = filtered_matches[filtered_matches["venue"] == selected_venue]

if filtered_matches.empty:
    st.warning(" No matches found.")
    st.stop()

match_ids = filtered_matches["id"].unique()
filtered_deliveries = deliveries[deliveries["match_id"].isin(match_ids)]

st.subheader(" Match Summary")
total_matches = len(filtered_matches)
total_runs = filtered_deliveries["total_runs"].sum()
total_wickets = filtered_deliveries["player_dismissed"].dropna().shape[0]

col1, col2, col3 = st.columns(3)
col1.metric("Total Matches", total_matches)
col2.metric("Total Runs", int(total_runs))
col3.metric("Total Wickets", int(total_wickets))


top_batsmen = (
    filtered_deliveries.groupby("batter")["batsman_runs"]
    .sum()
    .reset_index()
    .sort_values(by="batsman_runs", ascending=False)
    .head(10)
)

bowler_wickets = filtered_deliveries[filtered_deliveries["player_dismissed"].notna()]
top_bowlers = (
    bowler_wickets.groupby("bowler")["player_dismissed"]
    .count()
    .reset_index()
    .rename(columns={"player_dismissed": "wickets"})
    .sort_values(by="wickets", ascending=False)
    .head(10)
)

run_rate = (
    filtered_deliveries.groupby("over")["total_runs"]
    .sum()
    .reset_index()
    .sort_values("over")
)
run_rate = run_rate[run_rate["over"] <= 20]
st.subheader(" Visual Insights")
c1, c2 = st.columns(2)

with c1:
    st.markdown("###  Top 10 Batsmen")
    if not top_batsmen.empty:
        fig = px.bar(top_batsmen, x="batter", y="batsman_runs", color="batter", title="Top 10 Run Scorers")
        st.plotly_chart(fig, use_container_width=True)
        st.download_button("⬇ Download Top Batsmen CSV", top_batsmen.to_csv(index=False), "top_batsmen.csv")
    else:
        st.info("No batsman data found.")

with c2:
    st.markdown("### Top 10 Bowlers")
    if not top_bowlers.empty:
        fig = px.bar(top_bowlers, x="bowler", y="wickets", color="bowler", title="Top 10 Wicket Takers")
        st.plotly_chart(fig, use_container_width=True)
        st.download_button("⬇ Download Top Bowlers CSV", top_bowlers.to_csv(index=False), "top_bowlers.csv")
    else:
        st.info("No bowler data found.")
st.subheader("Run Rate Progression")
if not run_rate.empty:
    fig = px.line(run_rate, x="over", y="total_runs", markers=True, title="Run Rate per Over")
    st.plotly_chart(fig, use_container_width=True)
else:
    st.info("No run rate data available.")
st.markdown("---")
st.caption("Data: matches.csv & deliveries.csv |")
