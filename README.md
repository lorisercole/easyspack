# EasySpack: bridge EESSI/EasyBuild into Spack

EasySpack is a set of utilities that exposes packages built with [EasyBuild](https://easybuild.io) and distributed by [EESSI](https://www.eessi.io) to [Spack](https://spack.io). 
This makes Spack aware of the available EasyBuild/EESSI installation, thus letting it reuse the available packages when building new ones.

Most of the examples consider an existing EESSI installation, but similar logic can be applied to any EasyBuild installation that uses rpaths.

<!--
It can:

- Parse EESSI metadata and emit Spack externals, including compiler/runtime glue such as `gcc-runtime` and `glibc`.
- Detect additional system packages (e.g. from the EESSI compatibility layer) and add them automatically.
- Write the externals into a Spack upstream database and optionally update `packages.yaml` so Spack can reuse them.
-->

## Approaches at a glance (see blog/NOTES.md)
### 1. (New) Externals + dependencies (preferred)
This is the official Spack-onic way of exposing an EESSI installation to a Spack installation.
It consists of these steps:
  - Declare EESSI software-layer builds as external packages in a `packages.yaml` Spack configuration file (with [external dependencies](https://spack.readthedocs.io/en/latest/packages_yaml.html#specifying-dependencies-among-external-packages)).
    Example: [`examples/ext_install/externals_nocompat.yaml`](examples/ext_install/externals_nocompat.yaml).
  - (optionally) detect OS packages available under the EESSI compat-layer, and configure Spack to use them as externals. In EESSI, these packages are often dependencies of software-layer packages, so it is suggested to include them.
  - Externals are then visible via `spack find --show-configured-externals` and get reused during Spack solves by default.

> ***Example script***\
> TO BE ADDED

#### 1.a (optional) Convert externals into an upstream database
The above will suffice to have Spack reuse an available software stack. The only packages that Spack will have to "build" are:
  - `gcc-runtime` : Spack will simply copy the GCC runtime libraries into the local installation folder. This is a small 
  - `compiler-wrapper` : Spack's own compiler wrapper
  - anything that is not available as external package, of course

Externals defined in a YAML file such as [`examples/ext_install/packages.yaml`](examples/ext_install/packages.yaml) can be converted into a Spack database that can be used as upstream. Runtime deps (`glibc`, `gcc-runtime`) can be automatically injected. 
This is not the officially-supported method, but it works, and it should avoid the need to have a separate `gcc-runtime` copy. Packages can b

> ***Example script***\
> [`external_pkgs_install.py`](external_pkgs_install.py): reads an externals YAML file, injects runtime deps, detects OS packages, installs them into a Spack upstream DB, and updates `packages.yaml`.

What happens:
  - `UpstreamInstaller` parses the YAML, completes architectures/variants, and injects `glibc`/`gcc-runtime` runtime dependencies when relevant.
  - Additional detectable packages under `EESSI_EPREFIX` and `EESSI_EPREFIX/usr` are discovered and added as externals.
  - All externals are registered into the upstream DB at `/home/lercole/eessi/spack/upstreams/eessi`. Compilers are added to a `packages.yaml`.


## Legacy workflow: JSON spec loader (obsolete)


Minimal JSON structure:
```json
{
	"software_target": "skylake",
	"specs": [
		{
			"name": "fftw",
			"version": "3.3.10",
			"external_path": "/cvmfs/.../FFTW/3.3.10-GCC-13.2.0",
			"variants": "+openmp",
			"dependencies": [
				{"name": "gcc@13.2.0", "depflags": ["BUILD"], "virtuals": ["c", "cxx", "fortran"]}
			]
		}
	]
}
```
Run with:
```bash
spack-python upstreamdb_quick_start.py
```

### 2. (Legacy) Custom upstream DB via JSON
This older approach uses `SpecLoader` in [ebspack/loader.py](ebspack/loader.py) to read a dictionary provided by the user (following [ebspack/schema.py](ebspack/schema.py)), generate concrete specs, inject runtime libs, and writes a full upstream DB. This flow is kept for reference but it is superseded by the external packages approach.

> ***Example script***\
> [`upstreamdb_quick_start.py`](upstreamdb_quick_start.py) : example script for this approach, that uses the [`examples/upstream_db/eesi_example.py`](examples/upstream_db/eessi_example.py) example data.


## Requirements
- Python 3.7+
- Spack 1.1+ (ideally Spack 1.2, will include several bug fixes and improvements)
  > [!IMPORTANT]
  > At the moment, to work with EESSI, you must use a patched version of Spack: https://github.com/lorisercole/spack/tree/eessi
- EESSI environment if you want to mirror the published stacks.

## Installation & use
Development installation:
```bash
pip install -e .
```
Before running examples, make sure that the EESSI is activated, e.g.
```bash
export EESSI_VERSION=2023.06
module unuse ${MODULEPATH} && module use /cvmfs/software.eessi.io/init/modules && module load EESSI/${EESSI_VERSION}
```

### Use
  - Most of the scripts in this package should be run using the `spack-python` wrapper. This ensures the Spack is correctly imported and initialized.
  - Set the env variable `EBSPACK_DEBUG=1` for verbose logging.

### Spack configuration
If you want to define a custom Spack user-scope configuration directory, you can set these env vars as reported in the [documentation](https://spack.readthedocs.io/en/latest/configuration.html#overriding-local-configuration):
```bash
export SPACK_USER_CONFIG_PATH=/home/lercole/eessi/spack
export SPACK_USER_CACHE_PATH=/home/lercole/eessi/spack/cache
```
Example of configuration files can be found in the [`share/spack_config`](share/spack_config/) directory. In particular the following can be useful:
  - [`config.yaml`](share/spack_config/config.yaml) : to set the location of Spack-installed packages.
  - [`modules.yaml`](share/spack_config/modules.yaml) : to set the location of modules generated by Spack (if needed).
  - [`upstreams.yaml`](share/spack_config/upstreams.yaml) : to use an upstream database that was generated by easyspack.

The available configuration files exemplify a typical custom Spack user-scope configuration that would work with a system/site installation of Spack. The user should have write access to the paths defined in `config.yaml` and `modules.yaml`.


## Repository layout
- [ebspack/ext_install.py](ebspack/ext_install.py): core logic for externals parsing, runtime dep injection, and database writes via Spack's `UpstreamInstaller` modded class.
- [ebspack/loader.py](ebspack/loader.py): legacy loader for JSON-driven upstream DB population (`SpecLoader`).
- [ebspack/database.py](ebspack/database.py): Spack `Database` subclass that accepts non-standard prefixes for upstream entries.
- [examples/](examples): sample externals YAMLs and JSON configs used by the scripts.




## Practical notes and gotchas
- Only link/runtime deps need to be declared for externals that might be reused; pure build deps rarely matter for reuse and can be omitted.
- Build deps still influence the DAG hash; keep them consistent if you care about reproducibility.
- `glibc` is injected automatically when compilers are present; `gcc-runtime` is added when a GCC external is defined. Other compiler runtimes are not yet implemented.
- The EESSI compatibility layer filters some packages (e.g., `glibc`, `binutils`, `ncurses`, `xz`); be cautious when mirroring or detecting from it.
- The externals flow can detect additional packages under `EESSI_EPREFIX`/`usr`; disable detection if you need a minimal set.

## Logging and debugging
- Set `EBSPACK_DEBUG=1` to switch ebspack logging to debug level.
- The custom formatter in [ebspack/__init__.py](ebspack/__init__.py) prefixes debug logs with the emitting logger name.

## Notes and caveats
- Only link/runtime deps need to be declared for externals that may be reused by Spack; pure build deps can often be omitted.
- `glibc` is injected automatically when compilers are present; `gcc-runtime` is added when a GCC external is defined.
- The JSON flow expects `external_path` to exist on disk; paths are treated as prefixes when writing to the upstream DB.


## Contributing
You can join the discussion on the `#spack` channel of [EESSI Slack](https://join.slack.com/t/eessi-hpc/shared_invite/zt-2wg10p26d-m_CnRB89xQq3zk9qxf1k3g).

Notes of previous meetings can be found [here](https://hackmd.io/@EESSI/H1hd6Ng3xg).