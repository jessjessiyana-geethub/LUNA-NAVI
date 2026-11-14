
from modules.mission_scoring import rank_landing_sites
from datetime import datetime, timezone
from types import SimpleNamespace

import streamlit as st
import pandas as pd

from modules.solar import build_demo_solar_data


def create_site(name, latitude, longitude):
    return SimpleNamespace(
        site_name=name,
        latitude=latitude,
        longitude=longitude,
        datetime_utc=datetime(
            2026, 11, 14, 0, 0,
            tzinfo=timezone.utc
        )
    )


def run_mission_comparison():

    st.title("🌕 Mission Comparison")

    st.write(
        "Compare three lunar landing sites "
        "using demo solar position data."
    )

    sites = [
        create_site("Site A", -89.5, 30.0),
        create_site("Site B", -88.0, 45.0),
        create_site("Site C", -87.0, 60.0)
    ]

    # Mission Scoring
    scoring_inputs = [
        {
            "name": "Site A",
            "solar_score": 80,
            "terrain_score": 90,
            "safety_score": 85
        },
        {
            "name": "Site B",
            "solar_score": 75,
            "terrain_score": 70,
            "safety_score": 80
        },
        {
            "name": "Site C",
            "solar_score": 90,
            "terrain_score": 85,
            "safety_score": 95
        }
    ]

    scoring_results = rank_landing_sites(scoring_inputs)

    st.subheader("Mission Scoring Results")
    st.dataframe(
        scoring_results,
        use_container_width=True
    )

    # Mission Comparison
    results = []

    for site in sites:

        data = build_demo_solar_data(site)

        results.append({
            "Landing Site": site.site_name,
            "Latitude": site.latitude,
            "Longitude": site.longitude,
            "Average Sun Elevation (°)": round(
                data["Sun Elevation (°)"].mean(), 2
            ),
            "Average Sun Azimuth (°)": round(
                data["Sun Azimuth (°)"].mean(), 2
            )
        })

    comparison = pd.DataFrame(results)

    st.subheader("Landing Site Comparison")

    st.dataframe(
        comparison,
        use_container_width=True
    )

    # Mission Recommendation
    best_site = scoring_results.iloc[0]

    st.success(
        f"Recommended Landing Site: "
        f"{best_site['Landing Site']} "
        f"(Score: {best_site['Overall Score']})"
    )

    st.warning(
        "DEMO MODE: Solar values are artificial "
        "and should not be used as actual lunar measurements."
    )


if __name__ == "__main__":
    run_mission_comparison()
