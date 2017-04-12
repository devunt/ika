from ika.service import Listener
from ika.models import Channel
from ika.enums import Flags


class ChannelJoin(Listener):
    modemap = {
        Flags.OWNER: 'q',
        Flags.FOUNDER: 'q',
        Flags.PROTECT: 'a',
        Flags.OP: 'o',
        Flags.HALFOP: 'h',
        Flags.VOICE: 'v',
    }

    async def fjoin(self, sid, cname, timestamp, *modes_n_umodes):
        channel = Channel.get(cname)
        if not channel:
            return

        irc_channel = self.server.channels.get(channel.name)
        if not irc_channel:
            return

        umodes = modes_n_umodes[-1].split()
        for umode in umodes:
            uid = umode.split(',')[1]
            user = self.server.users[uid]
            flags = channel.get_flags_by_user(user)
            modes = str()
            for flag, mode in self.modemap.items():
                if (flags & flag) != 0:
                    modes += mode
            if len(modes) > 0:
                self.writesvsuserline('FMODE', irc_channel.name, irc_channel.timestamp, f'+{modes}', ' '.join((user.uid,) * len(modes)))
