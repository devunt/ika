import asyncio
import inspect
import re
from collections import defaultdict
from importlib import import_module

from ika.conf import settings
from ika.constants import Versions
from ika.logger import logger
from ika.utils import ircutils, timeutils


RE_SERVER = re.compile(rb'^:(\w{3}) ')
RE_USER = re.compile(rb'^:(\w{9}) ')


class Server:
    def __init__(self):
        self.name = settings.server.name
        self.description = settings.server.description
        self.sid = settings.server.sid
        self.link = settings.link
        self.services = defaultdict(list)

    @asyncio.coroutine
    def connect(self):
        self.reader, self.writer = yield from asyncio.open_connection(self.link.host, self.link.port)
        logger.debug('Connected')
        self.writeline('SERVER {0} {1} 0 {2} :{3}'.format(
            self.name, self.link.password, self.sid, self.description
        ))
        while 1:
            line = yield from self.readline()
            if not line:
                break
            if RE_SERVER.match(line):
                _, command, *params = ircutils.parseline(line)
                if command == b'PING':
                    self.writeserverline('PONG {0} {1}'.format(self.sid, self.link.sid))
            elif RE_USER.match(line):
                continue
            else:
                command, *params = ircutils.parseline(line)
                if command == b'SERVER':
                    try:
                        assert params[0] == self.link.name.encode()
                        assert params[1] == self.link.password.encode()
                    except AssertionError:
                        self.writeline('ERROR :Server information doesn\'t match.')
                        break
                    else:
                        self.link.sid = params[3].decode()
                        self.writeserverline('BURST {0}'.format(timeutils.unixtime()))
                        self.writeserverline('VERSION :{0} {1}'.format(Versions.IKA, self.name))
                        for services in self.services.values():
                            for service in services:
                                self.writeserverline('UID {uid} {timestamp} {nick} {host} {host} {ident} 0 {timestamp} + :{gecos}'.format(
                                    uid=service.uid,
                                    nick=service.name,
                                    ident=service.ident,
                                    host=settings.server.name,
                                    gecos=service.description,
                                    timestamp=timeutils.unixtime(),
                                ))
                                self.writeuserline(service.uid, 'OPERTYPE Services')
                        self.writeserverline('ENDBURST')
            # TODO: Implement each functions
        logger.debug('Disconnected')

    @asyncio.coroutine
    def readline(self):
        line = yield from self.reader.readline()
        line = line.rstrip(b'\r\n')
        logger.debug('>>> {0}'.format(line))
        return line

    def writeline(self, line, *args, **kwargs):
        if isinstance(line, str):
            line = line.format(*args, **kwargs)
            line = line.encode()
        self.writer.write(line + b'\r\n')
        logger.debug('<<< {0}'.format(line))

    def writeserverline(self, line, *args, **kwargs):
        prefix = ':{0} '.format(self.sid)
        self.writeline(prefix + line, *args, **kwargs)

    def writeuserline(self, uid, line, *args, **kwargs):
        prefix = ':{0} '.format(uid)
        self.writeline(prefix + line, *args, **kwargs)

    def register_services(self):
        idx = 621937810 # int('AAAAAA', 36)
        services = import_module('ika.services')
        for modulename in services.modulenames:
            module = import_module('.{0}'.format(modulename), 'ika.services')
            classes = inspect.getmembers(module, lambda member: inspect.isclass(member)
                and member.__module__ == 'ika.services.{0}'.format(modulename))
            for clsname, cls in classes:
                names = list(cls.aliases)
                names.insert(0, cls.name)
                for name in names:
                    instance = cls()
                    instance.id = ircutils.base36encode(idx)
                    instance.name = name
                    self.services[clsname].append(instance)
                    idx += 1
