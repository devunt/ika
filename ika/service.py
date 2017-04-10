import asyncio
import glob
import inspect
import re
import sys
from importlib import import_module, reload
from os.path import basename, dirname
from django.db import transaction

from ika.conf import settings
from ika.enums import Permission
from ika.ircobjects import IRCUser
from ika.logger import logger


class Service:
    id = 0
    name = ''
    aliases = ()
    description = (
        '설명이 없습니다.',
    )
    internal = False

    def __init__(self, server):
        self.commands = dict()
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

    def msg(self, user_or_uid, line, *args, **kwargs):
        if isinstance(user_or_uid, IRCUser):
            uid = user_or_uid.uid
        else:
            uid = user_or_uid
        self.writesvsuserline('NOTICE {} :{}'.format(uid, line), *args, **kwargs)

    def writesvsuserline(self, line, *args, **kwargs):
        self.server.writeuserline(self.uid, line, *args, **kwargs)

    def writeserverline(self, line, *args, **kwargs):
        self.server.writeserverline(line, *args, **kwargs)

    def process_command(self, user, line):
        if self.internal:
            return

        split = line.split(maxsplit=1)
        if len(split) == 0:
            self.msg(user, '명령을 입력해주세요. \x02/msg {} 도움말\x02 을 입력하시면 사용할 수 있는 명령의 목록을 볼 수 있습니다.', self.name)
        else:
            if len(split) == 1:
                split.append('')
            command, param = split
            command = command.upper()
            if command in self.commands:
                asyncio.async(self.commands[command].run(user, param))
            else:
                self.msg(user, '존재하지 않는 명령어입니다. \x02/msg {} 도움말\x02 을 입력해보세요.', self.name)

    def register_modules(self, names):
        if not self.internal:
            help_module = import_module('ika.services.help')
            help_command = help_module.Help(self)
            for command_name in help_command.names:
                self.commands[command_name] = help_command

        service_module_name = self.__module__

        if names == '*':
            names = list()
            paths = glob.glob('{}/**/*.py'.format(service_module_name.replace('.', '/')))
            for path in paths:
                names.append('{}.{}'.format(basename(dirname(path)), basename(path)[:-3]))

        for module_name in names:
            try:
                _module = reload(import_module('{}.{}'.format(service_module_name, module_name)))
            except ImportError:
                logger.exception('Missing module!')
            else:
                _, cls = inspect.getmembers(_module, lambda member: inspect.isclass(member)
                    and member.__module__ == '{}.{}'.format(service_module_name, module_name))[0]
                instance = cls(self)
                if isinstance(instance, Command):
                    for command_name in instance.names:
                        self.commands[command_name.upper()] = instance
                elif isinstance(instance, Listener):
                    methods = inspect.getmembers(instance, inspect.ismethod)
                    for name, method in methods:
                        if not name.startswith('__'):
                            hook = getattr(self.server.ev, name.upper())
                            hook += method

    def reload_modules(self):
        self.commands = dict()
        self.register_modules()


class Legacy:
    def __init__(self, *args, **kwargs):
        self.description = self.description + (
            ' ',
            '\x02이 기능은 하위호환용 기능입니다.\x02',
        )


class Module:
    def __init__(self, service: Service):
        self.service = service

    @property
    def server(self):
        return self.service.server

    def msg(self, user_or_uid, line, *args, **kwargs):
        self.service.msg(user_or_uid, line, *args, **kwargs)

    def writesvsuserline(self, line, *args, **kwargs):
        self.service.writesvsuserline(line, *args, **kwargs)

    def writeserverline(self, line, *args, **kwargs):
        self.service.writeserverline(line, *args, **kwargs)


class Command(Module):
    name = ''
    aliases = ()
    description = (
        '설명이 없습니다.',
    )
    syntax = ''
    regex = r''
    permission = Permission.EVERYONE

    @property
    def names(self):
        names = list(self.aliases)
        names.insert(0, self.name)
        return names

    async def execute(self, user, **kwargs):
        self.service.msg(user, '아직 구현되지 않은 명령어입니다.')
        raise RuntimeError('You must override `execute` method of Command class')

    async def run(self, user, param):
        if (self.permission is Permission.LOGIN_REQUIRED) and (user.account is None):
            self.service.msg(user, '로그인되어 있지 않습니다. \x02/msg {} 로그인\x02 명령을 이용해 로그인해주세요.', self.service.name)
        elif (self.permission is Permission.OPERATOR) and (not user.is_operator):
            self.service.msg(user, '권한이 없습니다. 오퍼레이터 인증을 해 주세요.')
        else:
            r = re.compile(r'^{}$'.format(self.regex))
            m = r.match(param)
            if m:
                try:
                    with transaction.atomic():
                        await self.execute(user, **m.groupdict())
                except:
                    ty, exc, tb = sys.exc_info()
                    self.service.msg(user, '\x02{}\x02 명령을 처리하는 도중 문제가 발생했습니다. '
                                           '잠시 후 다시 한번 시도해주세요. 문제가 계속된다면 #ozinger 에 말씀해주세요.', self.name)
                    self.service.writesvsuserline('PRIVMSG {} :ERROR! {} {}', settings.admin_channel, ty, str(exc).splitlines()[0])
                    raise
            else:
                self.service.msg(user, '사용법이 올바르지 않습니다. \x02/msg {} 도움말 {}\x02 를 입력해보세요.', self.service.name, self.name)


class Listener(Module):
    pass

