from ika import __version__
from ika.conf import settings
from ika.service import Listener
from ika.utils import chanmodes, usermodes, unixtime


class HandshakeCommands(Listener):
    # `Listener` already has `server` property. Don't overwrite.
    def SERVER(self, name, password, distance, sid, description):
        try:
            assert name == settings.link.name
            assert password == settings.link.password
        except AssertionError:
            self.server.writeline('ERROR :Server information does not match.', exempt_event=True)
            raise
        else:
            self.writeserverline('BURST', unixtime(), exempt_event=True)
            self.writeserverline('VERSION', __version__, exempt_event=True)
            self.writeserverline('ENDBURST', exempt_event=True)

    def capab(self, field, data=None):
        if field == 'CAPABILITIES':
            capabilities = dict(x.split('=') for x in data.split())
            chanmodes['A'], chanmodes['B'], chanmodes['C'], chanmodes['D'] = capabilities['CHANMODES'].split(',')
            usermodes['A'], usermodes['B'], usermodes['C'], usermodes['D'] = capabilities['USERMODES'].split(',')

    def error(self, error):
        raise RuntimeError('Remote server has returned an error: {}'.format(error))
