#!/usr/bin/env spack-python
"""
Simple example script to add specs to a Spack database.
For the sake of simplicity, the list of specs is loaded sequentially,
and we assume that dependencies are listed before the specs that depend on them.
"""

import spack.compilers.config
import spack.deptypes as dt
import spack.database
from spack.spec import ArchSpec, Spec
from ebspack.loader import populate_variants_with_defaults

DATABASE_PATH = "/home/lercole/ebspack/spack/upstreams/test-1"

spec_dict = {
    "architecture": {
        "platform": "linux",
        "os": "ubuntu24.04",
        "target": "skylake"
    },
    "specs": [
        {
            "name": "glibc",
            "version": "2.39",
            "variants": "",
            "external_path": "/usr",
            "dependencies": [],
        },
        {
            "name": "gcc-runtime",
            "version": "13.3.0",  # EBVERSIONGCC
            "variants": "",
            "external_path": "/home/lercole/ebspack/software/GCCcore/13.3.0", # EBROOTGCCCORE or EBROOTGCC
            "external_modules": ["/home/lercole/ebspack/modules/all/GCC/13.3.0.lua"],
            "dependencies": [
                {
                    "name": "glibc",
                    "depflags": dt.LINK,
                    "virtuals": ["libc"],
                },
            ],
        },
        # {
        #     "name": "compiler-wrapper",
        #     "version": "1.0",
        #     "variants": "",
        #     "external_path": "/home/lercole/ebspack/spack/compiler-wrapper",
        # },
        {
            "name": "gcc",
            "version": "13.3.0",  # EBVERSIONGCC
            "variants": "",
            "external_path": "/home/lercole/ebspack/software/GCCcore/13.3.0", # EBROOTGCCCORE or EBROOTGCC
            "external_modules": ["/home/lercole/ebspack/modules/all/GCC/13.3.0.lua"],
            "dependencies": [
                {
                    "name": "gcc-runtime",
                    "depflags": dt.LINK,
                },
                {
                    "name": "glibc",
                    "depflags": dt.LINK,
                    "virtuals": ["libc"],
                },
                # {
                #     "name": "compiler-wrapper",
                #     "depflags": dt.BUILD,
                # },
                # there are many more link dependencies
            ],
        },

        {
            "name": "gmake",
            "version": "4.4.1",  # EBVERSIONMAKE
            "variants": "",
            "external_path": "/home/lercole/ebspack/software/make/4.4.1-GCCcore-13.3.0", # EBROOTMAKE
            "external_modules": ["/home/lercole/ebspack/modules/all/make/4.4.1-GCCcore-13.3.0.lua"],
            "dependencies": [
                {
                    "name": "gcc",
                    "depflags": dt.BUILD,
                    "virtuals": ["c"],
                },
                {
                    "name": "gcc-runtime",
                    "depflags": dt.LINK,
                },
                {
                    "name": "glibc",
                    "depflags": dt.LINK,
                    "virtuals": ["libc"],
                },
                # {
                #     "name": "compiler-wrapper",
                #     "depflags": dt.BUILD,
                # },
            ],
        },
    ]
}

db = spack.database.Database(DATABASE_PATH)

# First pass: Create all spack Spec objects without dependencies
specs_map = {}
for spec_info in spec_dict["specs"]:
    name = spec_info["name"]
    version = spec_info["version"]
    variants = spec_info.get("variants", "")
    external_path = spec_info.get("external_path", None)
    external_modules = spec_info.get("external_modules", [])
    arch = spec_dict["architecture"]

    spec_str = f"builtin.{name}@={version}"
    if variants:
        spec_str += f" {variants}"

    # create spack Spec object
    # spec = Spec.from_detection(
    spec = Spec(
        spec_str,
        # external_path=spec_info.get("external_path", None),
        # external_modules=spec_info.get("external_modules", []),
    )
    populate_variants_with_defaults(spec)
    spec.architecture = ArchSpec((arch["platform"], arch["os"], arch["target"]))

    # set external prefix if provided
    if external_path:
        spec.external_prefix = external_path
    
    specs_map[name] = spec


# Second pass: Add dependencies
for spec_info in spec_dict["specs"]:
    name = spec_info["name"]
    spec = specs_map[name]

    for dep_info in spec_info.get("dependencies", []):
        dep_name = dep_info["name"]
        dep_spec = specs_map.get(dep_name, None)
        if dep_spec is None:
            raise RuntimeError(
                f"Dependency '{dep_name}' for '{spec.name}' "
                f"not found in spec list. Dependencies must be defined before their dependents."
            )
        spec.add_dependency_edge(
            dep_spec,
            depflag=dep_info["depflags"],
            virtuals=dep_info.get("virtuals", []),
            # direct=True,
        )


# Mark all specs as concrete
for spec in specs_map.values():
    spec._finalize_concretization()
    # spec._mark_concrete()

# Add specs to the database
try:
    with db.write_transaction():
        for spec in specs_map.values():
            print(f"Adding spec:\n              {spec}")
            deps = spec.dependencies()
            if deps:
                print(f"  with dependencies:")
                for dep in deps:
                     print(f"              {dep._str()}")
            db.add(spec)
except Exception as e:
    raise RuntimeError(f"Failed to add specs to database: {e}")


# Add compilers to Spack external packages configuration
new_compilers = spack.compilers.config.find_compilers(
    path_hints=[
        "/home/lercole/ebspack/software/GCCcore/13.3.0"
    ],  # paths to search for compilers
    scope='user',
    max_workers=4
)
