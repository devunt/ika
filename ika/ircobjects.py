from ika.models import Account, Channel
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
        return adds, removes


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

    @property
    def is_service(self):
        return self.opertype == 'Services'

    def update_modes(self, *modes):
        adds, removes = super().update_modes(*modes)
        if 'o' in removes.keys():
            self.opertype = None


class IRCChannel(IRCModeMixin):
    umodesdef = dict()

    def __init__(self, name, timestamp):
        super().__init__()

        self.name = name
        self.timestamp = int(timestamp)

        self.users = dict()
        self.usermodes = dict()
        self.metadata = dict()

    def __repr__(self):
        return f'<IRCChannel {self.name}>'

    @property
    def umodestring(self):
        return ' '.join([f'{"".join(mode)},{uid}' for uid, mode in self.usermodes.items()])

    @property
    def channel(self):
        return Channel.get(self.name)

    def update_modes(self, *modes):
        super().update_modes(*modes)
        adds, removes = tokenize_modestring(self.umodesdef, *modes)
        for mode, v in adds.items():
            for uid in v:
                self.usermodes.setdefault(uid, set())
                self.usermodes[uid].add(mode)
        for mode, v in removes.items():
            for uid in v:
                self.usermodes[uid].remove(mode)

    def generate_synchronizing_modestring(self, uid=None):
        if not self.channel:
            return ''

        to_be_added = list()
        to_be_removed = list()

        if uid:
            usermodes = {uid: self.usermodes[uid]}
        else:
            usermodes = self.usermodes

        for uid, umode in usermodes.items():
            user = self.users[uid]
            if user.is_service:
                continue

            flags = self.channel.get_flags_by_user(user)
            modes = flags.modes

            adds = modes - umode
            removes = umode - modes

            for add in adds:
                to_be_added.append((add, uid))
            for remove in removes:
                to_be_removed.append((remove, uid))

        modestring = str()
        params = list()

        if len(to_be_added) > 0:
            modestring += '+'
            for mode, uid in to_be_added:
                modestring += mode
                params.append(uid)

        if len(to_be_removed) > 0:
           modestring += '-'
           for mode, uid in to_be_removed:
               modestring += mode
               params.append(uid)

        if len(params) > 0:
            modestring += ' '
            modestring += ' '.join(params)

        return modestring
