"""Application services - Use cases and business logic orchestration."""

import structlog

from weather_app.domain.models import Location, WeatherForecast
from weather_app.domain.services import (
    IWeatherRepository,
    ILocationRepository,
    LocationValidatorService,
    WeatherUnitsService,
)
from weather_app.domain.exceptions import InvalidLocationFormatError
from weather_app.application.dtos import WeatherRequestDto, WeatherResponseDto


logger = structlog.get_logger(__name__)


class WeatherService:
    """Application service for weather operations."""

    def __init__(
        self, weather_repository: IWeatherRepository, location_repository: ILocationRepository
    ):
        self.weather_repository = weather_repository
        self.location_repository = location_repository
        self.validator = LocationValidatorService()
        self.units_service = WeatherUnitsService()

    async def get_weather_forecast(self, request: WeatherRequestDto) -> WeatherResponseDto:
        """Get weather forecast for a location."""
        logger.info("Processing weather request", request=request)

        # Validate request
        if not request.validate():
            raise InvalidLocationFormatError(
                "Request must include either zipcode or city with state/country"
            )

        # Create location object
        location = self._create_location_from_request(request)

        # Validate location format
        self._validate_location_format(location)

        # Resolve location to get coordinates
        resolved_location = await self.location_repository.resolve_location(location)

        # Get weather data
        forecast = await self.weather_repository.get_current_weather(resolved_location)

        # Convert to response DTO
        response = self._convert_to_response_dto(forecast)

        logger.info(
            "Weather request processed successfully", location=resolved_location.display_name
        )
        return response

    def _create_location_from_request(self, request: WeatherRequestDto) -> Location:
        """Create a Location object from the request DTO."""
        return Location(
            city=request.city or "",
            state=request.state,
            country=request.country,
            zipcode=request.zipcode,
        )

    def _validate_location_format(self, location: Location) -> None:
        """Validate location format."""
        if location.zipcode:
            if not self.validator.validate_zipcode(location.zipcode):
                raise InvalidLocationFormatError(f"Invalid zipcode format: {location.zipcode}")
        elif location.city and location.state and not location.country:
            if not self.validator.validate_city_state(location.city, location.state):
                raise InvalidLocationFormatError("City and state cannot be empty")
        elif location.city and location.state and location.country:
            if not self.validator.validate_city_state_country(
                location.city, location.state, location.country
            ):
                raise InvalidLocationFormatError("City, state, and country cannot be empty")
        else:
            raise InvalidLocationFormatError("Invalid location format")

    def _convert_to_response_dto(self, forecast: WeatherForecast) -> WeatherResponseDto:
        """Convert domain model to response DTO."""
        location = forecast.location
        current = forecast.current_weather

        # Get appropriate units for location
        temp_unit = self.units_service.get_temperature_unit_for_location(location)
        speed_unit = self.units_service.get_speed_unit_for_location(location)
        distance_unit = self.units_service.get_distance_unit_for_location(location)

        # Convert temperatures to appropriate unit
        current_temp = current.temperature.to_unit(temp_unit)
        feels_like_temp = current.feels_like.to_unit(temp_unit)

        # Format daily forecasts
        daily_forecasts = []
        for day in forecast.daily_forecasts:
            high_temp = day.high_temperature.to_unit(temp_unit)
            low_temp = day.low_temperature.to_unit(temp_unit)
            daily_forecasts.append(
                {
                    "date": day.date.strftime("%Y-%m-%d"),
                    "day_name": day.day_name,
                    "high_temperature": str(high_temp),
                    "low_temperature": str(low_temp),
                    "condition": day.condition.value,
                    "description": day.description,
                    "humidity": day.humidity,
                    "wind_speed": f"{day.wind_speed:.1f} {speed_unit}",
                    "precipitation_chance": f"{day.precipitation_chance}%",
                }
            )

        return WeatherResponseDto(
            location=location.display_name,
            current_temperature=str(current_temp),
            feels_like=str(feels_like_temp),
            condition=current.condition.value,
            description=current.description,
            humidity=current.humidity,
            pressure=current.pressure,
            visibility=f"{current.visibility:.1f} {distance_unit}",
            wind_speed=f"{current.wind_speed:.1f} {speed_unit}",
            wind_direction=current.wind_direction_text,
            timestamp=current.timestamp.strftime("%Y-%m-%d %H:%M:%S"),
            daily_forecasts=daily_forecasts,
            units={"temperature": temp_unit.value, "speed": speed_unit, "distance": distance_unit},
        )
