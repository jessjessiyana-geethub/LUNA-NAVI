
import streamlit as st
from modules.solar import render_solar_analysis
from modules.landing_sites import render_landing_site_selection

st.set_page_config(
    page_title="LUNA-NAVI",
    page_icon="🌙",
    layout="wide"
)

st.title("🌙 LUNA-NAVI")
st.subheader("Lunar Landing Site Navigator")

st.caption(
    "NASA Space Apps Challenge | "
    "Lunar landing site planning application"
)

scenario = render_landing_site_selection()

st.divider()
st.header("Selected Landing Site")

col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Site", scenario.site_name)

with col2:
    st.metric("Latitude", f"{scenario.latitude:.2f}°")

with col3:
    st.metric("Longitude", f"{scenario.longitude:.2f}°")

st.write(
    "Selected landing time (UTC):",
    scenario.datetime_utc.strftime("%Y-%m-%d %H:%M")
)

solar_tab, earth_tab, comparison_tab, visual_tab = st.tabs([
    "☀️ Solar Analysis",
    "🌍 Earth Visibility",
    "📊 Mission Comparison",
    "🌕 3D Lunar Visualization"
])

with solar_tab:
     render_solar_analysis(scenario)

with earth_tab:
    st.header("Earth Visibility Analysis")
    st.info("Irven's communication analysis will appear here.")

with comparison_tab:
    st.header("Mission Comparison")
    st.info("Chiew's landing site comparison will appear here.")

with visual_tab:
    st.header("3D Lunar Visualization")
    st.info("Davin's lunar visualization will appear here.")

st.divider()

st.warning(
    "Scientific validation status: Solar calculations use JPL DE440s "
    "and NAIF lunar-orientation kernels. Independent comparison against "
    "JPL Horizons is still pending."
)
