
from datetime import datetime, timezone, timedelta
from types import SimpleNamespace

from modules.solar import build_demo_solar_data


def create_test_scenario():
    """Create sample landing site data for testing."""

    return SimpleNamespace(
        site_name="Lunar South Pole",
        latitude=-89.5,
        longitude=30.0,
        datetime_utc=datetime(
            2026, 11, 14, 0, 0,
            tzinfo=timezone.utc
        )
    )


def test_solar_data_generation():
    """Check whether solar data is generated."""

    scenario = create_test_scenario()
    data = build_demo_solar_data(scenario)

    assert data is not None
    assert len(data) == 25


def test_solar_data_columns():
    """Check required data columns."""

    scenario = create_test_scenario()
    data = build_demo_solar_data(scenario)

    assert "Time (UTC)" in data.columns
    assert "Sun Elevation (°)" in data.columns
    assert "Sun Azimuth (°)" in data.columns

def test_solar_elevation_range():
    """Check solar elevation values."""

    scenario = create_test_scenario()
    data = build_demo_solar_data(scenario)

    assert data["Sun Elevation (°)"].between(
        -8, 8
    ).all()

def test_solar_azimuth_range():
    """Check solar azimuth values."""

    scenario = create_test_scenario()
    data = build_demo_solar_data(scenario)

    assert data["Sun Azimuth (°)"].between(
        0, 360
    ).all()


def test_solar_time_interval():
    """Check timestamps are one hour apart."""

    scenario = create_test_scenario()
    data = build_demo_solar_data(scenario)

    assert data["Time (UTC)"].iloc[0] == (
        scenario.datetime_utc
    )

    assert data["Time (UTC)"].iloc[-1] == (
        scenario.datetime_utc + timedelta(hours=24)
    )
