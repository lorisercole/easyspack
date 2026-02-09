"""
Main loader module for adding specs to Spack database.
"""

import logging
import json
import jsonschema
from pathlib import Path
from typing import Any, Dict, Iterator, List, Optional, Union

import spack.cmd.external
import spack.deptypes as dt
import spack.detection
from spack.spec import Spec, FlagMap, substitute_abstract_variants
from spack.util.libc import libc_from_dynamic_linker

from . import models
from ..database import Database
from .schema import SPEC_SCHEMA
from ..exceptions import ValidationError, DatabaseError
import re

logger = logging.getLogger(__name__)

# Packages that must be treated as external to be reused properly by Spack
DEFAULT_EXTERNAL_PACKAGES = ("gcc", "glibc")
DEFAULT_DETECTED_TAGS = ["detectable"]
NOT_IMPLEMENTED_COMPILERS = ("acfl", "aocc", "apple-clang", "cce", "fj", "intel-oneapi-compilers",
                             "intel-oneapi-compilers-classic", "llvm", "msvc", "nvhpc", "xl")

HOST_PLATFORM = spack.platforms.host()
HOST_OS = HOST_PLATFORM.default_operating_system()
HOST_TARGET = HOST_PLATFORM.default_target()
HOST_TARGET_FAMILY = HOST_TARGET.family


def populate_variants_with_defaults(spec: Spec) -> None:
    """Populate spec with all variants from package definition using defaults.
    
    For external packages or specs without variants, this function fills in all
    variant values from the package definition using their defaults.
    
    Args:
        spec: The Spec object to populate with variants
        
    Raises:
        ValidationError: If package class cannot be retrieved
    """
    import spack.repo
    
    try:
        pkg_cls = spack.repo.PATH.get_pkg_class(spec.fullname)
    except Exception as e:
        raise ValidationError(f"Could not get package class for {spec.fullname}: {e}")
    
    # Iterate through all variant names and add missing ones
    for variant_name in pkg_cls.variant_names():
        # Skip if variant is already set
        if variant_name in spec.variants:
            continue
        
        # Find the appropriate variant definition
        for when, variant_def in pkg_cls.variant_definitions(variant_name):
            if when.intersects(spec):
                # Create a default variant and add it directly to the map
                default_variant = variant_def.make_default()
                # Use direct assignment instead of substitute() for new variants
                spec.variants[variant_name] = default_variant
                break
    
    # Populate compiler flags if not set
    for flag_name in FlagMap.valid_compiler_flags():
        if flag_name not in spec.compiler_flags:
            spec.compiler_flags[flag_name] = []

def build_spack_spec(spec_config: models.SpecConfig, external_packages: Optional[List[str]] = ()) -> Spec:
    """Build a Spack Spec object from a SpecConfig.
    
    Args:
        spec_config: The SpecConfig object containing spec details

    Returns:
        A Spack Spec object built from the SpecConfig
    """
    if spec_config.name in external_packages:  # must be external
        spec = Spec.from_detection(
            spec_config.get_spec_string(),
            external_path=spec_config.external_path,
            external_modules=spec_config.external_modules,
            extra_attributes=spec_config.extra_attributes,
        )
    else:  # will be an upstream spec (NOTE: cannot have neither external_modules nor extra_attributes)
        spec = Spec(spec_config.get_spec_string())
        substitute_abstract_variants(spec)
        spec.set_prefix(spec_config.external_path)
        # Database._add does not write paths that do not follow spack's path layout, unless `external_path` is set.
        # We make it work by hacking the Databse._add method

    populate_variants_with_defaults(spec)

    spec._set_architecture(**spec_config.architecture.__dict__)

    logger.debug(f"Built spec: {spec.to_node_dict()}")
    return spec

def detect_packages(
    paths: List[Path],
    *, names: Optional[List[str]] = None, tags: Optional[List[str]] = None, exclude: Optional[List[str]] = None,
) -> Dict[str, List[Spec]]:
    """Detect packages and return a list of Spec

    Args:
        names: name of packages to include (optional, None = all of them)
        tags:  search packages with these tags (e.g. "detectable" (default), "core-packages", "build-tools")
        exclude: name of packages to exclude (optional)
        paths: paths to search
    """
    if not tags:
        tags = DEFAULT_DETECTED_TAGS

    logger.debug(f"Detecting packages:\n  paths: {paths}\n  names: {names}\n  tags: {tags}\n  exclude: {exclude}")
    candidate_packages = spack.cmd.external.packages_to_search_for(names=names, tags=tags, exclude=exclude)
    logger.debug(f"Candidate packages for detection: {candidate_packages}")
    if not candidate_packages:
        raise ValidationError("No candidate packages found for detection with the given criteria.")
    return spack.detection.by_path(candidate_packages, path_hints=paths)

def resolved_dependencies_for_spec(spec: "spack.spec.Spec") -> List[Dict[str, Any]]:
    """Return the package-level dependencies that actually apply to spec.

    This resolves all `when` conditions on the package's dependency metadata,
    merging entries that apply and returning a list of Dependency-like dicts.
    NOTE: variants should be populated/concrete.
    """
    import spack.deptypes as dt
    pkg_cls = spack.repo.PATH.get_pkg_class(spec.name)
    pkg = pkg_cls(spec)

    merged: Dict[str, spack.dependency.Dependency] = {}

    for when, deps_by_name in pkg.dependencies.items():
        if spec.satisfies(when):
            for name, dep in deps_by_name.items():
                if name in merged:
                    merged[name].merge(dep)
                else:
                    # make a shallow copy so we can mutate/merge safely
                    new_dep = spack.dependency.Dependency(dep.pkg, dep.spec.copy(), dep.depflag)
                    # copy patches dict (shallow copy is fine here)
                    new_dep.patches = {k: list(v) for k, v in dep.patches.items()}
                    merged[name] = new_dep

    out: List[Dict[str, Any]] = []
    for dep in merged.values():
        out.append(
            {
                "name": dep.name,
                "spec": dep.spec.format(),                     # constraint/spec expression
                "depflag": dep.depflag,     # e.g. 'BLR'
                "deptypes_list": [dt.flag_to_string(f) for f in dt.ALL_FLAGS if dep.depflag & f],
                "patches": dep.patches,
                "dep": dep,
            }
        )

    return out


class SpecLoader:
    """
    Load and add Spack specs to a database from JSON configuration.
    
    Example usage:
        loader = SpecLoader(database_path="/path/to/database")
        loader.load_configuration("specs.json")
        loader.add_to_database()
    """
    
    # Hard-coded default database path
    DEFAULT_DATABASE_PATH = "/home/lercole/spood/spack/upstreams/test"

    def __init__(self, database_path: Optional[str] = None):
        """Initialize the SpecLoader.
        
        Args:
            database_path: Path to the Spack database. If None, uses DEFAULT_DATABASE_PATH
        """
        self.config: Optional[models.SpecsConfiguration] = None
        self.arch_config: Optional[models.ArchitectureConfig] = None
        self.generic_arch_config: Optional[models.ArchitectureConfig] = None
        self._specs_map: Dict[str, Spec] = {}
        self._database_path = database_path or self.DEFAULT_DATABASE_PATH

        self.host_arch_config = models.ArchitectureConfig(
            platform=str(HOST_PLATFORM),
            os=str(HOST_OS),
            target=str(HOST_TARGET),
        )
        logger.info(f"HOST architecture: {self.host_arch_config}")

        # Initialize database with the configured path
        self._database = Database(self._database_path)

    @property
    def specs_map(self) -> Dict[str, Spec]:
        """Get the internal specs map."""
        return self._specs_map

    def _parse_configuration(self, data: dict) -> models.SpecsConfiguration:
        """Parse the validated configuration data into model objects."""
        # Parse default architecture
        target = spack.vendor.archspec.cpu.TARGETS.get(data["software_target"])
        if not target:
            raise ValidationError(f"Invalid software_target: {data['software_target']}")
        if not ((target == HOST_TARGET) or (target in HOST_TARGET.ancestors)):
            raise ValidationError(
                f"software_target '{data['software_target']}' is not compatible with host target '{HOST_TARGET.name}'"
            )
        self.arch_config = models.ArchitectureConfig(
            platform=str(HOST_PLATFORM),
            os=str(HOST_OS),
            target=data["software_target"],
        )
        logger.info(f"EESSI software architecture: {self.arch_config}")
        self.generic_arch_config = models.ArchitectureConfig(
            platform=str(HOST_PLATFORM),
            os=str(HOST_OS),
            target=str(HOST_TARGET_FAMILY),
        )
        logger.info(f"EESSI generic architecture: {self.generic_arch_config}")

        # Parse specs
        specs = []
        for spec_data in data["specs"]:
            # check if external_path is a valid path
            if not Path(spec_data["external_path"]).exists():
                raise ValidationError(f"External path does not exist: {spec_data['external_path']}")

            # Parse dependencies, sort them by name
            dependencies = []
            for dep_data in sorted(spec_data.pop("dependencies", []), key=lambda d: d.get("name", "")):
                dependencies.append(models.DependencyConfig(**dep_data))

            # Create spec config
            spec_config = models.SpecConfig(
                architecture=self.arch_config,
                dependencies=dependencies,
                **spec_data
            )
            specs.append(spec_config)

        return models.SpecsConfiguration(specs=specs)

    def load_configuration(self, source: Union[dict, str, Path]) -> None:
        """
        Load spec configuration from a dictionary or a JSON file.
        
        Args:
            source: Dictionary containing the spec configuration or a path to the JSON file
            
        Raises:
            ValidationError: If the data doesn't match the Spec schema
            FileNotFoundError: If the file doesn't exist (when source is a file path)
        """
        if isinstance(source, (str, Path)):
            # Load from file
            filepath = Path(source)
            if not filepath.exists():
                raise FileNotFoundError(f"Configuration file not found: {filepath}")
            with open(filepath, 'r') as f:
                data = json.load(f)
        elif isinstance(source, dict):
            # Use the provided dictionary
            data = source
        else:
            raise TypeError("Source must be a dictionary or a file path")

        # Validate against schema
        try:
            jsonschema.validate(instance=data, schema=SPEC_SCHEMA)
        except jsonschema.ValidationError as e:
            raise ValidationError(f"Configuration validation failed: {e.message}")

        # Parse configuration
        self.config = self._parse_configuration(data)

    def detect_add_packages(self, paths: List[Path]) -> None:
        """
        Detect packages at given paths and add them to the configuration.
        """
        if self.config is None:
            raise ValidationError("No configuration loaded. Call load_from_file or load_from_dict first.")

        detected_packages = detect_packages(paths=paths)
        for spec_list in detected_packages.values():
            for spec in spec_list:
                logger.info(f"Detected package:  {spec}")
                self.config.specs.append(
                    models.SpecConfig(
                        name=spec.name,
                        version=str(spec.versions),
                        architecture=self.generic_arch_config,
                        variants=str(spec.variants),
                        external_path=spec.external_path,
                        extra_attributes=spec.extra_attributes,
                    )
                )

    def inject_runtime_libs(self, dynamic_linker: str) -> None:
        """
        Detect libc and add it to the config and as dependency to all specs using a compiler.
        Add gcc-runtime or intel-oneapi-runtime as dependency to specs built with gcc or intel-oneapi-compilers.
        """
        if self.config is None:
            raise ValidationError("No configuration loaded. Call load_from_file or load_from_dict first.")

        # detect libc from dynamic linker
        libc = libc_from_dynamic_linker(dynamic_linker)
        if not libc:
            raise ValidationError(f"Could not detect libc from dynamic linker: {dynamic_linker}")
        logger.info(f"Detected libc spec:  {libc}")
        # add libc to config
        libc_config = models.SpecConfig(
                name=libc.name,
                version=str(libc.version),
                external_path=libc.external_path or "",
                architecture=self.generic_arch_config,
        )
        self.config.specs.append(libc_config)

        # add libc as a dependency to all specs built with a compiler, and to gcc-runtime
        for specconf in self.config.specs:
            if specconf.compiler or specconf.name == "gcc-runtime":
                specconf.dependencies.append(
                    models.DependencyConfig(
                        name=libc_config.spec_map_key,
                        depflags=["LINK"],
                        virtuals=["libc"],
                    )
                )
                logger.debug(f"Added libc dependency to spec: {specconf.spec_map_key}")

        # add gcc-runtime to config if gcc is defined. It has the compiler and glibc as dependencies
        # it uses the architecture of the host
        for specconf in self.config.specs:
            if specconf.name == "gcc":
                self.config.specs.append(
                    models.SpecConfig(
                        name="gcc-runtime",
                        version=specconf.version,
                        external_path=specconf.external_path,
                        external_modules=specconf.external_modules,
                        architecture=self.host_arch_config,
                        dependencies=[
                            models.DependencyConfig(name=specconf.spec_map_key, depflags=["BUILD"]),  # compiler
                            models.DependencyConfig(name=libc_config.spec_map_key, depflags=["LINK"], virtuals=["libc"])
                        ],
                    )
                )
                logger.debug(f"Added gcc-runtime for compiler spec: {specconf.spec_map_key}")
            elif specconf.name in NOT_IMPLEMENTED_COMPILERS:
                raise NotImplementedError(f"{specconf.name} runtime injection not implemented.")

        # add gcc-runtime as dependency to all specs built with gcc
        for specconf in self.config.specs:
            if specconf.compiler:
                match = re.match(r"^(?P<name>[\w\-]+)@(?P<version>[\w\.\-]+)$", specconf.compiler)
                if match:
                    compiler_version = match.group("version")
                    if match.group("name") == "gcc":
                        specconf.dependencies.append(
                            models.DependencyConfig(
                                name=f"gcc-runtime@{compiler_version}",
                                depflags=["LINK"]
                            )
                        )
                        logger.debug(f"Added gcc-runtime dependency to spec: {specconf.spec_map_key}")
                    else:
                        raise NotImplementedError(f"Compiler of spec: {specconf.spec_map_key} is not gcc.")
                else:
                    raise ValidationError(f"Invalid compiler format: {specconf.compiler}")

    def _add_dependencies(self, spec: Spec, spec_config: models.SpecConfig) -> None:
        """
        Add dependencies to a spec.
        
        Args:
            spec: The parent Spec object
            spec_config: Configuration containing dependency information
        """
        for dep_config in spec_config.dependencies:
            # Get the dependency spec from the specs map
            dep_spec = self._specs_map.get(dep_config.name)
            if dep_spec is None:
                raise ValidationError(
                    f"Dependency '{dep_config.name}' for '{spec_config.name}' "
                    f"not found in spec list. Dependencies must be defined before their dependents."
                )

            # Convert depflags from strings to Spack deptype constants
            depflag = 0
            for flag_name in dep_config.depflags:
                if hasattr(dt, flag_name):
                    depflag |= getattr(dt, flag_name)
                else:
                    raise ValidationError(f"Invalid dependency flag: {flag_name}")

            # Add the dependency edge
            spec.add_dependency_edge(
                dep_spec,
                depflag=depflag,
                virtuals=dep_config.virtuals,
                # direct=True,
            )

    def build_specs(self, external_packages: Optional[List[str]] = DEFAULT_EXTERNAL_PACKAGES) -> Dict[str, Spec]:
        """
        Build all Spec objects from the configuration into self.specs_map.

        Raises:
            ValidationError: If configuration is not loaded or invalid
        """
        if self.config is None:
            raise ValidationError("No configuration loaded. Call load_from_file or load_from_dict first.")

        self._specs_map = {}

        # First pass: Create all spack Spec objects without dependencies
        for spec_config in self.config.specs:
            spec_key = spec_config.spec_map_key
            if spec_key in self._specs_map:
                raise ValidationError(f"Duplicate spec name found: {spec_key}")
            self._specs_map[spec_key] = build_spack_spec(spec_config, external_packages)

        # Second pass: Add dependencies
        for spec_config in self.config.specs:
            spec = self._specs_map[spec_config.spec_map_key]
            self._add_dependencies(spec, spec_config)

        # Mark all specs as concrete
        # NOTE:
        # the hash is generated by spec.dag_hash, that calls spec._cached_hash(spack.hash_types.dag_hash),
        # that calls spec.spec_hash(spack.hash_types.dag_hash) that actually generates a hash based on
        # the dict returned by spec.to_node_dict().
        # The information included in this dict are:
        # name, version, arch, namespace, parameters (variants, flags), package_hash,
        # external, and dependencies will determine the DAG hash.
        for spec in self._specs_map.values():
            logger.debug(f"Concretizing spec: {spec.to_node_dict()} -- path: {spec._prefix}")
            spec._finalize_concretization()
            # spec._mark_concrete()

    def add_to_database(self, dry_run: bool = False) -> None:
        """
        Add specs to the Spack database.

        Args:
            dry_run: If True, build specs but don't add to database

        Raises:
            DatabaseError: If database operations fail
            ValidationError: If specs are not built yet
        """
        if not self.specs_map:
            self.build_specs()

        if self._database is None:
            raise DatabaseError("Database not initialized")

        # Add all specs from the configuration
        # TODO: only add root specs - dependencies will be added automatically
        specs_to_add_explicit = [(spec_config.spec_map_key, spec_config.explicit) for spec_config in self.config.specs]

        if dry_run:
            logger.info(f"Dry run: Would add {len(specs_to_add_explicit)} spec(s) to database:")
            for spec_key, _ in specs_to_add_explicit:
                logger.info(f"  - {spec_key}: {self.specs_map[spec_key]}")
            return

        # Add specs to database
        try:
            with self._database.write_transaction():
                for spec_key, explicit in specs_to_add_explicit:
                    if spec_key not in self.specs_map:
                        raise ValidationError(f"Spec '{spec_key}' not found in configuration")

                    spec = self.specs_map[spec_key]
                    self._database.add(spec, explicit=explicit)
                    logger.info(f"Added spec: {spec_key}")
                    logger.debug(f" {spec.to_node_dict()} -- path: {spec.prefix}")
        except Exception as e:
            raise DatabaseError(f"Failed to add specs to database: {e}")

    def get_spec(self, key: str) -> Optional[Spec]:
        """
        Get a built spec by key.

        Args:
            key: Key of the spec
            
        Returns:
            Spec object or None if not found
        """
        # Expecting "{name}@{version}%{compiler}@{compiler_version}"
        # REGEX: r"^(?P<name>[\w\-]+)(?:@(?P<version>[\w\.\-]+))?(?:%(?P<compiler>[\w\-]+)(?:@(?P<compiler_version>[\w\.\-]+))?)?$"
        return self.specs_map.get(key)

    def iter_specs(self) -> Iterator[Spec]:
        """
        Get an iterator over all Spec objects in the configuration.
        
        Returns:
            Iterator of Spec objects
        """
        return iter(self.specs_map.values())
    
    def list_compilers(self) -> List[Spec]:
        """
        Get list of all compiler specs in the configuration.
        
        Returns:
            List of Spec objects for compilers
        """
        if self.config is None:
            return []
        compilers = []
        for spec_config in self.config.specs:
            if spec_config.extra_attributes and "compilers" in spec_config.extra_attributes:
                spec = self.specs_map.get(spec_config.spec_map_key)
                if spec:
                    compilers.append(spec)
        return compilers


def add_packages_to_config(specs: Iterator[Spec], *, filter_names: Optional[List[str]] = DEFAULT_EXTERNAL_PACKAGES,
                           scope=None) -> None:
    """
    Add a list of packages to the packages.yaml configuration file, at the required scope.
    This ensures that Spack treats these packages as external.

    Args:
        specs (Iterator[Spec]): An iterator of `Spec` objects to be added to the configuration.
        filter_names (Optional[List[str]]): List of package names to filter and add as external.
            If None, all specs are added.
        scope (Optional[str]): The configuration scope where the packages should be added.
            If not provided, the default scope is used.
    """
    ext_pkg_names = filter_names or []
    logger.debug(f"Adding packages to config. Filter names: {ext_pkg_names}")
    
    # Group specs by name in dictionary
    by_name: Dict[str, List[Spec]] = {}
    for spec in specs:
        if spec.name in ext_pkg_names:
            by_name.setdefault(spec.name, []).append(spec)

    logger.info(f"Adding specs to packages.yaml configuration:")
    for sps in by_name.values():
        logger.info(f"   - {sps}")
    spack.detection.update_configuration(by_name, buildable=True, scope=scope)
