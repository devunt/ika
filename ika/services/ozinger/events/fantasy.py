import re

from ika.service import Listener


class Fantasy(Listener):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.pattern = re.compile(r'^{}(,|:)( (?P<line>.+))?$'.format(re.escape(self.service.name)))

    async def privmsg(self, uid, target_uid_or_cname, message):
        if not target_uid_or_cname.startswith('#'):
            return

        m = self.pattern.match(message)
        if m:
            line = m.group('line')
            self.service.process_command(self.server.users[uid], line or '?')
