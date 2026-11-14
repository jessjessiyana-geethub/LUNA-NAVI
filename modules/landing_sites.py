
import streamlit as st
import math

from dataclasses import dataclass
from datetime import date, datetime, time, timezone


# =====================================================
# 1. NASA LUNAR SOUTH POLE SITE CATALOGUE
# =====================================================

SOUTH_POLE_SITES = {
    "Site01 — Connecting Ridge": {
        "code": "Site01",
        "name": "Connecting Ridge",
        "latitude": -89.4632,
        "longitude": -137.49
    },
    "Site04 — Shackleton Rim": {
        "code": "Site04",
        "name": "Shackleton Rim",
        "latitude": -89.7668,
        "longitude": -171.87
    },
    "Site06 — Nobile Rim 1": {
        "code": "Site06",
        "name": "Nobile Rim 1",
        "latitude": -85.4381,
        "longitude": 37.36667
    },
    "Site07 — Peak Near Shackleton": {
        "code": "Site07",
        "name": "Peak Near Shackleton",
        "latitude": -88.8110,
        "longitude": 123.6901
    },
    "Site11 — de Gerlache Rim 1": {
        "code": "Site11",
        "name": "de Gerlache Rim 1",
        "latitude": -88.6834,
        "longitude": -67.9321
    },
    "Site20 — Leibnitz Beta Plateau": {
        "code": "Site20",
        "name": "Leibnitz Beta Plateau",
        "latitude": -85.4266,
        "longitude": 31.74276
    },
    "Site20v2 — Leibnitz Beta Plateau Extended": {
        "code": "Site20v2",
        "name": "Leibnitz Beta Plateau Extended",
        "latitude": -85.4266,
        "longitude": 31.74276
    },
    "Site23 — Malapert Massif": {
        "code": "Site23",
        "name": "Malapert Massif",
        "latitude": -85.9948,
        "longitude": -0.23578
    },
    "Site42 — de Gerlache-Kocher Massif": {
        "code": "Site42",
        "name": "de Gerlache-Kocher Massif",
        "latitude": -85.8296,
        "longitude": -116.322
    },
    "NPA — Cabeus Exterior Wall 1": {
        "code": "NPA",
        "name": "Cabeus Exterior Wall 1",
        "latitude": -86.9243,
        "longitude": -71.5651
    },
    "NPB — Amundsen 1": {
        "code": "NPB",
        "name": "Amundsen 1",
        "latitude": -83.9046,
        "longitude": 89.53545
    },
    "NPC — Idelson L Crater 1": {
        "code": "NPC",
        "name": "Idelson L Crater 1",
        "latitude": -84.5397,
        "longitude": 126.9045
    },
    "NPD — Malapert Crater 1": {
        "code": "NPD",
        "name": "Malapert Crater 1",
        "latitude": -84.8034,
        "longitude": 8.387032
    },
    "Shoemaker": {
        "code": "Shoemaker",
        "name": "Shoemaker",
        "latitude": -87.1835,
        "longitude": 62.83502
    },
    "SL2 — de Gerlache Rim 2": {
        "code": "SL2",
        "name": "de Gerlache Rim 2",
        "latitude": -88.2300,
        "longitude": -64.6284
    },
    "SL3 — Connecting Ridge Extension": {
        "code": "SL3",
        "name": "Connecting Ridge Extension",
        "latitude": -89.0324,
        "longitude": -101.999
    },
    "LM8 — Shoemaker Rim F": {
        "code": "LM8",
        "name": "Shoemaker Rim F",
        "latitude": -87.3417,
        "longitude": 60.25512
    }
}


# =====================================================
# 2. LANDING SCENARIO DATA MODEL
# =====================================================

@dataclass
class LandingScenario:
    site_code: str
    site_name: str
    latitude: float
    longitude: float
    datetime_utc: datetime


# =====================================================
# 3. VALIDATION FUNCTIONS
# =====================================================

def validate_site_name(site_name):

    errors = []

    if not site_name or not site_name.strip():
        errors.append("Landing-site name cannot be empty.")

    elif len(site_name.strip()) < 2:
        errors.append("Site name must contain at least 2 characters.")

    elif len(site_name.strip()) > 80:
        errors.append("Site name cannot exceed 80 characters.")

    return errors


def validate_latitude(latitude):

    errors = []

    try:
        value = float(latitude)
        valid = math.isfinite(value)
    except (TypeError, ValueError):
        valid = False
        value = 0

    if not valid:
        errors.append("Invalid latitude.")

    elif not -90 <= value <= -83:
        errors.append(
            "Latitude must be within the south-polar region."
        )

    return errors


def validate_longitude(longitude):

    errors = []

    try:
        value = float(longitude)
        valid = math.isfinite(value)
    except (TypeError, ValueError):
        valid = False
        value = 0

    if not valid:
        errors.append("Invalid longitude.")

    elif not -180 <= value <= 180:
        errors.append(
            "Longitude must be between -180° and +180°."
        )

    return errors


def validate_landing_site(site_name, latitude, longitude):

    errors = []

    errors.extend(validate_site_name(site_name))
    errors.extend(validate_latitude(latitude))
    errors.extend(validate_longitude(longitude))

    return errors


# =====================================================
# 4. CREATE UTC DATETIME
# =====================================================

def create_landing_datetime(landing_date, landing_time):

    return datetime.combine(
        landing_date,
        landing_time
    ).replace(tzinfo=timezone.utc)


# =====================================================
# 5. CREATE LANDING SCENARIO
# =====================================================

def create_landing_scenario(site, landing_date, landing_time):

    return LandingScenario(
        site_code=site["code"],
        site_name=site["name"],
        latitude=float(site["latitude"]),
        longitude=float(site["longitude"]),
        datetime_utc=create_landing_datetime(
            landing_date,
            landing_time
        )
    )


# =====================================================
# 6. MAIN LANDING SITE SELECTION FORM
# =====================================================

def render_landing_site_selection():

    st.title("🌙 Landing Site Selection")

    st.write(
        "Select a lunar south-pole landing-site feature "
        "and enter the planned landing schedule."
    )

    st.caption(
        "LUNA-NAVI | Lunar Landing Site Navigator"
    )

    st.divider()

    if "landing_scenario" not in st.session_state:
        st.session_state["landing_scenario"] = None

    site_labels = list(SOUTH_POLE_SITES.keys())

    # -------------------------------
    # INPUT FORM
    # -------------------------------

    with st.form("luna_landing_site_form"):

        st.subheader("1. South Pole Landing Site")

        selected_label = st.selectbox(
            "Select Landing Site",
            site_labels,
            index=1
        )

        selected_site = SOUTH_POLE_SITES[selected_label]

        st.text_input(
            "Site Code",
            value=selected_site["code"],
            disabled=True
        )

        st.text_input(
            "Landing-Site Name",
            value=selected_site["name"],
            disabled=True
        )

        st.subheader("2. Lunar Coordinates")

        col1, col2 = st.columns(2)

        with col1:
            st.number_input(
                "Latitude (°)",
                value=float(selected_site["latitude"]),
                format="%.5f",
                disabled=True
            )

        with col2:
            st.number_input(
                "Longitude (°)",
                value=float(selected_site["longitude"]),
                format="%.5f",
                disabled=True
            )

        st.caption(
            "South and west coordinates are negative."
        )

        st.divider()

        st.subheader("3. Landing Schedule")

        col3, col4 = st.columns(2)

        with col3:
            landing_date = st.date_input(
                "Landing Date",
                value=date.today(),
                format="DD/MM/YYYY"
            )

        with col4:
            landing_time = st.time_input(
                "Landing Time (UTC)",
                value=time(0, 0),
                step=60
            )

        submitted = st.form_submit_button(
            "🚀 Submit Landing Site",
            use_container_width=True
        )

    # -------------------------------
    # PROCESS SUBMISSION
    # -------------------------------

    if submitted:

        errors = validate_landing_site(
            selected_site["name"],
            selected_site["latitude"],
            selected_site["longitude"]
        )

        if errors:

            st.session_state["landing_scenario"] = None

            st.error("Please correct the following errors:")

            for error in errors:
                st.warning(error)

            return None

        scenario = create_landing_scenario(
            selected_site,
            landing_date,
            landing_time
        )

        st.session_state["landing_scenario"] = scenario

    # -------------------------------
    # DISPLAY RESULT
    # -------------------------------

    scenario = st.session_state["landing_scenario"]

    if scenario is None:

        st.info(
            "Select a landing site and submit the form."
        )

        return None

    st.success(
        "Landing-site information submitted successfully!"
    )

    st.subheader("Selected Landing Site")

    col1, col2, col3 = st.columns(3)

    col1.metric(
        "Site",
        scenario.site_name
    )

    col2.metric(
        "Latitude",
        f"{scenario.latitude:.5f}°"
    )

    col3.metric(
        "Longitude",
        f"{scenario.longitude:.5f}°"
    )

    st.write(
        "Landing Date and Time (UTC):",
        scenario.datetime_utc.strftime(
            "%d %B %Y, %H:%M UTC"
        )
    )

    with st.expander("Data Source and Information"):

        st.write(
            "NASA Lunar Surface Data Book, ACD-50044 Rev A, "
            "Appendix A, Table A2-2."
        )

        st.warning(
            "Reference feature coordinates are not certified "
            "landing points or proof of landing safety."
        )

    return scenario


# =====================================================
# END OF LANDING SITE SELECTION MODULE
# =====================================================

