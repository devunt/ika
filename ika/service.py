import asyncio
import glob
import inspect
import re
import sys
from django.db import transaction
from pydoc import locate as import_class

from ika.conf import settings
from ika.enums import Permission
from ika.format import Color, colorize
from ika.ircobjects import IRCUser
from ika.utils import CaseInsensitiveDict, base36encode, import_class_from_module, unixtime


class CommandError(RuntimeError):
    def __init__(self, user_or_uid, line):
        self.user_or_uid = user_or_uid
        self.line = colorize(line, Color.RED)


class Service:
    id = ''
    name = ''
    aliases = ()
    description = (
        '설명이 없습니다.',
    )
    internal = False

    def __init__(self, server):
        self.listeners = list()
        self.commands = CaseInsensitiveDict()
        self.event_handlers = list()
        self.uids = list()
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
        return f'사용법: {self.refer_command("ika.services.help.Help")}'

    def refer_command(self, cls_or_instance, *params):
        if isinstance(cls_or_instance, str):
            cls_or_instance = import_class(cls_or_instance)
        reference = f'\x02/msg {self.name} {cls_or_instance.name}'
        if len(params) > 0:
            reference += ' '
            reference += ' '.join(params)
        reference += '\x02'
        return reference

    def msg(self, user_or_uid, line, *args, **kwargs):
        if isinstance(user_or_uid, IRCUser):
            uid = user_or_uid.uid
        else:
            uid = user_or_uid
        self.writesvsuserline(f'NOTICE {uid} : {line}', *args, **kwargs)

    @staticmethod
    def err(user_or_uid, line, *args, **kwargs):
        raise CommandError(user_or_uid, line.format(*args, **kwargs))

    def writesvsuserline(self, line, *args, **kwargs):
        self.server.writeuserline(self.uid, line, *args, **kwargs)

    def writeserverline(self, line, *args, **kwargs):
        self.server.writeserverline(line, *args, **kwargs)

    def notify_admins(self, line, *args, **kwargs):
        self.writesvsuserline(f'PRIVMSG {settings.logging.irc.channel} : \x02[ika]\x02 {line}', *args, **kwargs)

    def process_command(self, user, line):
        if self.internal:
            return

        try:
            split = line.split(maxsplit=1)
            if len(split) == 0:
                self.err(user, f'명령을 입력해주세요. {self.refer_command("ika.services.help.Help")} 을 입력하시면 사용할 수 있는 명령의 목록을 볼 수 있습니다.')
            else:
                if len(split) == 1:
                    split.append('')
                command, param = split
                if param == '?':
                    param = command
                    command = '?'
                if command in self.commands:
                    asyncio.ensure_future(self.commands[command].run(user, param))
                else:
                    self.err(user, f'존재하지 않는 명령어입니다. {self.refer_command("ika.services.help.Help")} 을 입력해보세요.')
        except CommandError as ex:
            self.msg(ex.user_or_uid, ex.line)

    def register_irc_bots(self):
        if self.internal:
            return

        nicks = list(self.aliases)
        nicks.append(self.name)
        for nick in nicks:
            self.id = base36encode(self.server.gen_next_service_id())
            self.uids.append(self.uid)
            self.server.service_bots[self.uid] = self
            self.writeserverline('UID', self.uid, unixtime(), nick, '0.0.0.0', self.server.name, self.ident, '0.0.0.0', unixtime(), '+Iiko', self.gecos)
            self.server.writeuserline(self.uid, 'OPERTYPE Services')
            irc_channel = self.server.channels.get(settings.logging.irc.channel)
            timestamp, modes = (irc_channel.timestamp, irc_channel.modestring) if irc_channel else (unixtime(), '+')
            self.writeserverline('FJOIN', settings.logging.irc.channel, timestamp, modes, f'a,{self.uid}')

    def register_modules(self, module_names):
        service_name = self.__module__
        service_module_names = set()

        def _make_module_names(prefix, value):
            if isinstance(value, dict):
                for k, v in value.items():
                    _make_module_names(prefix + '.' + k, v)
            elif isinstance(value, list):
                for v in value:
                    _make_module_names(prefix, v)
            elif isinstance(value, str):
                if value == '*':
                    paths = glob.glob('{}/**/*.py'.format(prefix.replace('.', '/')), recursive=True)
                    for path in paths:
                        name = path[len(prefix) + 1:].replace('/', '.').replace('\\', '.')[:-3]
                        if not name.startswith('__'):
                            _make_module_names(prefix, name)
                else:
                    service_module_names.add(prefix + '.' + value)
        _make_module_names(service_name, module_names)

        self.register_module('ika.services.help')
        for service_module_name in service_module_names:
            self.register_module(service_module_name)

    def register_module(self, module_name):
        instance = import_class_from_module(module_name)(self)
        if isinstance(instance, Command):
            for command_name in instance.names:
                self.commands[command_name] = instance
        elif isinstance(instance, Listener):
            self.listeners.append(instance)
            methods = inspect.getmembers(instance, inspect.ismethod)
            for method_name, handler in methods:
                if not method_name.startswith('__'):
                    if self.internal:
                        hook = getattr(self.server.core_event_listener, method_name.upper())
                    else:
                        hook = getattr(self.server.event_listener, method_name.upper())
                    hook += handler
                    self.event_handlers.append((hook, handler))

    def unload_modules(self):
        for hook, handler in self.event_handlers:
            hook -= handler
        for listener in self.listeners:
            listener.__uninit__()
        self.commands = CaseInsensitiveDict()
        self.listeners = list()
        self.event_handlers = list()

    def unload_irc_bots(self, reason=''):
        for uid in self.uids:
            self.server.writeuserline(uid, 'QUIT', reason)
            del self.server.service_bots[uid]
        self.uids = list()


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

    def refer_command(self, cls, *params):
        return self.service.refer_command(cls, *params)

    def msg(self, user_or_uid, line, *args, **kwargs):
        self.service.msg(user_or_uid, line, *args, **kwargs)

    def err(self, user_or_uid, line, *args, **kwargs):
        self.service.err(user_or_uid, line, *args, **kwargs)

    def writesvsuserline(self, line, *args, **kwargs):
        self.service.writesvsuserline(line, *args, **kwargs)

    def writeserverline(self, line, *args, **kwargs):
        self.service.writeserverline(line, *args, **kwargs)

    def notify_admins(self, line, *args, **kwargs):
        self.service.notify_admins(line, *args, **kwargs)


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

    async def execute(self, **kwargs):
        self.msg(kwargs['user'], '아직 구현되지 않은 명령어입니다.')
        raise NotImplementedError('You must override `execute` method of Command class')

    async def run(self, user, param):
        try:
            if (self.permission is Permission.LOGIN_REQUIRED) and (user.account is None):
                self.err(user, f'로그인되어 있지 않습니다. {self.refer_command("ika.services.ozinger.commands.login.Login")} 명령을 이용해 로그인해주세요.')
            elif (self.permission is Permission.OPERATOR) and (not user.is_operator):
                self.err(user, '권한이 없습니다. 오퍼레이터 인증을 해 주세요.')
            else:
                r = re.compile(r'^{}$'.format(self.regex))
                m = r.match(param)
                if m:
                    try:
                        with transaction.atomic():
                            await self.execute(user=user, **m.groupdict())
                    except CommandError:
                        raise
                    except:
                        ty, exc, tb = sys.exc_info()
                        self.msg(user, f'\x02{self.name}\x02 명령을 처리하는 도중 문제가 발생했습니다. '
                                       f'잠시 후 다시 한번 시도해주세요. 문제가 계속된다면 #ozinger 에 말씀해주세요.')
                        self.writesvsuserline('PRIVMSG {} :ERROR! {} {}', settings.logging.irc.channel, ty, str(exc).splitlines()[0])
                        raise
                else:
                    self.err(user, f'사용법이 올바르지 않습니다. {self.refer_command(self, "?")} 를 입력해보세요.')
        except CommandError as ex:
            self.msg(ex.user_or_uid, ex.line)


class Listener(Module):
    def __uninit__(self):
        pass
