
from dataclasses import dataclass
from datetime import datetime, timezone


@dataclass
class LandingScenario:
    site_name: str
    latitude: float
    longitude: float
    datetime_utc: datetime

    def __post_init__(self):
        if not -90 <= self.latitude <= 90:
            raise ValueError("Latitude must be between -90 and 90.")

        if not -180 <= self.longitude <= 180:
            raise ValueError("Longitude must be between -180 and 180.")

        if self.datetime_utc.tzinfo is None:
            raise ValueError("Datetime must include a timezone.")

        self.datetime_utc = self.datetime_utc.astimezone(timezone.utc)
