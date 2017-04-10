import os
import yaml

from ika.utils import Map


class Settings:
    def __init__(self):
        self.settings = Map()
        self.reload()

    def reload(self):
        with open(os.path.join('config.yml'), 'r') as f:
            d = yaml.load(f)
        self.settings = Map(d)

    def __getattr__(self, attr):
        return getattr(self.settings, attr)


settings = Settings()
