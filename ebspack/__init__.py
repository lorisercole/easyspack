"""
Spack Spec Loader Package

A Python package to generalize the operation of adding specs (packages) 
to a Spack database from JSON configuration files.
"""

from .loader import SpecLoader
from .models import SpecConfig, DependencyConfig, ArchitectureConfig
from .exceptions import SpecLoaderError, ValidationError, DatabaseError

__version__ = "1.0.0"
__all__ = [
    "SpecLoader",
    "SpecConfig",
    "DependencyConfig",
    "ArchitectureConfig",
    "SpecLoaderError",
    "ValidationError",
    "DatabaseError",
]
