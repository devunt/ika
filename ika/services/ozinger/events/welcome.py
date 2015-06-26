import asyncio

from ika.classes import Listener


class Welcome(Listener):
    @asyncio.coroutine
    def UID(self, server, *params):
        self.service.msg(params[0], '오징어 IRC 네트워크에 오신 것을 환영합니다! 서비스봇 사용을 위해서는 \x02/msg {0} 도움말\x02 또는 \x02/s ?\x02 등을 입력해보세요.', self.service.name)
        self.service.msg(params[0], '오징어의 새 서비스봇인 ika는 현재 구현중에 있으며 시범적으로 기존 atheme 서비스봇을 대체해 운영되고 있습니다.')
        self.service.msg(params[0], '\x02기존 ㅇㅈㅇ와 오징오징어 명령 중 주로 쓰이던 몇몇 명령은 해당 봇 닉네임 그대로 이용하실 수 있습니다.\x02')
