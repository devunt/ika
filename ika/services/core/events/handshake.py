from ika import __version__
from ika.conf import settings
from ika.service import Listener
from ika.utils import unixtime


class HandshakeCommands(Listener):
    # `Listener` already has `server` property. Don't overwrite.
    async def SERVER(self, name, password, distance, sid, description):
        try:
            assert name == settings.link.name
            assert password == settings.link.password
        except AssertionError:
            self.service.writeline('ERROR :Server information does not match.')
            raise
        else:
            self.writeserverline('BURST', unixtime())
            self.writeserverline('VERSION', __version__)
            self.writeserverline('ENDBURST')
            """
                 idx = 621937810  # int('AAAAAA', 36)
                        for service in self.services_instances.values():
                            service.id = base36encode(idx)
                            names = list(service.aliases)
                            names.insert(0, service.name)
                            for name in names:
                                uid = '{}{}'.format(self.sid, service.id)
                                self.writeserverline('UID {uid} {timestamp} {nick} {host} {host} {ident} 0.0.0.0 {timestamp} +Iiko :{gecos}',
                                    uid=uid,
                                    nick=name,
                                    ident=service.ident,
                                    host=self.name,
                                    gecos=service.gecos,
                                    timestamp=unixtime(),
                                )
                                self.writeuserline(uid, 'OPERTYPE Services')
                                self.services[uid] = service
                                idx += 1
            """

    async def capab(self, field, data=None):
        pass

    async def error(self, error):
        raise RuntimeError('Remote server has returned an error: {}'.format(error))
