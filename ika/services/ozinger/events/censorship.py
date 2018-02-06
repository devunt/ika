import re
from hashlib import md5

from ika.service import Listener
from ika.conf import settings


class Censorship(Listener):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.patterns = {
            'supernet': re.compile(r's\s*u\s*p\s*e\s*r\s*n\s*e\s*t\s*s'),
        }

    async def privmsg(self, uid, target_uid_or_cname, message):
        if not target_uid_or_cname.startswith('#'):
            return

        for name, pattern in self.patterns.items():
            m = pattern.search(message)
            if m:
                usermask = self.server.users[uid].mask
                rule_id = md5(name.encode()).hexdigest()[:10]
                self.writesvsuserline('KICK', target_uid_or_cname, uid, f'이용자 보호 규칙 ({rule_id}) 위반')
                self.writesvsuserline(f'PRIVMSG {settings.logging.irc.channel} : \x02[ika]\x02 '
                                      f'User {usermask} violated censorship rule `{name}` with next message: {message}')
                break
