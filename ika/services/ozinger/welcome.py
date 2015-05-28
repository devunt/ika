import asyncio

from ika.classes import Listener


class Welcome(Listener):
    @asyncio.coroutine
    def UID(self, server, *params):
        self.service.msg(params[0], '오징어 IRC 네트워크에 오신 것을 환영합니다! 서비스봇 사용을 위해서는 \x02/msg {0} 도움말\x02 을 입력해보세요.', self.service.name)
