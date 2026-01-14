#!/usr/bin/env spack-python
"""
Quick start script -
reads external packages from a YAML file, detect OS packages, installs them into Spack upstream database, and generates
packages.yaml entries (for compilers)

Run this before running this script:
    export SPACK_USER_CONFIG_PATH=/home/lercole/eessi/spack
    export SPACK_USER_CACHE_PATH=/home/lercole/eessi/spack/cache

EBSPACK_DEBUG=1 ./external_example.py
"""

import os
import logging
logger = logging.getLogger(__name__)

import spack
from ebspack.ext_install import UpstreamInstaller

SPACK_DATABASE = "/home/lercole/eessi/spack/upstreams/eessi"
OS_PKGS_PATHS = [
    os.getenv("EESSI_EPREFIX"),
    os.path.join(os.getenv("EESSI_EPREFIX"), "usr")
]
###############################################################################
# boostrap spack
logger.debug("Bootstrapping Spack...")
spack.main.main(["bootstrap", "now"])

ui = UpstreamInstaller(database_path=SPACK_DATABASE)
ui.parse_externals_yaml(
    '/home/lercole/src/ebspack/examples/ext_install/externals_nocompat.yaml',
    inject_runtime_deps=True,
    detect_packages=True,
    detection_paths=OS_PKGS_PATHS
)
ui.install()
ui.add_externals_to_config()
