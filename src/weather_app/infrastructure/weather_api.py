"""Free weather API implementation using Open-Meteo."""

from datetime import datetime
from typing import Any, Dict

import httpx
import structlog

from weather_app.domain.exceptions import (
    LocationNotFoundError,
    NetworkError,
    WeatherDataUnavailableError,
)
from weather_app.domain.models import (
    DailyForecast,
    Location,
    Temperature,
    TemperatureUnit,
    WeatherCondition,
    WeatherData,
    WeatherForecast,
)
from weather_app.domain.services import IWeatherRepository

logger = structlog.get_logger(__name__)


class OpenMeteoWeatherRepository(IWeatherRepository):
    """Weather repository using Open-Meteo free API."""

    def __init__(self, timeout: int = 30):
        self.base_url = "https://api.open-meteo.com/v1"
        self.timeout = timeout

        # Weather code mappings from Open-Meteo to our domain
        self.weather_code_map = {
            0: (WeatherCondition.CLEAR, "Clear sky"),
            1: (WeatherCondition.CLOUDS, "Mainly clear"),
            2: (WeatherCondition.CLOUDS, "Partly cloudy"),
            3: (WeatherCondition.CLOUDS, "Overcast"),
            45: (WeatherCondition.FOG, "Fog"),
            48: (WeatherCondition.FOG, "Depositing rime fog"),
            51: (WeatherCondition.DRIZZLE, "Light drizzle"),
            53: (WeatherCondition.DRIZZLE, "Moderate drizzle"),
            55: (WeatherCondition.DRIZZLE, "Dense drizzle"),
            56: (WeatherCondition.DRIZZLE, "Light freezing drizzle"),
            57: (WeatherCondition.DRIZZLE, "Dense freezing drizzle"),
            61: (WeatherCondition.RAIN, "Slight rain"),
            63: (WeatherCondition.RAIN, "Moderate rain"),
            65: (WeatherCondition.RAIN, "Heavy rain"),
            66: (WeatherCondition.RAIN, "Light freezing rain"),
            67: (WeatherCondition.RAIN, "Heavy freezing rain"),
            71: (WeatherCondition.SNOW, "Slight snow fall"),
            73: (WeatherCondition.SNOW, "Moderate snow fall"),
            75: (WeatherCondition.SNOW, "Heavy snow fall"),
            77: (WeatherCondition.SNOW, "Snow grains"),
            80: (WeatherCondition.RAIN, "Slight rain showers"),
            81: (WeatherCondition.RAIN, "Moderate rain showers"),
            82: (WeatherCondition.RAIN, "Violent rain showers"),
            85: (WeatherCondition.SNOW, "Slight snow showers"),
            86: (WeatherCondition.SNOW, "Heavy snow showers"),
            95: (WeatherCondition.THUNDERSTORM, "Thunderstorm"),
            96: (WeatherCondition.THUNDERSTORM, "Thunderstorm with slight hail"),
            99: (WeatherCondition.THUNDERSTORM, "Thunderstorm with heavy hail"),
        }

    async def get_current_weather(self, location: Location) -> WeatherForecast:
        """Get current weather and forecast from Open-Meteo API."""
        logger.info("Fetching weather data", location=location.display_name)

        if not location.latitude or not location.longitude:
            raise LocationNotFoundError(
                f"Location coordinates not available for {location.display_name}"
            )

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                # Prepare API parameters
                params = {
                    "latitude": location.latitude,
                    "longitude": location.longitude,
                    "current": [
                        "temperature_2m",
                        "relative_humidity_2m",
                        "apparent_temperature",
                        "is_day",
                        "precipitation",
                        "rain",
                        "showers",
                        "snowfall",
                        "weather_code",
                        "cloud_cover",
                        "pressure_msl",
                        "surface_pressure",
                        "wind_speed_10m",
                        "wind_direction_10m",
                        "wind_gusts_10m",
                        "visibility",
                    ],
                    "daily": [
                        "weather_code",
                        "temperature_2m_max",
                        "temperature_2m_min",
                        "apparent_temperature_max",
                        "apparent_temperature_min",
                        "precipitation_sum",
                        "rain_sum",
                        "showers_sum",
                        "snowfall_sum",
                        "precipitation_hours",
                        "precipitation_probability_max",
                        "wind_speed_10m_max",
                        "wind_gusts_10m_max",
                        "wind_direction_10m_dominant",
                    ],
                    "timezone": "auto",
                    "forecast_days": 3,
                }

                response = await client.get(f"{self.base_url}/forecast", params=params)
                response.raise_for_status()
                data = response.json()

                return self._parse_weather_data(data, location)

        except httpx.HTTPStatusError as e:
            logger.error("HTTP error fetching weather data", status_code=e.response.status_code)
            raise WeatherDataUnavailableError(
                f"Weather service error: {e.response.status_code}"
            ) from e
        except httpx.RequestError as e:
            logger.error("Network error fetching weather data", error=str(e))
            raise NetworkError(f"Network error: {str(e)}") from e
        except Exception as e:
            logger.error("Unexpected error fetching weather data", error=str(e))
            raise WeatherDataUnavailableError(f"Unexpected error: {str(e)}") from e

    def _parse_weather_data(self, data: Dict[str, Any], location: Location) -> WeatherForecast:
        """Parse Open-Meteo API response to domain models."""
        current_data = data["current"]
        daily_data = data["daily"]

        # Parse current weather
        current_weather = self._parse_current_weather(current_data, location)

        # Parse daily forecasts
        daily_forecasts = self._parse_daily_forecasts(daily_data)

        return WeatherForecast(
            location=location,
            current_weather=current_weather,
            daily_forecasts=daily_forecasts,
            timestamp=datetime.now(),
        )

    def _parse_current_weather(self, data: Dict[str, Any], location: Location) -> WeatherData:
        """Parse current weather data."""
        weather_code = data.get("weather_code", 0)
        condition, description = self.weather_code_map.get(
            weather_code, (WeatherCondition.UNKNOWN, "Unknown")
        )

        # Temperatures are in Celsius from Open-Meteo
        temperature = Temperature(data.get("temperature_2m", 0), TemperatureUnit.CELSIUS)
        feels_like = Temperature(data.get("apparent_temperature", 0), TemperatureUnit.CELSIUS)

        return WeatherData(
            location=location,
            temperature=temperature,
            feels_like=feels_like,
            humidity=int(data.get("relative_humidity_2m", 0)),
            pressure=int(data.get("pressure_msl", 0)),
            visibility=data.get("visibility", 0) / 1000,  # Convert m to km
            wind_speed=data.get("wind_speed_10m", 0),  # km/h
            wind_direction=data.get("wind_direction_10m"),
            condition=condition,
            description=description,
            timestamp=datetime.fromisoformat(data["time"]),
        )

    def _parse_daily_forecasts(self, data: Dict[str, Any]) -> list[DailyForecast]:
        """Parse daily forecast data."""
        forecasts = []

        dates = data["time"]
        weather_codes = data["weather_code"]
        max_temps = data["temperature_2m_max"]
        min_temps = data["temperature_2m_min"]
        precipitation_probs = data.get("precipitation_probability_max", [0] * len(dates))
        wind_speeds = data.get("wind_speed_10m_max", [0] * len(dates))

        for i, date_str in enumerate(dates):
            date = datetime.fromisoformat(date_str)
            weather_code = weather_codes[i]
            condition, description = self.weather_code_map.get(
                weather_code, (WeatherCondition.UNKNOWN, "Unknown")
            )

            forecast = DailyForecast(
                date=date,
                high_temperature=Temperature(max_temps[i], TemperatureUnit.CELSIUS),
                low_temperature=Temperature(min_temps[i], TemperatureUnit.CELSIUS),
                condition=condition,
                description=description,
                humidity=50,  # Open-Meteo doesn't provide daily humidity average
                wind_speed=wind_speeds[i],
                precipitation_chance=int(precipitation_probs[i]) if precipitation_probs[i] else 0,
            )
            forecasts.append(forecast)

        return forecasts
