from ika.service import Listener
from ika.models import Channel


class Guard(Listener):
    async def endburst(self, sid):
        for irc_channel in self.server.channels.values():
            channel = Channel.get(irc_channel.name)
            if channel:
                self.writeserverline('FJOIN', irc_channel.name, irc_channel.timestamp, irc_channel.modestring, f'o,{self.service.uid}')

    async def fjoin(self, sid, cname, timestamp, *modes_n_umodes):
        channel = Channel.get(cname)
        if not channel:
            return

        irc_channel = self.server.channels[cname]
        if irc_channel not in self.server.users[self.service.uid].channels:
            self.writeserverline('FJOIN', cname, irc_channel.timestamp, irc_channel.modestring, f'o,{self.service.uid}')

    async def part(self, uid, cname, reason):
        irc_channel = self.server.channels[cname]
        if irc_channel not in self.server.users[self.service.uid].channels:
            return

        if next(iter(irc_channel.umodes.keys())) == self.service.uid:
            self.writesvsuserline('PART', cname, 'Never left without saying goodbye')

    async def quit(self, uid, reason):
        cnames = [irc_channel.name for irc_channel in self.server.users[self.service.uid].channels if next(iter(irc_channel.umodes.keys())) == self.service.uid]
        for cname in cnames:
            self.writesvsuserline('PART', cname, 'Never left without saying goodbye')
