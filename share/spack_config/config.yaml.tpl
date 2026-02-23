config:
  install_tree:
    root: ${INSTALL_BASE_PATH}/opt  # a directory where you have write permissions
  shared_linking:
    missing_library_policy: warn  # warn if installed binaries reference dynamic libraries that are not found in their specified rpaths