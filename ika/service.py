import asyncio
import glob
import inspect
import re
import sys
from os.path import basename, dirname
from django.db import transaction

from ika.conf import settings
from ika.enums import Permission
from ika.ircobjects import IRCUser
from ika.utils import CaseInsensitiveDict, base36encode, import_class_from_module, unixtime


class CommandError(RuntimeError):
    def __init__(self, user, line):
        self.user = user
        self.line = line


class Service:
    id = ''
    name = ''
    aliases = ()
    description = (
        '설명이 없습니다.',
    )
    internal = False

    def __init__(self, server):
        self.commands = CaseInsensitiveDict()
        self.event_handlers = list()
        self.server = server

    @property
    def uid(self):
        return f'{self.server.sid}{self.id}'

    @property
    def ident(self):
        if 'ident' in self.__class__.__dict__:
            return self.ident
        else:
            return self.__class__.__name__.lower()

    @property
    def gecos(self):
        return f'사용법: /msg {self.name} 도움말'

    def msg(self, user_or_uid, line, *args, **kwargs):
        if isinstance(user_or_uid, IRCUser):
            uid = user_or_uid.uid
        else:
            uid = user_or_uid
        self.writesvsuserline(f'NOTICE {uid} :{line}', *args, **kwargs)

    def writesvsuserline(self, line, *args, **kwargs):
        self.server.writeuserline(self.uid, line, *args, **kwargs)

    def writeserverline(self, line, *args, **kwargs):
        self.server.writeserverline(line, *args, **kwargs)

    def process_command(self, user, line):
        if self.internal:
            return

        split = line.split(maxsplit=1)
        if len(split) == 0:
            self.msg(user, f'명령을 입력해주세요. \x02/msg {self.name} 도움말\x02 을 입력하시면 사용할 수 있는 명령의 목록을 볼 수 있습니다.')
        else:
            if len(split) == 1:
                split.append('')
            command, param = split
            if command in self.commands:
                asyncio.ensure_future(self.commands[command].run(user, param))
            else:
                self.msg(user, f'존재하지 않는 명령어입니다. \x02/msg {self.name} 도움말\x02 을 입력해보세요.')

    def register_irc_bots(self):
        if self.internal:
            return

        _id = self.server.gen_next_service_id()
        self.id = base36encode(_id)
        nicks = list(self.aliases)
        nicks.insert(0, self.name)
        for nick in nicks:
            uid = f'{self.server.sid}{base36encode(_id)}'
            self.server.service_bots[uid] = self
            self.writeserverline('UID', uid, unixtime(), nick, '0.0.0.0', self.server.name, self.ident, '0.0.0.0', unixtime(), '+Iiko', self.gecos)
            self.server.writeuserline(uid, 'OPERTYPE Services')
            irc_channel = self.server.channels.get(settings.logging.irc.channel)
            if irc_channel:
                timestamp = irc_channel.timestamp
                modes = irc_channel.modes
            else:
                timestamp = unixtime()
                modes = '+'
            self.writeserverline('FJOIN', settings.logging.irc.channel, timestamp, modes, f'a,{uid}')
            _id = self.server.gen_next_service_id()

    def register_modules(self, names):
        service_name = self.__module__

        module_names = list()
        if names == '*':
            paths = glob.glob('{}/**/*.py'.format(service_name.replace('.', '/')))
            for path in paths:
                module_names.append('{}.{}'.format(basename(dirname(path)), basename(path)[:-3]))
        else:
            def _make_module_names(prefix, iterable):
                if isinstance(iterable, dict):
                    for k, v in iterable.items():
                        _make_module_names(prefix + k + '.', v)
                elif isinstance(iterable, list):
                    for v in iterable:
                        _make_module_names(prefix, v)
                elif isinstance(iterable, str):
                    module_names.append(prefix + iterable)
            _make_module_names('', names)

        self.register_module('ika.services.help')
        for module_name in module_names:
            self.register_module(f'{service_name}.{module_name}')

    def register_module(self, module_name):
        instance = import_class_from_module(module_name)(self)
        if isinstance(instance, Command):
            for command_name in instance.names:
                self.commands[command_name] = instance
        elif isinstance(instance, Listener):
            methods = inspect.getmembers(instance, inspect.ismethod)
            for method_name, handler in methods:
                if not method_name.startswith('__'):
                    if self.internal:
                        hook = getattr(self.server.core_event_listener, method_name.upper())
                    else:
                        hook = getattr(self.server.event_listener, method_name.upper())
                    hook += handler
                    self.event_handlers.append((hook, handler))


class Legacy:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
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

    @staticmethod
    def err(user, line, *args, **kwargs):
        raise CommandError(user, line.format(args, **kwargs))

    async def execute(self, **kwargs):
        self.msg(kwargs['user'], '아직 구현되지 않은 명령어입니다.')
        raise NotImplementedError('You must override `execute` method of Command class')

    async def run(self, user, param):
        if (self.permission is Permission.LOGIN_REQUIRED) and (user.account is None):
            self.msg(user, f'로그인되어 있지 않습니다. \x02/msg {self.service.name} 로그인\x02 명령을 이용해 로그인해주세요.')
        elif (self.permission is Permission.OPERATOR) and (not user.is_operator):
            self.msg(user, '권한이 없습니다. 오퍼레이터 인증을 해 주세요.')
        else:
            r = re.compile(r'^{}$'.format(self.regex))
            m = r.match(param)
            if m:
                try:
                    with transaction.atomic():
                        await self.execute(user=user, **m.groupdict())
                except CommandError as e:
                    self.msg(e.user, e.line)
                except:
                    ty, exc, tb = sys.exc_info()
                    self.msg(user, f'\x02{self.name}\x02 명령을 처리하는 도중 문제가 발생했습니다. '
                                   f'잠시 후 다시 한번 시도해주세요. 문제가 계속된다면 #ozinger 에 말씀해주세요.')
                    self.writesvsuserline('PRIVMSG {} :ERROR! {} {}', settings.logging.irc.channel, ty, str(exc).splitlines()[0])
                    raise
            else:
                self.msg(user, f'사용법이 올바르지 않습니다. \x02/msg {self.service.name} 도움말 {self.name}\x02 를 입력해보세요.')


class Listener(Module):
    pass

