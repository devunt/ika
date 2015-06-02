import asyncio
import inspect
import re
from importlib import import_module

from ika.conf import settings
from ika.enums import Permission
from ika.database import Account, Nick, Session
from ika.logger import logger


class Channel:
    def __init__(self, users, *params):
        self.users = dict()
        self.usermodes = dict()
        self.name = params[0]
        self.timestamp = int(params[1])
        self.fjoin(users, *params)

    def fjoin(self, users, *params):
        self.modes = ' '.join(params[2:-1])[1:]
        for usermode in params[-1].split():
            mode, uid = usermode.split(',')
            self.usermodes[uid] = mode
            self.users[uid] = users[uid]
            self.users[uid].channels[self.name] = self

    def remove_user(self, user):
        del self.users[user.uid]
        del self.usermodes[user.uid]
        del user.channels[self.name]


class User:
    def __init__(self, *params):
        self.metadata = dict()
        self.channels = dict()
        self.uid, self.timestamp, self.nick, self.host, self.dhost, \
            self.ident, self.ip, self.signon, self.modes, self.gecos = params
        self.timestamp = int(self.timestamp)
        self.signon = int(self.signon)
        self.opertype = None

    @property
    def account(self):
        name = self.metadata.get('accountname')
        if name is not None:
            return Session().query(Account).filter(Nick.name==name).first()
        return None


class Command:
    aliases = ()
    description = (
        '설명이 없습니다.',
    )
    syntax = ''
    regex = r''
    permission = Permission.EVERYONE

    def __init__(self, service):
        self.service = service

    @asyncio.coroutine
    def execute(self, user, **kwparams):
        self.service.msg(user, '아직 구현되지 않은 명령어입니다.')
        raise RuntimeError('You must override `execute` method of Command class')

    @asyncio.coroutine
    def run(self, user, param):
        if (self.permission is Permission.LOGIN_REQUIRED) and ('accountname' not in user.metadata):
            self.service.msg(user, '로그인되어 있지 않습니다. \x02/msg {} 로그인\x02 명령을 이용해 로그인해주세요.', self.service.name)
        elif (self.permission is Permission.OPERATOR) and (user.opertype != 'NetAdmin'):
            self.service.msg(user, '권한이 없습니다. 오퍼레이터 인증을 해 주세요.')
        else:
            r = re.compile(r'^{}$'.format(self.regex))
            m = r.match(param)
            if m:
                asyncio.async(self.execute(user, **m.groupdict()))
            else:
                self.service.msg(user, '사용법이 올바르지 않습니다. \x02/msg {} 도움말 {}\x02 를 입력해보세요.', self.service.name, self.name)


class Listener:
    def __init__(self, service):
        self.service = service


class Service:
    aliases = ()
    description = (
        '설명이 없습니다.',
    )

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
        if isinstance(user_or_uid, User):
            uid = user_or_uid.uid
        else:
            uid = user_or_uid
        self.server.writeuserline(self.uid, 'NOTICE {} :{}'.format(uid, line), *args, **kwargs)

    def process_command(self, user, line):
        split = line.split(maxsplit=1)
        if len(split) == 1:
            split.append('')
        command, param = split
        if command in self.commands:
            asyncio.async(self.commands[command].run(user, param))
        else:
            self.msg(user, '존재하지 않는 명령어입니다. \x02/msg {} 도움말\x02 을 입력해보세요.', self.name)

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
