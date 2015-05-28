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
    description = '설명이 없습니다.'

    def __init__(self, service):
        self.service = service

    @asyncio.coroutine
    def execute(self, uid, *params):
        self.service.msg(uid, '아직 구현되지 않은 명령어입니다.')
        raise RuntimeError('You must override `execute` method of Command class')


class Listener:
    def __init__(self, service):
        self.service = service


class Service:
    aliases = []
    description = '설명이 없습니다.'
    commands = dict()

    def __init__(self, server):
        self.server = server

    @property
    def uid(self):
        return '{}{}'.format(settings.server.sid, self.id)

    @property
    def ident(self):
        if 'ident' in self.__class__.__dict__:
            return self.ident
        else:
            return self.__class__.__name__.lower()

    @property
    def gecos(self):
        return '사용법: /msg {} 도움말'.format(self.name)

    def msg(self, uid, line, *args, **kwargs):
        self.server.writeuserline(self.uid, 'NOTICE {} :{}'.format(uid, line), *args, **kwargs)

    def process_command(self, uid, line):
        command, *params = line.split()
        if command in self.commands:
            asyncio.async(self.commands[command].execute(uid, *params))
        else:
            self.msg(uid, '존재하지 않는 명령어입니다. "/msg {} 도움말"을 입력해보세요.', self.name)

    def register_modules(self):
        from ika.services.help import Help
        help = Help(self)
        names = list(help.aliases)
        names.insert(0, help.name)
        for name in names:
            self.commands[name] = help
        service = self.__module__.lstrip('ika.services')
        for modulename in settings.services[service]:
            try:
                module = import_module('ika.services.{}.{}'.format(service, modulename))
            except ImportError:
                logger.exception('Missing module!')
            else:
                _, cls = inspect.getmembers(module, lambda member: inspect.isclass(member)
                    and member.__module__ == 'ika.services.{}.{}'.format(service, modulename))[0]
                instance = cls(self)
                if isinstance(instance, Command):
                    names = list(instance.aliases)
                    names.insert(0, instance.name)
                    for name in names:
                        self.commands[name] = instance
                elif isinstance(instance, Listener):
                    for event in self.server.ev.events:
                        if hasattr(instance, event):
                            hook = getattr(self.server.ev, event)
                            hook += getattr(instance, event)
