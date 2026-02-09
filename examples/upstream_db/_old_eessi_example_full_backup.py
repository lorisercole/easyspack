
# Old example showing full database configuration, including glibc and gcc-runtime deps

example_dict = {
    "architecture": {
        "platform": "linux",
        "os": "ubuntu24.04",
        "target": "skylake"  # the one detected by Spack (may differ from EESSI target)
    },
    "specs": [
        # COMPAT LAYER EXTERNAL PACKAGES ARE DETECTED AUTOMATICALLY BY SPACK
        {
            "name": "glibc",
            "version": "2.37",  # EBVERSIONMAKE
            "variants": "",
            "explicit": True,
            "external_path": "/cvmfs/software.eessi.io/versions/2023.06/compat/linux/x86_64",
            "dependencies": [],
        },

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
            "dependencies": [],
        },
        {
            "name": "gcc-runtime",
            "version": "13.2.0",  # EBVERSIONGCC
            "variants": "",
            "external_path": "/cvmfs/software.eessi.io/versions/2023.06/software/linux/x86_64/intel/haswell/software/GCCcore/13.2.0", # EBROOTGCCCORE or EBROOTGCC
            "dependencies": [
                {
                    "name": "gcc@13.2.0",
                    "depflags": ["BUILD"],
                },
                {
                    "name": "glibc@2.37",
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
            "external_path": "/cvmfs/software.eessi.io/versions/2023.06/software/linux/x86_64/intel/haswell/software/make/4.4.1-GCCcore-13.2.0", # EBROOTMAKE
            # "external_modules": ["/cvmfs/software.eessi.io/versions/2023.06/software/linux/x86_64/intel/haswell/modules/all/make/4.4.1-GCCcore-13.2.0.lua"],
            "dependencies": [
                {
                    "name": "gcc@13.2.0",
                    "depflags": ["BUILD"],
                    "virtuals": ["c"],
                },
                {
                    "name": "gcc-runtime@13.2.0",
                    "depflags": ["LINK"],
                },
                {
                    "name": "glibc@2.37",
                    "depflags": ["LINK"],
                    "virtuals": ["libc"],
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
        #             "name": "glibc@2.37",
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
        # {
        #     "name": "zlib",  # filtered dependency in EESSI
        #     "version": "1.3.1",  # EBVERSIONZLIB
        #     "variants": "",
        #     "external_path": "/home/lercole/spood/software/zlib/1.3.1-GCCcore-13.2.0", # EBROOTZLIB
        #     "dependencies": [
        #         {
        #             "name": "gcc@13.2.0",
        #             "depflags": ["BUILD"],
        #             "virtuals": ["c", "cxx"],
        #         },
        #         {
        #             "name": "gcc-runtime@13.2.0",
        #             "depflags": ["LINK"],
        #         },
        #         {
        #             "name": "glibc@2.37",
        #             "depflags": ["LINK"],
        #             "virtuals": ["libc"],
        #         },
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
                {
                    "name": "gcc-runtime@13.2.0",
                    "depflags": ["LINK"],
                },
                {
                    "name": "glibc@2.37",
                    "depflags": ["LINK"],
                    "virtuals": ["libc"],
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
                {
                    "name": "gcc-runtime@13.2.0",
                    "depflags": ["LINK"],
                },
                {
                    "name": "glibc@2.37",
                    "depflags": ["LINK"],
                    "virtuals": ["libc"],
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
        #         {
        #             "name": "gcc-runtime@13.2.0",
        #             "depflags": ["LINK"],
        #         },
        #         {
        #             "name": "glibc@2.37",
        #             "depflags": ["LINK"],
        #             "virtuals": ["libc"],
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
                    "name": "gcc-runtime@13.2.0",
                    "depflags": ["LINK"],
                },
                {
                    "name": "glibc@2.37",
                    "depflags": ["LINK"],
                    "virtuals": ["libc"],
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
                {
                    "name": "gcc-runtime@13.2.0",
                    "depflags": ["LINK"],
                },
                {
                    "name": "glibc@2.37",
                    "depflags": ["LINK"],
                    "virtuals": ["libc"],
                },
            ],
        },
        # {
        #     "name": "ncurses",  # filered dependency in EESSI
        #     "version": "6.5",  # EBVERSIONNCURSES
        #     "variants": "abi=6",  # detectable by Spack
        #     "external_path": "/home/lercole/spood/software/ncurses/6.5-GCCcore-13.2.0", # EBROOTNCURSES
        #     "dependencies": [
        #         {
        #             "name": "gcc@13.2.0",
        #             "depflags": ["BUILD"],
        #             "virtuals": ["c", "cxx"],
        #         },
        #         {
        #             "name": "gcc-runtime@13.2.0",
        #             "depflags": ["LINK"],
        #         },
        #         {
        #             "name": "glibc@2.37",
        #             "depflags": ["LINK"],
        #             "virtuals": ["libc"],
        #         },
        #     ],
        # },
        # {  # filtered dependency in EESSI
        #     "name": "bzip2",
        #     "version": "1.0.8",  # EBVERSIONBZIP2
        #     "variants": "",
        #     "external_path": "/home/lercole/spood/software/bzip2/1.0.8-GCCcore-13.2.0", # EBROOTBZIP2
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
        #             "name": "glibc@2.37",
        #             "depflags": ["LINK"],
        #             "virtuals": ["libc"],
        #         },
        #     ],
        # },
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
                {
                    "name": "gcc-runtime@13.2.0",
                    "depflags": ["LINK"],
                },
                {
                    "name": "glibc@2.37",
                    "depflags": ["LINK"],
                    "virtuals": ["libc"],
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
                # libarchive, bzip2, openssl --> not dependencies in cmake Spack package
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
