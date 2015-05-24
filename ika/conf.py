import sys, os
import json

from ika.utils import edict

basedir = os.path.dirname(sys.argv[0])
filepath = os.path.join(basedir, 'config.json')

with open(filepath, 'r') as f:
    d = json.load(f)

settings = edict(d)
