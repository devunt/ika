from ika.service import Listener


class Guard(Listener):
    async def endburst(self, sid):
        for irc_channel in self.server.channels.values():
            if irc_channel.channel:
                self.service.join_channel(irc_channel.name)
                modestring = irc_channel.generate_synchronizing_modestring()
                if modestring:
                    self.writesvsuserline('FMODE', irc_channel.name, irc_channel.timestamp, modestring)

    async def fjoin(self, sid, cname, timestamp, *modes_n_umodes):
        irc_channel = self.server.channels[cname]
        if not irc_channel.channel:
            return

        if irc_channel not in self.server.users[self.service.uid].channels:
            self.service.join_channel(irc_channel.name)
            modestring = irc_channel.generate_synchronizing_modestring()
            if modestring:
                self.writesvsuserline('FMODE', irc_channel.name, irc_channel.timestamp, modestring)

    async def kick(self, uid, cname, target_uid, reason=None):
        await self.part(target_uid, cname, reason)

    async def part(self, uid, cname, reason=None):
        irc_channel = self.server.channels.get(cname)
        if irc_channel and ((len(irc_channel.users) == 1) and (next(iter(irc_channel.users.keys())) == self.service.uid)):
            self.service.part_channel(cname)

    async def quit(self, uid, reason=None):
        cnames = [irc_channel.name for irc_channel in self.server.users[self.service.uid].channels if (len(irc_channel.users)) == 1 and (next(iter(irc_channel.users.keys())) == self.service.uid)]
        for cname in cnames:
            self.service.part_channel(cname)
