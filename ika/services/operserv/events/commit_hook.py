import asyncio
import subprocess

from ika.classes import Listener
from ika.conf import settings


class CommitHook(Listener):
    @asyncio.coroutine
    def UID(self, server, *params):
        if params[2] == settings.github_bot:
            self.service.writesvsuserline('PRIVMSG {} : \x02[ika]\x02 Fetching new changes...', settings.admin_channel)
            ret = subprocess.call(('git', 'pull'))
            self.service.writesvsuserline('PRIVMSG {} : \x02[ika]\x02 Fetching completed with return code {}', settings.admin_channel, ret)
            if ret == 0:
                self.service.server.reload_services()
                self.service.writesvsuserline('PRIVMSG {} : \x02[ika]\x02 Reloaded.', settings.admin_channel)
