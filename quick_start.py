#!/usr/bin/env spack-python
"""
Quick start script - converts the original add_pkg.py to use ebspack

Run this before running this script:
    export SPACK_USER_CONFIG_PATH=/home/lercole/ebspack/spack
"""

from ebspack import SpecLoader, add_packages_to_config

# Define the configuration as a dictionary (same as original add_pkg.py)
spec_dict = {
    "architecture": {
        "platform": "linux",
        "os": "ubuntu24.04",
        "target": "skylake"
    },
    "specs": [
        {  # SYSTEM COMPILER
            "name": "gcc",
            "version": "12.4.0",
            "variants": "",
            "external_path": "/usr",
            "extra_attributes": {
                "compilers": {
                    "c": "/usr/bin/gcc-12",
                    "cxx": "/usr/bin/g++-12",
                    "fortran": "/usr/bin/gfortran-1",
                }
            },
            "dependencies": [],
        },
        {
            "name": "glibc",
            "version": "2.39",
            "variants": "",
            "external_path": "/usr",
            "dependencies": [],
        },
        {
            "name": "gcc-runtime",
            "version": "12.4.0",
            "variants": "",
            "external_path": "/usr",
            "dependencies": [
                {
                    "name": "gcc@12.4.0",  # SYSTEM COMPILER
                    "depflags": ["BUILD"],
                },
                {
                    "name": "glibc@2.39",
                    "depflags": ["LINK"],
                    "virtuals": ["libc"],
                },
            ],
        },
        {
            "name": "gmake",
            "version": "4.4.1",  # EBVERSIONMAKE
            "variants": "",
            "external_path": "/home/lercole/ebspack/software/make/4.4.1-GCCcore-13.3.0", # EBROOTMAKE
            "dependencies": [
                # {
                #     "name": "compiler-wrapper",
                #     "depflags": ["BUILD"],
                # },
                {
                    "name": "gcc@12.4.0",
                    "depflags": ["BUILD"],
                    "virtuals": ["c"],
                },
                {
                    "name": "gcc-runtime@12.4.0",
                    "depflags": ["LINK"],
                },
                {
                    "name": "glibc@2.39",
                    "depflags": ["LINK"],
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
        {  # EB GCC COMPILER
            "name": "gcc",
            "version": "13.3.0",  # EBVERSIONGCC
            "variants": "",
            "external_path": "/home/lercole/ebspack/software/GCCcore/13.3.0", # EBROOTGCCCORE or EBROOTGCC
            # "external_modules": ["/home/lercole/ebspack/modules/all/GCC/13.3.0.lua"],
            "extra_attributes": {
                "compilers": {
                    "c": "/home/lercole/ebspack/software/GCCcore/13.3.0/bin/gcc",
                    "cxx": "/home/lercole/ebspack/software/GCCcore/13.3.0/bin/g++",
                    "fortran": "/home/lercole/ebspack/software/GCCcore/13.3.0/bin/gfortran",
                }
            },
            "dependencies": [
                # {
                #     "name": "gcc-runtime@12.4.0",
                #     "depflags": ["LINK"],
                # },
                # {
                #     "name": "glibc@2.39",
                #     "depflags": ["LINK"],
                #     "virtuals": ["libc"],
                # },
                # {
                #     "name": "gcc@12.4.0",  # SYSTEM COMPILER
                #     "depflags": ["BUILD"],
                #     "virtuals": ["c", "cxx"],
                # },
                # {
                #     "name": "compiler-wrapper",
                #     "depflags": ["BUILD"],
                # },
                # there are many more link dependencies
            ],
        },
        {
            "name": "gcc-runtime",
            "version": "13.3.0",  # EBVERSIONGCC
            "variants": "",
            "external_path": "/home/lercole/ebspack/software/GCCcore/13.3.0", # EBROOTGCCCORE or EBROOTGCC
            # "external_modules": ["/home/lercole/ebspack/modules/all/GCC/13.3.0.lua"],
            "dependencies": [
                {
                    "name": "gcc@13.3.0",  # EB GCC COMPILER
                    "depflags": ["BUILD"],
                },
                {
                    "name": "glibc@2.39",
                    "depflags": ["LINK"],
                    "virtuals": ["libc"],
                },
            ],
        },
        {
            "name": "gmake",
            "version": "4.4",  # EBVERSIONMAKE
            "variants": "",
            "external_path": "/home/lercole/ebspack/software/make/4.4.1-GCCcore-13.3.0", # EBROOTMAKE
            # "external_modules": ["/home/lercole/ebspack/modules/all/make/4.4.1-GCCcore-13.3.0.lua"],
            "dependencies": [
                # {
                #     "name": "compiler-wrapper",
                #     "depflags": ["BUILD"],
                # },
                {
                    "name": "gcc@13.3.0",
                    "depflags": ["BUILD"],
                    "virtuals": ["c"],
                },
                {
                    "name": "gcc-runtime@13.3.0",
                    "depflags": ["LINK"],
                },
                {
                    "name": "glibc@2.39",
                    "depflags": ["LINK"],
                    "virtuals": ["libc"],
                },
            ],
        },
        # {
        #     "name": "cmake",
        #     "version": "3.31.8",  # EBVERSIONCMAKE
        #     "variants": "",
        #     "external_path": "/home/lercole/ebspack/software/cmake/3.31.8-GCCcore-13.3.0", # EBROOTCMAKE
        #     "dependencies": [
        #         {
        #             "name": "gcc@13.3.0",
        #             "depflags": ["BUILD"],
        #             "virtuals": ["c", "cxx"],
        #         },
        #         {
        #             "name": "gcc-runtime@13.3.0",
        #             "depflags": ["LINK"],
        #         },
        #         {
        #             "name": "glibc@2.39",
        #             "depflags": ["LINK"],
        #             "virtuals": ["libc"],
        #         },
        #         {
        #             "name": "gmake@4.4.1",    # not for EasyBuild !
        #             "depflags": ["BUILD", "RUN"],
        #         },
        #         # {
        #         #     "name": "curl",
        #         #     "depflags": ["BUILD", "LINK"],
        #         # },
        #         # {
        #         #     "name": "ncurses",
        #         #     "depflags": ["BUILD", "LINK"],
        #         # },
        #         # {
        #         #     "name": "zlib-ng",   # but in EasyBuild it depends on zlib
        #         #     "depflags": ["BUILD", "LINK"],
        #         # },
                
        #         # libarchive, bzip2, openssl 3 --> not dependencies in cmake Spack package
        #     ],
        # },

    ]
}

# Create specloader and add to database
specloader = SpecLoader(database_path="/home/lercole/ebspack/spack/upstreams/test-1")
specloader.load_configuration(spec_dict)    
specloader.build_specs()

# Show what will be added
print("Specs that will be added:")
for key, spec in specloader._specs_map.items():
    print(f"  {key}: {spec}  [{spec.architecture}]")
    if spec.dependencies():
        print(f"    dependencies:  {[d.name for d in spec.dependencies()]}")

# Add to database
specloader.add_to_database()

# Add packages to packages.yaml configuration file
add_packages_to_config(specloader.iter_specs())

# # COMPILERS
# print("Compilers found: ", specloader.list_compilers())
# spack.compilers.config.add_compiler_to_config(specloader.list_compilers())

# new_compilers = spack.compilers.config.find_compilers(
#     path_hints=[
#         "/home/lercole/ebspack/software/GCCcore/13.3.0"
#     ],  # paths to search for compilers
#     scope='user',  # or 'site', 'system', etc.
#     max_workers=4  # parallel search
# )
# print("Compilers found: ", new_compilers)

# if new_compilers:
#     n = len(new_compilers)
#     s = "s" if n > 1 else ""
#     filename = spack.config.CONFIG.get_config_filename('user', "packages")
#     print(f"Added {n:d} new compiler{s} to {filename}")
#     compiler_strs = sorted(f"{spec.name}@{spec.versions}" for spec in new_compilers)
#     for c in reversed(compiler_strs):
#         print(f"    {c}")

