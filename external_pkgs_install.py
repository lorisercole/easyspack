#!/usr/bin/env spack-python
"""
[EXTRA FEATURE] Install external packages in a Spack upstream database using ebspack

Reads external packages from a YAML file, detect OS packages, installs them into Spack upstream database, and generates
`packages.yaml` entries (Spack needs to see compilers here).

Configure Spack user paths before running this script:
    export SPACK_USER_CONFIG_PATH=/home/lercole/eessi/spack
    export SPACK_USER_CACHE_PATH=/home/lercole/eessi/spack/cache

EBSPACK_DEBUG=1 ./external_pkgs_install.py
"""

import os
import logging
logger = logging.getLogger(__name__)

import spack
from ebspack.ext_install import UpstreamInstaller

SPACK_DATABASE = "/home/lercole/eessi/spack/upstreams/eessi"  # path to Spack upstream database
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
    './examples/ext_install/externals_nocompat.yaml',
    inject_runtime_deps=True,  # inject gcc-runtime and glibc runtime deps
    detect_packages=True,  # detect packages in OS_PKGS_PATHS
    detection_paths=OS_PKGS_PATHS
)
ui.install()
ui.add_externals_to_config()
