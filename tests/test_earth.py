
"""
LUNA-NAVI
Module 3: Earth Visibility Analysis
Earth Module Unit Tests
"""

import math
import numpy as np
import pandas as pd
import pytest

from datetime import datetime

from modules.earth import (
    normalize_vector,
    calculate_observer_position,
    calculate_terrain_horizon,
    classify_visibility,
    process_visibility_timeline,
    calculate_visibility_statistics,
    create_visibility_chart,
    create_azimuth_chart,
    export_visibility_results,
)


# ==========================================
# 1. VECTOR NORMALIZATION TEST
# ==========================================

def test_normalize_vector():

    vector = np.array([3, 4, 0])

    result = normalize_vector(vector)

    assert np.linalg.norm(result) == pytest.approx(1.0)
    assert result[0] == pytest.approx(0.6)
    assert result[1] == pytest.approx(0.8)


def test_normalize_zero_vector():

    with pytest.raises(ValueError):
        normalize_vector([0, 0, 0])


# ==========================================
# 2. LUNAR OBSERVER POSITION TEST
# ==========================================

def test_observer_position():

    position = calculate_observer_position(
        latitude=0,
        longitude=0,
        altitude_km=0
    )

    assert position.shape == (3,)

    assert position[0] == pytest.approx(1737.4)
    assert position[1] == pytest.approx(0)
    assert position[2] == pytest.approx(0)


# ==========================================
# 3. TERRAIN HORIZON TEST
# ==========================================

def test_terrain_horizon():

    terrain = pd.DataFrame({
        "azimuth_deg": [90],
        "distance_km": [0.1],
        "elevation_m": [100]
    })

    horizon = calculate_terrain_horizon(
        terrain_data=terrain,
        target_azimuth=90
    )

    assert horizon > 0
    assert horizon < 90


# ==========================================
# 4. VISIBILITY CLASSIFICATION TEST
# ==========================================

def test_visible_classification():

    result = classify_visibility(
        earth_elevation=30,
        terrain_horizon=10
    )

    assert result == "VISIBLE"


def test_obstructed_classification():

    result = classify_visibility(
        earth_elevation=5,
        terrain_horizon=15
    )

    assert result == "OBSTRUCTED"


# ==========================================
# 5. VISIBILITY TIMELINE TEST
# ==========================================

def test_visibility_timeline():

    ephemeris = pd.DataFrame({
        "Time": [
            "2026-11-14 00:00",
            "2026-11-14 01:00",
            "2026-11-14 02:00"
        ],
        "Earth Azimuth (deg)": [
            90, 120, 150
        ],
        "Earth Elevation (deg)": [
            30, -5, 20
        ]
    })

    results = process_visibility_timeline(
        ephemeris
    )

    assert len(results) == 3

    assert results["Visibility"].tolist() == [
        "VISIBLE",
        "OBSTRUCTED",
        "VISIBLE"
    ]


# ==========================================
# 6. VISIBILITY STATISTICS TEST
# ==========================================

def test_visibility_statistics():

    data = pd.DataFrame({
        "Visible": [
            True,
            False,
            True,
            True
        ]
    })

    statistics = calculate_visibility_statistics(
        data
    )

    assert statistics["Total Samples"] == 4

    assert statistics["Visible Samples"] == 3

    assert statistics["Obstructed Samples"] == 1

    assert statistics["Visibility Percentage"] == 75


def test_empty_statistics():

    with pytest.raises(ValueError):
        calculate_visibility_statistics(
            pd.DataFrame()
        )


# ==========================================
# 7. VISIBILITY CHART TEST
# ==========================================

def test_visibility_chart():

    data = pd.DataFrame({
        "Time": ["00:00", "01:00"],
        "Earth Elevation (deg)": [20, 30],
        "Terrain Horizon (deg)": [5, 10]
    })

    chart = create_visibility_chart(data)

    assert chart is not None
    assert len(chart.data) == 2


# ==========================================
# 8. AZIMUTH CHART TEST
# ==========================================

def test_azimuth_chart():

    data = pd.DataFrame({
        "Earth Azimuth (deg)": [90, 180],
        "Earth Elevation (deg)": [20, 30]
    })

    chart = create_azimuth_chart(data)

    assert chart is not None
    assert len(chart.data) == 1


# ==========================================
# 9. CSV EXPORT TEST
# ==========================================

def test_export_visibility_results():

    data = pd.DataFrame({
        "Time": ["2026-11-14 00:00"],
        "Visibility": ["VISIBLE"],
        "Visible": [True]
    })

    exported = export_visibility_results(data)

    assert isinstance(exported, bytes)

    assert b"VISIBLE" in exported

    assert b"Time" in exported

# ==========================================
# 10. ADDITIONAL EARTH FUNCTIONAL TESTS
# ==========================================

def test_earth_at_exact_terrain_horizon():

    result = classify_visibility(
        earth_elevation=10.0,
        terrain_horizon=10.0
    )

    assert result == "OBSTRUCTED"


def test_terrain_azimuth_wraparound():

    terrain = pd.DataFrame({
        "azimuth_deg": [359.5],
        "distance_km": [0.1],
        "elevation_m": [100]
    })

    horizon = calculate_terrain_horizon(
        terrain_data=terrain,
        target_azimuth=0.0
    )

    assert horizon > 0


def test_terrain_without_matching_azimuth():

    terrain = pd.DataFrame({
        "azimuth_deg": [180],
        "distance_km": [0.1],
        "elevation_m": [100]
    })

    horizon = calculate_terrain_horizon(
        terrain_data=terrain,
        target_azimuth=90
    )

    assert horizon == 0.0


def test_timeline_with_terrain_obstruction():

    ephemeris = pd.DataFrame({
        "Time": ["2026-11-14 00:00"],
        "Earth Azimuth (deg)": [90],
        "Earth Elevation (deg)": [5]
    })

    terrain = pd.DataFrame({
        "azimuth_deg": [90],
        "distance_km": [0.1],
        "elevation_m": [100]
    })

    results = process_visibility_timeline(
        ephemeris,
        terrain_data=terrain
    )

    assert results.iloc[0]["Visibility"] == "OBSTRUCTED"
    assert results.iloc[0]["Visible"] == False
