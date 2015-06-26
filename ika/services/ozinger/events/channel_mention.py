import asyncio
import re

from ika.classes import Listener


class ChannelMention(Listener):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.pattern = re.compile(r'^{}(,|:)( (?P<line>.+))?$'.format(self.service.name))

    @asyncio.coroutine
    def PRIVMSG(self, user, target, msg):
        if not target.startswith('#'):
            return
        m = self.pattern.match(msg)
        if m:
            line = m.group('line')
            self.service.process_command(user, line or '도움말')
