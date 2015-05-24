import asyncio
import re

import config
import constants
from logger import logger


RE_SERVER = re.compile(r'^:(\w{3}) ')
RE_USER = re.compile(r'^:(\w{9}) ')

class Server:
    def __init__(self):
        self.name = config.SERVER['NAME']
        self.description = config.SERVER['DESCRIPTION']
        self.uid = config.SERVER['UID']
        self.link_name = config.LINK['NAME']
        self.link_host = config.LINK['HOST']
        self.link_port = config.LINK['PORT']
        self.link_password = config.LINK['PASSWORD']

    @asyncio.coroutine
    def connect(self):
        self.reader, self.writer = yield from asyncio.open_connection(self.link_host, self.link_port)
        logger.debug('Connected')
        self.writeline('CAPAB START {0}'.format(constants.PROTOCOL_VERSION))
        while 1:
            line = yield from self.readline()
            line_str = line.decode('utf-8', 'ignore')
            if not line:
                pass
            if line == b'CAPAB END':
                # TODO: Implement CAPAB
                pass
                #self.writeline('CAPAB END')
                #self.writeline('SERVER {0} {1} 0 {2} :{3}'.format(
                #    self.name, self.link_password, self.uid, self.description
                #))

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
        prefix = ':{0} '.format(config.SERVER_ID)
        self.writeline(prefix + line, *args, **kwargs)
