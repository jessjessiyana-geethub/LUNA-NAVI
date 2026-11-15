
import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import spiceypy as spice

from pathlib import Path
from datetime import datetime, timedelta, timezone


# ==========================================
# NASA / JPL SPICE CONFIGURATION
# ==========================================

KERNEL_DIR = Path("data/kernels")

KERNELS = [
    "naif0012.tls",
    "pck00011.tpc",
    "moon_de440_250416.tf",
    "moon_pa_de440_200625.bpc",
    "de440s.bsp",
]

LUNAR_FRAME = "MOON_PA"


def load_spice_kernels():
    """Load the NASA/JPL SPICE kernels."""

    spice.kclear()

    for filename in KERNELS:
        kernel_path = KERNEL_DIR / filename

        if not kernel_path.exists():
            raise FileNotFoundError(
                f"Missing NASA kernel: {kernel_path}"
            )

        spice.furnsh(str(kernel_path))





   


def convert_to_et(datetime_utc):
    """Convert a UTC datetime to SPICE Ephemeris Time (ET)."""
    if datetime_utc.tzinfo is None:
        datetime_utc = datetime_utc.replace(tzinfo=timezone.utc)
    datetime_utc = datetime_utc.astimezone(timezone.utc)
    utc_string = datetime_utc.strftime("%Y-%m-%d %H:%M:%S") + " UTC"
    return spice.str2et(utc_string)


# ==========================================
# LUNAR SURFACE POSITION
# ==========================================

def get_lunar_site_position(latitude, longitude):
    """
    Calculate landing site position in Moon-fixed MOON_PA.

    Latitude and longitude are in degrees.
    Position is calculated on the reference ellipsoid.
    """

    _, radii = spice.bodvrd(
        "MOON", "RADII", 3
    )

    equatorial_radius = float(radii[0])
    polar_radius = float(radii[2])

    flattening = (
        equatorial_radius - polar_radius
    ) / equatorial_radius

    lat_rad = np.radians(latitude)
    lon_rad = np.radians(longitude)

    site_position = spice.georec(
        lon_rad,
        lat_rad,
        0.0,
        equatorial_radius,
        flattening
    )

    return np.asarray(site_position)


# ==========================================
# REAL SUN POSITION CALCULATION
# ==========================================

def calculate_solar_position(
    latitude,
    longitude,
    datetime_utc
):
    
      
    """Calculate geometric solar position at a lunar surface site.

    Azimuth is clockwise from lunar north (0-360 degrees). Elevation is
    measured from the local reference-ellipsoid horizon. SPICE kernels
    must already be loaded by the caller.
    """
    if not -90.0 <= float(latitude) <= 90.0:
        raise ValueError("Latitude must be between -90 and 90 degrees.")
    if not -180.0 <= float(longitude) <= 180.0:
        raise ValueError("Longitude must be between -180 and 180 degrees.")

    et = convert_to_et(datetime_utc)

    # Get Sun position relative to Moon centre.
    sun_position_j2000, light_time = spice.spkpos(
        "SUN",
        et,
        "J2000",
        "NONE",
        "MOON"
    )

    # Transform Sun vector into lunar body-fixed frame.
    rotation = spice.pxform(
        "J2000",
        LUNAR_FRAME,
        et
    )

    sun_position_fixed = (
        rotation @ sun_position_j2000
    )

    # Get landing site position in Moon-fixed frame.
    site_position = get_lunar_site_position(
        latitude,
        longitude
    )

    # Topocentric vector: landing site to Sun.
    local_sun_vector = (
        sun_position_fixed - site_position
    )

    # Local East, North and Up directions.
    lat = np.radians(latitude)
    lon = np.radians(longitude)

    east = np.array([
        -np.sin(lon),
        np.cos(lon),
        0.0
    ])

    north = np.array([
        -np.sin(lat) * np.cos(lon),
        -np.sin(lat) * np.sin(lon),
        np.cos(lat)
    ])

    up = np.array([
        np.cos(lat) * np.cos(lon),
        np.cos(lat) * np.sin(lon),
        np.sin(lat)
    ])

    # Project Sun vector onto local coordinates.
    east_component = np.dot(
        local_sun_vector, east
    )

    north_component = np.dot(
        local_sun_vector, north
    )

    up_component = np.dot(
        local_sun_vector, up
    )

    # Calculate solar elevation.
    horizontal_distance = np.hypot(
        east_component,
        north_component
    )

    elevation = np.degrees(
        np.arctan2(
            up_component,
            horizontal_distance
        )
    )

    # Calculate solar azimuth.
    azimuth = (
        np.degrees(
            np.arctan2(
                east_component,
                north_component
            )
        ) + 360
    ) % 360

    return {
        "Sun Elevation (°)": float(elevation),
        "Sun Azimuth (°)": float(azimuth),
        "Sun Distance (km)": float(
            np.linalg.norm(local_sun_vector)
        )
    }


# ==========================================
# GENERATE REAL SOLAR DATA
# ==========================================

def build_solar_data(scenario):

    start_time = scenario.datetime_utc

    if start_time.tzinfo is None:
        start_time = start_time.replace(
            tzinfo=timezone.utc
        )

    times = [
        start_time + timedelta(hours=i)
        for i in range(25)
    ]

    results = []

    load_spice_kernels()

    try:
        for timestamp in times:

            solar = calculate_solar_position(
                scenario.latitude,
                scenario.longitude,
                timestamp
            )

            results.append({
                "Time (UTC)": timestamp,
                **solar
            })

    finally:
        spice.kclear()

    return pd.DataFrame(results)


# ==========================================
# STREAMLIT SOLAR DASHBOARD
# ==========================================

def render_solar_analysis(scenario):

    st.header("☀️ Solar Position Analysis")

    st.success(
        "JPL DE440s ephemeris and NAIF lunar-orientation kernels loaded"
    )
    st.info(
        "The calculation is connected to JPL/NAIF data. Independent "
        "numerical cross-validation against JPL Horizons is still pending."
    )

    st.write(
        "**Landing Site:**",
        scenario.site_name
    )

    st.write(
        "**Latitude:**",
        f"{scenario.latitude:.4f}°"
    )

    st.write(
        "**Longitude:**",
        f"{scenario.longitude:.4f}°"
    )

    try:

        with st.spinner(
            "Calculating real lunar solar positions..."
        ):

            data = build_solar_data(scenario)

        # Current selected-time result.
        selected = data.iloc[0]

        col1, col2, col3 = st.columns(3)

        col1.metric(
            "Sun Elevation",
            f"{selected['Sun Elevation (°)']:.3f}°"
        )

        col2.metric(
            "Sun Azimuth",
            f"{selected['Sun Azimuth (°)']:.3f}°"
        )

        col3.metric(
            "Sun Distance",
            f"{selected['Sun Distance (km)']:,.0f} km"
        )

        # Elevation chart.
        st.subheader("Solar Elevation")

        fig = go.Figure()

        fig.add_trace(go.Scatter(
            x=data["Time (UTC)"],
            y=data["Sun Elevation (°)"],
            mode="lines+markers",
            name="Solar Elevation"
        ))

        fig.add_hline(
            y=0,
            line_dash="dash",
            annotation_text="Reference Horizon"
        )

        fig.update_layout(
            title="Real JPL Solar Elevation",
            xaxis_title="Time (UTC)",
            yaxis_title="Elevation (degrees)",
            hovermode="x unified",
            height=420
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

        # Azimuth chart.
        st.subheader("Solar Azimuth")

        azimuth_fig = go.Figure()

        azimuth_fig.add_trace(go.Scatter(
            x=data["Time (UTC)"],
            y=data["Sun Azimuth (°)"],
            mode="lines+markers",
            name="Solar Azimuth"
        ))

        azimuth_fig.update_layout(
            title="Real JPL Solar Azimuth",
            xaxis_title="Time (UTC)",
            yaxis_title="Azimuth (degrees)",
            yaxis_range=[0, 360],
            height=350
        )

        st.plotly_chart(
            azimuth_fig,
            use_container_width=True
        )

        st.subheader("Solar Ephemeris Data")

        st.dataframe(
            data,
            use_container_width=True
        )

        st.caption(
            "Ephemeris: JPL DE440s; lunar orientation: NAIF kernels. "
            "Values are geometric and referenced to the lunar reference "
            "ellipsoid. Terrain obstruction and local topography are not "
            "included. Independent comparison against JPL Horizons is "
            "still pending."
        )

    except Exception as error:

        st.error(
            f"Solar calculation failed: {error}"
        )

        st.exception(error)
