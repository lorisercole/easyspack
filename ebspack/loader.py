"""
Main loader module for adding specs to Spack database.
"""

import json
import jsonschema
from pathlib import Path
from typing import Dict, List, Optional, Union

import spack.deptypes as dt
import spack.database
from spack.spec import ArchSpec, Spec

from .models import (
    ArchitectureConfig,
    DependencyConfig,
    SpecConfig,
    SpecsConfiguration,
)
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
    DEFAULT_DATABASE_PATH = "/home/lercole/spack/databases/test1_db"

    def __init__(self, database_path: Optional[str] = None):
        """Initialize the SpecLoader.
        
        Args:
            database_path: Path to the Spack database. If None, uses DEFAULT_DATABASE_PATH
        """
        self.config: Optional[SpecsConfiguration] = None
        self._specs_map: Dict[str, Spec] = {}
        self._database_path = database_path or self.DEFAULT_DATABASE_PATH
        self._database: Optional[spack.database.Database] = None

    def load_from_file(self, filepath: Union[str, Path]) -> None:
        """
        Load spec configuration from a JSON file.
        
        Args:
            filepath: Path to the JSON configuration file
            
        Raises:
            ValidationError: If the JSON doesn't match the schema
            FileNotFoundError: If the file doesn't exist
        """
        filepath = Path(filepath)
        if not filepath.exists():
            raise FileNotFoundError(f"Configuration file not found: {filepath}")

        with open(filepath, 'r') as f:
            data = json.load(f)

        self.load_from_dict(data)

    def load_from_dict(self, data: dict) -> None:
        """
        Load spec configuration from a dictionary.
        
        Args:
            data: Dictionary containing the spec configuration
            
        Raises:
            ValidationError: If the data doesn't match the schema
        """
        # Validate against schema
        try:
            jsonschema.validate(instance=data, schema=SPEC_SCHEMA)
        except jsonschema.ValidationError as e:
            raise ValidationError(f"Configuration validation failed: {e.message}")

        # Parse configuration
        self.config = self._parse_configuration(data)
        
        # Initialize database with the configured path
        self._database = spack.database.Database(self._database_path)

    def _parse_configuration(self, data: dict) -> SpecsConfiguration:
        """Parse the validated configuration data into model objects."""
        # Parse default architecture
        arch_config = ArchitectureConfig(**data["architecture"])

        # Parse specs
        specs = []
        for spec_data in data["specs"]:
            # Parse spec-specific architecture if provided
            spec_arch = None
            if "architecture" in spec_data:
                spec_arch = ArchitectureConfig(**spec_data["architecture"])

            # Parse dependencies
            dependencies = []
            for dep_data in spec_data.get("dependencies", []):
                dependencies.append(DependencyConfig(**dep_data))

            # Create spec config
            spec_config = SpecConfig(
                name=spec_data["name"],
                version=spec_data["version"],
                variants=spec_data.get("variants"),
                external_path=spec_data.get("external_path"),
                external_modules=spec_data.get("external_modules", []),
                architecture=spec_arch,
                dependencies=dependencies,
            )
            specs.append(spec_config)

        return SpecsConfiguration(
            architecture=arch_config,
            specs=specs,
        )

    def _create_spec(self, spec_config: SpecConfig) -> Spec:
        """
        Create a Spack Spec object from configuration.
        
        Args:
            spec_config: Spec configuration object
            
        Returns:
            Spack Spec object
        """
        # Create the spec with optional external settings
        spec = Spec(
            spec_config.get_spec_string(),
            external_path=spec_config.external_path,
            external_modules=spec_config.external_modules,
        )

        # Set architecture (use spec-specific or default)
        arch_config = spec_config.architecture or self.config.architecture
        arch = ArchSpec(arch_config.to_tuple())
        spec.architecture = arch

        # Set external prefix if provided
        if spec_config.external_path:
            spec.external_prefix = spec_config.external_path

        return spec

    def _add_dependencies(self, spec: Spec, spec_config: SpecConfig) -> None:
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

        # First pass: Create all specs without dependencies
        for spec_config in self.config.specs:
            spec = self._create_spec(spec_config)
            self._specs_map[spec_config.name] = spec

        # Second pass: Add dependencies
        for spec_config in self.config.specs:
            spec = self._specs_map[spec_config.name]
            self._add_dependencies(spec, spec_config)

        # Mark all specs as concrete
        for spec in self._specs_map.values():
            spec._mark_concrete()

        return self._specs_map

    def add_to_database(
        self,
        specs_to_add: Optional[List[str]] = None,
        dry_run: bool = False
    ) -> None:
        """
        Add specs to the Spack database.
        
        Args:
            specs_to_add: List of spec names to add. If None, adds all root specs
                         (specs that are not dependencies of other specs)
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
            # Find root specs (specs that aren't dependencies of others)
            all_deps = set()
            for spec_config in self.config.specs:
                for dep_config in spec_config.dependencies:
                    all_deps.add(dep_config.name)
            
            specs_to_add = [
                spec_config.name 
                for spec_config in self.config.specs
                if spec_config.name not in all_deps
            ]

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
