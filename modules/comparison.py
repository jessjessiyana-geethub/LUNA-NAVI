
from datetime import timezone
from types import SimpleNamespace

import pandas as pd
import streamlit as st

from modules.landing_sites import SOUTH_POLE_SITES
from modules.solar import build_solar_data
from modules.earth import (
    get_horizons_earth_visibility,
    process_visibility_timeline,
)


def create_site(site, mission_time):
    """Create a site scenario using the selected mission time."""
    return SimpleNamespace(
        site_code=site["code"],
        site_name=site["name"],
        latitude=site["latitude"],
        longitude=site["longitude"],
        datetime_utc=mission_time,
    )


def find_column(data, prefix):
    """Find a column without depending on unit formatting."""
    return next(
        (col for col in data.columns if col.startswith(prefix)),
        None,
    )


def run_mission_comparison(scenario):
    st.title("Lunar Mission Site Comparison")

    st.write(
        "Compare solar conditions and Earth visibility "
        "across actual lunar south pole landing sites."
    )

    if scenario is None:
        st.warning("Please select a landing site first.")
        return

    mission_time = scenario.datetime_utc

    if mission_time.tzinfo is None:
        mission_time = mission_time.replace(tzinfo=timezone.utc)

    # Horizons request times are interpreted as UTC.
    mission_time = mission_time.astimezone(timezone.utc)

    site_options = list(SOUTH_POLE_SITES.keys())

    default_sites = [
        key for key, site in SOUTH_POLE_SITES.items()
        if site["code"] == scenario.site_code
    ]

    selected_sites = st.multiselect(
        "Select up to three landing sites",
        options=site_options,
        default=default_sites,
        max_selections=3,
    )

    st.caption(
        f"Mission start (UTC): {mission_time:%Y-%m-%d %H:%M}"
    )

    st.info(
        "Solar results use the project's SPICE calculations. "
        "Earth positions are requested from JPL Horizons. "
        "Terrain obstruction is not included in this comparison."
    )

    if not st.button("Run Mission Comparison"):
        return

    if not selected_sites:
        st.warning("Select at least one landing site.")
        return

    results = []
    timelines = []

    for site_key in selected_sites:
        site = SOUTH_POLE_SITES[site_key]
        site_scenario = create_site(site, mission_time)

        with st.spinner(
            f"Calculating conditions for {site['name']}..."
        ):
            result = {
                "Landing Site": site["name"],
                "Latitude": site["latitude"],
                "Longitude": site["longitude"],
                "Average Sun Elevation (deg)": None,
                "Sun Above Horizon (%)": None,
                "Average Earth Elevation (deg)": None,
                "Earth Above Geometric Horizon (%)": None,
                "Solar Status": "Unavailable",
                "Earth Status": "Unavailable",
            }

            # Solar calculations
            try:
                solar_data = build_solar_data(site_scenario)

                elevation_col = find_column(
                    solar_data, "Sun Elevation"
                )

                if elevation_col is None:
                    raise ValueError(
                        "Solar elevation column not found."
                    )

                elevations = pd.to_numeric(
                    solar_data[elevation_col],
                    errors="coerce",
                ).dropna()

                if elevations.empty:
                    raise ValueError(
                        "No valid solar elevation samples."
                    )

                result["Average Sun Elevation (deg)"] = round(
                    elevations.mean(), 2
                )

                result["Sun Above Horizon (%)"] = round(
                    (elevations > 0).mean() * 100, 2
                )

                result["Solar Status"] = "Calculated"

                timelines.append(
                    pd.DataFrame({
                        "Time": solar_data["Time (UTC)"],
                        "Landing Site": site["name"],
                        "Parameter": "Sun Elevation",
                        "Elevation (deg)": pd.to_numeric(
                            solar_data[elevation_col],
                            errors="coerce",
                        ),
                    })
                )

            except Exception as error:
                st.warning(
                    f"Solar calculation unavailable for "
                    f"{site['name']}: {error}"
                )

            # Earth ephemeris calculations
            try:
                earth_data = get_horizons_earth_visibility(
                    latitude=site["latitude"],
                    longitude=site["longitude"],
                    altitude_km=0.0,
                    observation_time=mission_time.replace(
                        tzinfo=None
                    ),
                    duration_hours=24,
                    step_hours=1,
                )

                visibility = process_visibility_timeline(
                    earth_data,
                    terrain_data=None,
                )

                earth_elevations = pd.to_numeric(
                    visibility["Earth Elevation (deg)"],
                    errors="coerce",
                ).dropna()

                if earth_elevations.empty:
                    raise ValueError(
                        "No valid Earth elevation samples."
                    )

                result["Average Earth Elevation (deg)"] = round(
                    earth_elevations.mean(), 2
                )

                result[
                    "Earth Above Geometric Horizon (%)"
                ] = round(
                    (earth_elevations > 0).mean() * 100, 2
                )

                result["Earth Status"] = (
                    "Calculated — geometric horizon only"
                )

                timelines.append(
                    pd.DataFrame({
                        "Time": pd.to_datetime(
                            visibility["Time"],
                            errors="coerce",
                            utc=True,
                        ),
                        "Landing Site": site["name"],
                        "Parameter": "Earth Elevation",
                        "Elevation (deg)": pd.to_numeric(
                            visibility["Earth Elevation (deg)"],
                            errors="coerce",
                        ),
                    })
                )

            except Exception as error:
                st.warning(
                    f"Earth calculation unavailable for "
                    f"{site['name']}: {error}"
                )

            results.append(result)

    comparison = pd.DataFrame(results)

    st.subheader("Landing Site Comparison")
    st.dataframe(
        comparison,
        use_container_width=True,
        hide_index=True,
    )

    if timelines:
        timeline_data = pd.concat(
            timelines, ignore_index=True
        )

        for parameter in [
            "Sun Elevation",
            "Earth Elevation",
        ]:
            subset = timeline_data[
                timeline_data["Parameter"] == parameter
            ]

            if subset.empty:
                continue

            st.subheader(f"{parameter} Timeline")

            chart_data = subset.pivot_table(
                index="Time",
                columns="Landing Site",
                values="Elevation (deg)",
                aggfunc="mean",
            )

            st.line_chart(chart_data)

    st.subheader("Mission Assessment")

    st.info(
        "Compare the measured elevation trends and "
        "geometric visibility windows. No overall mission "
        "suitability ranking is generated because terrain, "
        "surface safety, illumination duration and other "
        "mission constraints have not been fully validated."
    )

    st.caption(
        "Sun-above-horizon and Earth-above-horizon percentages "
        "are fractions of sampled timestamps, not verified "
        "continuous power or communication availability."
    )
