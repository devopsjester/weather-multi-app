"""Unit tests for domain models."""

import pytest
from datetime import datetime

from weather_app.domain.models import (
    Location, Temperature, TemperatureUnit, WeatherCondition,
    WeatherData, DailyForecast, WeatherForecast
)


class TestLocation:
    """Test Location model."""
    
    def test_location_with_zipcode(self):
        """Test location creation with zipcode."""
        location = Location(city="Beverly Hills", state="CA", zipcode="90210")
        assert location.zipcode == "90210"
        assert location.is_us_location is True
        assert "90210" in location.display_name
    
    def test_location_with_city_state(self):
        """Test location creation with city and state."""
        location = Location(city="Los Angeles", state="CA")
        assert location.city == "Los Angeles"
        assert location.state == "CA"
        assert location.zipcode is None
    
    def test_location_with_country(self):
        """Test location creation with country."""
        location = Location(city="Toronto", state="ON", country="Canada")
        assert location.country == "Canada"
        assert location.is_us_location is False
    
    def test_location_validation_failure(self):
        """Test location validation fails with insufficient data."""
        with pytest.raises(ValueError):
            Location(city="", state="", country="")
    
    def test_us_location_detection(self):
        """Test US location detection."""
        us_location1 = Location(city="LA", state="CA", country="US")
        us_location2 = Location(city="NY", state="NY", country="USA")
        us_location3 = Location(city="Chicago", zipcode="60601")
        
        assert us_location1.is_us_location is True
        assert us_location2.is_us_location is True
        assert us_location3.is_us_location is True
    
    def test_display_name_formats(self):
        """Test different display name formats."""
        zipcode_location = Location(city="Beverly Hills", state="CA", zipcode="90210")
        city_state_location = Location(city="Los Angeles", state="CA")
        international_location = Location(city="Toronto", state="ON", country="Canada")
        
        assert "90210" in zipcode_location.display_name
        assert "Los Angeles, CA" in city_state_location.display_name
        assert "Toronto, ON, Canada" in international_location.display_name


class TestTemperature:
    """Test Temperature model."""
    
    def test_temperature_creation(self):
        """Test temperature creation."""
        temp = Temperature(25.0, TemperatureUnit.CELSIUS)
        assert temp.value == 25.0
        assert temp.unit == TemperatureUnit.CELSIUS
    
    def test_celsius_to_fahrenheit(self):
        """Test Celsius to Fahrenheit conversion."""
        temp_c = Temperature(25.0, TemperatureUnit.CELSIUS)
        temp_f = temp_c.to_fahrenheit()
        assert abs(temp_f - 77.0) < 0.1  # 25°C = 77°F
    
    def test_fahrenheit_to_celsius(self):
        """Test Fahrenheit to Celsius conversion."""
        temp_f = Temperature(77.0, TemperatureUnit.FAHRENHEIT)
        temp_c = temp_f.to_celsius()
        assert abs(temp_c - 25.0) < 0.1  # 77°F = 25°C
    
    def test_temperature_unit_conversion(self):
        """Test temperature unit conversion."""
        temp_c = Temperature(0.0, TemperatureUnit.CELSIUS)
        temp_f = temp_c.to_unit(TemperatureUnit.FAHRENHEIT)
        
        assert temp_f.unit == TemperatureUnit.FAHRENHEIT
        assert temp_f.value == 32.0  # 0°C = 32°F
    
    def test_temperature_string_representation(self):
        """Test temperature string representation."""
        temp_c = Temperature(25.5, TemperatureUnit.CELSIUS)
        temp_f = Temperature(77.9, TemperatureUnit.FAHRENHEIT)
        
        assert "25.5°C" in str(temp_c)
        assert "77.9°F" in str(temp_f)


class TestWeatherData:
    """Test WeatherData model."""
    
    def test_weather_data_creation(self, sample_location, sample_temperature):
        """Test weather data creation."""
        weather = WeatherData(
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
            timestamp=datetime.now()
        )
        
        assert weather.location == sample_location
        assert weather.temperature == sample_temperature
        assert weather.humidity == 65
        assert weather.condition == WeatherCondition.CLEAR
    
    def test_wind_direction_text(self, sample_weather_data, sample_location, sample_temperature):
        """Test wind direction text conversion."""
        # South wind (180 degrees)
        assert sample_weather_data.wind_direction_text == "S"
        
        # Test None wind direction
        weather_with_no_wind = WeatherData(
            location=sample_location,
            temperature=sample_temperature,
            feels_like=Temperature(27.0, TemperatureUnit.CELSIUS),
            humidity=65,
            pressure=1013,
            visibility=10.0,
            wind_speed=15.5,
            wind_direction=None,  # No wind direction
            condition=WeatherCondition.CLEAR,
            description="Clear sky",
            timestamp=datetime.now()
        )
        assert weather_with_no_wind.wind_direction_text == "N/A"


class TestDailyForecast:
    """Test DailyForecast model."""
    
    def test_daily_forecast_creation(self, sample_daily_forecast):
        """Test daily forecast creation."""
        assert sample_daily_forecast.high_temperature.value == 28.0
        assert sample_daily_forecast.low_temperature.value == 18.0
        assert sample_daily_forecast.condition == WeatherCondition.CLEAR
        assert sample_daily_forecast.precipitation_chance == 10
    
    def test_day_name(self, sample_daily_forecast):
        """Test day name property."""
        day_name = sample_daily_forecast.day_name
        assert day_name in ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]


class TestWeatherForecast:
    """Test WeatherForecast model."""
    
    def test_weather_forecast_creation(self, sample_weather_forecast):
        """Test weather forecast creation."""
        assert sample_weather_forecast.location.city == "Los Angeles"
        assert len(sample_weather_forecast.daily_forecasts) == 1
        assert isinstance(sample_weather_forecast.timestamp, datetime)
    
    def test_forecast_validation_too_many_days(self, sample_location, sample_weather_data):
        """Test forecast validation fails with too many days."""
        too_many_forecasts = [DailyForecast(
            date=datetime.now(),
            high_temperature=Temperature(25.0, TemperatureUnit.CELSIUS),
            low_temperature=Temperature(15.0, TemperatureUnit.CELSIUS),
            condition=WeatherCondition.CLEAR,
            description="Sunny",
            humidity=60,
            wind_speed=10.0,
            precipitation_chance=0
        ) for _ in range(6)]  # 6 days is too many
        
        with pytest.raises(ValueError, match="Forecast cannot exceed 5 days"):
            WeatherForecast(
                location=sample_location,
                current_weather=sample_weather_data,
                daily_forecasts=too_many_forecasts,
                timestamp=datetime.now()
            )
    
    def test_forecast_validation_no_days(self, sample_location, sample_weather_data):
        """Test forecast validation fails with no days."""
        with pytest.raises(ValueError, match="Forecast must contain at least one day"):
            WeatherForecast(
                location=sample_location,
                current_weather=sample_weather_data,
                daily_forecasts=[],
                timestamp=datetime.now()
            )
