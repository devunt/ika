from ika.service import Listener


class UserCommands(Listener):
    def privmsg(self, uid, target_uid_or_cname, message):
        if target_uid_or_cname.startswith(self.server.sid):
            self.server.service_bots[target_uid_or_cname].process_command(self.server.users[uid], message)

    def opertype(self, uid, opertype):
        self.server.users[uid].opertype = opertype

    def idle(self, uid, target_uid, signon=None, idletime=None):
        service = self.server.service_bots.get(target_uid)
        if service is not None:
            self.server.writeuserline(service.uid, 'IDLE', uid, self.server.users[service.uid].signon, 0)

    def nick(self, uid, nick):
        self.server.users[uid].nick = nick

    def fhost(self, uid, dhost):
        self.server.users[uid].dhost = dhost

    # fmode can be both user and server command.
    def fmode(self, uid_or_sid, target_uid_or_cname, timestamp, *modes):
        if target_uid_or_cname.startswith('#'):
            self.server.channels[target_uid_or_cname].update_modes(*modes)
        else:
            self.server.users[target_uid_or_cname].update_modes(*modes)

    def mode(self, uid, target_uid, *modes):
        self.server.users[target_uid].update_modes(*modes)

    def kick(self, uid, cname, target_uid, reason):
        self.part(target_uid, cname, reason)

    def part(self, uid, cname, reason):
        irc_channel = self.server.channels[cname]
        self.server.users[uid].channels.remove(irc_channel)
        del irc_channel.umodes[uid]
        if len(irc_channel.umodes) == 0:
            del self.server.channels[cname]

    def quit(self, uid, reason):
        while len(self.server.users[uid].channels) > 0:
            irc_channel = next(iter(self.server.users[uid].channels))
            self.part(uid, irc_channel.name, reason)
        del self.server.users[uid]
