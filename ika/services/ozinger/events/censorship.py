import re
from datetime import datetime, timedelta
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

        user = self.server.users[uid]

        # 접속 시간 5분 미만 유저에게만 censorship 적용
        if (datetime.now() - user.connected_at) > timedelta(minutes=5):
            return

        for name, pattern in self.patterns.items():
            m = pattern.search(message)
            if m:
                usermask = user.mask
                rule_id = md5(name.encode()).hexdigest()[:7]
                self.writesvsuserline('KICK', target_uid_or_cname, uid, f'이용자 보호 규칙 위반 ({rule_id})')
                self.writesvsuserline(f'PRIVMSG {settings.logging.irc.channel} : \x02[ika]\x02 '
                                      f'User {usermask} violated censorship rule `{name}` on {target_uid_or_cname} '
                                      f'with next message: {message}')
                break
