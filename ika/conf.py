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

PASSWORD_HASHERS = (
    'ika.hashers.PasslibBCryptSHA256PasswordHasher',
    'ika.hashers.PasslibMD5CryptPasswordHasher',
)

INSTALLED_APPS = (
    'channels',
    'ika',
)

SECRET_KEY = 'ika'

DEBUG = settings.debug
ROOT_URLCONF = 'ika.web.routing'
ASGI_APPLICATION = 'ika.web.routing.application'
CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels_redis.core.RedisChannelLayer',
        'CONFIG': {
            "hosts": [settings.redis.url],
        },
    },
}
