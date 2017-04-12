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

    def fmode(self, uid, target_uid_or_cname, *modes):
        if target_uid_or_cname.startswith('#'):
            self.server.channels[target_uid_or_cname].update_modes(*modes)
        else:
            pass
        # TODO: Implement
        """
        if len(params) == 3:  # channel/user mode
            pass  # TODO: To be implemented
        elif len(params) == 4:  # channel user mode
            modes = params[2]
            method = 'update' if modes[0] == '+' else 'difference_update'
            if params[3] in self.channels[params[0].lower()].usermodes.keys():
                getattr(self.channels[params[0].lower()].usermodes[params[3]], method)(modes[1:])
        """

    def kick(self, uid, cname, target_uid, reason):
        del self.server.channels[cname].umodes[target_uid]
        if len(self.server.channels[cname].umodes) == 0:
            del self.server.channels[cname]

    def part(self, uid, cname, reason):
        del self.server.channels[cname].umodes[uid]
        if len(self.server.channels[cname].umodes) == 0:
            del self.server.channels[cname]

    def quit(self, uid, reason):
        # TODO: Remove from channel umodes too
        del self.server.users[uid]
