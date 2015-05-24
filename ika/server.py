import asyncio
import re

from ika.conf import settings
from ika.constants import Versions
from ika.logger import logger


RE_SERVER = re.compile(rb'^:(\w{3}) ')
RE_USER = re.compile(rb'^:(\w{9}) ')

class Server:
    def __init__(self):
        self.name = settings.server.name
        self.description = settings.server.description
        self.uid = settings.server.uid
        self.link_name = settings.link.name
        self.link_host = settings.link.host
        self.link_port = settings.link.port
        self.link_password = settings.link.password

    @asyncio.coroutine
    def connect(self):
        self.reader, self.writer = yield from asyncio.open_connection(self.link_host, self.link_port)
        logger.debug('Connected')
        #self.writeline('CAPAB START {0}'.format(Versions.INSPIRCD_PROTOCOL))
        self.writeline('SERVER {0} {1} 0 {2} :{3}'.format(
            self.name, self.link_password, self.uid, self.description
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
                continue
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
