# only if you want Spack to generate module files
modules:
  default:
    roots:
      lmod: ${INSTALL_BASE_PATH}/modules  # a directory where you have write permissions
      # tcl: ${INSTALL_BASE_PATH}/modules  # uncomment if you want Tcl modules
    lmod:
      core_compilers:
        - 'gcc'
