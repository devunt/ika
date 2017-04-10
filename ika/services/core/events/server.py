from ika.ircobjects import IRCChannel, IRCUser
from ika.models import Account
from ika.service import Listener


class ServerCommands(Listener):
    async def ping(self, origin, me):
        self.writeserverline('PONG', me, origin)

    async def uid(self, uid, timestamp, nick, host, dhost, ident, ipaddress, signon, modes, gecos):
        self.server.users[uid] = IRCUser(uid, timestamp, nick, host, dhost, ident, ipaddress, signon, modes, gecos)

    async def metadata(self, uid_or_cname, field, data):
        target = self.server.channels if uid_or_cname.startswith('#') else self.server.users

        if data == '':
            del target[field]
        else:
            target[field] = data

        if target is self.server.users:
            if field == 'accountname':
                account = Account.get(data)
                if (account is None) or (account.name != data):
                    self.writeserverline('METADATA', uid_or_cname, field, '')

    async def fjoin(self, cname, timestamp, modes, umodes):
        if cname not in self.server.channels:
            self.server.channels[cname] = IRCChannel(cname, timestamp, modes)
        for umode in umodes.split():
            mode, uid = umode.split(',')
            self.server.channels[cname].umodes[uid] = set(mode)
