import asyncio
import inspect
import re
from importlib import import_module

from ika.classes import Channel
from ika.conf import settings
from ika.constants import Versions
from ika.event import EventHandler
from ika.logger import logger
from ika.utils import ircutils, timeutils


RE_SERVER = re.compile(r'^:(\w{3}) ')
RE_USER = re.compile(r'^:(\w{9}) ')


class Server:
    def __init__(self):
        self.name = settings.server.name
        self.description = settings.server.description
        self.sid = settings.server.sid
        self.link = settings.link
        self.ev = EventHandler()
        self.services = dict()
        self.services_instances = list()
        self.uids = dict()
        self.channels = dict()

    @asyncio.coroutine
    def connect(self):
        self.reader, self.writer = yield from asyncio.open_connection(self.link.host, self.link.port)
        logger.debug('Connected')
        self.writeline('SERVER {0} {1} 0 {2} :{3}',
            self.name, self.link.password, self.sid, self.description
        )
        while 1:
            line = yield from self.readline()
            if not line:
                continue
            if RE_SERVER.match(line):
                server, command, *params = ircutils.parseline(line)
                sender = server
                if command == 'PING':
                    self.writeserverline('PONG {0} {1}', self.sid, self.link.sid)
                elif command == 'ENDBURST':
                    if settings.admin_channel in self.channels:
                        timestamp = self.channels[settings.admin_channel].timestamp
                    else:
                        timestamp = timeutils.unixtime()
                    self.writeserverline('FJOIN {0} {1} + :{2}', settings.admin_channel, timestamp,
                        ' '.join(map(lambda x: 'o,{0}'.format(x), self.services.keys())))
                elif command == 'FJOIN':
                    channel = params[0]
                    if channel in self.channels:
                        self.channels[channel].update(*params)
                    else:
                        self.channels[channel] = Channel(*params)
            elif RE_USER.match(line):
                uid, command, *params = ircutils.parseline(line)
                sender = uid
                if command == 'PRIVMSG':
                    target = params[0]
                    if target.startswith(self.sid):
                        self.services[target].process_command(sender, *params[1:])
            else:
                command, *params = ircutils.parseline(line)
                sender = None
                if command == 'SERVER':
                    try:
                        assert params[0] == self.link.name
                        assert params[1] == self.link.password
                    except AssertionError:
                        self.writeline('ERROR :Server information doesn\'t match.')
                        break
                    else:
                        self.link.sid = params[3]
                        self.writeserverline('BURST {0}', timeutils.unixtime())
                        self.writeserverline('VERSION :{0} {1}', Versions.IKA, self.name)
                        idx = 621937810 # int('AAAAAA', 36)
                        for service in self.services_instances:
                            service.id = ircutils.base36encode(idx)
                            names = list(service.aliases)
                            names.insert(0, service.name)
                            for name in names:
                                uid = '{0}{1}'.format(self.sid, ircutils.base36encode(idx))
                                self.writeserverline('UID {uid} {timestamp} {nick} {host} {host} {ident} 0 {timestamp} + :{gecos}',
                                    uid=uid,
                                    nick=name,
                                    ident=service.ident,
                                    host=self.name,
                                    gecos=service.description,
                                    timestamp=timeutils.unixtime(),
                                )
                                self.writeuserline(uid, 'OPERTYPE Services')
                                self.services[uid] = service
                                idx += 1
                        self.writeserverline('ENDBURST')
            if hasattr(self.ev, command):
                getattr(self.ev, command).fire(*params, sender=sender)
            # TODO: Implement each functions
        logger.debug('Disconnected')

    @asyncio.coroutine
    def readline(self):
        line = yield from self.reader.readline()
        if line == b'':
            raise RuntimeError('Disconnected')
        line = line.decode().rstrip('\r\n')
        logger.debug('>>> {0}'.format(line))
        return line

    def writeline(self, line, *args, **kwargs):
        if isinstance(line, str):
            line = line.format(*args, **kwargs)
        self.writer.write(line.encode() + b'\r\n')
        logger.debug('<<< {0}'.format(line))

    def writeserverline(self, line, *args, **kwargs):
        prefix = ':{0} '.format(self.sid)
        self.writeline(prefix + line, *args, **kwargs)

    def writeuserline(self, uid, line, *args, **kwargs):
        prefix = ':{0} '.format(uid)
        self.writeline(prefix + line, *args, **kwargs)

    def register_services(self):
        for modulename in settings.services:
            try:
                module = import_module('ika.services.{0}'.format(modulename))
            except ImportError:
                logger.exception('Missing module!')
            else:
                _, cls = inspect.getmembers(module, lambda member: inspect.isclass(member)
                    and member.__module__ == 'ika.services.{0}'.format(modulename))[0]
                instance = cls(self)
                instance.register_modules()
                self.services_instances.append(instance)
