
"""
LUNA-NAVI
EARTH VISIBILITY ANALYSIS (EVA)
Version 2.0 - NASA Horizons Integration

Features:
1. NASA JPL Horizons API
2. Lunar surface observer geometry
3. Earth azimuth and elevation
4. Terrain obstruction analysis
5. Earth visibility classification
6. Mission visibility timeline
7. Interactive charts and data export

NASA Horizons API:
https://ssd-api.jpl.nasa.gov/api/horizons.api
"""

import math
import csv
import io
import requests
import numpy as np
import pandas as pd
import streamlit as st
import plotly.graph_objects as go

from datetime import timedelta


# ==================================================
# 1. SCIENTIFIC CONSTANTS
# ==================================================

MOON_RADIUS_KM = 1737.4
EARTH_RADIUS_KM = 6371.0

HORIZONS_API = (
    "https://ssd.jpl.nasa.gov/api/horizons.api"
)


# ==================================================
# 2. VECTOR UTILITIES
# ==================================================

def normalize_vector(vector):

    vector = np.asarray(vector, dtype=float)

    magnitude = np.linalg.norm(vector)

    if magnitude == 0:
        raise ValueError("Invalid zero-length vector.")

    return vector / magnitude


# ==================================================
# 3. LUNAR OBSERVER POSITION
# ==================================================

def calculate_observer_position(
    latitude,
    longitude,
    altitude_km=0.0
):
    """
    Approximate spherical Moon-fixed observer position.

    Latitude: planetocentric degrees.
    Longitude: east longitude in degrees.
    Altitude: kilometres above mean lunar radius.
    """

    lat = math.radians(latitude)
    lon = math.radians(longitude)

    radius = MOON_RADIUS_KM + altitude_km

    x = radius * math.cos(lat) * math.cos(lon)
    y = radius * math.cos(lat) * math.sin(lon)
    z = radius * math.sin(lat)

    return np.array([x, y, z])


# ==================================================
# 4. NASA HORIZONS API
# ==================================================

def get_horizons_earth_visibility(
    latitude,
    longitude,
    altitude_km,
    observation_time,
    duration_hours=24,
    step_hours=1
):
    """
    Retrieve Earth apparent azimuth and elevation
    from a specified lunar surface location.

    Horizons observer:
        coord@301 = user-defined location on Moon

    Target:
        399 = Earth centre

    Coordinates:
        East longitude, latitude, altitude (km)
    """

    start_time = observation_time
    stop_time = (
        observation_time
        + timedelta(hours=duration_hours)
    )

    params = {
        "format": "json",
        "COMMAND": "'399'",
        "OBJ_DATA": "'NO'",
        "MAKE_EPHEM": "'YES'",
        "EPHEM_TYPE": "'OBSERVER'",
        "CENTER": "'coord@301'",
        "COORD_TYPE": "'GEODETIC'",
        "SITE_COORD": (
            f"'{longitude},{latitude},{altitude_km}'"
        ),
        "START_TIME": (
            f"'{start_time.strftime('%Y-%m-%d %H:%M')}'"
        ),
        "STOP_TIME": (
            f"'{stop_time.strftime('%Y-%m-%d %H:%M')}'"
        ),
        "STEP_SIZE": f"'{step_hours}h'",
        "QUANTITIES": "'4'",
        "ANG_FORMAT": "'DEG'",
        "CAL_FORMAT": "'CAL'",
        "CSV_FORMAT": "'YES'",
        "APPARENT": "'AIRLESS'"
    }

    response = requests.get(
        HORIZONS_API,
        params=params,
        timeout=90
    )

    response.raise_for_status()

    data = response.json()

    if "error" in data:
        raise RuntimeError(data["error"])

    result = data.get("result", "")

    if "$$SOE" not in result or "$$EOE" not in result:
        raise RuntimeError(
            "Horizons did not return an ephemeris table. "
            "Check coordinates and observation time."
        )

    table = result.split("$$SOE")[1].split("$$EOE")[0]

    rows = []

    for row in csv.reader(io.StringIO(table)):

        if len(row) < 3:
            continue

        try:
            date = row[0].strip()
            azimuth = float(row[1].strip())
            elevation = float(row[2].strip())

            rows.append({
                "Time": date,
                "Earth Azimuth (deg)": azimuth,
                "Earth Elevation (deg)": elevation
            })

        except (ValueError, IndexError):
            continue

    if not rows:
        raise RuntimeError(
            "No valid Earth position records were returned."
        )

    return pd.DataFrame(rows)


# ==================================================
# 5. TERRAIN HORIZON ANALYSIS
# ==================================================

def calculate_terrain_horizon(
    terrain_data,
    target_azimuth,
    observer_elevation_m=0.0
):
    """
    Estimate apparent terrain horizon from a CSV profile.

    Required CSV columns:
        azimuth_deg
        distance_km
        elevation_m

    The curvature correction uses a spherical Moon.
    This is a preliminary terrain model.
    """

    best_angle = 0.0

    for _, row in terrain_data.iterrows():

        azimuth_difference = abs(
            (
                float(row["azimuth_deg"])
                - target_azimuth
                + 180
            ) % 360 - 180
        )

        if azimuth_difference > 1.0:
            continue

        distance = float(row["distance_km"])

        if distance <= 0:
            continue

        terrain_height = (
            float(row["elevation_m"])
            - observer_elevation_m
        )

        curvature_drop = (
            distance ** 2
            / (2 * MOON_RADIUS_KM)
        ) * 1000

        apparent_angle = math.degrees(
            math.atan2(
                terrain_height - curvature_drop,
                distance * 1000
            )
        )

        best_angle = max(best_angle, apparent_angle)

    return best_angle


# ==================================================
# 6. VISIBILITY CLASSIFICATION
# ==================================================

def classify_visibility(
    earth_elevation,
    terrain_horizon=0.0
):
    """
    Classify the visibility of Earth's centre.

    This is a centre-line-of-sight test.
    It does not classify partial Earth-disc visibility.
    """

    if earth_elevation > terrain_horizon:
        return "VISIBLE"

    return "OBSTRUCTED"


# ==================================================
# 7. PROCESS VISIBILITY TIMELINE
# ==================================================

def process_visibility_timeline(
    ephemeris,
    terrain_data=None,
    observer_elevation_m=0.0
):

    results = []

    for _, row in ephemeris.iterrows():

        elevation = float(
            row["Earth Elevation (deg)"]
        )

        azimuth = float(
            row["Earth Azimuth (deg)"]
        )

        horizon = 0.0

        if terrain_data is not None:

            horizon = calculate_terrain_horizon(
                terrain_data,
                azimuth,
                observer_elevation_m
            )

        status = classify_visibility(
            elevation,
            horizon
        )

        results.append({
            "Time": row["Time"],
            "Earth Azimuth (deg)": azimuth,
            "Earth Elevation (deg)": elevation,
            "Terrain Horizon (deg)": horizon,
            "Visibility": status,
            "Visible": status == "VISIBLE"
        })

    return pd.DataFrame(results)


# ==================================================
# 8. VISIBILITY STATISTICS
# ==================================================

def calculate_visibility_statistics(data):

    if data.empty:
        raise ValueError("No visibility records available.")

    total = len(data)

    visible = int(data["Visible"].sum())

    obstructed = total - visible

    percentage = visible / total * 100

    return {
        "Total Samples": total,
        "Visible Samples": visible,
        "Obstructed Samples": obstructed,
        "Visibility Percentage": percentage
    }


# ==================================================
# 9. VISIBILITY CHART
# ==================================================

def create_visibility_chart(data):

    fig = go.Figure()

    fig.add_trace(
        go.Scatter(
            x=data["Time"],
            y=data["Earth Elevation (deg)"],
            mode="lines+markers",
            name="Earth Elevation"
        )
    )

    fig.add_trace(
        go.Scatter(
            x=data["Time"],
            y=data["Terrain Horizon (deg)"],
            mode="lines",
            name="Terrain Horizon",
            line=dict(dash="dash")
        )
    )

    fig.update_layout(
        title="Earth Visibility Mission Timeline",
        xaxis_title="Mission Time",
        yaxis_title="Elevation (degrees)",
        template="plotly_dark",
        height=450,
        hovermode="x unified"
    )

    return fig


# ==================================================
# 10. AZIMUTH CHART
# ==================================================

def create_azimuth_chart(data):

    fig = go.Figure()

    fig.add_trace(
        go.Scatterpolar(
            r=data["Earth Elevation (deg)"],
            theta=data["Earth Azimuth (deg)"],
            mode="markers+lines",
            name="Earth Position"
        )
    )

    fig.update_layout(
        title="Earth Position Around Lunar Observer",
        template="plotly_dark",
        polar=dict(
            angularaxis=dict(
                direction="clockwise",
                rotation=90
            )
        ),
        height=450
    )

    return fig


# ==================================================
# 11. EXPORT RESULTS
# ==================================================

def export_visibility_results(data):

    return data.to_csv(
        index=False
    ).encode("utf-8")


# ==================================================
# 12. MAIN STREAMLIT INTERFACE
# ==================================================

def render_earth_visibility(scenario):

    st.header("Earth Visibility Analysis")

    st.write(
        "NASA-based Earth visibility assessment "
        "from a selected lunar landing location."
    )

    # Mission information

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            "Landing Site",
            scenario.site_name
        )

    with col2:
        st.metric(
            "Latitude",
            f"{scenario.latitude:.3f}°"
        )

    with col3:
        st.metric(
            "Longitude",
            f"{scenario.longitude:.3f}°"
        )

    st.divider()

    # Analysis configuration

    st.subheader("Analysis Configuration")

    duration = st.selectbox(
        "Analysis Duration",
        [6, 12, 24, 48, 72],
        index=2,
        format_func=lambda x: f"{x} hours"
    )

    step = st.selectbox(
        "Sampling Interval",
        [1, 2, 3, 6],
        index=0,
        format_func=lambda x: f"Every {x} hour(s)"
    )

    altitude = st.number_input(
        "Observer Altitude Above Lunar Reference (km)",
        min_value=0.0,
        max_value=10.0,
        value=0.0,
        step=0.01
    )

    # Terrain upload

    st.subheader("Lunar Terrain Data")

    uploaded_file = st.file_uploader(
        "Upload terrain profile CSV (optional)",
        type=["csv"],
        help=(
            "Required columns: azimuth_deg, "
            "distance_km, elevation_m"
        )
    )

    terrain_data = None

    if uploaded_file is not None:

        try:

            terrain_data = pd.read_csv(uploaded_file)

            required = {
                "azimuth_deg",
                "distance_km",
                "elevation_m"
            }

            if not required.issubset(terrain_data.columns):
                raise ValueError(
                    "CSV must contain azimuth_deg, "
                    "distance_km and elevation_m."
                )

            st.success("Terrain CSV loaded successfully.")

        except Exception as error:

            st.error(f"Terrain data error: {error}")
            terrain_data = None

    # Run analysis

    if st.button(
        "Run Earth Visibility Analysis",
        type="primary",
        use_container_width=True
    ):

        try:

            with st.spinner(
                "Retrieving Earth ephemeris from NASA Horizons..."
            ):

                ephemeris = get_horizons_earth_visibility(
                    latitude=scenario.latitude,
                    longitude=scenario.longitude,
                    altitude_km=altitude,
                    observation_time=scenario.datetime_utc,
                    duration_hours=duration,
                    step_hours=step
                )

            with st.spinner(
                "Calculating Earth visibility..."
            ):

                results = process_visibility_timeline(
                    ephemeris,
                    terrain_data
                )

                statistics = calculate_visibility_statistics(
                    results
                )

            st.session_state["eva_results"] = results
            st.session_state["eva_statistics"] = statistics

            st.success(
                "NASA Horizons ephemeris retrieved successfully."
            )

        except Exception as error:

            st.error(
                f"Earth Visibility Analysis failed: {error}"
            )

            st.info(
                "Check the selected mission date, "
                "coordinates and internet connection."
            )

    # Display results

    if "eva_results" in st.session_state:

        results = st.session_state["eva_results"]

        statistics = st.session_state["eva_statistics"]

        st.divider()

        st.subheader("Earth Visibility Results")

        c1, c2, c3 = st.columns(3)

        c1.metric(
            "Visibility",
            f'{statistics["Visibility Percentage"]:.1f}%'
        )

        c2.metric(
            "Visible Samples",
            statistics["Visible Samples"]
        )

        c3.metric(
            "Obstructed Samples",
            statistics["Obstructed Samples"]
        )

        st.subheader("Earth Elevation Timeline")

        st.plotly_chart(
            create_visibility_chart(results),
            use_container_width=True
        )

        st.subheader("Earth Azimuth Analysis")

        st.plotly_chart(
            create_azimuth_chart(results),
            use_container_width=True
        )

        st.subheader("Detailed Results")

        st.dataframe(
            results,
            use_container_width=True,
            hide_index=True
        )

        st.download_button(
            "Download EVA Results (CSV)",
            data=export_visibility_results(results),
            file_name="LUNA_NAV_Earth_Visibility.csv",
            mime="text/csv",
            use_container_width=True
        )

        st.caption(
            "Source: NASA JPL Horizons. "
            "Terrain obstruction is evaluated only when "
            "a compatible terrain profile is supplied. "
            "Earth visibility percentage represents sampled "
            "geometric visibility, not radio communication uptime."
        )