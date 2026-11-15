
import streamlit as st

from modules.dashboard import render_dashboard
from modules.landing_sites import render_landing_site_selection
from modules.solar import render_solar_analysis
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
# SESSION STATE
# ==========================================

if "scenario" not in st.session_state:
    st.session_state["scenario"] = None


# ==========================================
# DASHBOARD NAVIGATION
# ==========================================

page = render_dashboard()

scenario = st.session_state["scenario"]


# ==========================================
# MAIN DASHBOARD
# ==========================================

if page == "dashboard":

    st.title("LUNA-NAVI Mission Dashboard")

    if scenario is not None:
        st.success(f"Selected Landing Site: {scenario.site_name}")
    else:
        st.warning(
            "Please select and confirm a landing site "
            "before running mission analysis."
        )

    solar_tab, earth_tab, comparison_tab, visual_tab = st.tabs([
        "☀️ Solar Analysis",
        "🌍 Earth Visibility",
        "📊 Mission Comparison",
        "🌕 3D Lunar Visualization"
    ])

    # ======================================
    # SOLAR ANALYSIS
    # ======================================

    with solar_tab:
        st.header("Solar Position Analysis")

        if scenario is not None:
            render_solar_analysis(scenario)
        else:
            st.info(
                "Please select a landing site "
                "before starting Solar Analysis."
            )

    # ======================================
    # EARTH VISIBILITY
    # ======================================

    with earth_tab:
        st.header("Earth Visibility Analysis")

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
                "Please select a landing site "
                "before starting Earth Visibility Analysis."
            )

    # ======================================
    # MISSION COMPARISON
    # ======================================

    with comparison_tab:
        st.header("Mission Comparison")

        if scenario is not None:
            run_mission_comparison(scenario)
        else:
            st.info(
                "Please select a landing site "
                "before starting Mission Comparison."
            )

    # ======================================
    # 3D LUNAR VISUALIZATION
    # ======================================

    with visual_tab:
        st.header("3D Lunar Visualization")

        if scenario is not None:
            render_3d_lunar_visualization(scenario)
        else:
            st.info(
                "Please select a landing site "
                "before starting 3D Visualization."
            )

    st.divider()

    st.info(
        "First comparison against the saved JPL Horizons "
        "reference case completed successfully. "
        "Further test cases are required for "
        "independent validation."
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

    selected_scenario = render_landing_site_selection()

    if selected_scenario is not None:
        st.session_state["scenario"] = selected_scenario
        st.success(
            f"Landing site confirmed: "
            f"{selected_scenario.site_name}"
        )

else:
    st.warning("Unknown dashboard page selected.")
