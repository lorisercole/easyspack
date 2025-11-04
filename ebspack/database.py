"""
Custom Spack Databse class
"""
from typing import Optional

import spack.database
from spack.database import (
    _TRACKED_DEPENDENCIES,
    _now,
    InstallRecord,
    NonConcreteSpecAddError,
)
import spack.deptypes as dt
from spack.directory_layout import (
    DirectoryLayoutError,
    InconsistentInstallDirectoryError,
)
import spack.llnl.util.tty as tty
import spack.spec


# modify Spack Database class to allow paths to be external for non external specs
# useful to define upstream packages that are not located in the standard Spack install tree
class Database(spack.database.Database):

    def _add(
        self,
        spec: "spack.spec.Spec",
        explicit: bool = False,
        installation_time: Optional[float] = None,
        allow_missing: bool = False,
    ):
        """Add an install record for this spec to the database.

        Also ensures dependencies are present and updated in the DB as either installed or missing.

        Args:
            spec: spec to be added
            explicit:
                Possible values: True, False, any

                A spec that was installed following a specific user request is marked as explicit.
                If instead it was pulled-in as a dependency of a user requested spec it's
                considered implicit.

            installation_time:
                Date and time of installation
            allow_missing: if True, don't warn when installation is not found on on disk
                This is useful when installing specs without build/test deps.
        """
        if not spec.concrete:
            raise NonConcreteSpecAddError("Specs added to DB must be concrete.")

        key = spec.dag_hash()
        spec_pkg_hash = spec._package_hash  # type: ignore[attr-defined]
        upstream, record = self.query_by_spec_hash(key)
        if upstream and record and record.installed:
            return

        installation_time = installation_time or _now()

        for edge in spec.edges_to_dependencies(depflag=_TRACKED_DEPENDENCIES):
            if edge.spec.dag_hash() in self._data:
                continue
            self._add(
                edge.spec,
                explicit=False,
                installation_time=installation_time,
                # allow missing build / test only deps
                allow_missing=allow_missing or edge.depflag & (dt.BUILD | dt.TEST) == edge.depflag,
            )

        # Make sure the directory layout agrees whether the spec is installed
        if not spec.external and self.layout:
            path = self.layout.path_for_spec(spec)
            installed = False
            try:
                self.layout.ensure_installed(spec)
                installed = True
                self._installed_prefixes.add(path)
            except DirectoryLayoutError as e:
                if not (allow_missing and isinstance(e, InconsistentInstallDirectoryError)):
                    action = "updated" if key in self._data else "registered"
                    tty.warn(
                        f"{spec.short_spec} is being {action} in the database with prefix {path}, "
                        "but this directory does not contain an installation of "
                        f"the spec, due to: {e}"
                    )
        elif spec.external_path:
            path = spec.external_path
            installed = True
        # LORIS: allow non-external specs to have external paths (that do not follow Spack layout)
        elif spec._prefix:
            path = str(spec._prefix)
            installed = True
        else:
            path = None
            installed = True

        if key not in self._data:
            # Create a new install record with no deps initially.
            new_spec = spec.copy(deps=False)
            self._data[key] = InstallRecord(
                new_spec,
                path=path,
                installed=installed,
                ref_count=0,
                explicit=explicit,
                installation_time=installation_time,
                origin=None if not hasattr(spec, "origin") else spec.origin,
            )

            # Connect dependencies from the DB to the new copy.
            for dep in spec.edges_to_dependencies(depflag=_TRACKED_DEPENDENCIES):
                dkey = dep.spec.dag_hash()
                upstream, record = self.query_by_spec_hash(dkey)
                assert record, f"Missing dependency {dep.spec.short_spec} in DB"
                new_spec._add_dependency(record.spec, depflag=dep.depflag, virtuals=dep.virtuals)
                if not upstream:
                    record.ref_count += 1

            # Mark concrete once everything is built, and preserve the original hashes of concrete
            # specs.
            new_spec._mark_concrete()
            new_spec._hash = key
            new_spec._package_hash = spec_pkg_hash

        else:
            # It is already in the database
            self._data[key].installed = installed
            self._data[key].installation_time = _now()

        self._data[key].explicit = explicit
