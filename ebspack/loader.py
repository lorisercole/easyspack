"""
Main loader module for adding specs to Spack database.
"""

import json
import jsonschema
from pathlib import Path
from typing import Dict, Iterator, List, Optional, Union

import spack.config
import spack.database
import spack.deptypes as dt
import spack.detection
from spack.spec import Spec, ArchSpec, FlagMap

from . import models
from .schema import SPEC_SCHEMA
from .exceptions import ValidationError, DatabaseError


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

def build_spack_spec(spec_config: models.SpecConfig) -> Spec:
    """Build a Spack Spec object from a SpecConfig.
    
    Args:
        spec_config: The SpecConfig object containing spec details

    Returns:
        A Spack Spec object built from the SpecConfig
    """
    # if spec_config.name in ("gcc", "glibc"):  # must be external
    #     spec = Spec.from_detection(
    #         spec_config.get_spec_string(),
    #         external_path=spec_config.external_path,
    #         external_modules=spec_config.external_modules,
    #         extra_attributes=spec_config.extra_attributes,
    #     )
    # else:
    #     spec = Spec(spec_config.get_spec_string())
    #     spec._prefix = spec_config.external_path
    #     # DOES NOT WORK: Database._add does not write paths that do not follow spack's path layout,
    #     # it does only if the an external_path is set.
    # set external prefix if provided -- USELESS
    # if spec_config.external_path:
    #     spec.external_prefix = spec_config.external_path


    spec = Spec.from_detection(
        spec_config.get_spec_string(),
        external_path=spec_config.external_path,
        external_modules=spec_config.external_modules,
        extra_attributes=spec_config.extra_attributes,
    )
    populate_variants_with_defaults(spec)
    # spec.architecture = ArchSpec(spec_config.architecture.to_tuple())
    spec._set_architecture(**spec_config.architecture.__dict__)

    # print(f"Built spec: {spec.__dict__}")
    return spec

def spec_map_key(spec_config: models.SpecConfig) -> str:
    return f"{spec_config.name}@{spec_config.version}"


class SpecLoader:
    """
    Load and add Spack specs to a database from JSON configuration.
    
    Example usage:
        loader = SpecLoader(database_path="/path/to/database")
        loader.load_configuration("specs.json")
        loader.add_to_database()
    """
    
    # Hard-coded default database path
    DEFAULT_DATABASE_PATH = "/home/lercole/ebspack/spack/upstreams/test"

    def __init__(self, database_path: Optional[str] = None):
        """Initialize the SpecLoader.
        
        Args:
            database_path: Path to the Spack database. If None, uses DEFAULT_DATABASE_PATH
        """
        self.config: Optional[models.SpecsConfiguration] = None
        self._specs_map: Dict[str, Spec] = {}
        self._database_path = database_path or self.DEFAULT_DATABASE_PATH
        
        # Initialize database with the configured path
        self._database = spack.database.Database(self._database_path)
        print("LAYOUT:", self._database.layout)

    @property
    def specs_map(self) -> Dict[str, Spec]:
        """Get the internal specs map."""
        return self._specs_map

    def _parse_configuration(self, data: dict) -> models.SpecsConfiguration:
        """Parse the validated configuration data into model objects."""
        # Parse default architecture
        arch_config = models.ArchitectureConfig(**data["architecture"])

        # Parse specs
        specs = []
        for spec_data in data["specs"]:

            # Parse dependencies, sort them by name
            dependencies = []
            for dep_data in sorted(spec_data.get("dependencies", []), key=lambda d: d.get("name", "")):
                dependencies.append(models.DependencyConfig(**dep_data))

            # Create spec config
            spec_config = models.SpecConfig(
                name=spec_data["name"],
                version=spec_data["version"],
                variants=spec_data.get("variants"),
                external_path=spec_data.get("external_path"),
                external_modules=spec_data.get("external_modules"), #, []),
                extra_attributes=spec_data.get("extra_attributes"),
                dependencies=dependencies,
                architecture=arch_config,
            )
            specs.append(spec_config)

        return models.SpecsConfiguration(specs=specs)
        # return models.SpecsConfiguration(architecture=arch_config, specs=specs)

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

    def build_specs(self) -> Dict[str, Spec]:
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
            spec_key = spec_map_key(spec_config)
            if spec_key in self._specs_map:
                raise ValidationError(f"Duplicate spec name found: {spec_key}")
            self._specs_map[spec_key] = build_spack_spec(spec_config)

        # Second pass: Add dependencies
        for spec_config in self.config.specs:
            spec = self._specs_map[spec_map_key(spec_config)]
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
            print(f"Concretizing spec: {spec.to_node_dict()} -- path: {spec._prefix}")
            spec._finalize_concretization()
            # spec._mark_concrete()

    def add_to_database(self, specs_to_add: Optional[List[str]] = None, dry_run: bool = False) -> None:
        """
        Add specs to the Spack database.

        Args:
            specs_to_add: List of spec names to add. If None, adds all specs
            dry_run: If True, build specs but don't add to database

        Raises:
            DatabaseError: If database operations fail
            ValidationError: If specs are not built yet
        """
        if not self.specs_map:
            self.build_specs()

        if self._database is None:
            raise DatabaseError("Database not initialized")

        # Determine which specs to add
        if specs_to_add is None:
            # Add all specs from the configuration
            specs_to_add = [spec_map_key(spec_config) for spec_config in self.config.specs]

        if dry_run:
            print(f"Dry run: Would add {len(specs_to_add)} spec(s) to database:")
            for spec_key in specs_to_add:
                print(f"  - {spec_key}: {self.specs_map[spec_key]}")
            return

        # Add specs to database
        try:
            with self._database.write_transaction():
                for spec_key in specs_to_add:
                    if spec_key not in self.specs_map:
                        raise ValidationError(f"Spec '{spec_key}' not found in configuration")

                    spec = self.specs_map[spec_key]
                    self._database.add(spec)
                    print(f"Added spec: {spec_key}")
                    print(f"     {spec.to_node_dict()} -- path: {spec.prefix}")
        except Exception as e:
            raise DatabaseError(f"Failed to add specs to database: {e}")

    def get_spec(self, name: str) -> Optional[Spec]:
        """
        Get a built spec by name.
        
        Args:
            name: Name of the spec
            
        Returns:
            Spec object or None if not found
        """
        # FIXME : specs_map uses key with version
        return self.specs_map.get(name)

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
                spec = self.specs_map.get(spec_map_key(spec_config))
                if spec:
                    compilers.append(spec)
        return compilers

    def add_gcc_runtime_externals(self, scope: str = "user") -> None:
        """Add all gcc-runtime packages from configuration to packages.yaml.
        
        This method scans self.config.specs for any gcc-runtime packages and
        adds them as external packages to the Spack packages.yaml configuration.
        
        Args:
            scope: Configuration scope ('user', 'site', or 'system')

        Raises:
            ValidationError: If no configuration is loaded
        """
        if self.config is None:
            raise ValidationError("No configuration loaded. Call load_from_file or load_from_dict first.")
        
        # Find all gcc-runtime specs in the configuration
        gcc_runtime_specs = [spec_config for spec_config in self.config.specs if spec_config.name == "gcc-runtime"]
        
        if not gcc_runtime_specs:
            print("No gcc-runtime packages found in configuration")
            return
        
        # Get current packages configuration
        packages = spack.config.get("packages", scope=scope)
        
        # Build the externals list for gcc-runtime
        externals = [
            {
                "spec": f"gcc-runtime@{spec_config.version}",
                "prefix": spec_config.external_path,
            } for spec_config in gcc_runtime_specs
        ]

        # Update or create gcc-runtime configuration
        if "gcc-runtime" in packages:
            # Merge with existing externals, avoiding duplicates
            existing_externals = packages["gcc-runtime"].get("externals", [])
            existing_specs = {e.get("spec") for e in existing_externals}
            
            for external in externals:
                if external["spec"] not in existing_specs:
                    existing_externals.append(external)
                    print(f"Added {external['spec']} at {external.get('prefix', 'N/A')}")
                else:
                    print(f"Skipped duplicate: {external['spec']}")
            
            packages["gcc-runtime"]["externals"] = existing_externals
        else:
            packages["gcc-runtime"] = {
                "externals": externals,
                # "buildable": buildable
            }
            for external in externals:
                print(f"Added {external['spec']} at {external.get('prefix', 'N/A')}")
        
        # Write back to configuration
        spack.config.set("packages", packages, scope=scope)
        print(f"Updated gcc-runtime configuration in '{scope}' scope")


def add_packages_to_config(specs: Iterator[Spec], *, scope=None) -> None:
    """
    Add a list of packages to the packages.yaml configuration file, at the required scope.
    This ensures that Spack treats these packages as external.

    Args:
        specs (Iterator[Spec]): An iterator of `Spec` objects to be added to the configuration.
        scope (Optional[str]): The configuration scope where the packages should be added.
            If not provided, the default scope is used.
    """
    # Group specs by name in dictionary
    by_name: Dict[str, List[spack.spec.Spec]] = {}
    for spec in specs:
        by_name.setdefault(spec.name, []).append(spec)

    spack.detection.update_configuration(by_name, buildable=True, scope=scope)
