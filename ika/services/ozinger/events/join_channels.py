import asyncio

from ika.classes import Listener
from ika.database import Channel, Session


class JoinChannels(Listener):
    @asyncio.coroutine
    def ENDBURST(self, server, linked_once):
        if linked_once:
            return
        session = Session()
        channels = session.query(Channel).all()
        for channel in channels:
            real_channel = self.service.server.channels.get(channel.name.lower())
            if real_channel:
                self.service.writeserverline('FJOIN {} {} +{} :a,{}',
                    real_channel.name, real_channel.timestamp, real_channel.modes, self.service.uid)
