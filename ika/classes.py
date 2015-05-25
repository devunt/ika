import asyncio
import inspect
from importlib import import_module

from ika.conf import settings
from ika.logger import logger


class Channel:
    users = dict()

    def __init__(self, *params):
        self.name = params[0]
        self.timestamp = int(params[1])
        self.modes = params[2]
        for user in params[3].split():
            mode, uid = user.split(',')
            self.users[uid] = mode

    def update(self, *params):
        pass


class Command:
    aliases = []

    @asyncio.coroutine
    def execute(self, future, *params):
        future.set_result('아직 구현되지 않은 명령어입니다.')
        raise RuntimeError('You must override `execute` method of Command class')


class Service:
    aliases = []
    commands = dict()

    @property
    def uid(self):
        return '{0}{1}'.format(settings.server.sid, self.id)

    @property
    def ident(self):
        if 'ident' in self.__class__.__dict__:
            return self.ident
        else:
            return self.__class__.__name__.lower()

    @property
    def description(self):
        if 'description' in self.__class__.__dict__:
            return self.description
        else:
            return '사용법: /msg {0} 도움말'.format(self.name)

    @asyncio.coroutine
    def process(self, future, line):
        command, *params = line.split()
        if command in self.commands:
            asyncio.async(self.commands[command].execute(future, *params))
        else:
            future.set_result('존재하지 않는 명령어입니다. {0}'.format(self.description))

    def register_commands(self):
        service = self.__module__.lstrip('ika.services')
        for modulename in settings.services[service]:
            try:
                module = import_module('ika.services.{0}.{1}'.format(service, modulename))
            except ImportError:
                logger.exception('Missing module!')
            else:
                _, cls = inspect.getmembers(module, lambda member: inspect.isclass(member)
                    and member.__module__ == 'ika.services.{0}.{1}'.format(service, modulename))[0]
                instance = cls()
                names = list(instance.aliases)
                names.insert(0, instance.name)
                for name in names:
                    self.commands[name] = instance
