"""Domain services for weather operations."""

from typing import Protocol

from .models import Location, WeatherForecast, TemperatureUnit


class LocationValidatorService:
    """Service for validating location inputs."""

    @staticmethod
    def validate_zipcode(zipcode: str) -> bool:
        """Validate US zipcode format."""
        import re

        # US zipcode patterns: 12345 or 12345-6789
        pattern = r"^\d{5}(-\d{4})?$"
        return bool(re.match(pattern, zipcode.strip()))

    @staticmethod
    def validate_city_state(city: str, state: str) -> bool:
        """Validate city and state inputs."""
        return bool(city.strip()) and bool(state.strip())

    @staticmethod
    def validate_city_state_country(city: str, state: str, country: str) -> bool:
        """Validate city, state, and country inputs."""
        return bool(city.strip()) and bool(state.strip()) and bool(country.strip())


class WeatherUnitsService:
    """Service for determining appropriate weather units based on location."""

    @staticmethod
    def get_temperature_unit_for_location(location: Location) -> TemperatureUnit:
        """Get the appropriate temperature unit for a location."""
        if location.is_us_location:
            return TemperatureUnit.FAHRENHEIT
        return TemperatureUnit.CELSIUS

    @staticmethod
    def get_speed_unit_for_location(location: Location) -> str:
        """Get the appropriate speed unit for a location."""
        if location.is_us_location:
            return "mph"
        return "km/h"

    @staticmethod
    def get_distance_unit_for_location(location: Location) -> str:
        """Get the appropriate distance unit for a location."""
        if location.is_us_location:
            return "miles"
        return "km"


class IWeatherRepository(Protocol):
    """Interface for weather data repository."""

    async def get_current_weather(self, location: Location) -> WeatherForecast:
        """Get current weather and forecast for a location."""
        ...


class ILocationRepository(Protocol):
    """Interface for location data repository."""

    async def resolve_location(self, location: Location) -> Location:
        """Resolve location to include coordinates and normalized data."""
        ...
