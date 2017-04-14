from ika.service import Listener
from ika.models import Channel


class ChannelJoin(Listener):
    async def fjoin(self, sid, cname, timestamp, *modes_n_umodes):
        channel = Channel.get(cname)
        if not channel:
            return
        irc_channel = self.server.channels[cname]
        for umode in modes_n_umodes[-1].split():
            uid = umode.split(',')[1]
            modestring = irc_channel.generate_synchronizing_modestring(uid)
            if modestring:
                self.writesvsuserline('FMODE', cname, irc_channel.timestamp, modestring)
