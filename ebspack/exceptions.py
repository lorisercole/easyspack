"""
Custom exceptions for the ebspack package.
"""


class SpecLoaderError(Exception):
    """Base exception for all ebspack errors."""
    pass


class ValidationError(SpecLoaderError):
    """Raised when spec configuration validation fails."""
    pass


class DatabaseError(SpecLoaderError):
    """Raised when database operations fail."""
    pass
