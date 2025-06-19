"""MCP (Model Context Protocol) server interface for VS Code integration."""

import asyncio
import structlog
from typing import Dict, Any, Optional
from fastmcp import FastMCP

from weather_app.application.services import WeatherService
from weather_app.application.dtos import WeatherRequestDto
from weather_app.infrastructure.weather_api import OpenMeteoWeatherRepository
from weather_app.infrastructure.location_service import OpenMeteoLocationRepository
from weather_app.domain.exceptions import (
    WeatherAppException,
    LocationNotFoundError,
    InvalidLocationFormatError,
    WeatherDataUnavailableError,
    NetworkError
)


# Configure logging
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.JSONRenderer()
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger(__name__)


# Initialize MCP server
mcp = FastMCP("Weather Multi-App MCP Server")

# Initialize services
weather_repo = OpenMeteoWeatherRepository()
location_repo = OpenMeteoLocationRepository()
weather_service = WeatherService(weather_repo, location_repo)


@mcp.tool()
async def get_weather_by_zipcode(zipcode: str) -> Dict[str, Any]:
    """Get current weather and 3-day forecast by US zipcode.
    
    Args:
        zipcode: US zipcode (e.g., "90210" or "90210-1234")
    
    Returns:
        Weather data including current conditions and 3-day forecast
    """
    logger.info("MCP: Getting weather by zipcode", zipcode=zipcode)
    
    try:
        request = WeatherRequestDto(zipcode=zipcode)
        response = await weather_service.get_weather_forecast(request)
        
        return {
            "status": "success",
            "location": response.location,
            "current": {
                "temperature": response.current_temperature,
                "feels_like": response.feels_like,
                "condition": response.condition,
                "description": response.description,
                "humidity": response.humidity,
                "pressure": response.pressure,
                "visibility": response.visibility,
                "wind_speed": response.wind_speed,
                "wind_direction": response.wind_direction,
                "timestamp": response.timestamp
            },
            "forecast": response.daily_forecasts,
            "units": response.units
        }
        
    except InvalidLocationFormatError as e:
        logger.error("MCP: Invalid zipcode format", error=str(e))
        return {"status": "error", "error": f"Invalid zipcode format: {e}"}
    except LocationNotFoundError as e:
        logger.error("MCP: Zipcode not found", error=str(e))
        return {"status": "error", "error": f"Zipcode not found: {e}"}
    except WeatherDataUnavailableError as e:
        logger.error("MCP: Weather data unavailable", error=str(e))
        return {"status": "error", "error": f"Weather data unavailable: {e}"}
    except NetworkError as e:
        logger.error("MCP: Network error", error=str(e))
        return {"status": "error", "error": f"Network error: {e}"}
    except WeatherAppException as e:
        logger.error("MCP: Weather app error", error=str(e))
        return {"status": "error", "error": str(e)}
    except Exception as e:  # pylint: disable=broad-except
        logger.exception("MCP: Unexpected error")
        return {"status": "error", "error": f"Unexpected error: {e}"}


@mcp.tool()
async def get_weather_by_city(
    city: str, 
    state: Optional[str] = None, 
    country: Optional[str] = None
) -> Dict[str, Any]:
    """Get current weather and 3-day forecast by city, state, and country.
    
    Args:
        city: City name (e.g., "Los Angeles")
        state: State or province (e.g., "CA" or "Ontario")
        country: Country name or code (e.g., "USA", "Canada", "UK")
    
    Returns:
        Weather data including current conditions and 3-day forecast
    """
    logger.info("MCP: Getting weather by city", city=city, state=state, country=country)
    
    try:
        request = WeatherRequestDto(city=city, state=state, country=country)
        response = await weather_service.get_weather_forecast(request)
        
        return {
            "status": "success",
            "location": response.location,
            "current": {
                "temperature": response.current_temperature,
                "feels_like": response.feels_like,
                "condition": response.condition,
                "description": response.description,
                "humidity": response.humidity,
                "pressure": response.pressure,
                "visibility": response.visibility,
                "wind_speed": response.wind_speed,
                "wind_direction": response.wind_direction,
                "timestamp": response.timestamp
            },
            "forecast": response.daily_forecasts,
            "units": response.units
        }
        
    except InvalidLocationFormatError as e:
        logger.error("MCP: Invalid location format", error=str(e))
        return {"status": "error", "error": f"Invalid location format: {e}"}
    except LocationNotFoundError as e:
        logger.error("MCP: Location not found", error=str(e))
        return {"status": "error", "error": f"Location not found: {e}"}
    except WeatherDataUnavailableError as e:
        logger.error("MCP: Weather data unavailable", error=str(e))
        return {"status": "error", "error": f"Weather data unavailable: {e}"}
    except NetworkError as e:
        logger.error("MCP: Network error", error=str(e))
        return {"status": "error", "error": f"Network error: {e}"}
    except WeatherAppException as e:
        logger.error("MCP: Weather app error", error=str(e))
        return {"status": "error", "error": str(e)}
    except Exception as e:  # pylint: disable=broad-except
        logger.exception("MCP: Unexpected error")
        return {"status": "error", "error": f"Unexpected error: {e}"}


@mcp.tool()
async def get_weather_summary(location_query: str) -> str:
    """Get a concise weather summary for any location.
    
    Args:
        location_query: Location query (zipcode, "city, state", or "city, state, country")
    
    Returns:
        Human-readable weather summary
    """
    logger.info("MCP: Getting weather summary", query=location_query)
    
    try:
        # Parse location query
        parts = [part.strip() for part in location_query.split(',')]
        
        if len(parts) == 1:
            # Assume zipcode if it's all digits, otherwise city only
            if parts[0].replace('-', '').isdigit():
                request = WeatherRequestDto(zipcode=parts[0])
            else:
                request = WeatherRequestDto(city=parts[0])
        elif len(parts) == 2:
            request = WeatherRequestDto(city=parts[0], state=parts[1])
        elif len(parts) >= 3:
            request = WeatherRequestDto(city=parts[0], state=parts[1], country=parts[2])
        else:
            return "Error: Invalid location format. Use zipcode, 'city, state', or 'city, state, country'"
        
        response = await weather_service.get_weather_forecast(request)
        
        # Create summary
        summary = f"Weather for {response.location}:\n"
        summary += f"Current: {response.current_temperature} ({response.description})\n"
        summary += f"Feels like: {response.feels_like}\n"
        summary += f"Humidity: {response.humidity}%\n"
        summary += f"Wind: {response.wind_speed} {response.wind_direction}\n\n"
        
        if response.daily_forecasts:
            summary += "3-Day Forecast:\n"
            for day in response.daily_forecasts:
                summary += f"{day['day_name']}: {day['high_temperature']}/{day['low_temperature']} - {day['description']}\n"
        
        summary += f"\nUnits: {response.units['temperature']}, {response.units['speed']}, {response.units['distance']}"
        summary += f"\nLast updated: {response.timestamp}"
        
        return summary
        
    except Exception as e:  # pylint: disable=broad-except
        logger.exception("MCP: Error getting weather summary")
        return f"Error getting weather: {e}"


def main():
    """Main entry point for MCP server."""
    print("Starting Weather Multi-App MCP Server...")
    print("Available tools:")
    print("- get_weather_by_zipcode: Get weather by US zipcode")
    print("- get_weather_by_city: Get weather by city/state/country")
    print("- get_weather_summary: Get human-readable weather summary")
    
    # Run the MCP server
    mcp.run()


if __name__ == '__main__':
    main()
