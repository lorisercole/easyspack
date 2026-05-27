import json
import pprint as pp
import re
import sys
import yaml

try:
    data = json.load(sys.stdin)
except json.JSONDecodeError:
    print("Error: Invalid JSON passed.", file=sys.stderr)
    sys.exit(1)

# TODO: should be a parameter?
eessi_base = "EESSI/2025.06"
#eessi_base = "EESSI/2023.06"

software_dict = data.get("software", {})

database = []

for key, value in software_dict.items():
    for v in value.get("versions", []):
        version = v.get("version", "N/A")
        full_module_name = v.get("module", {}).get("full_module_name", "N/A")
        with_cuda = "CUDA" in full_module_name

        req_modules = [
            req.get("full_module_name", "N/A")
            for req in v.get("required_modules", [])
        ]

        if not eessi_base in req_modules:
            continue
        req_modules.remove(eessi_base)

        req_modules.remove(full_module_name)
        req_str = "\n\t".join(req_modules) if req_modules else "None"

        with_openmpi = any(["OpenMPI" in whatever for whatever in req_modules])

        extensions = [
                {"type": ext.get("type"), "name": ext.get("name"), "version": ext.get("version")} for ext in v.get("extensions")
        ]

        res = {
            "full_module_name": full_module_name,
            "with_cuda": with_cuda,
            "with_openmpi": with_openmpi,
            "extensions": extensions,
            "req_modules": req_modules
        }
        database.append(res)

# "type": "component",
# "type": "octave",
# "type": "perl",
# "type": "python",
# "type": "r",
# "type": "ruby",

def heuristic_translate(full_module_name):
    spack_package_name = full_module_name.replace("-CUDA/", "/").replace(".MPI/", "/").split("/")[0].lower()
    version = full_module_name.replace(".MPI/", "/").split("/")[1].lower()
    spack_package_version = version.split("-")[0]

    if spack_package_name == "gcccore":
        spack_package_name = "gcc"

    return spack_package_name, spack_package_version


spack_database = []

for entry in database:
    spack_package_name, spack_package_version = heuristic_translate(entry["full_module_name"])
    version = entry["full_module_name"].replace(".MPI/", "/").split("/")[1].lower()

    dependencies = list()
    pattern = r"-(?P<cuda_name>cuda)-(?P<cuda_version>[\d\.]+)"
    match = re.search(pattern, version)
    if match:
        dependencies.append(f"{match.group(1)}@{match.group(2)}")

    for dep in entry["req_modules"]:
        n, v = heuristic_translate(dep)
        if n == "gcc":
            #compiler = f" %{n}@{v}"
            continue
        dependencies.append(f"{n}@{v}")

    for ext in entry["extensions"]:
        n, v = heuristic_translate(f"{ext['name']}/{ext['version']}")
        if ext["type"] == "python":
            n = "py-" + n
        elif ext["type"] == "perl":
            n = "perl-" + n
        elif ext["type"] == "r":
            n = "r-" + n
        ret = {
            "name": n,
            "version": v,
        }
        spack_database.append(ret)

    compiler = ""
    pattern = r"-(?P<gcc_name>gcccore)-(?P<gcc_version>[\d\.]+)"
    match = re.search(pattern, version)
    if match:
        compiler = f"gcc@{match.group(2)}"

    variant = ""
    variant += "+cuda" if entry["with_cuda"] else ""
    variant += "+mpi" if entry["with_openmpi"] else ""

    ret = {
        "name": spack_package_name,
        "version": spack_package_version,
    }
    if variant:
        ret["variant"] = variant
    if dependencies:
        ret["dependencies"] = dependencies
    if compiler:
        ret["compiler"] = compiler
    spack_database.append(ret)

packages_yaml = {}

# FIXME: translation of package names for dependencies missing
# FIXME: what about different (micro)architectures?

for entry in spack_database:
    compiler = f"{(' %' + entry['compiler']) if 'compiler' in entry else ''}"
    if not entry["name"] in packages_yaml:
        packages_yaml[entry["name"]] = {}
    if "externals" not in packages_yaml[entry["name"]]:
        packages_yaml[entry["name"]]["externals"] = []
    packages_yaml[entry["name"]]["externals"].append({
        "spec": f"{entry['name']}@{entry['version']}{entry.get('variant', '')}{(' %' + ' %'.join(entry['dependencies'])) if 'dependencies' in entry else ''}{compiler}",
        "prefix": "todo"
     })

#pp.pprint({"packages": packages_yaml})
print(yaml.dump({"packages": packages_yaml}))
