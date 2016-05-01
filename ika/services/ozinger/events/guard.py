import asyncio

from ika.classes import Listener
from ika.database import Channel, Session


class Guard(Listener):
    @asyncio.coroutine
    def ENDBURST(self, server, linked_once):
        if linked_once:
            return
        session = Session()
        channels = session.query(Channel).all()
        for channel in channels:
            real_channel = self.service.server.channels.get(channel.name.lower())
            if real_channel:
                self.service.join_channel(real_channel)

    @asyncio.coroutine
    def FJOIN(self, server, *params):
        channel = Channel.find_by_name(params[0])
        if not channel:
            return
        real_channel = self.service.server.channels.get(channel.name.lower())
        if not real_channel:
            return
        if real_channel.name.lower() not in self.service.joined_channels:
            self.service.join_channel(real_channel)

    @asyncio.coroutine
    def PART(self, user, channel, *params):
        if channel.lower() not in self.service.joined_channels:
            return
        real_channel = self.service.server.channels.get(channel.lower())
        if not real_channel:
            self.service.part_channel(channel, 'Never left without saying goodbye')

    @asyncio.coroutine
    def QUIT(self, user, *params):
        for channel in self.service.joined_channels:
            if channel not in self.service.server.channels.keys():
                self.service.part_channel(channel, 'Never left without saying goodbye')
