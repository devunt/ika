from ika.ircobjects import IRCChannel, IRCUser
from ika.models import Account
from ika.service import Listener


class ServerCommands(Listener):
    def burst(self, sid, timestamp):
        self.server.bursting = True

    def endburst(self, sid):
        self.server.bursting = False
        if sid == self.server.linked_sid:
            self.server.register_service_irc_bots()

    def squit(self, sid, quit_sid, reason):
        uids_to_be_removed = list()
        for uid, user in self.server.users.items():
            if uid[:3] != quit_sid:
                continue
            while len(user.channels) > 0:
                irc_channel = next(iter(self.server.users[uid].channels))
                del irc_channel.users[uid]
                del irc_channel.usermodes[uid]
                if len(irc_channel.users) == 0:
                    del self.server.channels[irc_channel.name]
                user.channels.remove(irc_channel)
            del self.server.nicks[user.nick]
            uids_to_be_removed.append(uid)
        for uid in uids_to_be_removed:
            del self.server.users[uid]

    def ping(self, sid, origin, me):
        self.writeserverline('PONG', me, origin)

    def uid(self, sid, uid, timestamp, nick, host, dhost, ident, ipaddress, signon, *modes_n_gecos):
        self.server.users[uid] = IRCUser(uid, timestamp, nick, host, dhost, ident, ipaddress, signon, modes_n_gecos[-1])
        self.server.users[uid].update_modes(*modes_n_gecos[:-1])
        self.server.nicks[nick] = self.server.users[uid]

    def metadata(self, sid, uid_or_cname, field, data):
        if uid_or_cname == '*':
            return
        elif uid_or_cname.startswith('#'):
            target = self.server.channels
        else:
            target = self.server.users

        if data == '':
            del target[uid_or_cname].metadata[field]
        else:
            target[uid_or_cname].metadata[field] = data

            if target is self.server.users:
                if field == 'accountname':
                    account = Account.get(data)
                    if (account is None) or (account.name != data):
                        self.writeserverline('METADATA', uid_or_cname, field, '')

    def fjoin(self, sid, cname, timestamp, *modes_n_umodes):
        if cname not in self.server.channels:
            self.server.channels[cname] = IRCChannel(cname, timestamp)
        self.server.channels[cname].timestamp = timestamp
        self.server.channels[cname].update_modes(*modes_n_umodes[:-1])
        for umode in modes_n_umodes[-1].split():
            mode, uid = umode.split(',')
            self.server.channels[cname].users[uid] = self.server.users[uid]
            self.server.channels[cname].usermodes[uid] = set(mode)
            self.server.users[uid].channels.add(self.server.channels[cname])

    def svsnick(self, sid, uid, nick, timestamp):
        if uid not in self.server.users:
            return

        irc_user = self.server.users[uid]
        del self.server.nicks[irc_user.nick]
        irc_user.nick = nick
        self.server.nicks[irc_user.nick] = irc_user
