#!/usr/bin/env spack-python
"""
Quick start script - converts the original add_pkg.py to use spec_loader
"""

from spec_loader import SpecLoader

# Define the configuration as a dictionary (same as original add_pkg.py)
config = {
    "architecture": {
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

# Create loader and add to database
loader = SpecLoader(database_path="/home/lercole/spack/databases/test1_db")
loader.load_from_dict(config)
loader.build_specs()

# Show what will be added
print("Specs that will be added:")
for name in loader.list_specs():
    spec = loader.get_spec(name)
    print(f"  {name}: {spec}")
    print(f"    Architecture: {spec.architecture}")
    if spec.dependencies():
        print(f"    Dependencies: {[d.name for d in spec.dependencies()]}")

# Add to database (uncomment to actually add)
# loader.add_to_database()

print("\nTo add to database, uncomment the last line.")
