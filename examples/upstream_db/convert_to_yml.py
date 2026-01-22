"""
This script converts the example_dict from eessi_example_full_backup.py into a package.yaml file
"""

import yaml
# from eessi_example_full_backup import example_dict
from eessi_example import example_dict


d = {'packages': {}}
for spec in example_dict['specs']:                                                                                                                                                                                                                                                                                                                                             
    d['packages'][spec['name']] = {
        'externals': [
            {
                'spec': f"{spec['name']}@{spec['version']}{spec['variants']}",
                'prefix': spec['external_path'],
                'dependencies': [],
            },
        ]
    }
    if 'extra_attributes' in spec:
        d['packages'][spec['name']]['externals'][0]['extra_attributes'] = spec['extra_attributes']

for spec in example_dict['specs']:
    for dep in spec['dependencies']:
        # if dep['name'].startswith('gcc@'): # skip gcc BUILD deps: multiple virtuals not accepted
            # continue
        # if dep['name'].startswith('gcc-runtime@'):
            # continue
        if dep['name'].startswith('glibc@'):  # glibc is added automatically by the concretizer, it would collide with it if specified
            continue
        d['packages'][spec['name']]['externals'][0]['dependencies'].append(
            {
                'spec': dep['name'].split("%")[0], # remove compiler from spec if present
                # deptypes and virtuals are inferred by Spack from the package recipe
                # but it does not work if dep is not known to Spack
                'deptypes': list(map(str.lower, dep['depflags'])),
            },
        )
        if dep.get('virtuals', None) and not dep['name'].startswith('gcc@'):
            d['packages'][spec['name']]['externals'][0]['dependencies'][-1]['virtuals'] = dep['virtuals']

with open('examples/eessi_example.yaml', 'w') as f:
    yaml.safe_dump(d, f, sort_keys=False, default_flow_style=False)
