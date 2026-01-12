
import logging
logger = logging.getLogger(__name__)
from typing import Any, Callable, Dict, List, Optional, Tuple

import spack.config
import spack.platforms
import spack.spec
import spack.util.spack_yaml as syaml
from spack.compilers.config import _EXTRA_ATTRIBUTES_KEY, CompilerFactory, supported_compilers
from spack.externals import (
    ExternalDict,
    ExternalSpecError,
    ExternalSpecsParser,
    complete_architecture,
    complete_variants_and_architecture,
    extract_dicts_from_configuration,
)
from spack.llnl.util import tty
from spack.solver.core import using_libc_compatibility
from spack.solver.reuse import SpecFilter
from spack.solver.runtimes import external_config_with_implicit_externals, _normalize_packages_yaml

from .database import Database
from .exceptions import ValidationError, DatabaseError

COMPILER_PACKAGE_NAMES = supported_compilers()
NOT_IMPLEMENTED_COMPILERS = ("acfl", "aocc", "apple-clang", "cce", "fj", "intel-oneapi-compilers",
                             "intel-oneapi-compilers-classic", "llvm", "msvc", "nvhpc", "xl")
DEFAULT_EXTERNAL_PACKAGES = ("gcc", "glibc")

HOST_PLATFORM = spack.platforms.host()
HOST_OS = HOST_PLATFORM.default_operating_system()
HOST_TARGET = HOST_PLATFORM.default_target()
HOST_TARGET_FAMILY = HOST_TARGET.family

def internal_node_from_dict(external_dict: ExternalDict) -> spack.spec.Spec:
    """
    Returns an non-external (upstream) spec node from a dictionary representation.
    Cannot have neither `modules` nor `extra_attributes`.
    The `external_path` is used as prefix.

    If the spec is one of the DEFAULT_EXTERNAL_PACKAGES, it is treated as external.
    """    
    result = spack.spec.Spec(
        # Allow `@x.y.z` instead of `@=x.y.z`
        str(spack.spec.parse_with_version_concrete(external_dict["spec"])),
    )
    if not result.versions.concrete:
        raise ExternalSpecError(
            f"The external spec '{external_dict['spec']}' doesn't have a concrete version"
        )

    if result.name in DEFAULT_EXTERNAL_PACKAGES:
        result = spack.externals.node_from_dict(external_dict)
        logger.debug(f"External node from dict: {result.to_node_dict()}")
        return result
    elif "modules" in external_dict or "extra_attributes" in external_dict:
        raise ExternalSpecError(
            f"The internal spec '{external_dict['spec']}' cannot have neither 'modules' nor 'extra_attributes'."
        )
    result.set_prefix(external_dict.get("prefix"))

    if "required_target" in external_dict:
        result.constrain(f"target={external_dict['required_target']}")
    logger.debug(f"Created internal node from dict: {result.to_node_dict()}")
    return result


# new spack.compilers.config.CompilerFactory staticmethod
@staticmethod
def from_packages_dict(packages_dict: Dict[str, Any]) -> List[spack.spec.Spec]:
    """Returns the compiler specs defined in the "packages" dictionary"""
    externals_dicts = []
    compiler_package_names = supported_compilers()
    for name, entry in packages_dict.items():
        if name not in compiler_package_names:
            continue

        externals_config = entry.get("externals", None)
        if not externals_config:
            continue

        for current in externals_config:
            # If extra_attributes is not there don't use this entry as a compiler.
            if _EXTRA_ATTRIBUTES_KEY not in current:
                header = f"The external spec '{current['spec']}' cannot be used as a compiler"
                tty.debug(f"[{__file__}] {header}: missing the '{_EXTRA_ATTRIBUTES_KEY}' key")
                continue

            externals_dicts.append(current)

    external_parser = ExternalSpecsParser(externals_dicts)
    return external_parser.all_specs()

CompilerFactory.from_packages_dict = from_packages_dict

def is_compiler(external_dict: ExternalDict) -> bool:
    """Returns True if the external dict corresponds to a compiler spec."""
    spec = spack.spec.Spec(external_dict["spec"])
    return spec.name in COMPILER_PACKAGE_NAMES #and _EXTRA_ATTRIBUTES_KEY in external_dict

# in spack.compilers.config
def all_compilers_from_dict(
    packages_dict: Dict[str, Any]
) -> List[spack.spec.Spec]:
    """Returns all the compilers from a packages dictionary.

    Args:
        packages_dict: dictionary corresponding to a "packages" section of a Spack configuration
    """
    compilers = CompilerFactory.from_packages_dict(packages_dict)
    return compilers

spack.compilers.config.all_compilers_from_dict = all_compilers_from_dict

# spack.solver.runtimes.external_config_with_implicit_externals
def external_config_with_implicit_externals(
    configuration: spack.config.Configuration,
    *,
    external_yaml: Optional[str] = None,
    inject_runtime_deps: bool = False,
) -> Dict[str, Any]:
    # Read packages.yaml and normalize it so that it will not contain entries referring to
    # virtual packages.
    if external_yaml:
        with open(external_yaml, "r") as f:
            packages_yaml = syaml.load_config(f)["packages"]
    else:
        packages_yaml = configuration.deepcopy_as_builtin("packages", line_info=True)
    _normalize_packages_yaml(packages_yaml)

    # Add externals for libc from compilers on Linux
    if not using_libc_compatibility():
        return packages_yaml

    seen = set()
    if external_yaml:
        all_compilers = spack.compilers.config.all_compilers_from_dict(packages_yaml)
    else:
        all_compilers = spack.compilers.config.all_compilers_from(configuration)
    for compiler in all_compilers:
        # add libc to list of external packages
        libc = spack.compilers.libraries.CompilerPropertyDetector(compiler).default_libc()
        if libc and libc not in seen:
            seen.add(libc)
            entry = {"spec": f"{libc}", "prefix": libc.external_path}
            packages_yaml.setdefault(libc.name, {}).setdefault("externals", []).append(entry)
    return packages_yaml

def inject_runtime_libs(external_dicts: List[ExternalDict]) -> None:
    """
    Inject runtime libraries into external specs based on their compiler's libc.

    Args:
        external_dicts: List of external spec dictionaries to modify
    """
    logger.debug("Injecting runtime libraries into external specs...")

    # add gcc-runtime to config if gcc is defined. It has the compiler and glibc as dependencies
    # it uses the architecture of the host
    for ext_dict in external_dicts:
        node = spack.spec.Spec(str(spack.spec.parse_with_version_concrete(ext_dict["spec"])))
        if node.name == "gcc":
            external_dicts.append({
                "spec": f"gcc-runtime@{node.version} target={HOST_TARGET}",
                "prefix": ext_dict["prefix"],
                "dependencies": [
                    {"spec": ext_dict["spec"], "deptypes": ["build"]},  # compiler
                    {"spec": "glibc", "deptypes": ["link"], "virtuals": "libc"},
                ],
            })
            logger.debug(f"Added gcc-runtime for compiler spec: {ext_dict['spec']}")
        elif node.name in NOT_IMPLEMENTED_COMPILERS:
            raise NotImplementedError(f"{node.name} runtime injection not implemented.")

    for ext_dict in external_dicts:
        logger.debug(f"  Processing external spec: {ext_dict['spec']}")
        for dep in ext_dict.get("dependencies", []).copy():
            if is_compiler(dep):  # we assume it is a build dependency
                # add libc to nodes compiled
                ## CANNOT DETECT LIBC, AS THE SPEC IS NOT CONCRETE YET. WE ASSUME GLIBC
                # # Determine the default libc for this compiler and add it as link dependency
                # libc = spack.compilers.libraries.CompilerPropertyDetector(dep).default_libc()
                # if not libc:
                #     raise ValidationError(f"Could not determine libc for compiler spec '{dep['spec']}'")

                ext_dict["dependencies"].append({
                    "spec": "glibc",
                    "deptypes": ["link"],
                    "virtuals": "libc",
                })
                logger.debug(f"    Injected glibc dependency into {ext_dict['spec']}")

                # add gcc-runtime to all nodes compiled with gcc, not to gcc-runtime itself
                if "gcc-runtime" in ext_dict["spec"]:
                    break
                dep_node = spack.spec.Spec(str(spack.spec.parse_with_version_concrete(dep["spec"])))
                if dep_node.name == "gcc":
                    # gcc runtime libraries
                    ext_dict["dependencies"].append({
                        "spec": f"gcc-runtime@{dep_node.version}",
                        "deptypes": ["link"],
                    })
                    logger.debug(f"    Injected gcc-runtime dependency into {ext_dict['spec']}")
                else:
                    raise NotImplementedError(f"Compiler of spec: {ext_dict['spec']} is not gcc.")
                break
        

# replaces spack.solver.reuse._create_external_parser
def _create_external_parser(
    configuration: spack.config.Configuration,
    *,
    external_yaml: Optional[str] = None,
    node_factory: Optional[Callable[[ExternalDict], spack.spec.Spec]] = None,
    inject_runtime_deps: bool = False,
) -> Tuple[ExternalSpecsParser, Any]:
    packages_yaml = external_config_with_implicit_externals(configuration, external_yaml=external_yaml)
    external_dicts = extract_dicts_from_configuration(packages_yaml)
    if inject_runtime_deps:
        inject_runtime_libs(external_dicts)
    result = configuration.get("concretizer:externals:completion")
    if result == "default_variants":
        complete_fn = complete_variants_and_architecture
    elif result == "architecture_only":
        complete_fn = complete_architecture
    else:
        raise ValueError(f"Unknown value for concretizer:externals:completion: {result!r}")
    return ExternalSpecsParser(external_dicts, complete_node=complete_fn, node_factory=node_factory), packages_yaml

# new spack.solver.reuse.SpecFilter static method
@staticmethod
def from_external_yaml(configuration, external_yaml, *, include, exclude, node_factory=None) -> SpecFilter:
    parser, packages_yaml = _create_external_parser(
        configuration, external_yaml=external_yaml, node_factory=node_factory, inject_runtime_deps=True)
    is_reusable = lambda spec: True  # assume all externals are reusable
    return SpecFilter(parser.all_specs, is_usable=is_reusable, include=include, exclude=exclude), parser

SpecFilter.from_external_yaml = from_external_yaml


class UpstreamInstaller:
    """
    Installs the external specs in a YAML file as a Spack upstream.
    """
    # Hard-coded default database path
    DEFAULT_DATABASE_PATH = "/home/lercole/eessi/spack/upstreams/test"

    def __init__(self, database_path: Optional[str] = None):
        """
        Args:
            database_path: Path to the Spack database. If None, uses DEFAULT_DATABASE_PATH
        """
        self._database_path = database_path or self.DEFAULT_DATABASE_PATH

        # Initialize database with the configured path
        self._database = Database(self._database_path)
        self.nodes: List[spack.spec.Spec] = []
    
    def parse_externals_yaml(self, external_yaml: str) -> List[spack.spec.Spec]:
        """
        Parses the external specs in the `self.external_yaml` file and returns a list of Spack specs.
        """
        # self.nodes = spack.solver.reuse.SpecFilter.from_external_yaml(
        #     spack.config.CONFIG, external_yaml, include=[], exclude=[], node_factory=internal_node_from_dict
        # ).selected_specs()
        self.filter, self.parser = spack.solver.reuse.SpecFilter.from_external_yaml(
            spack.config.CONFIG, external_yaml, include=[], exclude=[], node_factory=internal_node_from_dict
        )
        self.nodes = self.filter.selected_specs()

    def install(self, dry_run: bool = False) -> None:
        """
        Add specs to the Spack database.

        Args:
            dry_run: If True, build specs but don't add to database

        Raises:
            DatabaseError: If database operations fail
            ValidationError: If specs are not built yet
        """
        if not self.nodes:
            raise ValidationError("No specs parsed. Call 'parse_externals_yaml' first.")

        if self._database is None:
            raise DatabaseError("Database not initialized")

        # # Add all specs from the configuration
        # # TODO: only add root specs - dependencies will be added automatically
        # specs_to_add_explicit = [(spec_config.spec_map_key, spec_config.explicit) for spec_config in self.config.specs]

        if dry_run:
            logger.info(f"Dry run: Would add {len(self.nodes)} spec(s) to database:")
            for node in self.nodes:
                status = "[E]" if node.external else "[^]"
                logger.info(f"  {status} {node} [{node.architecture}] at {node.prefix}")
            return

        # Add specs to database
        try:
            with self._database.write_transaction():
                for node in self.nodes:
                    self._database.add(node, explicit=False)
                    status = "[E]" if node.external else "[^]"
                    logger.info(f"Added spec: {status} {node} [{node.architecture}] at {node.prefix}")
                    logger.debug(f" {node.to_node_dict()} -- path: {node.prefix}")
        except Exception as e:
            raise DatabaseError(f"Failed to add node to database: {e}")

    def add_externals_to_config(self, *, filter_names: Optional[List[str]] = DEFAULT_EXTERNAL_PACKAGES, scope=None) -> None:
        """
        Add the external specs to the Spack packages.yaml configuration file.

        Args:
            filter_names: List of package names to filter and add as external.
                If None, all specs are added.
            scope: The configuration scope where the packages should be added.
                If not provided, the default scope is used.
        """
        add_packages_to_config(self.nodes, filter_names=filter_names, scope=scope)


def add_packages_to_config(specs: List[spack.spec.Spec], *,
                           filter_names: Optional[List[str]] = DEFAULT_EXTERNAL_PACKAGES, scope=None) -> None:
    """
    Add a list of packages to the packages.yaml configuration file, at the required scope.
    This ensures that Spack treats these packages as external.

    Args:
        specs (List[Spec]): A list of `Spec` objects to be added to the configuration.
        filter_names (Optional[List[str]]): List of package names to filter and add as external.
            If None, all specs are added.
        scope (Optional[str]): The configuration scope where the packages should be added.
            If not provided, the default scope is used.
    """
    ext_pkg_names = filter_names or []
    logger.debug(f"Adding packages to config. Filter names: {ext_pkg_names}")
    
    # Group specs by name in dictionary
    by_name: Dict[str, List[Spec]] = {}
    for spec in specs:
        if spec.name in ext_pkg_names:
            by_name.setdefault(spec.name, []).append(spec)

    logger.info(f"Adding specs to packages.yaml configuration:")
    for sps in by_name.values():
        logger.info(f"   - {sps}")
    spack.detection.update_configuration(by_name, buildable=True, scope=scope)

