#!/usr/bin/env spack-python
"""
Quick start script - converts the original add_pkg.py to use ebspack

Run this before running this script:
    export SPACK_USER_CONFIG_PATH=/home/lercole/ebspack/spack
    export SPACK_USER_CACHE_PATH=/home/lercole/ebspack/spack/cache
or
    export SPACK_USER_CONFIG_PATH=/home/lercole/eessi/spack
    export SPACK_USER_CACHE_PATH=/home/lercole/eessi/spack/cache

EBSPACK_DEBUG=1 ./quick_start.py
"""

import os
import logging
logger = logging.getLogger(__name__)

import spack
from ebspack import SpecLoader, add_packages_to_config
# from examples.example import example_dict
from examples.eessi_example import example_dict

# SPACK_DATABASE = "/home/lercole/ebspack/spack/upstreams/test-1"
SPACK_DATABASE = "/home/lercole/eessi/spack/upstreams/eessi"
# DYNAMIC_LINKER = "/lib64/ld-linux-x86-64.so.2"
DYNAMIC_LINKER = os.path.join(os.getenv("EESSI_EPREFIX"), "lib64/ld-linux-x86-64.so.2")
OS_PKGS_PATHS = [os.getenv("EESSI_EPREFIX"), os.path.join(os.getenv("EESSI_EPREFIX"), "usr")]
EXTERNAL_PACKAGES = (
    "gcc",
    "glibc",
    # "binutils",
    # "bzip2",
    # "git",
    # "m4",
    # "ncurses",
    # "openssl",
    # "rsync",
    # "zlib",
)
###############################################################################
# boostrap spack
logger.debug("Bootstrapping Spack...")
spack.main.main(["bootstrap", "now"])

# Create specloader and add to database
specloader = SpecLoader(database_path=SPACK_DATABASE)
specloader.load_configuration(example_dict)
specloader.detect_add_packages(OS_PKGS_PATHS)
specloader.inject_runtime_libs(DYNAMIC_LINKER)
specloader.build_specs(external_packages=EXTERNAL_PACKAGES)

# Show what will be added
logger.info("Specs that will be added:")
for key, spec in specloader._specs_map.items():
    external = "[E]" if spec.name in EXTERNAL_PACKAGES else "   "
    logger.info(f"  {external} {key:16}: {spec}  [{spec.architecture}]")
    if spec.dependencies():
        logger.info(f"        dependencies:  {[d.name for d in spec.dependencies()]}")

# Add to database
specloader.add_to_database()

# Add must-external packages to packages.yaml configuration file
add_packages_to_config(specloader.iter_specs(), filter_names=EXTERNAL_PACKAGES)
