import asyncio

from ika.conf import settings
from ika.enums import Message
from ika.event import EventListener
from ika.logger import logger
from ika.utils import CaseInsensitiveDict, import_class_from_module, parseline


class Server:
    def __init__(self):
        self.name = settings.server.name
        self.description = settings.server.description
        self.sid = settings.server.sid
        self.link = settings.link

        self.core_event_listener = EventListener()
        self.event_listener = EventListener()

        self.services = dict()
        self.service_bots = dict()

        self._next_service_id = int('AAAAAA', 36)

        self.users = dict()
        self.nicks = CaseInsensitiveDict()
        self.channels = CaseInsensitiveDict()

        self.reader = None
        self.writer = None

        self.bursting = False

    async def connect(self):
        self.reader, self.writer = await asyncio.open_connection(self.link.host, self.link.port)
        logger.debug('Connected')

        self.writeline('SERVER', self.name, self.link.password, 0, self.sid, self.description, exempt_event=True)

        while True:
            line = await self.readline()
            if not line:
                continue

            self.fire_events(line)

    async def readline(self):
        line = await self.reader.readline()
        if line == b'':
            raise RuntimeError('Disconnected')
        line = line.decode(self.link.encoding, errors='surrogateescape').rstrip('\r\n')
        logger.debug(f'>>> {line}')
        return line

    def writeline(self, line, *args, **kwargs):
        exempt_event = kwargs.pop('exempt_event', False)
        if isinstance(line, str):
            if '{}' in line:
                line = line.format(*args, **kwargs)
            else:
                params = list()
                trailing = False
                semi_trailing = False
                for param in args:
                    if trailing:
                        raise ValueError(
                            'writeline: Parameter with space character should be used once and at the last position')
                    param = str(param)
                    if param.startswith('+') or param.startswith('-'):
                        if semi_trailing:
                            raise ValueError(
                                'writeline: Parameter starts with + or - character should be used once')
                        semi_trailing = True
                        params.append(param)
                    elif (param == '') or (' ' in param):
                        params.append(':' + param)
                        trailing = True
                    else:
                        params.append(param)
                if len(params) > 0:
                    line = '{} {}'.format(line, ' '.join(params))
        if '\n' in line:
            raise ValueError('writeline: Message should not be multi-lined')
        self.writer.write(line.encode(self.link.encoding, errors='surrogateescape') + b'\r\n')
        logger.debug(f'<<< {line}')
        if not exempt_event:
            self.fire_events(line, mine=True)

    def writeprefixline(self, prefix, line, *args, **kwargs):
        self.writeline(':' + prefix + ' ' + line, *args, **kwargs)

    def writeserverline(self, line, *args, **kwargs):
        self.writeprefixline(self.sid,  line, *args, **kwargs)

    def writeuserline(self, uid, line, *args, **kwargs):
        self.writeprefixline(uid, line, *args, **kwargs)

    def fire_events(self, line, mine=False):
        message_type, prefix, command, params = parseline(line)

        if (message_type is Message.USER) or (message_type is Message.SERVER):
            params.insert(0, prefix)

        getattr(self.core_event_listener, command)(*params)
        if (not mine) and (not self.bursting):
            getattr(self.event_listener, command)(*params)

    def register_services(self):
        self.register_service('core')
        for service_name in settings.services:
            self.register_service(service_name, settings.services[service_name])

    def register_service(self, service_name, module_names='*'):
        instance = import_class_from_module(f'ika.services.{service_name}')(self)
        instance.register_modules(module_names)
        self.services[service_name] = instance

    def register_service_irc_bots(self):
        for service_name in self.services.keys():
            self.register_service_irc_bot(service_name)

    def register_service_irc_bot(self, service_name):
        self.services[service_name].register_irc_bots()

    def unload_service(self, service_name):
        instance = self.services[service_name]
        instance.unload_irc_bots(reason='Service unloaded')
        instance.unload_modules()

        del self.services[service_name]

    def reload_service_modules(self):
        for service_name in self.services.keys():
            self.reload_service_module(service_name)

    def reload_service_module(self, service_name):
        instance = self.services[service_name]
        instance.unload_modules()
        if instance.internal:
            instance.register_modules('*')
        else:
            instance.register_modules(settings.services[service_name])

    def reload_services(self):
        for service_name in list(self.services.keys()):
            self.unload_service(service_name)
        self.register_services()
        self.register_service_irc_bots()

    def reload_service(self, service_name):
        self.unload_service(service_name)
        self.register_service(service_name)
        self.register_service_irc_bot(service_name)

    def gen_next_service_id(self):
        self._next_service_id += 1
        return self._next_service_id

    def disconnect(self, reason=''):
        for instance in self.services.values():
            instance.unload_irc_bots(reason=reason)
        self.writeserverline('SQUIT', self.link.name, reason)
        self.writeserverline(f'ERROR :Service disconnected ({reason})', exempt_event=True)
