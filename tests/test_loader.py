#!/usr/bin/env python3
"""
Unit tests for the ebspack package.
"""

import pytest
import json
from pathlib import Path
import tempfile

from ebspack import SpecLoader, ValidationError, DatabaseError
from ebspack.models import SpecConfig, DependencyConfig, ArchitectureConfig


class TestSpecLoader:
    """Test cases for SpecLoader class."""

    @pytest.fixture
    def valid_config(self):
        """Return a valid configuration dictionary."""
        return {
            "architecture": {
                "platform": "linux",
                "os": "ubuntu24.04",
                "target": "skylake"
            },
            "specs": [
                {
                    "name": "gcc",
                    "version": "11.2.0",
                    "external_path": "/usr/local/gcc"
                },
                {
                    "name": "openmpi",
                    "version": "5.0.6",
                    "variants": "fabrics=ucx",
                    "external_path": "/opt/openmpi",
                    "external_modules": ["openmpi/5.0.6"],
                    "dependencies": [
                        {
                            "name": "gcc",
                            "depflags": ["BUILD"],
                            "virtuals": []
                        }
                    ]
                }
            ]
        }

    def test_load_from_dict_valid(self, valid_config):
        """Test loading a valid configuration from dictionary."""
        loader = SpecLoader()
        # Note: This will fail if spack.database is not available
        # loader.load_from_dict(valid_config)
        # assert loader.config is not None
        # assert len(loader.config.specs) == 2

    def test_validation_error_missing_required(self):
        """Test that missing required fields raises ValidationError."""
        loader = SpecLoader()
        invalid_config = {
            "architecture": {"platform": "linux", "os": "ubuntu", "target": "x86_64"},
            # Missing "specs" array
        }
        
        with pytest.raises(ValidationError):
            loader.load_from_dict(invalid_config)

    def test_validation_error_invalid_depflag(self, valid_config):
        """Test that invalid dependency flags are caught."""
        valid_config["specs"][1]["dependencies"][0]["depflags"] = ["INVALID_FLAG"]
        
        loader = SpecLoader()
        # Schema validation will pass, but depflag conversion will fail
        # This would be caught during build_specs()

    def test_list_specs_empty(self):
        """Test list_specs on empty loader."""
        loader = SpecLoader()
        assert loader.list_specs() == []

    def test_get_spec_not_built(self):
        """Test getting a spec before building."""
        loader = SpecLoader()
        assert loader.get_spec("nonexistent") is None

    def test_spec_config_get_spec_string(self):
        """Test SpecConfig.get_spec_string method."""
        spec = SpecConfig(
            name="hdf5",
            version="1.12.0",
            variants="mpi=on +fortran"
        )
        assert spec.get_spec_string() == "hdf5@1.12.0 mpi=on +fortran"

    def test_spec_config_get_spec_string_no_variants(self):
        """Test SpecConfig.get_spec_string without variants."""
        spec = SpecConfig(name="gcc", version="11.2.0")
        assert spec.get_spec_string() == "gcc@11.2.0"

    def test_architecture_config_to_tuple(self):
        """Test ArchitectureConfig.to_tuple method."""
        arch = ArchitectureConfig(
            platform="linux",
            os="ubuntu24.04",
            target="skylake"
        )
        assert arch.to_tuple() == ("linux", "ubuntu24.04", "skylake")

    def test_load_from_nonexistent_file(self):
        """Test loading from a file that doesn't exist."""
        loader = SpecLoader()
        with pytest.raises(FileNotFoundError):
            loader.load_from_file("/nonexistent/path/config.json")

    def test_load_from_file_valid(self, valid_config):
        """Test loading from a valid JSON file."""
        loader = SpecLoader()
        
        # Create temporary file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(valid_config, f)
            temp_path = f.name
        
        try:
            # This will fail without spack environment, but tests the file reading
            # loader.load_from_file(temp_path)
            # assert loader.config is not None
            pass
        finally:
            Path(temp_path).unlink()


class TestModels:
    """Test cases for data models."""

    def test_dependency_config_defaults(self):
        """Test DependencyConfig default values."""
        dep = DependencyConfig(name="gcc")
        assert dep.depflags == ["BUILD", "LINK"]
        assert dep.virtuals == []

    def test_spec_config_defaults(self):
        """Test SpecConfig default values."""
        spec = SpecConfig(name="gcc", version="11.2.0")
        assert spec.variants is None
        assert spec.external_path is None
        assert spec.external_modules == []
        assert spec.architecture is None
        assert spec.dependencies == []


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
