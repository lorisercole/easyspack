# Spack Spec Loader

A Python package to generalize the operation of adding specs (packages) to a Spack database from JSON configuration files.

## Overview

This package provides a clean, declarative way to define Spack package specifications and their dependencies in JSON format, then automatically add them to a Spack database. It handles:

- External package definitions
- Dependency relationships
- Architecture specifications
- Module environments
- Batch operations on multiple specs

## Package Structure

```
ebspack/
├── ebspack/
│   ├── __init__.py          # Package initialization
│   ├── loader.py            # Main SpecLoader class
│   ├── models.py            # Data models (dataclasses)
│   ├── schema.py            # JSON schema definition
│   └── exceptions.py        # Custom exceptions
├── examples/
│   ├── specs_example.json       # Simple example configuration
│   ├── complex_example.json     # Complex multi-dependency example
│   └── use_ebspack.py       # Usage examples
├── add_pkg.py               # Original example script
└── README.md                # This file
```

## JSON Schema

The package uses a well-defined JSON schema with the following structure:

### Top-level Structure

```json
{
  "architecture": {
    "platform": "linux",
    "os": "ubuntu24.04",
    "target": "skylake"
  },
  "specs": [
    // Array of spec objects
  ]
}
```

**Note:** The database path is now configured when creating the `SpecLoader` instance, not in the JSON file.

### Spec Object

```json
{
  "name": "package_name",
  "version": "1.2.3",
  "variants": "variant1=value1,variant2=value2",  // Optional
  "external_path": "/path/to/package",             // Optional
  "external_modules": ["module/name"],             // Optional
  "architecture": {                                 // Optional, overrides default
    "platform": "linux",
    "os": "centos7",
    "target": "x86_64"
  },
  "dependencies": [                                 // Optional
    {
      "name": "dependency_name",
      "depflags": ["BUILD", "LINK"],               // Optional, default: ["BUILD", "LINK"]
      "virtuals": ["mpi"]                          // Optional, default: []
    }
  ]
}
```

### Dependency Flags

Valid dependency flags:
- `BUILD`: Build-time dependency
- `LINK`: Link-time dependency
- `RUN`: Runtime dependency
- `TEST`: Test-time dependency

## Usage

### 1. Create a JSON Configuration File

Create a file `specs.json`:

```json
{
  "architecture": {
    "platform": "linux",
    "os": "ubuntu24.04",
    "target": "skylake"
  },
  "specs": [
    "platform": "linux",
    "os": "ubuntu24.04",
    "target": "skylake"
  },
  "specs": [
    {
      "name": "openmpi",
      "version": "5.0.6",
      "variants": "fabrics=ucx,psm,psm2,verbs",
      "external_path": "/path/to/openmpi",
      "external_modules": ["eessi/openmpi/5.0.6"]
    },
    {
      "name": "hdf5",
      "version": "3.31.6",
      "external_path": "/path/to/hdf5",
      "external_modules": ["eessi/hdf5/3.31.6"],
      "dependencies": [
        {
          "name": "openmpi",
          "depflags": ["BUILD", "LINK"],
          "virtuals": ["mpi"]
        }
      ]
    }
  ]
}
```

### 2. Use the SpecLoader

```python
#!/usr/bin/env spack-python

from ebspack import SpecLoader

# Create loader instance with database path
loader = SpecLoader(database_path="/home/user/spack/databases/my_db")
# Or use the default path: loader = SpecLoader()

# Load configuration from file
loader.load_from_file("specs.json")

# Build specs (creates Spack Spec objects)
specs = loader.build_specs()

# Add to database
loader.add_to_database()

# Or do a dry run first
loader.add_to_database(dry_run=True)
```

### 3. Advanced Usage

```python
#!/usr/bin/env spack-python

from ebspack import SpecLoader

# Specify custom database path
loader = SpecLoader(database_path="/custom/path/to/database")

# Load from dictionary instead of file
config = {
    "architecture": {"platform": "linux", "os": "ubuntu24.04", "target": "skylake"},
    "specs": [{"name": "gcc", "version": "11.2.0", "external_path": "/usr/local/gcc"}]
}
loader.load_from_dict(config)

# List available specs
print(loader.list_specs())

# Build specs
specs = loader.build_specs()

# Get individual spec
hdf5_spec = loader.get_spec("hdf5")

# Add only specific specs to database (by name)
loader.add_to_database(specs_to_add=["hdf5"])
```

## Important Notes

### Dependency Ordering

Dependencies must be defined **before** the specs that depend on them in the JSON file. The package processes specs in order and will raise an error if a dependency is referenced before it's defined.

✅ Correct order:
```json
{
  "specs": [
    {"name": "openmpi", ...},
    {"name": "hdf5", ..., "dependencies": [{"name": "openmpi"}]}
  ]
}
```

❌ Incorrect order:
```json
{
  "specs": [
    {"name": "hdf5", ..., "dependencies": [{"name": "openmpi"}]},
    {"name": "openmpi", ...}
  ]
}
```

### Root Specs

By default, `add_to_database()` adds only "root" specs (specs that are not dependencies of other specs). This is because Spack automatically adds dependencies when you add a spec.

To add specific specs, use the `specs_to_add` parameter:

```python
loader.add_to_database(specs_to_add=["hdf5", "openmpi"])
```

## Error Handling

The package provides custom exceptions:

- `SpecLoaderError`: Base exception
- `ValidationError`: JSON schema validation errors
- `DatabaseError`: Database operation errors

```python
from ebspack import SpecLoader, ValidationError, DatabaseError

try:
    loader = SpecLoader()
    loader.load_from_file("specs.json")
    loader.add_to_database()
except ValidationError as e:
    print(f"Configuration error: {e}")
except DatabaseError as e:
    print(f"Database error: {e}")
```

## Examples

See the `examples/` directory for:

1. **specs_example.json**: Simple two-package example (openmpi + hdf5)
2. **complex_example.json**: Multi-level dependency chain (gcc → ucx → openmpi → hdf5 → netcdf)
3. **use_ebspack.py**: Runnable Python examples showing various usage patterns

Run the examples:

```bash
cd examples
spack-python use_ebspack.py
```

## Development

### Requirements

- Spack installation
- Python 3.7+
- jsonschema package

### Installing Dependencies

```bash
pip install jsonschema
```

## License

This package follows the same license as Spack.
