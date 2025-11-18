"""
Spack Spec Loader Package

A Python package to generalize the operation of adding specs (packages) 
to a Spack database from JSON configuration files.
"""

from .loader import SpecLoader, populate_variants_with_defaults, build_spack_spec, detect_packages, add_packages_to_config
from .models import SpecConfig, DependencyConfig, ArchitectureConfig
from .exceptions import SpecLoaderError, ValidationError, DatabaseError

__version__ = "1.0.0"
__all__ = [
    "SpecLoader",
    "populate_variants_with_defaults",
    "build_spack_spec",
    "detect_packages",
    "add_packages_to_config",
    "SpecConfig",
    "DependencyConfig",
    "ArchitectureConfig",
    "SpecLoaderError",
    "ValidationError",
    "DatabaseError",
]

import copy, logging, os

class DebugOnlyFormatter(logging.Formatter):
    def format(self, record):
        # shallow copy so we don't mutate the original record globally
        r = copy.copy(record)
        # add a 'levelprefix' field used only in the format string
        r.levelprefix = "[DEBUG : " if r.levelno == logging.DEBUG else ""
        r.name = f"{r.name}] " if r.levelno == logging.DEBUG else ""
        return super().format(r)

# Setup logging
logging.basicConfig(level=logging.DEBUG if os.getenv("EBSPACK_DEBUG") else logging.INFO)
for h in logging.root.handlers:
    h.setFormatter(DebugOnlyFormatter("%(levelprefix)s%(name)s%(message)s"))