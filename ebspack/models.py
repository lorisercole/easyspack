"""
Data models for spec configuration.
"""

from dataclasses import dataclass, field
from typing import List, Optional, Dict


@dataclass
class ArchitectureConfig:
    """Architecture configuration."""
    platform: str
    os: str
    target: str

    def to_tuple(self) -> tuple:
        """Convert to tuple format for ArchSpec."""
        return (self.platform, self.os, self.target)


@dataclass
class DependencyConfig:
    """Dependency configuration."""
    name: str
    depflags: List[str] = field(default_factory=lambda: ["BUILD", "LINK"])
    virtuals: List[str] = field(default_factory=list)


@dataclass
class SpecConfig:
    """Spec configuration."""
    name: str
    version: str
    variants: Optional[str] = None
    external_path: Optional[str] = None
    external_modules: List[str] = field(default_factory=list)
    architecture: Optional[ArchitectureConfig] = None
    dependencies: List[DependencyConfig] = field(default_factory=list)

    def get_spec_string(self) -> str:
        """Generate the spec string for Spack."""
        spec_str = f"{self.name}@{self.version}"
        if self.variants:
            spec_str += f" {self.variants}"
        return spec_str


@dataclass
class DatabaseConfig:
    """Database configuration."""
    root: str
    name: str

    def get_path(self) -> str:
        """Get the full database path."""
        return f"{self.root}/{self.name}"


@dataclass
class SpecsConfiguration:
    """Complete configuration for all specs."""
    architecture: ArchitectureConfig
    specs: List[SpecConfig]
