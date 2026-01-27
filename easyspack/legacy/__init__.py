"""
Legacy Spack Spec Loader Package

A Python package to generalize the operation of adding specs (packages) 
to a Spack database from JSON configuration files.
"""

from .loader import SpecLoader, populate_variants_with_defaults, build_spack_spec, detect_packages, add_packages_to_config
from .models import SpecConfig, DependencyConfig, ArchitectureConfig

__all__ = [
    "SpecLoader",
    "populate_variants_with_defaults",
    "build_spack_spec",
    "detect_packages",
    "add_packages_to_config",
    "SpecConfig",
    "DependencyConfig",
    "ArchitectureConfig",
]
