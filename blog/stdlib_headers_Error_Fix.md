I figured out what caused the following error when installing gromacs and kokkos:
```bash
[  0%] Building CXX object src/gromacs/selection/CMakeFiles/scanner.dir/parser.cpp.o
cd /tmp/lercole/spack-stage/spack-stage-gromacs-2024.5-re6i4nx2jdh4qbjkcnm6waq5or7z4fh3/spack-build-re6i4nx/src/gromacs/selection && /home/lercole/eessi/spack/opt/linux-skylake/compiler-wrapper-1.0-rtilhiy5qjawa2tohqo6jrptnldwmanq/libexec/spack/gcc/g++ -DGMX_DOUBLE=0 -DHAVE_CONFIG_H -DTMPI_USE_VISIBILITY -I/tmp/lercole/spack-stage/spack-stage-gromacs-2024.5-re6i4nx2jdh4qbjkcnm6waq5or7z4fh3/spack-src/api/legacy/include -I/tmp/lercole/spack-stage/spack-stage-gromacs-2024.5-re6i4nx2jdh4qbjkcnm6waq5or7z4fh3/spack-build-re6i4nx/api/legacy/include -I/tmp/lercole/spack-stage/spack-stage-gromacs-2024.5-re6i4nx2jdh4qbjkcnm6waq5or7z4fh3/spack-src/src -I/tmp/lercole/spack-stage/spack-stage-gromacs-2024.5-re6i4nx2jdh4qbjkcnm6waq5or7z4fh3/spack-src/src/gromacs/utility/include -I/tmp/lercole/spack-stage/spack-stage-gromacs-2024.5-re6i4nx2jdh4qbjkcnm6waq5or7z4fh3/spack-src/src/include -I/tmp/lercole/spack-stage/spack-stage-gromacs-2024.5-re6i4nx2jdh4qbjkcnm6waq5or7z4fh3/spack-build-re6i4nx/src/include -isystem /tmp/lercole/spack-stage/spack-stage-gromacs-2024.5-re6i4nx2jdh4qbjkcnm6waq5or7z4fh3/spack-src/src/external/thread_mpi/include -isystem /cvmfs/software.eessi.io/versions/2023.06/software/linux/x86_64/intel/haswell/software/hwloc/2.9.2-GCCcore-13.2.0/include -isystem /cvmfs/software.eessi.io/versions/2023.06/software/linux/x86_64/intel/haswell/software/FFTW/3.3.10-GCC-13.2.0/include -O3 -DNDEBUG -std=c++17 -fPIC -fexcess-precision=fast -funroll-all-loops -mavx2 -mfma -Wno-missing-field-initializers -Wno-unused -Wno-unused-parameter -Wno-missing-declarations -Wno-null-conversion -MD -MT src/gromacs/selection/CMakeFiles/scanner.dir/parser.cpp.o -MF CMakeFiles/scanner.dir/parser.cpp.o.d -o CMakeFiles/scanner.dir/parser.cpp.o -c /tmp/lercole/spack-stage/spack-stage-gromacs-2024.5-re6i4nx2jdh4qbjkcnm6waq5or7z4fh3/spack-src/src/gromacs/selection/parser.cpp
In file included from /tmp/lercole/spack-stage/spack-stage-gromacs-2024.5-re6i4nx2jdh4qbjkcnm6waq5or7z4fh3/spack-src/api/legacy/include/gromacs/utility/unique_cptr.h:45,
                 from parser.y:57:
/cvmfs/software.eessi.io/versions/2023.06/software/linux/x86_64/intel/haswell/software/GCCcore/13.2.0/include/c++/13.2.0/cstdlib:79:15: fatal error: stdlib.h: No such file or directory
   79 | #include_next <stdlib.h>
      |               ^~~~~~~~~~
compilation terminated. 
make[2]: *** [src/gromacs/selection/CMakeFiles/scanner.dir/build.make:79: src/gromacs/selection/CMakeFiles/scanner.dir/parser.cpp.o] Error 1
```

The problem was introduced by spack compiler wrapper: the compilation was successful if I used the (easybuild-built) g++ compiler directly in the same build environment.
I inspected the wrapper debug logs and found that it adds several `-isystem` header flags to the compilation line. In particular, 
```bash
-isystem /cvmfs/software.eessi.io/versions/2023.06/compat/linux/x86_64/usr/include
```
was causing the problem, because it was changing the order of the header paths searched by the compiler, moving it upper in the list.
(`/cvmfs/software.eessi.io/versions/2023.06/compat/linux/x86_64` is EESSI's sysroot path)
So when the declaration `#include_next <stdlib.h>` of `GCCcore/13.2.0/include/c++/13.2.0/cstdlib` was interpreted, the compiler could not find this header in the remaining paths in the list. The stdlib header path should be way down in the list.

After some digging, I found that the [`spack.build_environment.set_wrapper_variables`](https://github.com/spack/spack/blob/5f6121d8f67f0cebab2e67a5edac79626e27cc90/lib/spack/spack/build_environment.py#L474) function sets the `SPACK_INCLUDE_DIRS` env var that is read by the wrapper to generate the `-isystem` flags. This function [_excludes_ the system paths](https://github.com/spack/spack/blob/5f6121d8f67f0cebab2e67a5edac79626e27cc90/lib/spack/spack/build_environment.py#L509-L514) from the list by checking the hard-coded list of `SYSTEM_PATHS` defined in [`spack/lib/spack/spack/util/environment.py`](https://github.com/spack/spack/blob/5f6121d8f67f0cebab2e67a5edac79626e27cc90/lib/spack/spack/util/environment.py#L40-L43).
To fix our issue, I had to add `/cvmfs/software.eessi.io/versions/2023.06/compat/linux/x86_64` to the `SYSTEM_PATHS` list.

Now, EESSI's GCC compilers are configured with the the `--with-sysroot=/cvmfs/software.eessi.io/versions/2023.06/compat/linux/x86_64` option, so perhaphs Spack should use this information to build the list of system paths that are excluded from the wrappers env variables? I guess this could potentially affect other Spack users, although 