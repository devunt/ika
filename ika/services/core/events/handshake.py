from ika import __version__
from ika.conf import settings
from ika.service import Listener
from ika.utils import unixtime


class HandshakeCommands(Listener):
    # `Listener` already has `server` property. Don't overwrite.
    def SERVER(self, name, password, distance, sid, description):
        try:
            assert name == settings.link.name
            assert password == settings.link.password
        except AssertionError:
            self.service.writeline('ERROR :Server information does not match.')
            raise
        else:
            self.writeserverline('BURST', unixtime(), exempt_event=True)
            self.writeserverline('VERSION', __version__, exempt_event=True)
            self.writeserverline('ENDBURST', exempt_event=True)

    def capab(self, field, data=None):
        pass

    def error(self, error):
        raise RuntimeError('Remote server has returned an error: {}'.format(error))
