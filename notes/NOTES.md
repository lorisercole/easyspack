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
- all packages should have runtime and link dependencies declared -- automatically injected by easyspack
- compilers (gcc) should not have dependencies, but have `extra_attributes` with compiler paths
- `glibc` is detected and dependencies are automatically added
- `gcc-runtime` is automatically injected by easyspack
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
