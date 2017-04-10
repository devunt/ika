from ika.service import Listener
from ika.utils import unixtime


class UserCommands(Listener):
    async def privmsg(self, uid, target_uid_or_cname, message):
        if target_uid_or_cname.startswith(self.server.sid):
            self.server.services[target_uid_or_cname].process_command(self.server.users[uid], message)

    async def opertype(self, uid, opertype):
        self.server.users[uid].opertype = opertype

    async def idle(self, uid, target_uid):
        service = self.server.services[target_uid]
        self.server.writeuserline(service.uid, 'IDLE', uid, unixtime(), 0)

    async def nick(self, uid, nick):
        self.server.users[uid].nick = nick

    async def fhost(self, uid, dhost):
        self.server.users[uid].dhost = dhost

    async def fmode(self, uid, target_uid_or_cname, *args):
        """
        if len(params) == 3:  # channel/user mode
            pass  # TODO: To be implemented
        elif len(params) == 4:  # channel user mode
            modes = params[2]
            method = 'update' if modes[0] == '+' else 'difference_update'
            if params[3] in self.channels[params[0].lower()].usermodes.keys():
                getattr(self.channels[params[0].lower()].usermodes[params[3]], method)(modes[1:])
        """
        pass

    async def kick(self, uid, cname, target_uid, reason):
        del self.server.channels[cname].umodes[target_uid]
        if len(self.server.channels[cname].umodes) == 0:
            del self.server.channels[cname]

    async def part(self, uid, cname, reason):
        del self.server.channels[cname].umodes[uid]
        if len(self.server.channels[cname].umodes) == 0:
            del self.server.channels[cname]

    async def quit(self, uid, reason):
        # TODO: Remove from channel umodes too
        del self.server.users[uid]
