#!/usr/bin/env spack-python

import spack.deptypes as dt
import spack.database
from spack.spec import ArchSpec, Spec

SPACK_DB_ROOT = "/home/lercole/spack/databases/"
SPACK_DB_NAME = "test1_db"

db = spack.database.Database(f"{SPACK_DB_ROOT}/{SPACK_DB_NAME}")

hdf5 = Spec(
    "hdf5@3.31.6",
    external_path="/path/to/hdf5",
    external_modules=["eessi/hdf5/3.31.6"]
)

openmpi = Spec(
    "openmpi@5.0.6 fabrics=ucx,psm,psm2,verbs",
    external_path="/path/to/openmpi",
    external_modules=["eessi/openmpi/5.0.6"]
)

# arch = ArchSpec(("linux", "eessi", "icelake"))
arch = ArchSpec(("linux", "ubuntu24.04", "skylake"))
hdf5.architecture = arch
openmpi.architecture = arch

hdf5.add_dependency_edge(
    openmpi,
    depflag=dt.BUILD | dt.LINK,
    virtuals=["mpi"]
)

hdf5.external_prefix = "/path/to/hdf5"
openmpi.external_prefix = "/path/to/openmpi"

hdf5._mark_concrete()
openmpi._mark_concrete()

with db.write_transaction():
    db.add(hdf5)

