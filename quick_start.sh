#!/bin/bash

# EasySpack Quick Start Demo - Approach #1 (Externals + Dependencies)
# Creates a demo Spack installation with EESSI externals

usage() {
    cat << EOF
Usage: $(basename "$0") [OPTIONS] [DEMO_DIR]

EasySpack Quick Start Demo - Creates a demo Spack installation with EESSI externals

Prerequisites:
  - EESSI environment must be initialized (EESSI_EPREFIX defined)
  - Spack must be installed and available in PATH

Arguments:
  DEMO_DIR              Directory for demo installation (default: demo_easyspack)

Options:
  -h, --help            Show this help message and exit

Examples:
  $(basename "$0")
  $(basename "$0") ./demo
  $(basename "$0") --help

EOF
}

set -e

# Parse command line arguments
HELP=false
while [[ $# -gt 0 ]]; do
    case $1 in
        -h|--help)
            usage
            shift
            ;;
        *)
            DEMO_DIR="$1"
            shift
            ;;
    esac
done

# Set default demo directory if not provided
DEMO_DIR=$(realpath "${DEMO_DIR:-demo_easyspack}")

# Create demo directory if it doesn't exist
mkdir -p "$DEMO_DIR"

# Check that EESSI_EPREFIX is defined
if [[ -z "${EESSI_EPREFIX}" ]]; then
    echo "Error: EESSI_EPREFIX environment variable is not set. Have you initialized EESSI?"
    exit 1
fi

# Check that spack is available
if ! command -v spack &> /dev/null; then
    echo "Error: spack command not found. Please ensure Spack is installed and available in your PATH."
    exit 1
elif ! spack --version &> /dev/null; then
    echo "Error: spack command is not functioning properly. Please check your Spack installation."
    # exit 1
fi

EASYSPACK_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SHARE_DIR="${EASYSPACK_ROOT}/share/spack_config"
EXAMPLES_DIR="${EASYSPACK_ROOT}/examples/ext_install"
EESSI_COMPAT_PKGS_PATHS=(
    "${EESSI_EPREFIX}"
    "${EESSI_EPREFIX}/usr"
)

echo -e "\033[1;38m============  EasySpack Demo Setup  ============\033[0m"
echo -e "\033[1;38m • Demo directory:\033[0m"
echo "     $DEMO_DIR"

# Configuring Spack environment variables
echo -e "\033[1;38m • Configuring Spack environment variables...\033[0m"
export SPACK_USER_CONFIG_PATH=$DEMO_DIR
export SPACK_USER_CACHE_PATH=$DEMO_DIR/cache
export EASYSPACK_DEBUG=0
echo "   - SPACK_USER_CONFIG_PATH=$SPACK_USER_CONFIG_PATH"
echo "   - SPACK_USER_CACHE_PATH=$SPACK_USER_CACHE_PATH"

# Create demo directory structure
mkdir -p "$DEMO_DIR"
mkdir -p "$DEMO_DIR/cache"
mkdir -p "$DEMO_DIR/opt"

cd $DEMO_DIR

# Copy/generate configuration files using pre-defined SPACK_USER_CONFIG_PATH
echo -e "\033[1;38m • Copying/generating Spack configuration files...\033[0m"
cp $SHARE_DIR/concretizer.yaml $SPACK_USER_CONFIG_PATH/concretizer.yaml
echo "   - $SHARE_DIR/concretizer.yaml -->  $SPACK_USER_CONFIG_PATH/concretizer.yaml"
export INSTALL_BASE_PATH=$DEMO_DIR
envsubst < $SHARE_DIR/config.yaml.tpl > $SPACK_USER_CONFIG_PATH/config.yaml
echo "   - $SHARE_DIR/config.yaml.tpl  -->  $SPACK_USER_CONFIG_PATH/config.yaml"
envsubst < $SHARE_DIR/modules.yaml.tpl > $SPACK_USER_CONFIG_PATH/modules.yaml
echo "   - $SHARE_DIR/modules.yaml.tpl -->  $SPACK_USER_CONFIG_PATH/modules.yaml"
# envsubst < $SHARE_DIR/upstreams.yaml.tpl > $SPACK_USER_CONFIG_PATH/upstreams.yaml
# echo "   - $SHARE_DIR/upstreams.yaml.tpl  -->  $SPACK_USER_CONFIG_PATH/upstreams.yaml"

# Copy and rename externals to packages.yaml
echo -e "\033[1;38m • Creating packages.yaml from externals_nocompat.yaml...\033[0m"
cp $EXAMPLES_DIR/externals_nocompat.yaml $SPACK_USER_CONFIG_PATH/packages.yaml
echo "   - $EXAMPLES_DIR/externals_nocompat.yaml  -->  $SPACK_USER_CONFIG_PATH/packages.yaml"

# Bootstrap Spack
echo -e "\033[1;38m • Bootstrapping Spack...\033[0m"
spack bootstrap now > /dev/null 2>&1

# Detect EESSI compat layer packages
echo -e "\033[1;38m • Detecting EESSI compat layer packages...\033[0m"
for path in "${EESSI_COMPAT_PKGS_PATHS[@]}"; do
    echo "   $ spack external find --all -p $path --exclude gcc"
    spack external find --all -p "$path" --exclude gcc
done

echo
echo -e "\033[1;38m============  Setup Complete  ============\033[0m"
echo
cat << EOF
  To use this demo Spack installation, run:

    export SPACK_USER_CONFIG_PATH=$DEMO_DIR
    export SPACK_USER_CACHE_PATH=$DEMO_DIR/cache

  Spack config directory:   $DEMO_DIR"
  Spack install directory:  $DEMO_DIR/opt"
  Spack modules directory:  $DEMO_DIR/modules"

EOF
echo -e "\033[1;38m============  Demo Commands  ============\033[0m"

# 1. Show configured externals
echo -e "\033[1;38m 1. List configured external packages:\033[0m"
echo "   $ spack find -p --show-configured-externals"
echo
spack find -p --show-configured-externals

# 2. Show available compilers
echo
echo -e "\033[1;38m 2. Check available compilers:\033[0m"
echo "   $ spack compiler list"
echo
spack compiler list

# 3. Try a sample spec
echo
echo -e "\033[1;38m 3. Concretize a sample spec (reusing externals):\033[0m"
echo "   $ spack spec -Ilt quantum-espresso~mpi"
echo
spack spec -Ilt "quantum-espresso~mpi"

# 4. Install a sample spec
echo
echo -e "\033[1;38m 4. Install a sample spec (if desired):\033[0m"
echo "   $ spack install quantum-espresso~mpi"
echo
spack install "quantum-espresso~mpi"

# 5. Verify the installation
echo
echo -e "\033[1;38m 5. Verify the installation:\033[0m"
echo "   $ ldd $(spack location -i quantum-espresso)/bin/pw.x"
echo
ldd $(spack location -i quantum-espresso)/bin/pw.x
echo
echo -e "\033[1;38m============  End of Demo  ============\033[0m"
