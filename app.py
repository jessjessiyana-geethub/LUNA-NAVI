
import streamlit as st

from modules.dashboard import render_dashboard
from modules.landing_sites import render_landing_site_selection


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

        st.divider()
        st.header("Selected Landing Site")

        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric("Site", scenario.site_name)

        with col2:
            st.metric(
                "Latitude",
                f"{scenario.latitude:.2f}°"
            )

        with col3:
            st.metric(
                "Longitude",
                f"{scenario.longitude:.2f}°"
            )

        st.write(
            "Selected landing time (UTC):",
            scenario.datetime_utc.strftime(
                "%Y-%m-%d %H:%M"
            )
        )

    else:
        st.info(
            "Please select a landing site and submit the form."
        )


# ==========================================
# OTHER MODULE PAGES
# ==========================================

elif page == "earth":

    st.button(
        "← Back to Dashboard",
        on_click=lambda: st.session_state.update(
            {"luna_navi_page": "dashboard"}
        )
    )

    st.title("🌍 Earth Visibility")
    st.info("Earth visibility module will appear here.")


elif page == "solar":

    st.button(
        "← Back to Dashboard",
        on_click=lambda: st.session_state.update(
            {"luna_navi_page": "dashboard"}
        )
    )

    st.title("☀️ Solar Analysis")
    st.info("Solar analysis module will appear here.")


elif page == "comparison":

    st.button(
        "← Back to Dashboard",
        on_click=lambda: st.session_state.update(
            {"luna_navi_page": "dashboard"}
        )
    )

    st.title("📊 Mission Comparison")
    st.info("Mission comparison module will appear here.")


elif page == "mission_scoring":

    st.button(
        "← Back to Dashboard",
        on_click=lambda: st.session_state.update(
            {"luna_navi_page": "dashboard"}
        )
    )

    st.title("📈 Mission Scoring")
    st.info("Mission scoring module will appear here.")


elif page == "visualization_3d":

    st.button(
        "← Back to Dashboard",
        on_click=lambda: st.session_state.update(
            {"luna_navi_page": "dashboard"}
        )
    )

    st.title("🌕 3D Lunar Visualization")
    st.info("3D visualization module will appear here.")


# ==========================================
# FOOTER
# ==========================================

st.divider()

st.caption(
    "LUNA-NAVI | NASA Space Apps Challenge"
)
