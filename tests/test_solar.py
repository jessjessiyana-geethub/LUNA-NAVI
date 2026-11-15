
from datetime import datetime, timezone

from modules.solar import (
    calculate_solar_position,
    load_spice_kernels
)


def test_solar_position_calculation():

    # Load NASA/JPL SPICE kernels
    load_spice_kernels()

    # Test landing site
    latitude = -89.5
    longitude = 30.0

    # Test date and time
    datetime_utc = datetime(
        2026, 11, 14, 0, 0,
        tzinfo=timezone.utc
    )

    # Calculate real solar position
    result = calculate_solar_position(
        latitude,
        longitude,
        datetime_utc
    )

    # Check returned data
    assert "Sun Elevation (°)" in result
    assert "Sun Azimuth (°)" in result
    assert "Sun Distance (km)" in result

    # Check values
    assert -90 <= result["Sun Elevation (°)"] <= 90

    assert 0 <= result["Sun Azimuth (°)"] < 360

    assert result["Sun Distance (km)"] > 0
