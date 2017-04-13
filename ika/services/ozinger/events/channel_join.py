from ika.service import Listener
from ika.models import Channel
from ika.enums import Flags


class ChannelJoin(Listener):
    async def fjoin(self, sid, cname, timestamp, *modes_n_umodes):
        channel = Channel.get(cname)
        if not channel:
            return
        irc_channel = self.server.channels[cname]
        for umode in modes_n_umodes[-1].split():
            uid = umode.split(',')[1]
            user = self.server.users[uid]
            flags = channel.get_flags_by_user(user)
            if flags:
                modestring = flags.modestring
                self.writesvsuserline('FMODE', cname, irc_channel.timestamp, f'+{modestring}', *((uid,) * len(modestring)))
