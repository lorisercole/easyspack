
# Define the configuration as a dictionary (same as original add_pkg.py)
# NOTES:
# - compilers (gcc) should not have dependencies, but have extra_attributes with compiler paths
# - all packages should have runtime and link dependencies declared
# - the only build dependency needed is the compiler with c/cxx/fortran virtuals, this is shows which compiler was used to build
# - dependencies are automatically sorted by name by the loader
# - Skipping dependencies that are not needed for EasyBuild or Spack does not seem to lead to problems
# - default variants are automatically added by the loader if not specified. This seems the best approach with the current solver

example_dict = {
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
            "explicit": True,
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
            "explicit": True,
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
            "explicit": True,
            "external_path": "/home/lercole/ebspack/software/GCCcore/13.3.0", # EBROOTGCCCORE or EBROOTGCC
            # "external_modules": ["/home/lercole/ebspack/modules/all/GCC/13.3.0.lua"],
            "extra_attributes": {
                "compilers": {
                    "c": "/home/lercole/ebspack/software/GCCcore/13.3.0/bin/gcc",
                    "cxx": "/home/lercole/ebspack/software/GCCcore/13.3.0/bin/g++",
                    "fortran": "/home/lercole/ebspack/software/GCCcore/13.3.0/bin/gfortran",
                }
            },
            "dependencies": []
            #     {
            #         "name": "gcc-runtime@12.4.0",
            #         "depflags": ["LINK"],
            #     },
            #     {
            #         "name": "glibc@2.39",
            #         "depflags": ["LINK"],
            #         "virtuals": ["libc"],
            #     },
            #     {
            #         "name": "gcc@12.4.0",  # SYSTEM COMPILER
            #         "depflags": ["BUILD"],
            #         "virtuals": ["c", "cxx"],
            #     },
            #     {
            #         "name": "compiler-wrapper",
            #         "depflags": ["BUILD"],
            #     },
            #     # there are many more link dependencies
            # ],
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
            "explicit": True,
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
        {
            "name": "zlib",
            "version": "1.3.1",  # EBVERSIONZLIB
            "variants": "",
            "external_path": "/home/lercole/ebspack/software/zlib/1.3.1-GCCcore-13.3.0", # EBROOTZLIB
            "dependencies": [
                {
                    "name": "gcc@13.3.0",
                    "depflags": ["BUILD"],
                    "virtuals": ["c", "cxx"],
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
        {
            "name": "libarchive",
            "version": "3.7.4",  # EBVERSIONLIBARCHIVE
            "variants": "",
            "external_path": "/home/lercole/ebspack/software/libarchive/3.7.4-GCCcore-13.3.0", # EBROOTLIBARCHIVE
            "dependencies": [
                {
                    "name": "gcc@13.3.0",
                    "depflags": ["BUILD"],
                    "virtuals": ["c", "cxx"],
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
        {
            "name": "bzip2",
            "version": "1.0.8",  # EBVERSIONBZIP2
            "variants": "",
            "external_path": "/home/lercole/ebspack/software/bzip2/1.0.8-GCCcore-13.3.0", # EBROOTBZIP2
            "dependencies": [
                {
                    "name": "gcc@13.3.0",
                    "depflags": ["BUILD"],
                    "virtuals": ["c", "cxx"],
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
        {
            "name": "cmake",
            "version": "3.31.8",  # EBVERSIONCMAKE
            "variants": "",
            "explicit": True,
            "external_path": "/home/lercole/ebspack/software/CMake/3.31.8-GCCcore-13.3.0", # EBROOTCMAKE
            "dependencies": [
                {
                    "name": "gcc@13.3.0",
                    "depflags": ["BUILD"],
                    "virtuals": ["c", "cxx"],
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
                # {
                #     "name": "gmake@4.4.1",    # not for EasyBuild !
                #     "depflags": ["BUILD", "RUN"],
                # },
                # {
                #     "name": "curl",
                #     "depflags": ["BUILD", "LINK"],
                # },
                # {
                #     "name": "ncurses",
                #     "depflags": ["BUILD", "LINK"],
                # },
                {
                    "name": "zlib@1.3.1",   # in Spack it depends on the virtual zlib-api (zlib or zlib-ng)
                    "depflags": ["BUILD", "LINK"],
                },
                
                # libarchive, bzip2, openssl 3 --> not dependencies in cmake Spack package
                {
                    "name": "libarchive@3.7.4",  # in Spack it is not needed if +ownlib
                    "depflags": ["BUILD", "LINK"],
                },
                {
                    "name": "bzip2@1.0.8",   # in Spack it depends on the virtual zlib-api (zlib or zlib-ng)
                    "depflags": ["LINK"],
                },
            ],
        },

    ]
}
