# NOTES

## General notes about Spack
- pure build dependencies are not included in Spack solve, but they affect the hash
- a node has a hash determined by the content of `node.to_node_dict()`
- installed compiled packages typically have `gcc-runtime` and `glibc` link deps.
- `glibc` is automatically detected from the compiler and added
- the only BUILD dependency needed is the compiler with `c/cxx/fortran` virtuals, this shows which compiler was used to build the pkg
- skipping dependencies that are not needed for EasyBuild or Spack does not seem to lead to problems
- if a version does not exist in Spack, it is not a problem
- we need to be careful with **EESSI compat layer**, and packages that have been filtered out (e.g. glibc, binutils, etc)\
  **EESSI filtered dependencies**:
  - Autoconf
  - Automake
  - Autotools
  - binutils
  - bzip2
  - DBus
  - flex
  - gettext
  - gperf
  - help2man
  - intltool
  - libreadline
  - libtool
  - M4
  - makeinfo
  - ncurses
  - util-linux
  - XZ
  - zlib


## 1. Old approach: create custom upstream database
- all packages should have runtime and link dependencies declared -- automatically injected by spood
- compilers (gcc) should not have dependencies, but have `extra_attributes` with compiler paths
- `glibc` is detected and dependencies are automatically added
- `gcc-runtime` is automatically injected by spood
- dependencies are automatically sorted by name by the loader
- default variants are automatically added by the loader if not specified. This seems the best approach with the current solver


## 2. New approach: (new) externals with dependencies
- it works, but they can only be seen with `spack find --show-configured-externals`, unless they have been installed
- **only packages that can be link/runtime dependencies of other packages actually need their dependencies declared**. If they are build deps, specifying them won't affect the resulting build.
- we have code to create an (upstream) database, but we should stick with the official approach using external pkgs

### To Do:
- script to generate `packages.yaml` (or JSON, when spack will support it) from EESSI metadata
- test MPI/CUDA, more complex cases

### Example: externals + their deps in packages.yaml
(Specifying dependencies does not seem to change the installation in this case.)
We also specified deps coming from the OS (compat layer)
```
$ spack spec -Ilt quantum-espresso~mpi
 -   kansnbl  [    ]  quantum-espresso@7.4.1~clock+epw~fox~gipaw~ipo~libxc~mpi~nvtx+openmp+patch~qmcpack build_system=cmake build_type=Release generator=make hdf5=none platform=linux os=ubuntu24.04 target=skylake %c,cxx,fortran=gcc@13.2.0
[e]  jqhlhqs  [b   ]      ^cmake@3.31.8~doc+ncurses+ownlibs~qtgui build_system=generic build_type=Release platform=linux os=ubuntu24.04 target=haswell %c,cxx=gcc@13.2.0
[e]  tu5vpke  [ l  ]          ^bzip2@1.0.8~debug~pic+shared build_system=generic platform=linux os=ubuntu24.04 target=x86_64
[e]  zpbw4on  [bl  ]          ^curl@8.3.0~gssapi~ldap~libidn2~librtmp~libssh~libssh2+nghttp2 build_system=autotools libs:=shared,static tls:=openssl platform=linux os=ubuntu24.04 target=haswell %c,cxx=gcc@13.2.0
[e]  atohw4p  [bl  ]          ^libarchive@3.7.2+iconv build_system=autotools compression:=bz2lib,lz4,lzma,lzo2,zlib,zstd crypto=openssl libs:=shared,static programs:=none xar=libxml2 platform=linux os=ubuntu24.04 target=haswell %c,cxx=gcc@13.2.0
[e]  4osmizu  [bl  ]          ^ncurses@6.4.20230401+symlinks+termlib abi:=6 build_system=autotools platform=linux os=ubuntu24.04 target=x86_64
[e]  fkyk67i  [bl  ]          ^openssl@1.1.1w~docs+shared build_system=generic certs=mozilla platform=linux os=ubuntu24.04 target=x86_64
[e]  pt7lg52  [bl  ]          ^zlib@1.2.13+optimize+pic+shared build_system=makefile platform=linux os=ubuntu24.04 target=x86_64
 -   rtilhiy  [b   ]      ^compiler-wrapper@1.0 build_system=generic platform=linux os=ubuntu24.04 target=skylake
[e]  evnxv5r  [bl  ]      ^fftw@3.3.10~mpi+openmp~pfft_patches+shared build_system=autotools precision:=double,float,long_double,quad platform=linux os=ubuntu24.04 target=haswell %c,fortran=gcc@13.2.0
[e]  f4hdzzh  [b   ]      ^gcc@13.2.0~binutils+bootstrap~graphite~mold~nvptx~piclibs~profiled~strip build_system=autotools build_type=RelWithDebInfo languages:='c,c++,fortran' platform=linux os=ubuntu24.04 target=haswell
 -   qzvkemk  [ l  ]      ^gcc-runtime@13.2.0 build_system=generic platform=linux os=ubuntu24.04 target=skylake
[e]  34vxbjt  [b   ]      ^git@2.41.0+man+nls+perl+subtree~svn~tcltk build_system=autotools platform=linux os=ubuntu24.04 target=x86_64
[e]  hrhksje  [ l  ]      ^glibc@2.37 build_system=autotools platform=linux os=ubuntu24.04 target=x86_64
[e]  ujaicej  [b   ]      ^gmake@4.4.1~guile build_system=generic platform=linux os=ubuntu24.04 target=haswell %c=gcc@13.2.0
[e]  gz4jmks  [b   ]      ^m4@1.4.19+sigsegv build_system=autotools platform=linux os=ubuntu24.04 target=x86_64
[e]  fs3sguj  [bl  ]      ^openblas@0.3.24~bignuma~consistent_fpcsr+dynamic_dispatch+fortran~ilp64+locking+pic+shared build_system=makefile symbol_suffix=none threads:=openmp platform=linux os=ubuntu24.04 target=haswell %c,cxx,fortran=gcc@13.2.0

$ ldd $(spack location -i quantum-espresso)/bin/pw.x
    linux-vdso.so.1 (0x00007869b12e2000)
    libfftw3.so.3 => /cvmfs/software.eessi.io/versions/2023.06/software/linux/x86_64/intel/haswell/software/FFTW/3.3.10-GCC-13.2.0/lib/libfftw3.so.3 (0x00007869b1000000)
    libfftw3_omp.so.3 => /cvmfs/software.eessi.io/versions/2023.06/software/linux/x86_64/intel/haswell/software/FFTW/3.3.10-GCC-13.2.0/lib/libfftw3_omp.so.3 (0x00007869b12d4000)
    libgomp.so.1 => /home/lercole/eessi/spack/opt/linux-skylake/gcc-runtime-13.2.0-qzvkemkvff7xpkoecxtxmcnzdukdcp2v/lib/libgomp.so.1 (0x00007869b0fae000)
    libgfortran.so.5 => /home/lercole/eessi/spack/opt/linux-skylake/gcc-runtime-13.2.0-qzvkemkvff7xpkoecxtxmcnzdukdcp2v/lib/libgfortran.so.5 (0x00007869b0c00000)
    libm.so.6 => /cvmfs/software.eessi.io/versions/2023.06/compat/linux/x86_64/lib64/libm.so.6 (0x00007869b0b20000)
    libmvec.so.1 => /cvmfs/software.eessi.io/versions/2023.06/compat/linux/x86_64/lib64/libmvec.so.1 (0x00007869b0a28000)
    libopenblas.so.0 => /cvmfs/software.eessi.io/versions/2023.06/software/linux/x86_64/intel/haswell/software/OpenBLAS/0.3.24-GCC-13.2.0/lib/libopenblas.so.0 (0x00007869afc00000)
    libgcc_s.so.1 => /home/lercole/eessi/spack/opt/linux-skylake/gcc-runtime-13.2.0-qzvkemkvff7xpkoecxtxmcnzdukdcp2v/lib/libgcc_s.so.1 (0x00007869b12a2000)
    libc.so.6 => /cvmfs/software.eessi.io/versions/2023.06/compat/linux/x86_64/lib64/libc.so.6 (0x00007869afa2f000)
    /cvmfs/software.eessi.io/versions/2023.06/compat/linux/x86_64/lib64/ld-linux-x86-64.so.2 (0x00007869b12e4000)
```


# Feb 2026

## Problematic compat-layer dependencies
`curl` and `zlib` do not work properly when building a new `cmake` from source (see [this error report](./compat_pkgs_problems.md)). We should exclude them from the automatic detection.

I wonder if dependencies on compat-layer packages are actually needed.

## OpenMPI tests
I've tried to use EESSI's OpenMPI. It requires many dependencies.
In particular, `libpciaccess` is needed by the MPI linker. Without it, the `hwloc` library cannot find `libpciaccess` symbols
```bash
$ mpicxx -o test test.cpp
/cvmfs/software.eessi.io/versions/2023.06/compat/linux/x86_64/usr/bin/ld: warning: libpciaccess.so.0, needed by /cvmfs/software.eessi.io/versions/2023.06/software/linux/x86_64/intel/haswell/software/OpenMPI/4.1.6-GCC-13.2.0/lib/libmpi.so, not found (try using -rpath or -rpath-link)
/cvmfs/software.eessi.io/versions/2023.06/compat/linux/x86_64/usr/bin/ld: /cvmfs/software.eessi.io/versions/2023.06/software/linux/x86_64/intel/haswell/software/hwloc/2.9.2-GCCcore-13.2.0/lib/libhwloc.so.15: undefined reference to `pci_device_cfg_read'
/cvmfs/software.eessi.io/versions/2023.06/compat/linux/x86_64/usr/bin/ld: /cvmfs/software.eessi.io/versions/2023.06/software/linux/x86_64/intel/haswell/software/hwloc/2.9.2-GCCcore-13.2.0/lib/libhwloc.so.15: undefined reference to `pci_system_cleanup'
/cvmfs/software.eessi.io/versions/2023.06/compat/linux/x86_64/usr/bin/ld: /cvmfs/software.eessi.io/versions/2023.06/software/linux/x86_64/intel/haswell/software/hwloc/2.9.2-GCCcore-13.2.0/lib/libhwloc.so.15: undefined reference to `pci_slot_match_iterator_create'
/cvmfs/software.eessi.io/versions/2023.06/compat/linux/x86_64/usr/bin/ld: /cvmfs/software.eessi.io/versions/2023.06/software/linux/x86_64/intel/haswell/software/hwloc/2.9.2-GCCcore-13.2.0/lib/libhwloc.so.15: undefined reference to `pci_system_init'
/cvmfs/software.eessi.io/versions/2023.06/compat/linux/x86_64/usr/bin/ld: /cvmfs/software.eessi.io/versions/2023.06/software/linux/x86_64/intel/haswell/software/hwloc/2.9.2-GCCcore-13.2.0/lib/libhwloc.so.15: undefined reference to `pci_device_probe'
/cvmfs/software.eessi.io/versions/2023.06/compat/linux/x86_64/usr/bin/ld: /cvmfs/software.eessi.io/versions/2023.06/software/linux/x86_64/intel/haswell/software/hwloc/2.9.2-GCCcore-13.2.0/lib/libhwloc.so.15: undefined reference to `pci_device_next'
/cvmfs/software.eessi.io/versions/2023.06/compat/linux/x86_64/usr/bin/ld: /cvmfs/software.eessi.io/versions/2023.06/software/linux/x86_64/intel/haswell/software/hwloc/2.9.2-GCCcore-13.2.0/lib/libhwloc.so.15: undefined reference to `pci_iterator_destroy'
/cvmfs/software.eessi.io/versions/2023.06/compat/linux/x86_64/usr/bin/ld: /cvmfs/software.eessi.io/versions/2023.06/software/linux/x86_64/intel/haswell/software/hwloc/2.9.2-GCCcore-13.2.0/lib/libhwloc.so.15: undefined reference to `pci_get_strings'
```

This is an issue originated from EESSI's OpenMPI installation:
```bash
(base) lercole@cecampc21:~/tests/mpicode$ module load OpenMPI/4.1.6-GCC-13.2.0
(base) lercole@cecampc21:~/tests/mpicode$ mpicxx -o test test.cpp
# all good here

# but if we unload the libpciaccess module...
(base) lercole@cecampc21:~/tests/mpicode$ module unload libpciaccess/0.17-GCCcore-13.2.0
(base) lercole@cecampc21:~/tests/mpicode$ mpicxx -o test test.cpp
/cvmfs/software.eessi.io/versions/2023.06/compat/linux/x86_64/usr/bin/ld: warning: libpciaccess.so.0, needed by /cvmfs/software.eessi.io/versions/2023.06/software/linux/x86_64/intel/haswell/software/OpenMPI/4.1.6-GCC-13.2.0/lib/libmpi.so, not found (try using -rpath or -rpath-link)
/cvmfs/software.eessi.io/versions/2023.06/compat/linux/x86_64/usr/bin/ld: /cvmfs/software.eessi.io/versions/2023.06/software/linux/x86_64/intel/haswell/software/hwloc/2.9.2-GCCcore-13.2.0/lib/libhwloc.so.15: undefined reference to `pci_device_cfg_read'
/cvmfs/software.eessi.io/versions/2023.06/compat/linux/x86_64/usr/bin/ld: /cvmfs/software.eessi.io/versions/2023.06/software/linux/x86_64/intel/haswell/software/hwloc/2.9.2-GCCcore-13.2.0/lib/libhwloc.so.15: undefined reference to `pci_system_cleanup'
/cvmfs/software.eessi.io/versions/2023.06/compat/linux/x86_64/usr/bin/ld: /cvmfs/software.eessi.io/versions/2023.06/software/linux/x86_64/intel/haswell/software/hwloc/2.9.2-GCCcore-13.2.0/lib/libhwloc.so.15: undefined reference to `pci_slot_match_iterator_create'
/cvmfs/software.eessi.io/versions/2023.06/compat/linux/x86_64/usr/bin/ld: /cvmfs/software.eessi.io/versions/2023.06/software/linux/x86_64/intel/haswell/software/hwloc/2.9.2-GCCcore-13.2.0/lib/libhwloc.so.15: undefined reference to `pci_system_init'
/cvmfs/software.eessi.io/versions/2023.06/compat/linux/x86_64/usr/bin/ld: /cvmfs/software.eessi.io/versions/2023.06/software/linux/x86_64/intel/haswell/software/hwloc/2.9.2-GCCcore-13.2.0/lib/libhwloc.so.15: undefined reference to `pci_device_probe'
/cvmfs/software.eessi.io/versions/2023.06/compat/linux/x86_64/usr/bin/ld: /cvmfs/software.eessi.io/versions/2023.06/software/linux/x86_64/intel/haswell/software/hwloc/2.9.2-GCCcore-13.2.0/lib/libhwloc.so.15: undefined reference to `pci_device_next'
/cvmfs/software.eessi.io/versions/2023.06/compat/linux/x86_64/usr/bin/ld: /cvmfs/software.eessi.io/versions/2023.06/software/linux/x86_64/intel/haswell/software/hwloc/2.9.2-GCCcore-13.2.0/lib/libhwloc.so.15: undefined reference to `pci_iterator_destroy'
/cvmfs/software.eessi.io/versions/2023.06/compat/linux/x86_64/usr/bin/ld: /cvmfs/software.eessi.io/versions/2023.06/software/linux/x86_64/intel/haswell/software/hwloc/2.9.2-GCCcore-13.2.0/lib/libhwloc.so.15: undefined reference to `pci_get_strings'
collect2: error: ld returned 1 exit status

# can be solved if we add /cvmfs/software.eessi.io/versions/2023.06/software/linux/x86_64/intel/haswell/software/libpciaccess/0.17-GCCcore-13.2.0/lib64 to LIBRARY_PATH
# or load the libpciaccess module
```
Here is `libmpi.so` library tree, showing the dependencies on `libpciaccess` and `hwloc`:
```bash
(base) lercole@cecampc21:/cvmfs/software.eessi.io/versions/2023.06/software/linux/x86_64/intel/haswell/software/OpenMPI/4.1.6-GCC-13.2.0/lib$ libtree libmpi.so
libmpi.so.40
├── libopen-rte.so.40 [rpath]
│   ├── libopen-pal.so.40 [rpath]
│   │   ├── libevent_core-2.1.so.7 [rpath]
│   │   ├── libevent_pthreads-2.1.so.7 [rpath]
│   │   ├── libhwloc.so.15 [rpath]
│   │   │   ├── libpciaccess.so.0 [rpath]
│   │   │   ├── libxml2.so.2 [rpath]
│   │   │   │   ├── libz.so.1 [rpath]
│   │   │   │   └── liblzma.so.5 [rpath]
│   │   │   ├── liblzma.so.5 [rpath]
│   │   │   └── libz.so.1 [rpath]
│   │   ├── libpciaccess.so.0 [rpath]
│   │   ├── libxml2.so.2 [rpath]
│   │   ├── liblzma.so.5 [rpath]
│   │   └── libz.so.1 [rpath]
│   ├── libevent_pthreads-2.1.so.7 [rpath]
│   ├── libevent_core-2.1.so.7 [rpath]
│   ├── libhwloc.so.15 [rpath]
│   ├── libpciaccess.so.0 [rpath]
│   ├── libxml2.so.2 [rpath]
│   ├── liblzma.so.5 [rpath]
│   └── libz.so.1 [rpath]
├── libopen-pal.so.40 [rpath]
├── libevent_pthreads-2.1.so.7 [rpath]
├── libevent_core-2.1.so.7 [rpath]
├── libhwloc.so.15 [rpath]
├── libpciaccess.so.0 [rpath]
├── libxml2.so.2 [rpath]
├── liblzma.so.5 [rpath]
└── libz.so.1 [rpath]
```
whereas the `libmpi.so` of an OpenMPI built with Spack looks slightly different:
```bash
$ libtree libmpi.so
libmpi.so.40
├── libopen-pal.so.80 [rpath]
│   ├── libpmix.so.2 [rpath]
│   │   ├── libz.so.1 [rpath]
│   │   ├── libevent_pthreads-2.1.so.7 [rpath]
│   │   ├── libevent_core-2.1.so.7 [rpath]
│   │   └── libhwloc.so.15 [rpath]
│   │       ├── libxml2.so.2 [rpath]
│   │       │   ├── liblzma.so.5 [rpath]
│   │       │   └── libiconv.so.2 [rpath]
│   │       └── libpciaccess.so.0 [rpath]
│   ├── libevent_core-2.1.so.7 [rpath]
│   ├── libevent_pthreads-2.1.so.7 [rpath]
│   └── libhwloc.so.15 [rpath]
├── libpmix.so.2 [rpath]
├── libevent_pthreads-2.1.so.7 [rpath]
├── libevent_core-2.1.so.7 [rpath]
└── libhwloc.so.15 [rpath]
```

### QuantumESPRESSO build problem
When building QuantumESPRESSO with Spack, we get the following error:
```bash
1 error found in build log:
  31    This warning is for project developers.  Use -Wno-dev to suppress it.
  32
  33    -- Enable sanitizer QE_ENABLE_SANITIZER=none
  34    -- C preprocessor used by qe_preprocess_source in qeHelpers.cmake: /cvmfs/software.eessi.io/versions/2023.06/software/linux/x86_64/intel/haswell/software/GCCcore/13.2.0/bin/cpp
  35    -- Performing Test Fortran_ISYSTEM_SUPPORTED
  36    -- Performing Test Fortran_ISYSTEM_SUPPORTED - Success
>> 37    CMake Error at /cvmfs/software.eessi.io/versions/2023.06/software/linux/x86_64/intel/haswell/software/CMake/3.27.6-GCCcore-13.2.0/share/cmake-3.27/Modules/FindPackageHandleStandardArgs.cmake:230 (message):
 38      Could NOT find OpenMP_Fortran (missing: OpenMP_Fortran_FLAGS
  39      OpenMP_Fortran_LIB_NAMES)
  40    Call Stack (most recent call first):
  41      /cvmfs/software.eessi.io/versions/2023.06/software/linux/x86_64/intel/haswell/software/CMake/3.27.6-GCCcore-13.2.0/share/cmake-3.27/Modules/FindPackageHandleStandardArgs.cmake:600 (_FPHSA_FAILURE_MESSAGE)
  42      /cvmfs/software.eessi.io/versions/2023.06/software/linux/x86_64/intel/haswell/software/CMake/3.27.6-GCCcore-13.2.0/share/cmake-3.27/Modules/FindOpenMP.cmake:577 (find_package_handle_standard_args)
  43      CMakeLists.txt:304 (find_package)
```
This is actually a CMake-related problem. QE calls `cmake` [with these flags](https://github.com/spack/spack-packages/blob/d3a40be2f4c9fffc7a4983db77ec13bbb243bc06/repos/spack_repo/builtin/packages/quantum_espresso/package.py#L476-L479):
```bash
'-DCMAKE_C_COMPILER:STRING=/cvmfs/software.eessi.io/versions/2023.06/software/linux/x86_64/intel/haswell/software/OpenMPI/4.1.6-GCC-13.2.0/bin/mpicc'
'-DCMAKE_Fortran_COMPILER:STRING=/cvmfs/software.eessi.io/versions/2023.06/software/linux/x86_64/intel/haswell/software/OpenMPI/4.1.6-GCC-13.2.0/bin/mpif90'
```

If we try to build a simple CMake project with the same flags, we get the same error:
```bash
cat > CMakeLists.txt << EOF
cmake_minimum_required(VERSION 3.14)
project(TestOpenMP Fortran)
find_package(MPI REQUIRED)
find_package(OpenMP REQUIRED)
message(STATUS "MPI Fortran compiler: ${MPI_Fortran_COMPILER}")
message(STATUS "OpenMP found: ${OpenMP_FOUND}")
message(STATUS "OpenMP Fortran flags: ${OpenMP_Fortran_FLAGS}")
message(STATUS "OpenMP Fortran libraries: ${OpenMP_Fortran_LIBRARIES}")
EOF
$ cmake -S . -B build \
    -DCMAKE_Fortran_COMPILER=/cvmfs/software.eessi.io/versions/2023.06/software/linux/x86_64/intel/haswell/software/OpenMPI/4.1.6-GCC-13.2.0/bin/mpifort
-- The Fortran compiler identification is GNU 13.2.0
-- Detecting Fortran compiler ABI info
-- Detecting Fortran compiler ABI info - failed
-- Check for working Fortran compiler: /cvmfs/software.eessi.io/versions/2023.06/software/linux/x86_64/intel/haswell/software/OpenMPI/4.1.6-GCC-13.2.0/bin/mpifort
-- Check for working Fortran compiler: /cvmfs/software.eessi.io/versions/2023.06/software/linux/x86_64/intel/haswell/software/OpenMPI/4.1.6-GCC-13.2.0/bin/mpifort - works
-- Checking whether /cvmfs/software.eessi.io/versions/2023.06/software/linux/x86_64/intel/haswell/software/OpenMPI/4.1.6-GCC-13.2.0/bin/mpifort supports Fortran 90
-- Checking whether /cvmfs/software.eessi.io/versions/2023.06/software/linux/x86_64/intel/haswell/software/OpenMPI/4.1.6-GCC-13.2.0/bin/mpifort supports Fortran 90 - no
-- Found MPI_Fortran: /cvmfs/software.eessi.io/versions/2023.06/software/linux/x86_64/intel/haswell/software/OpenMPI/4.1.6-GCC-13.2.0/bin/mpifort (found version "3.1") 
-- Found MPI: TRUE (found version "3.1")  
CMake Error at /cvmfs/software.eessi.io/versions/2023.06/software/linux/x86_64/intel/haswell/software/CMake/3.27.6-GCCcore-13.2.0/share/cmake-3.27/Modules/FindPackageHandleStandardArgs.cmake:230 (message):
  Could NOT find OpenMP_Fortran (missing: OpenMP_Fortran_FLAGS
  OpenMP_Fortran_LIB_NAMES)
Call Stack (most recent call first):
  /cvmfs/software.eessi.io/versions/2023.06/software/linux/x86_64/intel/haswell/software/CMake/3.27.6-GCCcore-13.2.0/share/cmake-3.27/Modules/FindPackageHandleStandardArgs.cmake:600 (_FPHSA_FAILURE_MESSAGE)
  /cvmfs/software.eessi.io/versions/2023.06/software/linux/x86_64/intel/haswell/software/CMake/3.27.6-GCCcore-13.2.0/share/cmake-3.27/Modules/FindOpenMP.cmake:577 (find_package_handle_standard_args)
  CMakeLists.txt:4 (find_package)

-- Configuring incomplete, errors occurred!
```
But it works if we explicitly specify the OpenMP flags and libraries:
```bash
$ cmake -S . -B build \
    -DCMAKE_Fortran_COMPILER=/cvmfs/software.eessi.io/versions/2023.06/software/linux/x86_64/intel/haswell/software/OpenMPI/4.1.6-GCC-13.2.0/bin/mpifort \
    -DOpenMP_Fortran_FLAGS="-fopenmp" \
    -DOpenMP_Fortran_LIB_NAMES="gomp" \
    -DOpenMP_gomp_LIBRARY=/cvmfs/software.eessi.io/versions/2023.06/software/linux/x86_64/intel/haswell/software/GCCcore/13.2.0/lib64/libgomp.so
-- The Fortran compiler identification is GNU 13.2.0
-- Detecting Fortran compiler ABI info
-- Detecting Fortran compiler ABI info - failed
-- Check for working Fortran compiler: /cvmfs/software.eessi.io/versions/2023.06/software/linux/x86_64/intel/haswell/software/OpenMPI/4.1.6-GCC-13.2.0/bin/mpifort
-- Check for working Fortran compiler: /cvmfs/software.eessi.io/versions/2023.06/software/linux/x86_64/intel/haswell/software/OpenMPI/4.1.6-GCC-13.2.0/bin/mpifort - works
-- Checking whether /cvmfs/software.eessi.io/versions/2023.06/software/linux/x86_64/intel/haswell/software/OpenMPI/4.1.6-GCC-13.2.0/bin/mpifort supports Fortran 90
-- Checking whether /cvmfs/software.eessi.io/versions/2023.06/software/linux/x86_64/intel/haswell/software/OpenMPI/4.1.6-GCC-13.2.0/bin/mpifort supports Fortran 90 - no
-- Found MPI_Fortran: /cvmfs/software.eessi.io/versions/2023.06/software/linux/x86_64/intel/haswell/software/OpenMPI/4.1.6-GCC-13.2.0/bin/mpifort (found version "3.1") 
-- Found MPI: TRUE (found version "3.1")  
-- Found OpenMP_Fortran: -fopenmp (found version "4.5") 
-- Found OpenMP: TRUE (found version "4.5")  
-- MPI Fortran compiler: /cvmfs/software.eessi.io/versions/2023.06/software/linux/x86_64/intel/haswell/software/OpenMPI/4.1.6-GCC-13.2.0/bin/mpifort
-- OpenMP found: TRUE
-- OpenMP Fortran flags: -fopenmp
-- OpenMP Fortran libraries: /cvmfs/software.eessi.io/versions/2023.06/software/linux/x86_64/intel/haswell/software/GCCcore/13.2.0/lib64/libgomp.so
-- Configuring done (1.0s)
-- Generating done (0.0s)
-- Build files have been written to: /home/lercole/tests/mpifort_cmake/build
```
However, the error can be avoided altogether if we do not specify `CMAKE_Fortran_COMPILER``, and let CMake find the Fortran compiler on its own:
```bash
$ cmake -S . -B build
-- The Fortran compiler identification is GNU 13.2.0
-- Detecting Fortran compiler ABI info
-- Detecting Fortran compiler ABI info - done
-- Check for working Fortran compiler: /home/lercole/eessi/spack/opt/linux-skylake/compiler-wrapper-1.0-i54t7tjn3prjyb363kdjgrkiawikdvyu/libexec/spack/gcc/gfortran - skipped
-- Found MPI_Fortran: /cvmfs/software.eessi.io/versions/2023.06/software/linux/x86_64/intel/haswell/software/OpenMPI/4.1.6-GCC-13.2.0/lib/libmpi_usempif08.so (found version "3.1") 
-- Found MPI: TRUE (found version "3.1")  
-- Found OpenMP_Fortran: -fopenmp (found version "4.5") 
-- Found OpenMP: TRUE (found version "4.5")  
-- MPI Fortran compiler: /cvmfs/software.eessi.io/versions/2023.06/software/linux/x86_64/intel/haswell/software/OpenMPI/4.1.6-GCC-13.2.0/bin/mpif90
-- OpenMP found: TRUE
-- OpenMP Fortran flags: -fopenmp
-- OpenMP Fortran libraries: /cvmfs/software.eessi.io/versions/2023.06/software/linux/x86_64/intel/haswell/software/GCCcore/13.2.0/lib64/libgomp.so;/cvmfs/software.eessi.io/versions/2023.06/compat/linux/x86_64/usr/lib64/libpthread.a
-- Configuring done (0.9s)
-- Generating done (0.0s)
-- Build files have been written to: /home/lercole/tests/mpifort_cmake/build
```
I'm not sure why QE developers added this flag.
I'm opening an issue to fix the Spack recipe: ...

