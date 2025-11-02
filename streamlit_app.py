import io
import logging
import streamlit as st

from config.settings import config
from services.riot_api import RiotAPIClient, RiotAPIError
from services.insights_engine import InsightsEngine
from services.visualizations import visualization_generator

st.set_page_config(page_title="LoL Analytics Agent", page_icon="🎮", layout="wide")
logger = logging.getLogger(__name__)

st.title("🎮 LoL Analytics Agent")
st.caption("AI-Powered player insights using Riot API and AWS Bedrock")

with st.sidebar:
    st.header("Settings")
    region = st.selectbox("Riot Region", ["americas", "europe", "asia", "sea"], index=["americas","europe","asia","sea"].index(config.RIOT_API_REGION))
    platform = st.text_input("Platform (e.g., na1, euw1)", value=config.RIOT_API_PLATFORM)
    max_matches = st.slider("Max Matches", min_value=10, max_value=200, value=min(100, config.MATCH_HISTORY_LIMIT), step=10)
    days_back = st.slider("Days Back", min_value=30, max_value=365, value=config.ANALYSIS_LOOKBACK_DAYS, step=15)
    st.markdown("---")
    st.markdown("Backend features:")
    st.checkbox("Bedrock enabled", value=config.ENABLE_BEDROCK, disabled=True)

st.subheader("Enter your Riot ID")
col1, col2, col3 = st.columns([4,2,2])
with col1:
    game_name = st.text_input("Game Name", placeholder="PlayerName")
with col2:
    tag_line = st.text_input("Tag Line", placeholder="NA1")
with col3:
    run_btn = st.button("Generate Insights", type="primary")

if run_btn:
    if not game_name or not tag_line:
        st.error("Please enter both Game Name and Tag Line")
        st.stop()

    try:
        client = RiotAPIClient(region=region, platform=platform)
        acct = client.get_summoner_by_riot_id(game_name, tag_line)
        puuid = acct.get("puuid")
        if not puuid:
            st.error("Failed to resolve player PUUID")
            st.stop()

        with st.spinner("Fetching match history and generating insights..."):
            matches = client.get_full_match_history(puuid, max_matches=max_matches, days_back=days_back)
            if not matches:
                st.warning("No match history found.")
                st.stop()
            engine = InsightsEngine()
            insights = engine.generate_comprehensive_insights(matches, puuid, f"{game_name}#{tag_line}")

        st.success("Insights generated!")

        # Overview metrics
        stats = insights.get("overall_stats", {})
        c1,c2,c3,c4 = st.columns(4)
        c1.metric("Win Rate", f"{stats.get('win_rate',0)}%", f"{stats.get('wins',0)}W/{stats.get('losses',0)}L")
        c2.metric("Avg KDA", f"{stats.get('avg_kda',0)}", f"{stats.get('avg_kills',0)}/{stats.get('avg_deaths',0)}/{stats.get('avg_assists',0)}")
        c3.metric("Games", f"{stats.get('total_games',0)}", f"{stats.get('total_time_played_hours',0)}h")
        c4.metric("Avg Damage", f"{stats.get('avg_damage_dealt',0)}", f"Max {stats.get('max_damage_dealt',0)}")

        # Strengths and weaknesses
        st.subheader("Strengths & Areas to Improve")
        s1,s2 = st.columns(2)
        with s1:
            strengths = insights.get("strengths", {})
            if strengths:
                for v in strengths.values():
                    st.success(f"{v.get('metric')}: {v.get('value')}\n\n{v.get('description')}")
            else:
                st.info("Keep playing to identify your strengths!")
        with s2:
            weaknesses = insights.get("weaknesses", {})
            if weaknesses:
                for v in weaknesses.values():
                    st.warning(f"{v.get('metric')}: {v.get('value')}\n\nTip: {v.get('suggestion')}")
            else:
                st.info("No major weaknesses identified! Keep it up!")

        # Coaching tips
        st.subheader("Coaching Tips")
        tips = insights.get("coaching_tips", [])
        if tips:
            for t in tips:
                st.write(f"- {t}")
        else:
            st.write("No specific tips at this time.")

        # Achievements
        st.subheader("Achievements")
        ach = insights.get("achievements", [])
        if ach:
            st.write(" ".join([(a.get('icon') or '⭐') + ' ' + a.get('title','') for a in ach]))
        else:
            st.write("Keep playing to unlock achievements!")

        # Year-end report button
        st.markdown("---")
        if st.button("Generate Year-End Report"):
            with st.spinner("Generating year-end report..."):
                report = InsightsEngine().generate_year_end_report(matches, puuid, f"{game_name}#{tag_line}")
            st.json(report)

        # Social card
        st.markdown("---")
        st.subheader("Social Media Card")
        img_bytes = visualization_generator.create_social_media_card(insights)
        st.image(img_bytes, caption="Shareable Stat Card", use_column_width=True)
        st.download_button("Download Card", data=io.BytesIO(img_bytes), file_name=f"lol-stats-{game_name}-{tag_line}.jpg", mime="image/jpeg")

    except RiotAPIError as e:
        st.error(f"Riot API error: {e}")
    except Exception as e:
        logger.exception("Unexpected error")
        st.error("An unexpected error occurred while generating insights.")
