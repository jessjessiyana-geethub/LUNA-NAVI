
import streamlit as st
from modules.solar import render_solar_analysis
from modules.landing_sites import render_landing_site_selection
from modules.comparison import run_mission_comparison
from modules.earth import render_earth_visibility
from modules.terrain_loader import get_terrain_file
from modules.visualization_3d import render_3d_lunar_visualization


# ==========================================
# PAGE CONFIGURATION
# ==========================================

st.set_page_config(
    page_title="LUNA-NAVI",
    page_icon="🌙",
    layout="wide"
)


# ==========================================
# DASHBOARD NAVIGATION
# ==========================================

page = render_dashboard()


# ==========================================
# MAIN DASHBOARD
# ==========================================

if page == "dashboard":

    solar_tab, earth_tab, comparison_tab, visual_tab = st.tabs([
        "☀️ Solar Analysis",
        "🌍 Earth Visibility",
        "📊 Mission Comparison",
        "🌕 3D Lunar Visualization"
    ])

    with solar_tab:
        st.header("Solar Position Analysis")
        st.info(
            "Ethan's solar calculation module will appear here."
        )

    with earth_tab:
        st.header("Earth Visibility Analysis")
        st.info(
            "Irven's communication analysis will appear here."
        )

    with comparison_tab:
        st.header("Mission Comparison")
        st.info(
            "Chiew's landing site comparison will appear here."
        )

    with visual_tab:
        st.header("3D Lunar Visualization")
        st.info(
            "Davin's lunar visualization will appear here."
        )

    st.divider()

    st.warning(
        "Development version: Scientific calculations are "
        "not yet connected to validated NASA data."
    )


# ==========================================
# LANDING SITE SELECTION
# ==========================================

elif page == "landing_sites":

    st.button(
        "← Back to Dashboard",
        on_click=lambda: st.session_state.update(
            {"luna_navi_page": "dashboard"}
        )
    )

    st.title("🌙 Landing Site Selection")

    scenario = render_landing_site_selection()

    if scenario is not None:

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

    render_3d_lunar_visualization(scenario)

st.divider()

st.info(
    "First comparison against the saved JPL Horizons reference case "
    "completed successfully. Further test cases are required for "
    "independent validation."
)
