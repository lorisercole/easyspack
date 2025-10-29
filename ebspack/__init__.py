"""
Spack Spec Loader Package

A Python package to generalize the operation of adding specs (packages) 
to a Spack database from JSON configuration files.
"""

from .loader import SpecLoader, populate_variants_with_defaults, build_spack_spec
from .models import SpecConfig, DependencyConfig, ArchitectureConfig
from .exceptions import SpecLoaderError, ValidationError, DatabaseError

__version__ = "1.0.0"
__all__ = [
    "SpecLoader",
    "populate_variants_with_defaults",
    "build_spack_spec",
    "SpecConfig",
    "DependencyConfig",
    "ArchitectureConfig",
    "SpecLoaderError",
    "ValidationError",
    "DatabaseError",
]
