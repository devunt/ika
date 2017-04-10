import os
import yaml

from ika.utils import Map


########## ika settings ##########

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


########## Django settings ##########

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.' + settings.database.engine,
        'NAME': settings.database.name,
        'USER': settings.database.user,
        'PASSWORD': settings.database.password,
        'HOST': settings.database.host,
        'PORT': settings.database.port,
    }
}

INSTALLED_APPS = (
    'ika',
)

SECRET_KEY = 'ika'
