"""Custom exceptions for the ML Kijkcijfer project."""


class DataError(Exception):
    """Base exception for data operations."""
    pass


class APIError(DataError):
    """Exception raised when API requests fail."""
    pass


class DataProcessingError(DataError):
    """Exception raised when data processing fails."""
    pass


class ValidationError(DataError):
    """Exception raised when data validation fails."""
    pass