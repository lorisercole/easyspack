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
    depflags: List[str] = field(default_factory=lambda: ["BUILD", "LINK", "RUN", "TEST"])
    virtuals: List[str] = field(default_factory=list)


@dataclass
class SpecConfig:
    """Spec configuration."""
    name: str
    version: str
    architecture: ArchitectureConfig
    variants: Optional[str] = None
    explicit: Optional[bool] = False
    external_path: str = None
    external_modules: Optional[List[str]] = field(default_factory=list)
    extra_attributes: Optional[Dict] = field(default_factory=dict)
    dependencies: List[DependencyConfig] = field(default_factory=list)

    def get_spec_string(self) -> str:
        """Generate the spec string for Spack."""
        spec_str = f"builtin.{self.name}@={self.version}"
        if self.variants:
            spec_str += f" {self.variants}"
        return spec_str

    @property
    def compiler(self) -> Optional[str]:
        """Get the compiler name if defined in the dependencies. A compiler is identified
        as a dependency with BUILD depflag and virtuals including 'c', 'cxx', or 'fortran'.
        """
        for dep in self.dependencies:
            if "BUILD" in dep.depflags and any(v in dep.virtuals for v in ["c", "cxx", "fortran"]):
                return dep.name
        return None

    @property
    def spec_map_key(self) -> str:
        """A (supposedly) unique key for the spec map based on name and version."""
        key = f"{self.name}@{self.version}"
        if self.compiler:
            key += f"%{self.compiler}"
        return key

    # def get_spack_spec(self) -> Spec:
    #     """Generate a Spack Spec object."""
    #     spec_str = self.get_spec_string()
    #     spec = Spec(
    #         self.get_spec_string(),
    #         external_path=self.external_path,
    #         external_modules=self.external_modules,
    #     )
    #     spec.architecture = ArchSpec(self.architecture.to_tuple())

    #     # set external prefix if provided
    #     if self.external_path:
    #         spec.external_prefix = self.external_path
    #     return spec


@dataclass
class SpecsConfiguration:
    """Complete configuration for all specs."""
    specs: List[SpecConfig]
