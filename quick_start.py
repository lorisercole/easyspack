#!/usr/bin/env spack-python
"""
Quick start script - converts the original add_pkg.py to use ebspack

Run this before running this script:
    export SPACK_USER_CONFIG_PATH=/home/lercole/ebspack/spack
"""

from ebspack import SpecLoader
import spack.compilers.config

# Define the configuration as a dictionary (same as original add_pkg.py)
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
            # "variants": "build_system=generic",
            "external_path": "/home/lercole/ebspack/software/GCCcore/13.3.0", # EBROOTGCCCORE or EBROOTGCC
            # "external_modules": ["/home/lercole/ebspack/modules/all/GCC/13.3.0.lua"]
            "dependencies": [
                {
                    "name": "glibc",
                    "depflags": ["LINK"],
                    "virtuals": ["libc"],
                },
            ],
        },
        {
            "name": "gcc",
            "version": "13.3.0",  # EBVERSIONGCC
            "variants": "",
            "external_path": "/home/lercole/ebspack/software/GCCcore/13.3.0", # EBROOTGCCCORE or EBROOTGCC
            # "external_modules": ["/home/lercole/ebspack/modules/all/GCC/13.3.0.lua"]
            "dependencies": [
                {
                    "name": "gcc-runtime",
                    "depflags": ["LINK"],
                },
                {
                    "name": "glibc",
                    "depflags": ["LINK"],
                    "virtuals": ["libc"],
                },
            ],
        },

        {
            "name": "gmake",
            "version": "4.4.1",  # EBVERSIONMAKE
            "variants": "~guile",
            "external_path": "/home/lercole/ebspack/software/make/4.4.1-GCCcore-13.3.0", # EBROOTMAKE
            "dependencies": [
                {
                    "name": "gcc-runtime",
                    "depflags": ["LINK"],
                },
                {
                    "name": "glibc",
                    "depflags": ["LINK"],
                    "virtuals": ["libc"],
                },
            ],
        },
        {
            "name": "cmake",
            "version": "3.31.8",  # EBVERSIONCMAKE
            "variants": "+ncurses",
            "external_path": "/home/lercole/ebspack/software/cmake/3.31.8-GCCcore-13.3.0", # EBROOTCMAKE
            "dependencies": [
                {
                    "name": "gcc-runtime",
                    "depflags": ["LINK"],
                },
                {
                    "name": "glibc",
                    "depflags": ["LINK"],
                    "virtuals": ["libc"],
                },
                {
                    "name": "gmake",    # not for EasyBuild !
                    "depflags": ["BUILD", "RUN"],
                },
                # {
                #     "name": "curl",
                #     "depflags": ["BUILD", "LINK"],
                # },
                # {
                #     "name": "ncurses",
                #     "depflags": ["BUILD", "LINK"],
                # },
                # {
                #     "name": "zlib-ng",   # but in EasyBuild it depends on zlib
                #     "depflags": ["BUILD", "LINK"],
                # },
                
                # libarchive, bzip2, openssl 3 --> not dependencies in cmake Spack package
            ],
        },

    ]
}

# Create specloader and add to database
specloader = SpecLoader(database_path="/home/lercole/ebspack/spack/upstreams/test-1")
specloader.load_configuration(spec_dict)
specloader.build_specs()

# Show what will be added
print("Specs that will be added:")
for name in specloader.list_specs():
    spec = specloader.get_spec(name)
    print(f"  {name}: {spec}  [{spec.architecture}]")
    if spec.dependencies():
        print(f"    dependencies:  {[d.name for d in spec.dependencies()]}")

# Add to database
specloader.add_to_database()

# Optionally add GCC runtime externals (if gcc-runtime spec is defined)
specloader.add_gcc_runtime_externals()

# COMPILERS
new_compilers = spack.compilers.config.find_compilers(
    path_hints=[
        "/home/lercole/ebspack/software/GCCcore/13.3.0"
    ],  # paths to search for compilers
    scope='user',  # or 'site', 'system', etc.
    max_workers=4  # parallel search
)

if new_compilers:
    n = len(new_compilers)
    s = "s" if n > 1 else ""
    filename = spack.config.CONFIG.get_config_filename('user', "packages")
    print(f"Added {n:d} new compiler{s} to {filename}")
    compiler_strs = sorted(f"{spec.name}@{spec.versions}" for spec in new_compilers)
    for c in reversed(compiler_strs):
        print(f"    {c}")

