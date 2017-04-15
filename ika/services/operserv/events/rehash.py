from ika.service import Listener
from ika.conf import settings


class Rehash(Listener):
    async def rehash(self, uid, target):
        if target == self.server.name:
            self.msg(uid, 'Services will be reloaded now.')
            settings.reload()
            self.server.reload_services()
