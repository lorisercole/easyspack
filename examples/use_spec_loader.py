#!/usr/bin/env spack-python
"""
Example usage of the ebspack package.
"""

import sys
from pathlib import Path

# Add parent directory to path to import ebspack
sys.path.insert(0, str(Path(__file__).parent.parent))

from ebspack import SpecLoader


def main():
    """Main example function."""
    
    # Example 1: Load from JSON file
    print("=" * 60)
    print("Example 1: Loading from JSON file")
    print("=" * 60)
    
    # Create loader with custom database path (or use default)
    loader = SpecLoader(database_path="/home/lercole/ebspack/spack/upstreams/test-1")
    # Or use default: loader = SpecLoader()
    
    # Load configuration
    config_file = Path(__file__).parent / "specs_example.json"
    print(f"\nLoading configuration from: {config_file}")
    loader.load_from_file(config_file)
    
    # List specs
    print(f"\nSpecs to be added: {loader.list_specs()}")
    
    # Build specs
    print("\nBuilding specs...")
    specs = loader.build_specs()
    
    # Display built specs
    for name, spec in specs.items():
        print(f"\n{name}:")
        print(f"  Full spec: {spec}")
        print(f"  Architecture: {spec.architecture}")
        print(f"  External path: {spec.external_path}")
        print(f"  Dependencies: {[d.name for d in spec.dependencies()]}")
    
    # Dry run to see what would be added
    print("\n" + "=" * 60)
    print("Performing dry run...")
    print("=" * 60)
    loader.add_to_database(dry_run=True)
    
    # Actually add to database (commented out for safety)
    print("\n" + "=" * 60)
    print("To actually add to database, uncomment the following line:")
    print("# loader.add_to_database()")
    print("=" * 60)
    
    # Example 2: Load from dictionary
    print("\n\n" + "=" * 60)
    print("Example 2: Loading from dictionary")
    print("=" * 60)
    
    config_dict = {
        "architecture": {
            "platform": "linux",
            "os": "ubuntu24.04",
            "target": "x86_64"
        },
        "specs": [
            {
                "name": "python",
                "version": "3.11.0",
                "external_path": "/usr/bin/python3.11",
                "external_modules": []
            }
        ]
    }
    
    loader2 = SpecLoader(database_path="/home/lercole/spack/databases/test_db")
    loader2.load_from_dict(config_dict)
    print(f"\nSpecs: {loader2.list_specs()}")
    loader2.build_specs()
    loader2.add_to_database(dry_run=True)


if __name__ == "__main__":
    main()
