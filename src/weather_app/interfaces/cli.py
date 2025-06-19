"""CLI interface for the weather application."""

import asyncio
import click
import structlog
from typing import Optional

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


@click.group()
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose logging')
def cli(verbose: bool):
    """Weather Multi-Interface Application CLI.
    
    Get current weather and 3-day forecasts for any location worldwide.
    """
    if verbose:
        import logging
        logging.basicConfig(level=logging.DEBUG)


@cli.command()
@click.option('--zipcode', '-z', help='US zipcode (e.g., 90210)')
@click.option('--city', '-c', help='City name')
@click.option('--state', '-s', help='State or province')
@click.option('--country', '-C', help='Country name or code')
def weather(zipcode: Optional[str], city: Optional[str], state: Optional[str], country: Optional[str]):
    """Get current weather and forecast for a location.
    
    Examples:
        weather --zipcode 90210
        weather --city "Los Angeles" --state "CA"
        weather --city "Toronto" --state "ON" --country "CA"
    """
    asyncio.run(get_weather_async(zipcode, city, state, country))


async def get_weather_async(zipcode: Optional[str], city: Optional[str], state: Optional[str], country: Optional[str]):
    """Async function to get weather data."""
    try:
        # Create request DTO
        request = WeatherRequestDto(
            zipcode=zipcode,
            city=city,
            state=state,
            country=country
        )
        
        # Validate request
        if not request.validate():
            click.echo("❌ Error: Please provide either a zipcode or city with state/country")
            click.echo("Examples:")
            click.echo("  weather --zipcode 90210")
            click.echo("  weather --city 'Los Angeles' --state 'CA'")
            click.echo("  weather --city 'Toronto' --state 'ON' --country 'CA'")
            return
        
        # Initialize services
        weather_repo = OpenMeteoWeatherRepository()
        location_repo = OpenMeteoLocationRepository()
        weather_service = WeatherService(weather_repo, location_repo)
        
        # Get weather data
        click.echo("🌤️  Fetching weather data...")
        response = await weather_service.get_weather_forecast(request)
        
        # Display results
        display_weather_results(response)
        
    except InvalidLocationFormatError as e:
        logger.error("Invalid location format", error=str(e))
        click.echo(f"❌ Invalid location format: {e}")
    except LocationNotFoundError as e:
        logger.error("Location not found", error=str(e))
        click.echo(f"❌ Location not found: {e}")
    except WeatherDataUnavailableError as e:
        logger.error("Weather data unavailable", error=str(e))
        click.echo(f"❌ Weather data unavailable: {e}")
    except NetworkError as e:
        logger.error("Network error", error=str(e))
        click.echo(f"❌ Network error: {e}")
    except WeatherAppException as e:
        logger.error("Weather app error", error=str(e))
        click.echo(f"❌ Error: {e}")
    except Exception as e:  # pylint: disable=broad-except
        logger.exception("Unexpected error")
        click.echo(f"❌ Unexpected error: {e}")


def display_weather_results(response):
    """Display weather results in a nice format."""
    click.echo()
    click.echo(f"📍 Location: {response.location}")
    click.echo(f"🕐 Last updated: {response.timestamp}")
    click.echo()
    
    # Current weather
    click.echo("🌡️  Current Weather")
    click.echo("─" * 40)
    click.echo(f"Temperature: {response.current_temperature}")
    click.echo(f"Feels like: {response.feels_like}")
    click.echo(f"Condition: {response.description.title()}")
    click.echo(f"Humidity: {response.humidity}%")
    click.echo(f"Pressure: {response.pressure} hPa")
    click.echo(f"Visibility: {response.visibility}")
    click.echo(f"Wind: {response.wind_speed} {response.wind_direction}")
    click.echo()
    
    # Daily forecast
    if response.daily_forecasts:
        click.echo("📅 3-Day Forecast")
        click.echo("─" * 40)
        
        for day in response.daily_forecasts:
            click.echo(f"{day['day_name']:<10} {day['high_temperature']:<8} {day['low_temperature']:<8} {day['description']}")
            click.echo(f"{'':10} Humidity: {day['humidity']}% | Wind: {day['wind_speed']} | Rain: {day['precipitation_chance']}")
            click.echo()
    
    # Units info
    click.echo(f"📏 Units: Temperature in {response.units['temperature']}, "
               f"Speed in {response.units['speed']}, Distance in {response.units['distance']}")


def main():
    """Main entry point for CLI."""
    import sys
    cli(sys.argv[1:])


if __name__ == '__main__':
    main()
