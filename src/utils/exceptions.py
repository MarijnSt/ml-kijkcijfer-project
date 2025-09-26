"""Custom exceptions for the ML Kijkcijfer project."""


class RatingsDataError(Exception):
    """Base exception for ratings data operations."""
    pass


class APIError(RatingsDataError):
    """Exception raised when API requests fail."""
    pass


class DataProcessingError(RatingsDataError):
    """Exception raised when data processing fails."""
    pass


class ValidationError(RatingsDataError):
    """Exception raised when data validation fails."""
    pass