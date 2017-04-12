from ika.models import Account
from ika.utils import tokenize_modestring


class IRCModeMixin:
    modesdef = dict()

    def __init__(self):
        self.modes = dict()

    @property
    def modestring(self):
        string = '+'
        params = list()
        for k, v in self.modes.items():
            string += k
            if v:
                params.append(v)
        if len(params) > 0:
            string += ' ' + ' '.join(params)
        return string

    def update_modes(self, *modes):
        adds, removes = tokenize_modestring(self.modesdef, *modes)
        for k, v in adds.items():
            self.modes[k] = v
        for k, v in removes.items():
            if v and self.modes[k] != v:
                continue
            del self.modes[k]


class IRCUser(IRCModeMixin):
    def __init__(self, uid, timestamp, nick, host, dhost, ident, ipaddress, signon, gecos):
        super().__init__()

        self.uid = uid
        self.timestamp = int(timestamp)
        self.nick = nick
        self.host = host
        self.dhost = dhost
        self.ident = ident
        self.ipaddress = ipaddress
        self.signon = int(signon)
        self.gecos = gecos

        self.opertype = None
        self.metadata = dict()

    @property
    def mask(self):
        return '{}!{}@{}'.format(self.nick, self.ident, self.dhost)

    @property
    def account(self) -> Account:
        name = self.metadata.get('accountname')
        return name and Account.get(name)

    @property
    def is_operator(self):
        return self.opertype == 'NetAdmin'


class IRCChannel(IRCModeMixin):
    def __init__(self, name, timestamp):
        super().__init__()

        self.name = name
        self.timestamp = int(timestamp)

        self.umodes = dict()
        self.metadata = dict()

    @property
    def umodestring(self):
        return ' '.join([f'{mode},{uid}' for uid, mode in self.umodes.items()])
