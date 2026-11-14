
import streamlit as st
from datetime import datetime, timezone
from utils.data_models import LandingScenario


def render_landing_site_selection():
    st.sidebar.header("🌙 Landing Site Selection")

    site_name = st.sidebar.text_input(
        "Landing Site Name",
        value="Candidate A"
    )

    latitude = st.sidebar.number_input(
        "Latitude (°)",
        min_value=-90.0,
        max_value=90.0,
        value=-89.5,
        step=0.1
    )

    longitude = st.sidebar.number_input(
        "Longitude (°)",
        min_value=-180.0,
        max_value=180.0,
        value=30.0,
        step=0.1
    )

    landing_date = st.sidebar.date_input(
        "Landing Date"
    )

    landing_time = st.sidebar.time_input(
        "Landing Time (UTC)"
    )

    selected_datetime = datetime.combine(
        landing_date,
        landing_time,
        tzinfo=timezone.utc
    )

    return LandingScenario(
        site_name=site_name,
        latitude=latitude,
        longitude=longitude,
        datetime_utc=selected_datetime
    )
