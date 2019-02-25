import asyncio

from channels.layers import get_channel_layer
from ika.service import Listener


class Web(Listener):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.channel_layer = get_channel_layer()
        asyncio.ensure_future(self.__loop())

    async def privmsg(self, uid, target_uid_or_cname, message):
        if not target_uid_or_cname.startswith('#'):
            return

        await self.channel_layer.group_send('ika', {
            'type': 'ika.message',
            'origin': '*',
            'sender': self.server.users[uid].nick,
            'target': target_uid_or_cname,
            'message': message,
        })

    async def __loop(self):
        while True:
            content = await self.channel_layer.receive('ika_reverse')
            if content['type'] == 'ika.reversed_message':
                self.writesvsuserline('FAKEMSG {} {} :{}', content['sender'], content['target'], content['message'])
