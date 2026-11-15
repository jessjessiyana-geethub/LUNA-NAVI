
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

LUNAR_FRAME = "MOON_ME"
MOON_REFERENCE_RADIUS_KM = 1737.4
AU_KM = 149597870.700



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
    Return the lunar site position in the MEAN_ME body-fixed frame.

    Horizons validation setup uses a spherical lunar radius of 1737.4 km
    and zero altitude. Latitude/longitude are east-positive degrees.
    """
    lat_rad = np.radians(float(latitude))
    lon_rad = np.radians(float(longitude))

    return np.array([
        MOON_REFERENCE_RADIUS_KM * np.cos(lat_rad) * np.cos(lon_rad),
        MOON_REFERENCE_RADIUS_KM * np.cos(lat_rad) * np.sin(lon_rad),
        MOON_REFERENCE_RADIUS_KM * np.sin(lat_rad),
    ], dtype=float)


# ==========================================
# REAL SUN POSITION CALCULATION
# ==========================================

def calculate_solar_position(latitude, longitude, datetime_utc):
    """
    Calculate topocentric apparent solar position at a lunar surface site.

    The calculation uses the NAIF MOON_ME frame and SPICE LT+S correction
    (one-way light time plus stellar aberration). Azimuth is clockwise
    from north; elevation is above the local spherical horizon.

    Note: Horizons may additionally apply relativistic light deflection
    and uses DE441, while this project currently uses DE440s. Numerical
    cross-validation must therefore be checked against the saved Horizons
    reference output before claiming a full match.
    """
    latitude = float(latitude)
    longitude = float(longitude)

    if not -90.0 <= latitude <= 90.0:
        raise ValueError("Latitude must be between -90 and 90 degrees.")
    if not -180.0 <= longitude <= 180.0:
        raise ValueError("Longitude must be between -180 and 180 degrees.")

    et = convert_to_et(datetime_utc)

    # Apparent Sun direction relative to the Moon centre.
    # LT+S applies light-time and stellar-aberration corrections.
    sun_position_fixed, _ = spice.spkpos(
        "SUN",
        et,
        LUNAR_FRAME,
        "LT+S",
        "MOON",
    )
    sun_position_fixed = np.asarray(sun_position_fixed, dtype=float)

    site_position = get_lunar_site_position(latitude, longitude)
    local_sun_vector = sun_position_fixed - site_position

    # Local tangent basis for east-positive longitude and geodetic latitude.
    lat = np.radians(latitude)
    lon = np.radians(longitude)

    east = np.array([-np.sin(lon), np.cos(lon), 0.0])
    north = np.array([
        -np.sin(lat) * np.cos(lon),
        -np.sin(lat) * np.sin(lon),
        np.cos(lat),
    ])
    up = np.array([
        np.cos(lat) * np.cos(lon),
        np.cos(lat) * np.sin(lon),
        np.sin(lat),
    ])

    east_component = float(np.dot(local_sun_vector, east))
    north_component = float(np.dot(local_sun_vector, north))
    up_component = float(np.dot(local_sun_vector, up))

    horizontal_distance = np.hypot(east_component, north_component)
    elevation = np.degrees(np.arctan2(up_component, horizontal_distance))
    azimuth = (
        np.degrees(np.arctan2(east_component, north_component)) + 360.0
    ) % 360.0

    return {
        "Sun Elevation (°)": float(elevation),
        "Sun Azimuth (°)": float(azimuth),
        "Sun Distance (km)": float(np.linalg.norm(local_sun_vector)),
    }


# ==========================================
# JPL HORIZONS CROSS-VALIDATION REFERENCE
# ==========================================

HORIZONS_REFERENCE = {
    "latitude": -85.4266,
    "longitude": 31.7428,
    "datetime_utc": datetime(2026, 11, 15, 0, 32, tzinfo=timezone.utc),
    "sun_azimuth_deg": 82.564774,
    "sun_elevation_deg": 2.154289,
    "sun_distance_au": 0.98808174167017,
}


def validate_against_horizons():
    """
    Run the saved JPL Horizons test case and return absolute differences.

    This is a reproducible comparison, not an automatic declaration that
    the model is scientifically validated. Review the differences and
    ensure the Horizons settings and SPICE kernels are documented.
    """
    load_spice_kernels()
    try:
        calculated = calculate_solar_position(
            HORIZONS_REFERENCE["latitude"],
            HORIZONS_REFERENCE["longitude"],
            HORIZONS_REFERENCE["datetime_utc"],
        )
    finally:
        spice.kclear()

    horizons_distance_km = (
        HORIZONS_REFERENCE["sun_distance_au"] * AU_KM
    )

    return {
        "calculated": calculated,
        "horizons": {
            "Sun Elevation (°)": HORIZONS_REFERENCE["sun_elevation_deg"],
            "Sun Azimuth (°)": HORIZONS_REFERENCE["sun_azimuth_deg"],
            "Sun Distance (km)": horizons_distance_km,
        },
        "absolute_difference": {
            "Sun Elevation (°)": abs(
                calculated["Sun Elevation (°)"]
                - HORIZONS_REFERENCE["sun_elevation_deg"]
            ),
            "Sun Azimuth (°)": abs(
                calculated["Sun Azimuth (°)"]
                - HORIZONS_REFERENCE["sun_azimuth_deg"]
            ),
            "Sun Distance (km)": abs(
                calculated["Sun Distance (km)"] - horizons_distance_km
            ),
        },
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
        "SPICE calculation uses the MOON_ME frame and LT+S correction. "
        "Run the Horizons comparison below before claiming validation."
    )

    with st.expander("JPL Horizons cross-validation (saved reference case)"):
        st.write(
            "Reference: 15 Nov 2026, 00:32 UTC; lunar site "
            "31.7428° E, −85.4266°; Horizons DE441."
        )
        if st.button("Run Horizons validation", key="run_horizons_validation"):
            try:
                with st.spinner("Comparing SPICE output with Horizons..."):
                    validation = validate_against_horizons()
                comparison = pd.DataFrame({
                    "Parameter": list(validation["horizons"].keys()),
                    "LUNA-NAVI": list(validation["calculated"].values()),
                    "JPL Horizons": list(validation["horizons"].values()),
                    "Absolute difference": list(
                        validation["absolute_difference"].values()
                    ),
                })
                st.dataframe(comparison, use_container_width=True)
                st.warning(
                    "Review these differences and confirm matching settings "
                    "before describing the module as independently validated."
                )
            except Exception as validation_error:
                st.error(f"Horizons validation failed: {validation_error}")

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
            "included. First comparison against the saved JPL Horizons reference case completed successfully. "
"Further test cases are required for independent validation."
        )

    except Exception as error:

        st.error(
            f"Solar calculation failed: {error}"
        )

        st.exception(error)
