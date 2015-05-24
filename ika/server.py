import asyncio
import re

from ika.conf import settings
from ika.constants import Versions
from ika.logger import logger
from ika.utils import ircutils


RE_SERVER = re.compile(rb'^:(\w{3}) ')
RE_USER = re.compile(rb'^:(\w{9}) ')


class Server:
    def __init__(self):
        self.name = settings.server.name
        self.description = settings.server.description
        self.uid = settings.server.uid
        self.link = settings.link

    @asyncio.coroutine
    def connect(self):
        self.reader, self.writer = yield from asyncio.open_connection(self.link.host, self.link.port)
        logger.debug('Connected')
        self.writeline('SERVER {0} {1} 0 {2} :{3}'.format(
            self.name, self.link.password, self.uid, self.description
        ))
        while 1:
            line = yield from self.readline()
            if not line:
                break
            if RE_SERVER.match(line):
                continue
            elif RE_USER.match(line):
                continue
            else:
                command, *params = ircutils.parseline(line)
                if command == b'SERVER':
                    assert params[0] == self.link.name.encode()
                    assert params[1] == self.link.password.encode()
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
        prefix = ':{0} '.format(self.uid)
        self.writeline(prefix + line, *args, **kwargs)
