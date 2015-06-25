import asyncio

from ika.classes import Listener
from ika.database import Channel, Session
from ika.enums import Flags


class ChannelJoin(Listener):
    modemap = {
        Flags.OWNER: 'q',
        Flags.PROTECT: 'a',
        Flags.OP: 'o',
        Flags.HALFOP: 'h',
        Flags.VOICE: 'v',
    }

    @asyncio.coroutine
    def FJOIN(self, server, *params):
        channel = Channel.find_by_name(params[0])
        if not channel:
            return
        real_channel = self.service.server.channels.get(channel.name.lower())
        if not real_channel:
            return
        usermodes = params[-1].split()
        for usermode in usermodes:
            uid = usermode.split(',')[1]
            user = self.service.server.users[uid]
            flags = channel.get_flags_by_user(user)
            modes = ''
            for flag, mode in self.modemap.items():
                if (flags & flag) != 0:
                    modes += mode
            self.service.writesvsuserline('FMODE {} {} +{} {}', real_channel.name, real_channel.timestamp, modes, user.uid)
