"""Domain exceptions for the weather application."""


class WeatherAppException(Exception):
    """Base exception for weather application."""


class LocationNotFoundError(WeatherAppException):
    """Raised when a location cannot be found."""


class WeatherDataUnavailableError(WeatherAppException):
    """Raised when weather data is not available."""


class InvalidLocationFormatError(WeatherAppException):
    """Raised when location format is invalid."""


class ApiRateLimitError(WeatherAppException):
    """Raised when API rate limit is exceeded."""


class NetworkError(WeatherAppException):
    """Raised when network communication fails."""
