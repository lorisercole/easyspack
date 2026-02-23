
# zlib
While installing `cmake`, the compat-layer `zlib` seems to have problems:
```
 -   dx2jye5  [    ]  cmake@3.14.7~doc+ncurses+ownlibs~qtgui build_system=generic build_type=Release patches:=1c54004,fdea723 platform=linux os=ubuntu24.04 target=skylake %c,cxx=gcc@13.2.0
[+]  i54t7tj  [b   ]      ^compiler-wrapper@1.0 build_system=generic platform=linux os=ubuntu24.04 target=skylake
[e]  a7ji6tm  [bl  ]      ^curl@8.3.0~gssapi~ldap~libidn2~librtmp~libssh~libssh2+nghttp2 build_system=autotools libs:=shared,static tls:=openssl platform=linux os=ubuntu24.04 target=haswell %c,cxx=gcc@13.2.0
[e]  unuxtwd  [bl  ]          ^openssl@1.1.1w~docs+shared build_system=generic certs=mozilla platform=linux os=ubuntu24.04 target=x86_64
[e]  wgqd7hc  [b   ]      ^gcc@13.2.0+binutils+bootstrap~graphite+libsanitizer~mold~nvptx~piclibs~profiled~strip build_system=autotools build_type=RelWithDebInfo languages:='c,c++,fortran' platform=linux os=ubuntu24.04 target=haswell
[+]  xq2ynci  [ l  ]      ^gcc-runtime@13.2.0 build_system=generic platform=linux os=ubuntu24.04 target=skylake
[e]  hrhksje  [ l  ]      ^glibc@2.37 build_system=autotools platform=linux os=ubuntu24.04 target=x86_64
[e]  nrpaqif  [b r ]      ^gmake@4.4.1~guile build_system=generic platform=linux os=ubuntu24.04 target=haswell %c=gcc@13.2.0
[e]  svkp3h4  [bl  ]      ^ncurses@6.4.20230401+symlinks+termlib abi:=6 build_system=autotools platform=linux os=ubuntu24.04 target=x86_64
[e]  pt7lg52  [bl  ]      ^zlib@1.2.13+optimize+pic+shared build_system=makefile platform=linux os=ubuntu24.04 target=x86_64

(ebspack) lercole@cecampc21:~/eessi/spack$ spack install cmake@3.14
==> Warning: Spack is trying attach a Python dependency to 'meson@=1.1.1 build_system=python_pip platform=linux os=ubuntu24.04 target=x86_64'. This feature is deprecated, and will be removed in v1.2. Please make the dependency explicit in your configuration.
[+] /cvmfs/software.eessi.io/versions/2023.06/compat/linux/x86_64/usr (external zlib-1.2.13-pt7lg52yyiyhphc45qcqh3lmsvdumrej)
[+] /cvmfs/software.eessi.io/versions/2023.06/compat/linux/x86_64/usr (external ncurses-6.4.20230401-svkp3h4f2rhmtkv5g5uzep72waqkqelj)
[+] /cvmfs/software.eessi.io/versions/2023.06/software/linux/x86_64/intel/haswell/software/GCCcore/13.2.0 (external gcc-13.2.0-wgqd7hcs3ocrjdduyjkmmntmw5guajmd)
[+] /cvmfs/software.eessi.io/versions/2023.06/compat/linux/x86_64/usr (external openssl-1.1.1w-unuxtwdan7wpn6sxff6cw3y7zpci25ul)
[+] /cvmfs/software.eessi.io/versions/2023.06/compat/linux/x86_64 (external glibc-2.37-hrhksjeecpgpidarbd6pk3q3pyvbpkch)
[+] /home/lercole/eessi/spack/opt/linux-skylake/compiler-wrapper-1.0-i54t7tjn3prjyb363kdjgrkiawikdvyu
[+] /cvmfs/software.eessi.io/versions/2023.06/software/linux/x86_64/intel/haswell/software/make/4.4.1-GCCcore-13.2.0 (external gmake-4.4.1-nrpaqifyotwyqphn3s6jdtqo6eq3z2vu)
[+] /cvmfs/software.eessi.io/versions/2023.06/software/linux/x86_64/intel/haswell/software/cURL/8.3.0-GCCcore-13.2.0 (external curl-8.3.0-a7ji6tmwf6gnag3ltkpvizpgvh6eygxy)
[+] /home/lercole/eessi/spack/opt/linux-skylake/gcc-runtime-13.2.0-xq2ynciabmcqshyme3kyqgli6iyfwkci
==> No binary for cmake-3.14.7-dx2jye5ouzsa4b3icohkrih2tubon4vb found: installing from source
==> Installing cmake-3.14.7-dx2jye5ouzsa4b3icohkrih2tubon4vb [10/10]
==> Using cached archive: /home/lercole/src/spack/var/spack/cache/_source-cache/archive/92/9221993e0af3e6d10124d840ff24f5b2f3b884416fca04d3312cb0388dec1385.tar.gz
==> Using cached archive: /home/lercole/src/spack/var/spack/cache/_source-cache/archive/fd/fdea723be9713f3ed4624055bf21ef5876647d63c151b91006608ec44a912ae1
==> Applied patch https://github.com/kitware/cmake/commit/1b0c92a3a1b782ff3e1c4499b6ab8db614d45bcd.patch?full_index=1
==> Applied patch /home/lercole/.spack/package_repos/fncqgg4/repos/spack_repo/builtin/packages/cmake/ignore_crayxc_warnings.patch
==> Ran patch() for cmake
==> cmake: Executing phase: 'bootstrap'
==> Error: ProcessError: Command exited with status 11:
    './bootstrap' '--prefix=/home/lercole/eessi/spack/opt/linux-skylake/cmake-3.14.7-dx2jye5ouzsa4b3icohkrih2tubon4vb' '--parallel=16' '--no-system-libs' '--system-curl' '--no-qt-gui' '--' '-DCMAKE_BUILD_TYPE=Release' '-DCMake_TEST_INSTALL=OFF' '-DBUILD_CursesDialog=ON' '-DBUILD_QtDialog=OFF' '-DCMAKE_INSTALL_RPATH_USE_LINK_PATH=ON' '-DCMAKE_INSTALL_RPATH=/home/lercole/eessi/spack/opt/linux-skylake/cmake-3.14.7-dx2jye5ouzsa4b3icohkrih2tubon4vb/lib;/home/lercole/eessi/spack/opt/linux-skylake/cmake-3.14.7-dx2jye5ouzsa4b3icohkrih2tubon4vb/lib64' '-DCMAKE_PREFIX_PATH=/home/lercole/eessi/spack/opt/linux-skylake/compiler-wrapper-1.0-i54t7tjn3prjyb363kdjgrkiawikdvyu;/home/lercole/eessi/spack/opt/linux-skylake/gcc-runtime-13.2.0-xq2ynciabmcqshyme3kyqgli6iyfwkci;/cvmfs/software.eessi.io/versions/2023.06/software/linux/x86_64/intel/haswell/software/cURL/8.3.0-GCCcore-13.2.0;/cvmfs/software.eessi.io/versions/2023.06/software/linux/x86_64/intel/haswell/software/GCCcore/13.2.0;/cvmfs/software.eessi.io/versions/2023.06/software/linux/x86_64/intel/haswell/software/make/4.4.1-GCCcore-13.2.0;/cvmfs/software.eessi.io/versions/2023.06/compat/linux/x86_64'

2 errors found in build log:
     319    -- Checking whether CXX compiler has getloadavg - yes
     320    -- Checking whether <ext/stdio_filebuf.h> is available
     321    -- Checking whether <ext/stdio_filebuf.h> is available - yes
     322    -- Using system-installed CURL
     323    -- Using system-installed ZLIB
     324    -- Could NOT find ZLIB (missing: ZLIB_LIBRARY) (found version "1.2.13")
  >> 325    CMake Error at CMakeLists.txt:396 (message):
     326      CMAKE_USE_SYSTEM_ZLIB is ON but a zlib is not found!
     327    Call Stack (most recent call first):
     328      CMakeLists.txt:682 (CMAKE_BUILD_UTILITIES)
     329
     330
     331    -- Configuring incomplete, errors occurred!
     332    See also "/tmp/lercole/spack-stage/spack-stage-cmake-3.14.7-dx2jye5ouzsa4b3icohkrih2tubon4vb/spack-src/CMakeFiles/CMakeOutput.log".
     333    See also "/tmp/lercole/spack-stage/spack-stage-cmake-3.14.7-dx2jye5ouzsa4b3icohkrih2tubon4vb/spack-src/CMakeFiles/CMakeError.log".
     334    ---------------------------------------------
  >> 335    Error when bootstrapping CMake:
     336    Problem while running initial CMake
     337    ---------------------------------------------

See build log for details:
  /tmp/lercole/spack-stage/spack-stage-cmake-3.14.7-dx2jye5ouzsa4b3icohkrih2tubon4vb/spack-build-out.txt
```
`zlib` is link dep of many external packages. In order to avoid Spack reusing it, I have to remove the `zlib` entry from the `packages.yaml` file. This should not cause big problems I think.
A (newer) `zlib` can be installed by Spack.


# curl
While installing `cmake`, the compat-layer `curl` seems to have problems:
```
 -   w7y5y7g  [    ]  cmake@3.14.7~doc+ncurses+ownlibs~qtgui build_system=generic build_type=Release patches:=1c54004,fdea723 platform=linux os=ubuntu24.04 target=skylake %c,cxx=gcc@13.2.0
[+]  i54t7tj  [b   ]      ^compiler-wrapper@1.0 build_system=generic platform=linux os=ubuntu24.04 target=skylake
[e]  p2vexfg  [bl  ]      ^curl@8.3.0~gssapi~ldap~libidn2~librtmp~libssh~libssh2+nghttp2 build_system=autotools libs:=shared,static tls:=openssl platform=linux os=ubuntu24.04 target=x86_64
[e]  wgqd7hc  [b   ]      ^gcc@13.2.0+binutils+bootstrap~graphite+libsanitizer~mold~nvptx~piclibs~profiled~strip build_system=autotools build_type=RelWithDebInfo languages:='c,c++,fortran' platform=linux os=ubuntu24.04 target=haswell
[+]  xq2ynci  [ l  ]      ^gcc-runtime@13.2.0 build_system=generic platform=linux os=ubuntu24.04 target=skylake
[e]  hrhksje  [ l  ]      ^glibc@2.37 build_system=autotools platform=linux os=ubuntu24.04 target=x86_64
[e]  nrpaqif  [b r ]      ^gmake@4.4.1~guile build_system=generic platform=linux os=ubuntu24.04 target=haswell %c=gcc@13.2.0
[e]  svkp3h4  [bl  ]      ^ncurses@6.4.20230401+symlinks+termlib abi:=6 build_system=autotools platform=linux os=ubuntu24.04 target=x86_64
[+]  m5bexyf  [bl  ]      ^zlib@1.3.1+optimize+pic+shared build_system=makefile platform=linux os=ubuntu24.04 target=skylake %c,cxx=gcc@13.2.0

(ebspack) lercole@cecampc21:~/eessi/spack$ spack install cmake@3.14 ^zlib@1.3.1
==> Warning: Spack is trying attach a Python dependency to 'meson@=1.1.1 build_system=python_pip platform=linux os=ubuntu24.04 target=x86_64'. This feature is deprecated, and will be removed in v1.2. Please make the dependency explicit in your configuration.
[+] /cvmfs/software.eessi.io/versions/2023.06/compat/linux/x86_64 (external glibc-2.37-hrhksjeecpgpidarbd6pk3q3pyvbpkch)
[+] /cvmfs/software.eessi.io/versions/2023.06/compat/linux/x86_64/usr (external ncurses-6.4.20230401-svkp3h4f2rhmtkv5g5uzep72waqkqelj)
[+] /cvmfs/software.eessi.io/versions/2023.06/compat/linux/x86_64/usr (external curl-8.3.0-p2vexfgnzs46gjk6oqhmvs43pcvcxcg4)
[+] /cvmfs/software.eessi.io/versions/2023.06/software/linux/x86_64/intel/haswell/software/make/4.4.1-GCCcore-13.2.0 (external gmake-4.4.1-nrpaqifyotwyqphn3s6jdtqo6eq3z2vu)
[+] /cvmfs/software.eessi.io/versions/2023.06/software/linux/x86_64/intel/haswell/software/GCCcore/13.2.0 (external gcc-13.2.0-wgqd7hcs3ocrjdduyjkmmntmw5guajmd)
[+] /home/lercole/eessi/spack/opt/linux-skylake/compiler-wrapper-1.0-i54t7tjn3prjyb363kdjgrkiawikdvyu
[+] /home/lercole/eessi/spack/opt/linux-skylake/gcc-runtime-13.2.0-xq2ynciabmcqshyme3kyqgli6iyfwkci
[+] /home/lercole/eessi/spack/opt/linux-skylake/zlib-1.3.1-m5bexyff47h7ommtjfoscr7drpsr7l4i
==> No binary for cmake-3.14.7-w7y5y7ge2z2vmlgidp7rjclkaspywu45 found: installing from source
==> Installing cmake-3.14.7-w7y5y7ge2z2vmlgidp7rjclkaspywu45 [9/9]
==> Using cached archive: /home/lercole/src/spack/var/spack/cache/_source-cache/archive/92/9221993e0af3e6d10124d840ff24f5b2f3b884416fca04d3312cb0388dec1385.tar.gz
==> Using cached archive: /home/lercole/src/spack/var/spack/cache/_source-cache/archive/fd/fdea723be9713f3ed4624055bf21ef5876647d63c151b91006608ec44a912ae1
==> Applied patch https://github.com/kitware/cmake/commit/1b0c92a3a1b782ff3e1c4499b6ab8db614d45bcd.patch?full_index=1
==> Applied patch /home/lercole/.spack/package_repos/fncqgg4/repos/spack_repo/builtin/packages/cmake/ignore_crayxc_warnings.patch
==> Ran patch() for cmake
==> cmake: Executing phase: 'bootstrap'
==> Error: ProcessError: Command exited with status 11:
    './bootstrap' '--prefix=/home/lercole/eessi/spack/opt/linux-skylake/cmake-3.14.7-w7y5y7ge2z2vmlgidp7rjclkaspywu45' '--parallel=16' '--no-system-libs' '--system-curl' '--no-qt-gui' '--' '-DCMAKE_BUILD_TYPE=Release' '-DCMake_TEST_INSTALL=OFF' '-DBUILD_CursesDialog=ON' '-DBUILD_QtDialog=OFF' '-DCMAKE_INSTALL_RPATH_USE_LINK_PATH=ON' '-DCMAKE_INSTALL_RPATH=/home/lercole/eessi/spack/opt/linux-skylake/cmake-3.14.7-w7y5y7ge2z2vmlgidp7rjclkaspywu45/lib;/home/lercole/eessi/spack/opt/linux-skylake/cmake-3.14.7-w7y5y7ge2z2vmlgidp7rjclkaspywu45/lib64' '-DCMAKE_PREFIX_PATH=/home/lercole/eessi/spack/opt/linux-skylake/compiler-wrapper-1.0-i54t7tjn3prjyb363kdjgrkiawikdvyu;/home/lercole/eessi/spack/opt/linux-skylake/zlib-1.3.1-m5bexyff47h7ommtjfoscr7drpsr7l4i;/home/lercole/eessi/spack/opt/linux-skylake/gcc-runtime-13.2.0-xq2ynciabmcqshyme3kyqgli6iyfwkci;/cvmfs/software.eessi.io/versions/2023.06/software/linux/x86_64/intel/haswell/software/GCCcore/13.2.0;/cvmfs/software.eessi.io/versions/2023.06/software/linux/x86_64/intel/haswell/software/make/4.4.1-GCCcore-13.2.0;/cvmfs/software.eessi.io/versions/2023.06/compat/linux/x86_64'

2 errors found in build log:
     320    -- Checking whether <ext/stdio_filebuf.h> is available
     321    -- Checking whether <ext/stdio_filebuf.h> is available - yes
     322    -- Using system-installed CURL
     323    -- Using system-installed ZLIB
     324    -- Found ZLIB: /home/lercole/eessi/spack/opt/linux-skylake/zlib-1.3.1-m5bexyff47h7ommtjfoscr7drpsr7l4i/lib/libz.so (found version "1.3.1")
     325    -- Could NOT find CURL (missing: CURL_LIBRARY CURL_INCLUDE_DIR) (found version "8.3.0")
  >> 326    CMake Error at CMakeLists.txt:413 (message):
     327      CMAKE_USE_SYSTEM_CURL is ON but a curl is not found!
     328    Call Stack (most recent call first):
     329      CMakeLists.txt:682 (CMAKE_BUILD_UTILITIES)
     330
     331
     332    -- Configuring incomplete, errors occurred!
     333    See also "/tmp/lercole/spack-stage/spack-stage-cmake-3.14.7-w7y5y7ge2z2vmlgidp7rjclkaspywu45/spack-src/CMakeFiles/CMakeOutput.log".
     334    See also "/tmp/lercole/spack-stage/spack-stage-cmake-3.14.7-w7y5y7ge2z2vmlgidp7rjclkaspywu45/spack-src/CMakeFiles/CMakeError.log".
     335    ---------------------------------------------
  >> 336    Error when bootstrapping CMake:
     337    Problem while running initial CMake
     338    ---------------------------------------------

See build log for details:
  /tmp/lercole/spack-stage/spack-stage-cmake-3.14.7-w7y5y7ge2z2vmlgidp7rjclkaspywu45/spack-build-out.txt
```
I removed the compat-layer `curl` entry from the `packages.yaml` file. This should not cause big problems I think.
We can use the software-layer `curl` instead.