"""Domain models for the weather application.

These models represent the core business entities and value objects.
"""

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Optional


class TemperatureUnit(Enum):
    """Temperature unit enumeration."""

    CELSIUS = "celsius"
    FAHRENHEIT = "fahrenheit"


class WeatherCondition(Enum):
    """Weather condition enumeration."""

    CLEAR = "clear"
    CLOUDS = "clouds"
    RAIN = "rain"
    SNOW = "snow"
    THUNDERSTORM = "thunderstorm"
    DRIZZLE = "drizzle"
    MIST = "mist"
    HAZE = "haze"
    FOG = "fog"
    UNKNOWN = "unknown"


@dataclass(frozen=True)
class Location:
    """Location value object."""

    city: str
    state: Optional[str] = None
    country: Optional[str] = None
    zipcode: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None

    def __post_init__(self):
        """Validate location data."""
        if not any([self.zipcode, (self.city and (self.state or self.country))]):
            raise ValueError("Location must have either zipcode or city with state/country")

    @property
    def display_name(self) -> str:
        """Get a human-readable display name for the location."""
        if self.zipcode:
            return f"{self.city}, {self.state} {self.zipcode}"
        elif self.state and self.country:
            return f"{self.city}, {self.state}, {self.country}"
        elif self.state:
            return f"{self.city}, {self.state}"
        elif self.country:
            return f"{self.city}, {self.country}"
        else:
            return self.city

    @property
    def is_us_location(self) -> bool:
        """Check if this is a US location."""
        return self.zipcode is not None or (
            self.country is not None and self.country.upper() in ["US", "USA", "UNITED STATES"]
        )


@dataclass(frozen=True)
class Temperature:
    """Temperature value object with unit conversion."""

    value: float
    unit: TemperatureUnit

    def to_celsius(self) -> float:
        """Convert temperature to Celsius."""
        if self.unit == TemperatureUnit.CELSIUS:
            return self.value
        return (self.value - 32) * 5 / 9

    def to_fahrenheit(self) -> float:
        """Convert temperature to Fahrenheit."""
        if self.unit == TemperatureUnit.FAHRENHEIT:
            return self.value
        return (self.value * 9 / 5) + 32

    def to_unit(self, target_unit: TemperatureUnit) -> "Temperature":
        """Convert to a specific unit."""
        if target_unit == TemperatureUnit.CELSIUS:
            return Temperature(self.to_celsius(), TemperatureUnit.CELSIUS)
        else:
            return Temperature(self.to_fahrenheit(), TemperatureUnit.FAHRENHEIT)

    def __str__(self) -> str:
        """String representation with unit symbol."""
        symbol = "°C" if self.unit == TemperatureUnit.CELSIUS else "°F"
        return f"{self.value:.1f}{symbol}"


@dataclass(frozen=True)
class WeatherData:
    """Current weather data for a location."""

    location: Location
    temperature: Temperature
    feels_like: Temperature
    humidity: int  # Percentage
    pressure: int  # hPa
    visibility: float  # km
    wind_speed: float  # km/h or mph depending on location
    wind_direction: Optional[int]  # degrees
    condition: WeatherCondition
    description: str
    timestamp: datetime

    @property
    def wind_direction_text(self) -> str:
        """Convert wind direction degrees to compass direction."""
        if self.wind_direction is None:
            return "N/A"

        directions = [
            "N",
            "NNE",
            "NE",
            "ENE",
            "E",
            "ESE",
            "SE",
            "SSE",
            "S",
            "SSW",
            "SW",
            "WSW",
            "W",
            "WNW",
            "NW",
            "NNW",
        ]
        idx = round(self.wind_direction / 22.5) % 16
        return directions[idx]


@dataclass(frozen=True)
class DailyForecast:
    """Daily forecast data."""

    date: datetime
    high_temperature: Temperature
    low_temperature: Temperature
    condition: WeatherCondition
    description: str
    humidity: int
    wind_speed: float
    precipitation_chance: int  # Percentage

    @property
    def day_name(self) -> str:
        """Get the day name (e.g., 'Monday')."""
        return self.date.strftime("%A")


@dataclass(frozen=True)
class WeatherForecast:
    """Multi-day weather forecast."""

    location: Location
    current_weather: WeatherData
    daily_forecasts: list[DailyForecast]
    timestamp: datetime

    def __post_init__(self):
        """Validate forecast data."""
        if len(self.daily_forecasts) > 5:
            raise ValueError("Forecast cannot exceed 5 days")
        if not self.daily_forecasts:
            raise ValueError("Forecast must contain at least one day")
