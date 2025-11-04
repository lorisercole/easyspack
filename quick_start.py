#!/usr/bin/env spack-python
"""
Quick start script - converts the original add_pkg.py to use ebspack

Run this before running this script:
    export SPACK_USER_CONFIG_PATH=/home/lercole/ebspack/spack
"""

import logging
logger = logging.getLogger(__name__)

from ebspack import SpecLoader, add_packages_to_config
from examples.example import example_dict


# Create specloader and add to database
specloader = SpecLoader(database_path="/home/lercole/ebspack/spack/upstreams/test-1")
specloader.load_configuration(example_dict)
specloader.build_specs()

# Show what will be added
logger.info("Specs that will be added:")
for key, spec in specloader._specs_map.items():
    logger.info(f"  {key}: {spec}  [{spec.architecture}]")
    if spec.dependencies():
        logger.info(f"    dependencies:  {[d.name for d in spec.dependencies()]}")

# Add to database
specloader.add_to_database()

# Add must-external packages to packages.yaml configuration file
add_packages_to_config(specloader.iter_specs())
