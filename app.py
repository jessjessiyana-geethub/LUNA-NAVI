
import streamlit as st

st.set_page_config(
    page_title="LUNA NAV",
    page_icon="🌙",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Application header
st.title("🌙 LUNA NAV")
st.subheader("Lunar Landing Site Navigator")

st.markdown("""
Welcome to LUNA NAV.

An interactive mission-planning application
for lunar south pole landing site assessment.
""")

st.divider()

st.header("Mission Overview")

col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Analysis Modules", "5")

with col2:
    st.metric("Candidate Sites", "3")

with col3:
    st.metric("Mission Status", "Ready")

st.info(
    "Select an analysis section from the sidebar "
    "to begin exploring the mission."
)

st.caption(
    "LUNA NAV | NASA Space Apps Challenge 2026"
)
