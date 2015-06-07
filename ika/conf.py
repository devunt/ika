import json
import os
import sys

from ika.utils import edict


basedir = os.path.dirname(sys.argv[0])
filepath = os.path.join(basedir, 'config.json')


class Settings:
    def __init__(self):
        self.reload()

    def reload(self):
        with open(filepath, 'r') as f:
            d = json.load(f)
        self.settings = edict(d)

    def __getattr__(self, attr):
        return getattr(self.settings, attr)


settings = Settings()
