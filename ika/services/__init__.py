import fnmatch
import os


modulenames = list()
for basedir, _, filenames in os.walk(os.path.dirname(__file__)):
    for filename in fnmatch.filter(filenames, '*.py'):
        if filename != '__init__.py':
            path = os.path.join(basedir, filename)
            base = path.lstrip(os.path.dirname(__file__))
            name = base[:-3].replace('/', '.')
            modulenames.append(name)
