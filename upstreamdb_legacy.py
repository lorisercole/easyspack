#!/usr/bin/env spack-python
"""
[OBSOLETE] Upstream database creation method using easyspack.
---

Configure Spack user paths before running this script:
    export SPACK_USER_CONFIG_PATH=/home/lercole/easyspack/spack
    export SPACK_USER_CACHE_PATH=/home/lercole/easyspack/spack/cache
or
    export SPACK_USER_CONFIG_PATH=/home/lercole/eessi/spack
    export SPACK_USER_CACHE_PATH=/home/lercole/eessi/spack/cache

EASYSPACK_DEBUG=1 ./upstreamdb_quick_start.py
"""

import os
import logging
logger = logging.getLogger(__name__)

import spack
from easyspack.legacy import SpecLoader, add_packages_to_config

from examples.upstream_db.eessi_example import example_dict

SPACK_DATABASE = "/home/lercole/eessi/spack/upstreams/eessi"
DYNAMIC_LINKER = os.path.join(os.getenv("EESSI_EPREFIX"), "lib64/ld-linux-x86-64.so.2")
OS_PKGS_PATHS = [
    os.getenv("EESSI_EPREFIX"),
    os.path.join(os.getenv("EESSI_EPREFIX"), "usr")
]
EXTERNAL_PACKAGES = (
    "gcc",
    "glibc",
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
