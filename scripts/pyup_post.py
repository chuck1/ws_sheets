import sys
from pprint import pprint
import toml

print('this should only be run right after merging a pull request from pyup')
print('there are not checks to make sure this is the case')
input('press enter to continue')

with open('Pipfile') as f:
    s = f.read()
pipfile = toml.loads(s)
p = pipfile['packages']

pprint(p)


def read_requirements():
    with open('requirements.txt') as f:
        s = f.read()
    for s in s.strip().split('\n'):
        k, v = tuple(s.strip().split('=='))
        yield k, v

r = dict(read_requirements())

pprint(r)
print()

differ=False
for k, v in r.items():
    if k in p:
        pv = p[k]
        if pv.startswith('=='):
            pv = pv[2:]
            if pv != v:
                print('versions differ',k,pv,v)
                p[k] = '=='+v
                differ=True

if not differ:
    sys.exit(0)

print()
pprint(pipfile)

s = toml.dumps(pipfile)

with open('Pipfile', 'w') as f:
    f.write(s)



