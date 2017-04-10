from ika.models import Account


class IRCUser:
    def __init__(self, uid, timestamp, nick, host, dhost, ident, ipaddress, signon, modes, gecos):
        self.uid = uid
        self.timestamp = int(timestamp)
        self.nick = nick
        self.host = host
        self.dhost = dhost
        self.ident = ident
        self.ipaddress = ipaddress
        self.signon = int(signon)
        self.modes = modes
        self.gecos = gecos

        self.opertype = None
        self.metadata = dict()

    @property
    def mask(self):
        return '{}!{}@{}'.format(self.nick, self.ident, self.dhost)

    @property
    def account(self):
        name = self.metadata.get('accountname')
        return name and Account.get(name)

    @property
    def is_operator(self):
        return self.opertype == 'NetAdmin'


class IRCChannel:
    def __init__(self, name, timestamp, modes):
        self.name = name
        self.timestamp = int(timestamp)
        self.modes = modes

        self.umodes = dict()
        self.metadata = dict()
