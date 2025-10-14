# Spec Loader API Quick Reference

## Main Class: SpecLoader

### Initialization
```python
from ebspack import SpecLoader

# Use default database path
loader = SpecLoader()

# Or specify custom database path
loader = SpecLoader(database_path="/path/to/database")
```

**Default database path:** `/home/lercole/spack/databases/test1_db`

### Loading Configuration

#### From JSON file:
```python
loader.load_from_file("specs.json")
```

#### From dictionary:
```python
config = {
    "architecture": {"platform": "linux", "os": "ubuntu24.04", "target": "skylake"},
    "specs": [...]
}
loader.load_from_dict(config)
```

### Building Specs
```python
# Build all specs defined in configuration
specs = loader.build_specs()  # Returns Dict[str, Spec]
```

### Adding to Database

#### Add all root specs (default):
```python
loader.add_to_database()
```

#### Dry run (don't actually add):
```python
loader.add_to_database(dry_run=True)
```

#### Add specific specs:
```python
loader.add_to_database(specs_to_add=["hdf5", "openmpi"])
```

### Querying Specs

#### List all spec names:
```python
names = loader.list_specs()  # Returns List[str]
```

#### Get a specific built spec:
```python
spec = loader.get_spec("hdf5")  # Returns Spec or None
```

## JSON Configuration Format

### Minimal Example
```json
{
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
    }
  ]
}
```

### Full Example with Dependencies
```json
{
  "architecture": {
    "platform": "linux",
    "os": "ubuntu24.04",
    "target": "skylake"
  },
  "specs": [
    {
      "name": "openmpi",
      "version": "5.0.6",
      "variants": "fabrics=ucx,psm",
      "external_path": "/opt/openmpi",
      "external_modules": ["openmpi/5.0.6"]
    },
    {
      "name": "hdf5",
      "version": "3.31.6",
      "external_path": "/opt/hdf5",
      "external_modules": ["hdf5/3.31.6"],
      "architecture": {
        "platform": "linux",
        "os": "centos7",
        "target": "x86_64"
      },
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

## Field Reference

### Architecture Object
- **platform** (required): Platform name (e.g., "linux", "darwin")
- **os** (required): OS name (e.g., "ubuntu24.04", "centos7")
- **target** (required): CPU target (e.g., "skylake", "x86_64")

### Spec Object
- **name** (required): Package name
- **version** (required): Package version
- **variants** (optional): Spack variants string
- **external_path** (optional): Path to external installation
- **external_modules** (optional): List of module names
- **architecture** (optional): Override default architecture
- **dependencies** (optional): List of dependency objects

### Dependency Object
- **name** (required): Name of dependency spec
- **depflags** (optional): List of flags ["BUILD", "LINK", "RUN", "TEST"]
  - Default: ["BUILD", "LINK"]
- **virtuals** (optional): List of virtual package names
  - Default: []

## Exception Handling

```python
from ebspack import SpecLoader, ValidationError, DatabaseError

try:
    loader = SpecLoader()
    loader.load_from_file("specs.json")
    loader.add_to_database()
except ValidationError as e:
    print(f"Invalid configuration: {e}")
except DatabaseError as e:
    print(f"Database error: {e}")
except FileNotFoundError as e:
    print(f"File not found: {e}")
```

## Common Patterns

### Pattern 1: Simple batch add
```python
loader = SpecLoader(database_path="/path/to/db")
loader.load_from_file("specs.json")
loader.add_to_database()
```

### Pattern 2: Validate before adding
```python
loader = SpecLoader(database_path="/path/to/db")
loader.load_from_file("specs.json")
specs = loader.build_specs()

# Inspect specs
for name, spec in specs.items():
    print(f"{name}: {spec}")

# Add if validation passes
loader.add_to_database()
```

### Pattern 3: Conditional adding
```python
loader = SpecLoader(database_path="/path/to/db")
loader.load_from_file("specs.json")
loader.build_specs()

# Only add specific specs based on some condition
to_add = []
for name in loader.list_specs():
    spec = loader.get_spec(name)
    if some_condition(spec):
        to_add.append(name)

loader.add_to_database(specs_to_add=to_add)
```

### Pattern 4: Build from multiple sources
```python
import json

loader = SpecLoader(database_path="/path/to/db")

# Load base config
with open("base_specs.json") as f:
    config = json.load(f)

# Modify programmatically
config["specs"].append({
    "name": "python",
    "version": "3.11.0",
    "external_path": "/usr/bin/python3.11"
})

loader.load_from_dict(config)
loader.add_to_database()
```

## Important Notes

1. **Database path** is configured in Python code via `SpecLoader(database_path=...)`
2. **Default database path** is `/home/lercole/spack/databases/test1_db`
3. **Dependencies must be defined before dependents** in the specs array
4. **Root specs** are auto-detected (specs not depended on by others)
3. **External packages** should have both `external_path` and `external_modules` when applicable
4. **Architecture** can be overridden per-spec or use global default
5. All specs are **marked as concrete** before being added to the database
