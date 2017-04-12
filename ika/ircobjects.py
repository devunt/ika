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
            if not isinstance(v, set):
                string += k
                if v:
                    params.append(v)
        if len(params) > 0:
            string += ' ' + ' '.join(params)
        return string

    @property
    def listmodestring(self):
        string = '+'
        params = list()
        for k, v in self.modes.items():
            if isinstance(v, set):
                for e in v:
                    string += k
                    params.append(e)
        if len(params) > 0:
            string += ' ' + ' '.join(params)
        return string

    def update_modes(self, *modes):
        adds, removes = tokenize_modestring(self.modesdef, *modes)
        for k, v in adds.items():
            if isinstance(v, set):
                s = self.modes.get(k, set())
                self.modes[k] = s | v
            else:
                self.modes[k] = v
        for k, v in removes.items():
            if isinstance(v, set):
                self.modes[k] -= v
                if len(self.modes[k]) == 0:
                    del self.modes[k]
            else:
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

        # For backref
        self.channels = set()

    def __repr__(self):
        return f'<IRCUser {self.mask}>'

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
    umodesdef = dict()

    def __init__(self, name, timestamp):
        super().__init__()

        self.name = name
        self.timestamp = int(timestamp)

        self.umodes = dict()
        self.metadata = dict()

    def __repr__(self):
        return f'<IRCChannel {self.name}>'

    @property
    def umodestring(self):
        return ' '.join([f'{"".join(mode)},{uid}' for uid, mode in self.umodes.items()])

    def update_modes(self, *modes):
        super().update_modes(*modes)
        adds, removes = tokenize_modestring(self.umodesdef, *modes)
        for mode, v in adds.items():
            for uid in v:
                self.umodes.setdefault(uid, set())
                self.umodes[uid].add(mode)
        for mode, v in removes.items():
            for uid in v:
                self.umodes[uid].remove(mode)
                if len(self.umodes[uid]) == 0:
                    del self.umodes[uid]
