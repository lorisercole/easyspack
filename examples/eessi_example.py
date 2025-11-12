
# Define the configuration as a dictionary (same as original add_pkg.py)
# NOTES:
# - compilers (gcc) should not have dependencies, but have extra_attributes with compiler paths
# - all packages should have runtime and link dependencies declared
# - the only build dependency needed is the compiler with c/cxx/fortran virtuals, this is shows which compiler was used to build
# - dependencies are automatically sorted by name by the loader
# - Skipping dependencies that are not needed for EasyBuild or Spack does not seem to lead to problems
# - default variants are automatically added by the loader if not specified. This seems the best approach with the current solver
# - if a version does not exist in Spack, it is not a problem
# - we'll need to be careful with EESSI compat layer, and packages that have been filtered out (e.g. glibc, binutils, etc)
# - EESSI filtered dependencies:
#   Autoconf,Automake,Autotools,binutils,bzip2,DBus,flex,gettext,gperf,help2man,intltool,libreadline,libtool,M4,makeinfo,ncurses,util-linux,XZ,zlib
# - glibc is detected by Spack and dependencies are automatically added
# - gcc-runtime is added by Spack

example_dict = {
    "architecture": {
        "platform": "linux",
        "os": "ubuntu24.04",
        "target": "skylake"  # the one detected by Spack (may differ from EESSI target)
    },
    "specs": [
        # COMPAT LAYER EXTERNAL PACKAGES ARE DETECTED AUTOMATICALLY BY SPACK

        # SOFTWARE PACKAGES
        {  # EB GCC COMPILER
            "name": "gcc",
            "version": "13.2.0",  # EBVERSIONGCC
            "variants": "",
            "explicit": True,
            "external_path": "/cvmfs/software.eessi.io/versions/2023.06/software/linux/x86_64/intel/haswell/software/GCCcore/13.2.0", # EBROOTGCCCORE or EBROOTGCC
            # "external_modules": ["/cvmfs/software.eessi.io/versions/2023.06/software/linux/x86_64/intel/haswell/modules/all/GCC/13.2.0.lua"],
            "extra_attributes": {
                "compilers": {
                    "c": "/cvmfs/software.eessi.io/versions/2023.06/software/linux/x86_64/intel/haswell/software/GCCcore/13.2.0/bin/gcc",
                    "cxx": "/cvmfs/software.eessi.io/versions/2023.06/software/linux/x86_64/intel/haswell/software/GCCcore/13.2.0/bin/g++",
                    "fortran": "/cvmfs/software.eessi.io/versions/2023.06/software/linux/x86_64/intel/haswell/software/GCCcore/13.2.0/bin/gfortran",
                }
            },
            "dependencies": []
        },
        {
            "name": "gmake",
            "version": "4.4.1",  # EBVERSIONMAKE
            "variants": "",
            "explicit": True,
            "external_path": "/cvmfs/software.eessi.io/versions/2023.06/software/linux/x86_64/intel/haswell/software/make/4.4.1-GCCcore-13.2.0", # EBROOTMAKE
            # "external_modules": ["/cvmfs/software.eessi.io/versions/2023.06/software/linux/x86_64/intel/haswell/modules/all/make/4.4.1-GCCcore-13.2.0.lua"],
            "dependencies": [
                {
                    "name": "gcc@13.2.0",
                    "depflags": ["BUILD"],
                    "virtuals": ["c"],
                },
            ],
        },
        # {
        #     "name": "git",
        #     "version": "2.42.0",  # EBVERSIONGIT
        #     "variants": "",
        #     "explicit": True,
        #     "external_path": "/cvmfs/software.eessi.io/versions/2023.06/software/linux/x86_64/intel/haswell/software/git/2.42.0-GCCcore-13.2.0", # EBROOTGIT
        #     "dependencies": [
        #         {
        #             "name": "gcc@13.2.0",
        #             "depflags": ["BUILD"],
        #             "virtuals": ["c"],
        #         },
        #         {
        #             "name": "gcc-runtime@13.2.0",
        #             "depflags": ["LINK"],
        #         },
        #         {
        #             "name": "glibc@2.36",
        #             "depflags": ["LINK"],
        #             "virtuals": ["libc"],
        #         },
        #         {
        #             "name": "curl@8.3.0",
        #             "depflags": ["BUILD", "LINK"],
        #         },
        #         {
        #             "name": "openssl@1.1.1w",
        #             "depflags": ["BUILD", "LINK"],
        #         },
        #         # missing: gettext, Perl, expat
        #     ],
        # },
        {
            "name": "openblas",
            "version": "0.3.24",  # EBVERSIONOPENBLAS
            "variants": "~ilp64 threads=openmp",  # not detectable by Spack
            "explicit": True,
            "external_path": "/cvmfs/software.eessi.io/versions/2023.06/software/linux/x86_64/intel/haswell/software/OpenBLAS/0.3.24-GCC-13.2.0", # EBROOTOPENBLAS
            # "external_modules": ["/cvmfs/software.eessi.io/versions/2023.06/software/linux/x86_64/intel/haswell/modules/all/OpenBLAS/0.3.24-GCC-13.2.0.lua"],
            "dependencies": [
                {
                    "name": "gcc@13.2.0",
                    "depflags": ["BUILD"],
                    "virtuals": ["c", "cxx", "fortran"],
                },
            ],
        },
        {
            "name": "fftw",
            "version": "3.3.10",  # EBVERSIONFFTW
            "variants": "~mpi+openmp+shared precision=float,double,long_double,quad",  # not detectable by Spack  # precision: EB builds all of them if possible - to be checked (there are exceptions, like when using MPI or on ARM)
            "explicit": True,
            "external_path": "/cvmfs/software.eessi.io/versions/2023.06/software/linux/x86_64/intel/haswell/software/FFTW/3.3.10-GCC-13.2.0", # EBROOTFFTW
            # "external_modules": ["/cvmfs/software.eessi.io/versions/2023.06/software/linux/x86_64/intel/haswell/modules/all/FFTW/3.3.10-GCC-13.2.0.lua"],
            "dependencies": [
                {
                    "name": "gcc@13.2.0",
                    "depflags": ["BUILD"],
                    "virtuals": ["c", "fortran"],
                },
            ],
        },
        # {
        #     "name": "fftw",
        #     "version": "3.3.10",  # EBVERSIONFFTWMPI
        #     "variants": "+mpi~openmp+shared precision=float,double,long_double",  # not detectable by Spack  # precision: EB builds all of them if possible - to be checked (there are exceptions, like when using MPI or on ARM)
        #     "explicit": True,
        #     "external_path": "/cvmfs/software.eessi.io/versions/2023.06/software/linux/x86_64/intel/haswell/software/FFTW.MPI/3.3.10-gompi-2023b", # EBROOTFFTWMPI
        #     # "external_modules": ["/cvmfs/software.eessi.io/versions/2023.06/software/linux/x86_64/intel/haswell/modules/all/FFTW.MPI/3.3.10-gompi-2023b.lua"],
        #     "dependencies": [
        #         {
        #             "name": "gcc@13.2.0",
        #             "depflags": ["BUILD"],
        #             "virtuals": ["c", "fortran"],
        #         },
        #         ...
        #     ],
        # },
        {
            "name": "curl",
            "version": "8.3.0",  # EBVERSIONCURL
            "variants": "+nghttp2",
            "external_path": "/cvmfs/software.eessi.io/versions/2023.06/software/linux/x86_64/intel/haswell/software/cURL/8.3.0-GCCcore-13.2.0", # EBROOTCURL
            "dependencies": [
                {
                    "name": "gcc@13.2.0",
                    "depflags": ["BUILD"],
                    "virtuals": ["c", "cxx"],
                },
                {
                    "name": "zlib@1.2.13",
                    "depflags": ["LINK"],
                },
                {
                    "name": "openssl@1.1.1w",
                    "depflags": ["BUILD", "LINK"],
                },
                # nghttp2 : not a dependency in EB
            ],
        },
        {
            "name": "libarchive",
            "version": "3.7.2",  # EBVERSIONLIBARCHIVE
            "variants": "",
            "external_path": "/cvmfs/software.eessi.io/versions/2023.06/software/linux/x86_64/intel/haswell/software/libarchive/3.7.2-GCCcore-13.2.0", # EBROOTLIBARCHIVE
            "dependencies": [
                {
                    "name": "gcc@13.2.0",
                    "depflags": ["BUILD"],
                    "virtuals": ["c", "cxx"],
                },
            ],
        },
        {
            "name": "cmake",
            "version": "3.31.8",  # EBVERSIONCMAKE
            "variants": "",
            "explicit": True,
            "external_path": "/cvmfs/software.eessi.io/versions/2023.06/software/linux/x86_64/intel/haswell/software/CMake/3.27.6-GCCcore-13.2.0", # EBROOTCMAKE
            "dependencies": [
                {
                    "name": "gcc@13.2.0",
                    "depflags": ["BUILD"],
                    "virtuals": ["c", "cxx"],
                },
                # {
                #     "name": "gmake@4.4.1",    # not for EasyBuild !
                #     "depflags": ["BUILD", "RUN"],
                # },
                {
                    "name": "curl@8.3.0%gcc@13.2.0",
                    "depflags": ["BUILD", "LINK"],
                },
                {  # filtered dependency in EESSI
                    "name": "ncurses@6.4.20230401",
                    "depflags": ["BUILD", "LINK"],
                },
                {  # filtered dependency in EESSI
                    "name": "zlib@1.2.13",   # in Spack it depends on the virtual zlib-api (zlib or zlib-ng)
                    "depflags": ["BUILD", "LINK"],
                },
                # libarchive, bzip2, openssl 3 --> not dependencies in cmake Spack package
                {
                    "name": "libarchive@3.7.2%gcc@13.2.0",  # in Spack it is not needed if +ownlib
                    "depflags": ["BUILD", "LINK"],
                },
                {  # filtered dependency in EESSI
                    "name": "bzip2@1.0.8",
                    "depflags": ["LINK"],
                },
                {  # EESSI module points to compat layer
                    "name": "openssl@1.1.1w",
                    "depflags": ["BUILD", "LINK"],
                },
            ],
        },
    ]
}