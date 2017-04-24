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

            entrymsg = channel.data.get('entrymsg')
            if entrymsg:
                self.msg(uid, f'\x02[{channel.name}] {entrymsg}\x02')

            url = channel.data.get('url')
            if url:
                self.msg(uid, f'\x02[{channel.name}] 채널 웹사이트: {url}\x02')

            email = channel.data.get('email')
            if email:
                self.msg(uid, f'\x02[{channel.name}] 채널 이메일: {email}\x02')
