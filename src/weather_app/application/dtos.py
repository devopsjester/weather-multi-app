"""Application layer - DTOs (Data Transfer Objects)."""

from dataclasses import dataclass
from typing import Optional


@dataclass
class WeatherRequestDto:
    """DTO for weather requests."""

    zipcode: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    country: Optional[str] = None

    def validate(self) -> bool:
        """Validate that the request has sufficient information."""
        if self.zipcode:
            return True
        if self.city and (self.state or self.country):
            return True
        return False


@dataclass
class WeatherResponseDto:
    """DTO for weather responses."""

    location: str
    current_temperature: str
    feels_like: str
    condition: str
    description: str
    humidity: int
    pressure: int
    visibility: str
    wind_speed: str
    wind_direction: str
    timestamp: str
    daily_forecasts: list[dict]
    units: dict
