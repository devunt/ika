import asyncio
import inspect
from importlib import import_module

from ika.conf import settings
from ika.enums import Message
from ika.event import EventListener
from ika.logger import logger
from ika.utils import CaseInsensitiveDict, parseline


class Server:
    def __init__(self):
        self.name = settings.server.name
        self.description = settings.server.description
        self.sid = settings.server.sid
        self.link = settings.link

        self.ev = EventListener()

        self.services = dict()
        self.service_instances = dict()

        self.users = dict()
        self.channels = CaseInsensitiveDict()

        self.linked_once = False
        self.reader = None
        self.writer = None

    async def connect(self):
        self.reader, self.writer = await asyncio.open_connection(self.link.host, self.link.port)
        logger.debug('Connected')

        self.writeline('SERVER', self.name, self.link.password, 0, self.sid, self.description)

        while True:
            line = await self.readline()
            if not line:
                continue

            message_type, prefix, command, params = parseline(line)

            if message_type is Message.USER:
                getattr(self.ev, command)(prefix, *params)
            else:
                getattr(self.ev, command)(*params)

    async def readline(self):
        line = await self.reader.readline()
        if line == b'':
            raise RuntimeError('Disconnected')
        line = line.decode(errors='ignore').rstrip('\r\n')
        logger.debug('>>> {}'.format(line))
        return line

    def writeline(self, line, *args, **kwargs):
        if isinstance(line, str):
            if '{}' in line:
                line = line.format(*args, **kwargs)
            else:
                params = list()
                trailing = False
                for param in args:
                    if trailing:
                        raise ValueError(
                            'writeline: Parameter with space character should be used once and at the last position')
                    param = str(param)
                    if (param == '') or (' ' in param):
                        params.append(':' + param)
                        trailing = True
                    else:
                        params.append(param)
                if len(params) > 0:
                    line = '{} {}'.format(line, ' '.join(params))
        if '\n' in line:
            raise ValueError('writeline: Message should not be multi-lined')
        self.writer.write(line.encode() + b'\r\n')
        logger.debug('<<< {}'.format(line))
        message_type, prefix, command, params = parseline(line)
        if message_type is Message.USER:
            getattr(self.ev, command)(prefix, *params)
        elif message_type is Message.SERVER:
            getattr(self.ev, command)(*params)

    def writeprefixline(self, prefix, line, *args, **kwargs):
        self.writeline(':' + prefix + ' ' + line, *args, **kwargs)

    def writeserverline(self, line, *args, **kwargs):
        self.writeprefixline(self.sid,  line, *args, **kwargs)

    def writeuserline(self, uid, line, *args, **kwargs):
        self.writeprefixline(uid, line, *args, **kwargs)

    def register_services(self):
        self.register_service('core')
        for name in settings.services:
            self.register_service(name, settings.services[name])

    def register_service(self, service_name, module_names='*'):
        try:
            _module = import_module('ika.services.{}'.format(service_name))
        except ImportError:
            logger.exception('Missing module!')
        else:
            _, cls = inspect.getmembers(_module, lambda member: inspect.isclass(member)
                and member.__module__ == 'ika.services.{}'.format(service_name))[0]
            instance = cls(self)
            instance.register_modules(module_names)
            self.service_instances[cls.__name__] = instance

    def reload_services(self):
        settings.reload()
        self.ev = EventListener()
        for instance in self.service_instances.values():
            instance.reload_modules()

    def disconnect(self, reason=''):
        for uid in self.services.keys():
            self.writeuserline(uid, 'QUIT', reason)
        self.writeserverline('SQUIT', self.link.name, reason)
        self.writeserverline('ERROR :Service disconnected ({})', reason)
