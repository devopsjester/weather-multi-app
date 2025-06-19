"""Test configuration and fixtures."""

import pytest
import asyncio
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock

from weather_app.domain.models import (
    Location,
    WeatherData,
    DailyForecast,
    WeatherForecast,
    Temperature,
    TemperatureUnit,
    WeatherCondition,
)


@pytest.fixture
def sample_location():
    """Sample location for testing."""
    return Location(
        city="Los Angeles",
        state="CA",
        country="US",
        zipcode="90210",
        latitude=34.0901,
        longitude=-118.4065,
    )


@pytest.fixture
def sample_temperature():
    """Sample temperature for testing."""
    return Temperature(value=25.0, unit=TemperatureUnit.CELSIUS)


@pytest.fixture
def sample_weather_data(sample_location, sample_temperature):
    """Sample weather data for testing."""
    return WeatherData(
        location=sample_location,
        temperature=sample_temperature,
        feels_like=Temperature(27.0, TemperatureUnit.CELSIUS),
        humidity=65,
        pressure=1013,
        visibility=10.0,
        wind_speed=15.5,
        wind_direction=180,
        condition=WeatherCondition.CLEAR,
        description="Clear sky",
        timestamp=datetime.now(),
    )


@pytest.fixture
def sample_daily_forecast():
    """Sample daily forecast for testing."""
    return DailyForecast(
        date=datetime.now(),
        high_temperature=Temperature(28.0, TemperatureUnit.CELSIUS),
        low_temperature=Temperature(18.0, TemperatureUnit.CELSIUS),
        condition=WeatherCondition.CLEAR,
        description="Sunny",
        humidity=60,
        wind_speed=12.0,
        precipitation_chance=10,
    )


@pytest.fixture
def sample_weather_forecast(sample_location, sample_weather_data, sample_daily_forecast):
    """Sample weather forecast for testing."""
    return WeatherForecast(
        location=sample_location,
        current_weather=sample_weather_data,
        daily_forecasts=[sample_daily_forecast],
        timestamp=datetime.now(),
    )


@pytest.fixture
def mock_weather_repository():
    """Mock weather repository."""
    return AsyncMock()


@pytest.fixture
def mock_location_repository():
    """Mock location repository."""
    return AsyncMock()


@pytest.fixture
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()
