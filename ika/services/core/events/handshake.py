import re

from ika import __version__
from ika.conf import settings
from ika.service import Listener
from ika.utils import unixtime
from ika.ircobjects import IRCChannel, IRCUser


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
            IRCChannel.umodesdef = dict(A=re.match(r'\(([a-zA-Z]+?)\)', capabilities['PREFIX']).group(1))
            a, b, c, d = capabilities['CHANMODES'].split(',')
            IRCChannel.modesdef = dict(A=a, B=b, C=c, D=d)
            a, b, c, d = capabilities['USERMODES'].split(',')
            IRCUser.modesdef = dict(A=a, B=b, C=c, D=d)

    # ERROR can be both handshake and server command.
    def error(self, *sid_and_error):
        raise RuntimeError(f'Remote server has returned an error: {sid_and_error[-1]}')
