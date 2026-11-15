
import streamlit as st
from datetime import datetime


# ==========================================
# LUNA-NAVI DASHBOARD
# Lunar Landing Site Navigator
# ==========================================

def navigate_to(page):
    """Save the selected page for app.py navigation."""
    st.session_state["luna_navi_page"] = page


def render_dashboard():

    # --------------------------------------
    # PAGE CONFIGURATION / SESSION STATE
    # --------------------------------------

    if "luna_navi_page" not in st.session_state:
        st.session_state["luna_navi_page"] = "dashboard"

    # --------------------------------------
    # CUSTOM NASA-INSPIRED DESIGN
    # --------------------------------------

    st.markdown("""
        <style>
        .stApp {
            background-color: #080E1B;
            color: #E8F0FF;
        }

        .block-container {
            padding-top: 2rem;
            padding-bottom: 3rem;
            max-width: 1250px;
        }

        .hero {
            background: linear-gradient(120deg, #101F3D, #173B68, #091426);
            padding: 35px;
            border-radius: 18px;
            border: 1px solid #294B75;
            margin-bottom: 25px;
        }

        .hero h1 {
            color: #FFFFFF;
            font-size: 42px;
            margin-bottom: 5px;
        }

        .hero p {
            color: #B8CCE8;
            font-size: 16px;
        }

        .section-title {
            color: #80BFFF;
            font-size: 23px;
            font-weight: bold;
            margin-top: 25px;
            margin-bottom: 15px;
        }

        .metric-card {
            background: #111D32;
            border: 1px solid #263E5D;
            border-radius: 13px;
            padding: 20px;
            min-height: 125px;
        }

        .metric-label {
            color: #A9BCD5;
            font-size: 14px;
        }

        .metric-value {
            color: #FFFFFF;
            font-size: 30px;
            font-weight: bold;
            margin-top: 8px;
        }

        .metric-description {
            color: #80BFFF;
            font-size: 12px;
        }

        .module-card {
            background: #111D32;
            border: 1px solid #263E5D;
            border-radius: 13px;
            padding: 18px;
            min-height: 130px;
        }

        .module-card h3 {
            color: #FFFFFF;
            font-size: 18px;
        }

        .module-card p {
            color: #A9BCD5;
            font-size: 13px;
        }

        .info-card {
            background: #111D32;
            border-left: 4px solid #398BDB;
            padding: 18px;
            border-radius: 8px;
            color: #D6E5F8;
        }

        div.stButton > button {
            width: 100%;
            border-radius: 8px;
            border: 1px solid #367FC4;
            background-color: #173B68;
            color: white;
            font-weight: bold;
            min-height: 42px;
        }

        div.stButton > button:hover {
            background-color: #2866A5;
            border-color: #80BFFF;
            color: white;
        }

        </style>
    """, unsafe_allow_html=True)

    # --------------------------------------
    # HERO SECTION
    # --------------------------------------

    st.markdown("""
        <div class="hero">
            <h1>🌙 LUNA-NAVI</h1>
            <p>LUNAR LANDING SITE NAVIGATOR</p>
            <p>
                Explore, evaluate and compare potential lunar
                landing locations for future Moon missions.
            </p>
        </div>
    """, unsafe_allow_html=True)

    # --------------------------------------
    # DATE AND TIME
    # --------------------------------------

    current_time = datetime.now().strftime("%d %B %Y")

    st.caption(f"MISSION CONTROL  |  {current_time}")

    # --------------------------------------
    # MISSION OVERVIEW
    # --------------------------------------

    st.markdown(
        '<div class="section-title">MISSION OVERVIEW</div>',
        unsafe_allow_html=True
    )

    metric_columns = st.columns(4)

    metrics = [
        ("17", "LANDING SITES", "Candidate site catalogue"),
        ("6", "PROJECT MODULES", "Main system components"),
        ("1", "MISSION REGION", "Lunar South Pole"),
        ("NASA", "DATA SOURCE", "NASA lunar datasets")
    ]

    for column, metric in zip(metric_columns, metrics):
        value, label, description = metric

        with column:
            st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-label">{label}</div>
                    <div class="metric-value">{value}</div>
                    <div class="metric-description">{description}</div>
                </div>
            """, unsafe_allow_html=True)

    # --------------------------------------
    # MISSION OBJECTIVE
    # --------------------------------------

    st.markdown(
        '<div class="section-title">MISSION OBJECTIVE</div>',
        unsafe_allow_html=True
    )

    st.markdown("""
        <div class="info-card">
            <b>Our Mission</b><br><br>
            LUNA-NAVI is designed to support lunar landing site
            exploration and mission planning by providing tools
            to examine potential landing locations, solar
            conditions, terrain information and mission scoring.
            <br><br>
            The system focuses on the Lunar South Pole, an
            important region for future lunar exploration.
        </div>
    """, unsafe_allow_html=True)

    # --------------------------------------
    # MAIN MODULE NAVIGATION
    # --------------------------------------

    st.markdown(
        '<div class="section-title">MISSION CONTROL MODULES</div>',
        unsafe_allow_html=True
    )

    modules = [
        {
            "name": "Earth Data",
            "icon": "🌍",
            "description": "Explore Earth-related data and information.",
            "page": "earth"
        },
        {
            "name": "Landing Site Selection",
            "icon": "🌙",
            "description": "Select and examine potential lunar landing sites.",
            "page": "landing_sites"
        },
        {
            "name": "Solar Analysis",
            "icon": "☀️",
            "description": "Explore solar energy and sunlight conditions.",
            "page": "solar"
        },
        {
            "name": "Mission Comparison",
            "icon": "🛰️",
            "description": "Compare different lunar mission scenarios.",
            "page": "comparison"
        },
        {
            "name": "Mission Scoring",
            "icon": "📊",
            "description": "Evaluate and rank potential landing sites.",
            "page": "mission_scoring"
        },
        {
            "name": "3D Visualization",
            "icon": "🗺️",
            "description": "Visualize lunar terrain in three dimensions.",
            "page": "visualization_3d"
        }
    ]

    for row_start in range(0, len(modules), 3):

        columns = st.columns(3)

        for column, module in zip(
            columns,
            modules[row_start:row_start + 3]
        ):

            with column:

                st.markdown(f"""
                    <div class="module-card">
                        <h3>{module['icon']} {module['name']}</h3>
                        <p>{module['description']}</p>
                    </div>
                """, unsafe_allow_html=True)

                st.button(
                    f"Open {module['name']}",
                    key=f"open_{module['page']}",
                    on_click=navigate_to,
                    args=(module["page"],)
                )

    # --------------------------------------
    # QUICK INFORMATION
    # --------------------------------------

    st.markdown(
        '<div class="section-title">LUNAR SOUTH POLE</div>',
        unsafe_allow_html=True
    )

    left, right = st.columns(2)

    with left:
        st.markdown("""
            <div class="info-card">
                <b>Why the Lunar South Pole?</b><br><br>
                • Potential water ice resources<br>
                • Areas with extended sunlight<br>
                • Opportunities for scientific research<br>
                • Supports future lunar exploration
            </div>
        """, unsafe_allow_html=True)

    with right:
        st.markdown("""
            <div class="info-card">
                <b>Mission Planning Factors</b><br><br>
                • Landing site location<br>
                • Terrain and surface slope<br>
                • Solar illumination<br>
                • Mission suitability and safety
            </div>
        """, unsafe_allow_html=True)

    # --------------------------------------
    # FOOTER
    # --------------------------------------

    st.divider()

    st.markdown("""
        <div style="text-align:center; color:#8298B5;
                    font-size:12px;">
            LUNA-NAVI | LUNAR LANDING SITE NAVIGATOR<br>
            Designed for Lunar Exploration and Mission Planning
        </div>
    """, unsafe_allow_html=True)

    # --------------------------------------
    # RETURN SELECTED PAGE TO APP.PY
    # --------------------------------------

    return st.session_state["luna_navi_page"]
