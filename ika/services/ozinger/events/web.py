import re

from channels.layers import get_channel_layer
from ika.service import Listener


class Web(Listener):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.channel_layer = get_channel_layer()

    async def privmsg(self, uid, target_uid_or_cname, message):
        if not target_uid_or_cname.startswith('#'):
            return

        await self.channel_layer.group_send('hello', {
            'type': 'user_message',
            'channel': target_uid_or_cname,
            'message': message,
        })
