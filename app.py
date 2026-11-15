
import streamlit as st
from modules.solar import render_solar_analysis
from modules.landing_sites import render_landing_site_selection
from modules.comparison import run_mission_comparison
from modules.earth import render_earth_visibility
from modules.terrain_loader import get_terrain_file

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


if scenario is not None:

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

else:
    st.info("Please select a landing site and submit the form.")


solar_tab, earth_tab, comparison_tab, visual_tab = st.tabs([
    "☀️ Solar Analysis",
    "🌍 Earth Visibility",
    "📊 Mission Comparison",
    "🌕 3D Lunar Visualization"
])

with solar_tab:
    if scenario is not None:
        render_solar_analysis(scenario)
    else:
        st.warning(
            "Please select and confirm a landing site "
            "before running Solar Analysis."
        )

with earth_tab:
    if scenario is not None:

        st.write("Selected Site:", scenario.site_name)
        st.write("Site Code:", scenario.site_code)

        terrain_file = get_terrain_file(scenario)

        if terrain_file is not None:
            st.success(
                f"Terrain file found: {terrain_file.name}"
            )
        else:
            st.warning(
                "No processed NASA terrain profile "
                "is available for this site yet."
            )

        render_earth_visibility(scenario)

    else:
        st.info(
            "Please select and submit a landing site "
            "before starting Earth Visibility Analysis."
        )

with comparison_tab:
    if scenario is not None:
        run_mission_comparison(scenario)
    else:
        st.info(
            "Please select and submit a landing site "
            "before starting Mission Comparison."
        )

with visual_tab:
    st.header("3D Lunar Visualization")
    st.info("Davin's lunar visualization will appear here.")

st.divider()

st.info(
    "First comparison against the saved JPL Horizons reference case "
    "completed successfully. Further test cases are required for "
    "independent validation."
)

