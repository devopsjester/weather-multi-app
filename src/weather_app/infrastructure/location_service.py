"""Location service implementation using free geocoding APIs."""

import httpx
import structlog

from weather_app.domain.models import Location
from weather_app.domain.services import ILocationRepository
from weather_app.domain.exceptions import LocationNotFoundError, NetworkError


logger = structlog.get_logger(__name__)


class OpenMeteoLocationRepository(ILocationRepository):
    """Location repository using Open-Meteo geocoding API."""

    def __init__(self, timeout: int = 30):
        self.geocoding_url = "https://geocoding-api.open-meteo.com/v1"
        self.timeout = timeout

    async def resolve_location(self, location: Location) -> Location:
        """Resolve location to include coordinates and normalized data."""
        logger.info("Resolving location", location=location.display_name)

        if location.zipcode:
            return await self._resolve_zipcode(location)
        else:
            return await self._resolve_city_state_country(location)

    async def _resolve_zipcode(self, location: Location) -> Location:
        """Resolve US zipcode to coordinates and city/state."""
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                # For US zipcodes, we'll use a different approach
                # Open-Meteo geocoding doesn't directly support zipcodes
                # We'll use nominatim service for zipcode resolution
                nominatim_url = "https://nominatim.openstreetmap.org/search"
                params = {
                    "q": f"{location.zipcode}, USA",
                    "format": "json",
                    "limit": 1,
                    "addressdetails": 1,
                }

                response = await client.get(nominatim_url, params=params)
                response.raise_for_status()
                data = response.json()

                if not data:
                    raise LocationNotFoundError(f"Zipcode not found: {location.zipcode}")

                result = data[0]
                address = result.get("address", {})

                return Location(
                    city=address.get("city") or address.get("town") or address.get("village", ""),
                    state=address.get("state", ""),
                    country="US",
                    zipcode=location.zipcode,
                    latitude=float(result["lat"]),
                    longitude=float(result["lon"]),
                )

        except httpx.HTTPStatusError as e:
            logger.error("HTTP error resolving zipcode", status_code=e.response.status_code)
            raise LocationNotFoundError(f"Could not resolve zipcode: {location.zipcode}") from e
        except httpx.RequestError as e:
            logger.error("Network error resolving zipcode", error=str(e))
            raise NetworkError(f"Network error: {str(e)}") from e
        except (KeyError, ValueError, IndexError) as e:
            logger.error("Error parsing zipcode response", error=str(e))
            raise LocationNotFoundError(f"Invalid response for zipcode: {location.zipcode}") from e

    async def _resolve_city_state_country(self, location: Location) -> Location:
        """Resolve city/state/country to coordinates."""
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                # Build search query
                query_parts = [location.city]
                if location.state:
                    query_parts.append(location.state)
                if location.country:
                    query_parts.append(location.country)

                params = {
                    "name": ", ".join(query_parts),
                    "count": 1,
                    "language": "en",
                    "format": "json",
                }

                response = await client.get(f"{self.geocoding_url}/search", params=params)
                response.raise_for_status()
                data = response.json()

                if not data.get("results"):
                    raise LocationNotFoundError(f"Location not found: {location.display_name}")

                result = data["results"][0]

                return Location(
                    city=result.get("name", location.city),
                    state=result.get("admin1", location.state),
                    country=result.get("country", location.country),
                    zipcode=location.zipcode,
                    latitude=result["latitude"],
                    longitude=result["longitude"],
                )

        except httpx.HTTPStatusError as e:
            logger.error("HTTP error resolving location", status_code=e.response.status_code)
            raise LocationNotFoundError(
                f"Could not resolve location: {location.display_name}"
            ) from e
        except httpx.RequestError as e:
            logger.error("Network error resolving location", error=str(e))
            raise NetworkError(f"Network error: {str(e)}") from e
        except (KeyError, ValueError) as e:
            logger.error("Error parsing location response", error=str(e))
            raise LocationNotFoundError(
                f"Invalid response for location: {location.display_name}"
            ) from e
