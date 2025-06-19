#!/usr/bin/env python3
"""
Demo script for Weather Multi-App

This script demonstrates all three interfaces of the weather application.
"""

import asyncio
import time
from weather_app.application.services import WeatherService
from weather_app.application.dtos import WeatherRequestDto
from weather_app.infrastructure.weather_api import OpenMeteoWeatherRepository
from weather_app.infrastructure.location_service import OpenMeteoLocationRepository


async def demo_api():
    """Demonstrate the core API functionality."""
    print("🌤️  Weather Multi-App Demo")
    print("=" * 50)

    # Initialize services
    weather_repo = OpenMeteoWeatherRepository()
    location_repo = OpenMeteoLocationRepository()
    service = WeatherService(weather_repo, location_repo)

    # Test different location formats
    test_locations = [
        WeatherRequestDto(city="London", country="UK"),
        WeatherRequestDto(city="Tokyo", country="Japan"),
        WeatherRequestDto(city="New York", state="NY"),
    ]

    for request in test_locations:
        try:
            print(f"\n🌍 Fetching weather for {request.city}...")
            response = await service.get_weather_forecast(request)

            print(f"📍 Location: {response.location}")
            print(f"🌡️  Current: {response.current_temperature} (feels like {response.feels_like})")
            print(f"🌤️  Condition: {response.description}")
            print(f"💨 Wind: {response.wind_speed} {response.wind_direction}")
            print(f"💧 Humidity: {response.humidity}%")
            print(f"📅 {len(response.daily_forecasts)}-day forecast available")

            # Show first forecast day
            if response.daily_forecasts:
                forecast = response.daily_forecasts[0]
                print(
                    f"   Tomorrow: {forecast['high_temperature']}/{forecast['low_temperature']} - {forecast['description']}"
                )

        except Exception as e:
            print(f"❌ Error for {request.city}: {e}")

        # Small delay between requests
        await asyncio.sleep(1)


def demo_cli():
    """Demonstrate CLI usage."""
    print("\n" + "=" * 50)
    print("🖥️  CLI Interface Demo")
    print("=" * 50)
    print("To use the CLI interface:")
    print()
    print("# Install the package")
    print("pip install -e .")
    print()
    print("# Get weather by zipcode")
    print("python -m weather_app cli weather --zipcode 90210")
    print()
    print("# Get weather by city and state")
    print("python -m weather_app cli weather --city 'Los Angeles' --state 'CA'")
    print()
    print("# Get weather for international location")
    print("python -m weather_app cli weather --city 'London' --country 'UK'")


def demo_web():
    """Demonstrate web interface."""
    print("\n" + "=" * 50)
    print("🌐 Web Interface Demo")
    print("=" * 50)
    print("To use the web interface:")
    print()
    print("# Start the web server")
    print("python -m weather_app web --host 0.0.0.0 --port 5000")
    print()
    print("# Then visit: http://localhost:5000")
    print()
    print("Features:")
    print("- Beautiful responsive UI with Bootstrap")
    print("- Support for all location formats")
    print("- Interactive forms with validation")
    print("- Mobile-friendly design")
    print("- Real-time weather icons")


def demo_mcp():
    """Demonstrate MCP server."""
    print("\n" + "=" * 50)
    print("🔌 MCP Server Demo")
    print("=" * 50)
    print("To use the MCP server with VS Code:")
    print()
    print("# Start the MCP server")
    print("python -m weather_app mcp")
    print()
    print("# Configure in VS Code MCP settings:")
    print("# Add the server endpoint to your MCP configuration")
    print()
    print("Available MCP tools:")
    print("- get_weather_by_zipcode: Get weather by US zipcode")
    print("- get_weather_by_city: Get weather by city/state/country")
    print("- get_weather_summary: Get human-readable weather summary")


def main():
    """Run the complete demo."""
    print("🚀 Starting Weather Multi-App Demo...")
    print("This may take a moment as we make real API calls...")

    # Demo API functionality
    try:
        asyncio.run(demo_api())
    except KeyboardInterrupt:
        print("\n❌ Demo interrupted by user")
    except Exception as e:
        print(f"\n❌ Demo failed: {e}")

    # Demo other interfaces (instructions only)
    demo_cli()
    demo_web()
    demo_mcp()

    print("\n" + "=" * 50)
    print("🎉 Demo complete!")
    print("Check out the GitHub repository: https://github.com/devopsjester/weather-multi-app")
    print("=" * 50)


if __name__ == "__main__":
    main()
