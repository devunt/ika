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
            self.server.register_service_irc_bots()

    async def capab(self, field, data=None):
        pass

    async def error(self, error):
        raise RuntimeError('Remote server has returned an error: {}'.format(error))
