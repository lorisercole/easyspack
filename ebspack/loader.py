"""
Main loader module for adding specs to Spack database.
"""

import json
import jsonschema
from pathlib import Path
from typing import Dict, List, Optional, Union

import spack.config
import spack.deptypes as dt
import spack.database
from spack.spec import Spec

from . import models
from .schema import SPEC_SCHEMA
from .exceptions import ValidationError, DatabaseError


class SpecLoader:
    """
    Load and add Spack specs to a database from JSON configuration.
    
    Example usage:
        loader = SpecLoader(database_path="/path/to/database")
        loader.load_from_file("specs.json")
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
        self._database: Optional[spack.database.Database] = None

    def _parse_configuration(self, data: dict) -> models.SpecsConfiguration:
        """Parse the validated configuration data into model objects."""
        # Parse default architecture
        arch_config = models.ArchitectureConfig(**data["architecture"])

        # Parse specs
        specs = []
        for spec_data in data["specs"]:

            # Parse dependencies
            dependencies = []
            for dep_data in spec_data.get("dependencies", []):
                dependencies.append(models.DependencyConfig(**dep_data))

            # Create spec config
            spec_config = models.SpecConfig(
                name=spec_data["name"],
                version=spec_data["version"],
                variants=spec_data.get("variants"),
                external_path=spec_data.get("external_path"),
                external_modules=spec_data.get("external_modules", []),
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
        
        # Initialize database with the configured path
        self._database = spack.database.Database(self._database_path)

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
        Build all Spec objects from the configuration.
        
        Returns:
            Dictionary mapping spec names to Spec objects
            
        Raises:
            ValidationError: If configuration is not loaded or invalid
        """
        if self.config is None:
            raise ValidationError("No configuration loaded. Call load_from_file or load_from_dict first.")

        self._specs_map = {}

        # First pass: Create all spack Spec objects without dependencies
        for spec_config in self.config.specs:
            if spec_config.name in self._specs_map:
                raise ValidationError(f"Duplicate spec name found: {spec_config.name}")
            self._specs_map[spec_config.name] = spec_config.get_spack_spec()

        # Second pass: Add dependencies
        for spec_config in self.config.specs:
            spec = self._specs_map[spec_config.name]
            self._add_dependencies(spec, spec_config)

        # Mark all specs as concrete
        for spec in self._specs_map.values():
            spec._finalize_concretization()
            # spec._mark_concrete()

        return self._specs_map

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
        if not self._specs_map:
            self.build_specs()

        if self._database is None:
            raise DatabaseError("Database not initialized")

        # Determine which specs to add
        if specs_to_add is None:
            # Add all specs from the configuration
            specs_to_add = [spec_config.name for spec_config in self.config.specs]

        if dry_run:
            print(f"Dry run: Would add {len(specs_to_add)} spec(s) to database:")
            for spec_name in specs_to_add:
                print(f"  - {spec_name}: {self._specs_map[spec_name]}")
            return

        # Add specs to database
        try:
            with self._database.write_transaction():
                for spec_name in specs_to_add:
                    if spec_name not in self._specs_map:
                        raise ValidationError(f"Spec '{spec_name}' not found in configuration")
                    
                    spec = self._specs_map[spec_name]
                    self._database.add(spec)
                    print(f"Added spec: {spec_name}")
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
        return self._specs_map.get(name)

    def list_specs(self) -> List[str]:
        """
        Get list of all spec names in the configuration.
        
        Returns:
            List of spec names
        """
        if self.config is None:
            return []
        return [spec.name for spec in self.config.specs]

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
