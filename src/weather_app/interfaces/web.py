"""Flask web interface for the weather application."""

import asyncio
import structlog
from flask import Flask, render_template, request, jsonify, flash, redirect, url_for
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
    NetworkError,
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
        structlog.processors.JSONRenderer(),
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger(__name__)


def create_app():
    """Create and configure the Flask application."""
    app = Flask(__name__, template_folder="templates")
    app.secret_key = "dev-secret-key-change-in-production"

    # Initialize services
    weather_repo = OpenMeteoWeatherRepository()
    location_repo = OpenMeteoLocationRepository()
    weather_service = WeatherService(weather_repo, location_repo)

    @app.route("/")
    def index():
        """Home page with search form."""
        return render_template("index.html")

    @app.route("/weather", methods=["GET", "POST"])
    def weather():
        """Weather results page."""
        if request.method == "GET":
            return redirect(url_for("index"))

        # Get form data
        zipcode = request.form.get("zipcode", "").strip() or None
        city = request.form.get("city", "").strip() or None
        state = request.form.get("state", "").strip() or None
        country = request.form.get("country", "").strip() or None

        try:
            # Create request DTO
            request_dto = WeatherRequestDto(
                zipcode=zipcode, city=city, state=state, country=country
            )

            # Validate request
            if not request_dto.validate():
                flash("Please provide either a zipcode or city with state/country", "error")
                return redirect(url_for("index"))

            # Get weather data
            response = asyncio.run(weather_service.get_weather_forecast(request_dto))

            return render_template("weather.html", weather=response)

        except InvalidLocationFormatError as e:
            logger.error("Invalid location format", error=str(e))
            flash(f"Invalid location format: {e}", "error")
        except LocationNotFoundError as e:
            logger.error("Location not found", error=str(e))
            flash(f"Location not found: {e}", "error")
        except WeatherDataUnavailableError as e:
            logger.error("Weather data unavailable", error=str(e))
            flash(f"Weather data unavailable: {e}", "error")
        except NetworkError as e:
            logger.error("Network error", error=str(e))
            flash(f"Network error: {e}", "error")
        except WeatherAppException as e:
            logger.error("Weather app error", error=str(e))
            flash(f"Error: {e}", "error")
        except Exception as e:  # pylint: disable=broad-except
            logger.exception("Unexpected error")
            flash(f"Unexpected error: {e}", "error")

        return redirect(url_for("index"))

    @app.route("/api/weather", methods=["POST"])
    def api_weather():
        """API endpoint for weather data."""
        try:
            data = request.get_json()
            if not data:
                return jsonify({"error": "No JSON data provided"}), 400

            # Create request DTO
            request_dto = WeatherRequestDto(
                zipcode=data.get("zipcode"),
                city=data.get("city"),
                state=data.get("state"),
                country=data.get("country"),
            )

            # Validate request
            if not request_dto.validate():
                return (
                    jsonify(
                        {"error": "Please provide either a zipcode or city with state/country"}
                    ),
                    400,
                )

            # Get weather data
            response = asyncio.run(weather_service.get_weather_forecast(request_dto))

            # Convert to dict for JSON serialization
            return jsonify(
                {
                    "location": response.location,
                    "current_temperature": response.current_temperature,
                    "feels_like": response.feels_like,
                    "condition": response.condition,
                    "description": response.description,
                    "humidity": response.humidity,
                    "pressure": response.pressure,
                    "visibility": response.visibility,
                    "wind_speed": response.wind_speed,
                    "wind_direction": response.wind_direction,
                    "timestamp": response.timestamp,
                    "daily_forecasts": response.daily_forecasts,
                    "units": response.units,
                }
            )

        except InvalidLocationFormatError as e:
            logger.error("Invalid location format", error=str(e))
            return jsonify({"error": f"Invalid location format: {e}"}), 400
        except LocationNotFoundError as e:
            logger.error("Location not found", error=str(e))
            return jsonify({"error": f"Location not found: {e}"}), 404
        except WeatherDataUnavailableError as e:
            logger.error("Weather data unavailable", error=str(e))
            return jsonify({"error": f"Weather data unavailable: {e}"}), 503
        except NetworkError as e:
            logger.error("Network error", error=str(e))
            return jsonify({"error": f"Network error: {e}"}), 503
        except WeatherAppException as e:
            logger.error("Weather app error", error=str(e))
            return jsonify({"error": str(e)}), 500
        except Exception as e:  # pylint: disable=broad-except
            logger.exception("Unexpected error")
            return jsonify({"error": f"Unexpected error: {e}"}), 500

    @app.errorhandler(404)
    def not_found(error):
        """Handle 404 errors."""
        return render_template("error.html", error="Page not found"), 404

    @app.errorhandler(500)
    def internal_error(error):
        """Handle 500 errors."""
        return render_template("error.html", error="Internal server error"), 500

    return app


def main():
    """Main entry point for web interface."""
    app = create_app()
    app.run(host="0.0.0.0", port=5000, debug=True)


if __name__ == "__main__":
    main()
