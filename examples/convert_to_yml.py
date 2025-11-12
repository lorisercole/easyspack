from examples.eessi_example import example_dict
import yaml

d = {'packages': {}}
for spec in example_dict['specs']:                                                                                                                                                                                                                                                                                                                                             
    d['packages'][spec['name']] = {'externals': [{
        'spec': f"{spec['name']}@{spec['version']}{spec['variants']}",
        'prefix': spec['external_path'],
        'dependencies': []
    }]}

for spec in example_dict['specs']:
    for dep in spec['dependencies']:
        d['packages'][spec['name']]['externals'][0]['dependencies'].append(
            {'spec': dep['name'], 'deptypes': dep['depflags'], 'virtuals': dep.get('virtuals', [])})

with open('examples/eessi_example.yml', 'w') as f:
    yaml.dump(d, f)
