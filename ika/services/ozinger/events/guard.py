from ika.service import Listener
from ika.models import Channel


class Guard(Listener):
    async def endburst(self):
        # TODO: Implement
        """
        if linked_once:
            return
        channels = session.query(Channel).all()
        for channel in channels:
            real_channel = self.server.channels.get(channel.name.lower())
            if real_channel:
                self.service.join_channel(real_channel)
        """
        pass

    async def fjoin(self, cname, timestamp, modes, umodes):
        channel = Channel.get(cname)
        if not channel:
            return

        irc_channel = self.server.channels.get(channel.name)
        if not irc_channel:
            return

        if irc_channel.name not in self.service.joined_channels:
            self.service.join_channel(irc_channel)

    async def part(self, uid, cname, reason):
        if cname not in self.service.joined_channels:
            return

        irc_channel = self.server.channels.get(cname)
        if not irc_channel:
            self.service.part_channel(cname, 'Never left without saying goodbye')

    async def quit(self, uid, reason):
        for cname in self.service.joined_channels:
            if cname not in self.server.channels.keys():
                self.service.part_channel(cname, 'Never left without saying goodbye')
