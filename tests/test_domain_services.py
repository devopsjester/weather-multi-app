"""Unit tests for domain services."""

import pytest

from weather_app.domain.models import Location, TemperatureUnit
from weather_app.domain.services import LocationValidatorService, WeatherUnitsService


class TestLocationValidatorService:
    """Test LocationValidatorService."""

    def test_validate_zipcode_valid(self):
        """Test valid zipcode validation."""
        assert LocationValidatorService.validate_zipcode("90210") is True
        assert LocationValidatorService.validate_zipcode("90210-1234") is True
        assert LocationValidatorService.validate_zipcode("  12345  ") is True

    def test_validate_zipcode_invalid(self):
        """Test invalid zipcode validation."""
        assert LocationValidatorService.validate_zipcode("9021") is False
        assert LocationValidatorService.validate_zipcode("902101") is False
        assert LocationValidatorService.validate_zipcode("abc12") is False
        assert LocationValidatorService.validate_zipcode("") is False

    def test_validate_city_state_valid(self):
        """Test valid city/state validation."""
        assert LocationValidatorService.validate_city_state("Los Angeles", "CA") is True
        assert LocationValidatorService.validate_city_state("New York", "NY") is True

    def test_validate_city_state_invalid(self):
        """Test invalid city/state validation."""
        assert LocationValidatorService.validate_city_state("", "CA") is False
        assert LocationValidatorService.validate_city_state("LA", "") is False
        assert LocationValidatorService.validate_city_state("  ", "  ") is False

    def test_validate_city_state_country_valid(self):
        """Test valid city/state/country validation."""
        assert (
            LocationValidatorService.validate_city_state_country("Toronto", "ON", "Canada") is True
        )
        assert (
            LocationValidatorService.validate_city_state_country("London", "England", "UK") is True
        )

    def test_validate_city_state_country_invalid(self):
        """Test invalid city/state/country validation."""
        assert LocationValidatorService.validate_city_state_country("", "ON", "Canada") is False
        assert (
            LocationValidatorService.validate_city_state_country("Toronto", "", "Canada") is False
        )
        assert LocationValidatorService.validate_city_state_country("Toronto", "ON", "") is False


class TestWeatherUnitsService:
    """Test WeatherUnitsService."""

    def test_get_temperature_unit_for_us_location(self):
        """Test temperature unit for US locations."""
        us_location = Location(city="LA", state="CA", country="US")
        zipcode_location = Location(city="Beverly Hills", zipcode="90210")

        assert (
            WeatherUnitsService.get_temperature_unit_for_location(us_location)
            == TemperatureUnit.FAHRENHEIT
        )
        assert (
            WeatherUnitsService.get_temperature_unit_for_location(zipcode_location)
            == TemperatureUnit.FAHRENHEIT
        )

    def test_get_temperature_unit_for_international_location(self):
        """Test temperature unit for international locations."""
        international_location = Location(city="Toronto", state="ON", country="Canada")

        assert (
            WeatherUnitsService.get_temperature_unit_for_location(international_location)
            == TemperatureUnit.CELSIUS
        )

    def test_get_speed_unit_for_us_location(self):
        """Test speed unit for US locations."""
        us_location = Location(city="LA", state="CA", country="US")

        assert WeatherUnitsService.get_speed_unit_for_location(us_location) == "mph"

    def test_get_speed_unit_for_international_location(self):
        """Test speed unit for international locations."""
        international_location = Location(city="Toronto", state="ON", country="Canada")

        assert WeatherUnitsService.get_speed_unit_for_location(international_location) == "km/h"

    def test_get_distance_unit_for_us_location(self):
        """Test distance unit for US locations."""
        us_location = Location(city="LA", state="CA", country="US")

        assert WeatherUnitsService.get_distance_unit_for_location(us_location) == "miles"

    def test_get_distance_unit_for_international_location(self):
        """Test distance unit for international locations."""
        international_location = Location(city="Toronto", state="ON", country="Canada")

        assert WeatherUnitsService.get_distance_unit_for_location(international_location) == "km"
