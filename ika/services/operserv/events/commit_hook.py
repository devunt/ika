import subprocess

from ika.service import Listener
from ika.conf import settings


class CommitHook(Listener):
    async def uid(self, sid, uid, timestamp, nick, host, dhost, ident, ipaddress, signon, *modes_n_gecos):
        if nick == settings.github_bot:
            self.writesvsuserline(f'PRIVMSG {settings.logging.irc.channel} : \x02[ika]\x02 Fetching new changes...')
            proc = subprocess.run(['git', 'pull'])
            self.writesvsuserline(f'PRIVMSG {settings.logging.irc.channel} : \x02[ika]\x02 Fetching completed with return code {proc.returncode}')
