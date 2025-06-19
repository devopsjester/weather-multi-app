"""Unit tests for application services."""

import pytest
from unittest.mock import AsyncMock
from datetime import datetime

from weather_app.application.services import WeatherService
from weather_app.application.dtos import WeatherRequestDto
from weather_app.domain.models import Location, WeatherForecast, TemperatureUnit
from weather_app.domain.exceptions import InvalidLocationFormatError


@pytest.mark.asyncio
class TestWeatherService:
    """Test WeatherService."""
    
    async def test_get_weather_forecast_success(
        self, 
        mock_weather_repository, 
        mock_location_repository,
        sample_location,
        sample_weather_forecast
    ):
        """Test successful weather forecast retrieval."""
        # Arrange
        request = WeatherRequestDto(zipcode="90210")
        mock_location_repository.resolve_location.return_value = sample_location
        mock_weather_repository.get_current_weather.return_value = sample_weather_forecast
        
        service = WeatherService(mock_weather_repository, mock_location_repository)
        
        # Act
        response = await service.get_weather_forecast(request)
        
        # Assert
        assert response.location == sample_location.display_name
        mock_location_repository.resolve_location.assert_called_once()
        mock_weather_repository.get_current_weather.assert_called_once()
    
    async def test_get_weather_forecast_invalid_request(
        self, 
        mock_weather_repository, 
        mock_location_repository
    ):
        """Test weather forecast with invalid request."""
        # Arrange
        invalid_request = WeatherRequestDto()  # No location data
        service = WeatherService(mock_weather_repository, mock_location_repository)
        
        # Act & Assert
        with pytest.raises(InvalidLocationFormatError):
            await service.get_weather_forecast(invalid_request)
    
    async def test_create_location_from_request_zipcode(
        self, 
        mock_weather_repository, 
        mock_location_repository
    ):
        """Test location creation from zipcode request."""
        # Arrange
        request = WeatherRequestDto(zipcode="90210")
        service = WeatherService(mock_weather_repository, mock_location_repository)
        
        # Act
        location = service._create_location_from_request(request)
        
        # Assert
        assert location.zipcode == "90210"
        assert location.city == ""
    
    async def test_create_location_from_request_city_state(
        self, 
        mock_weather_repository, 
        mock_location_repository
    ):
        """Test location creation from city/state request."""
        # Arrange
        request = WeatherRequestDto(city="Los Angeles", state="CA")
        service = WeatherService(mock_weather_repository, mock_location_repository)
        
        # Act
        location = service._create_location_from_request(request)
        
        # Assert
        assert location.city == "Los Angeles"
        assert location.state == "CA"
        assert location.zipcode is None
    
    async def test_validate_location_format_valid_zipcode(
        self, 
        mock_weather_repository, 
        mock_location_repository
    ):
        """Test location format validation for valid zipcode."""
        # Arrange
        location = Location(city="", zipcode="90210")
        service = WeatherService(mock_weather_repository, mock_location_repository)
        
        # Act & Assert (should not raise)
        service._validate_location_format(location)
    
    async def test_validate_location_format_invalid_zipcode(
        self, 
        mock_weather_repository, 
        mock_location_repository
    ):
        """Test location format validation for invalid zipcode."""
        # Arrange
        location = Location(city="", zipcode="invalid")
        service = WeatherService(mock_weather_repository, mock_location_repository)
        
        # Act & Assert
        with pytest.raises(InvalidLocationFormatError):
            service._validate_location_format(location)
    
    async def test_convert_to_response_dto(
        self, 
        mock_weather_repository, 
        mock_location_repository,
        sample_weather_forecast
    ):
        """Test conversion to response DTO."""
        # Arrange
        service = WeatherService(mock_weather_repository, mock_location_repository)
        
        # Act
        response = service._convert_to_response_dto(sample_weather_forecast)
        
        # Assert
        assert response.location == sample_weather_forecast.location.display_name
        assert len(response.daily_forecasts) == len(sample_weather_forecast.daily_forecasts)
        assert response.units["temperature"] in ["celsius", "fahrenheit"]
