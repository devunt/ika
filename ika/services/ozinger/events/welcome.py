import asyncio

from ika.classes import Listener


class Welcome(Listener):
    @asyncio.coroutine
    def UID(self, server, *params):
        self.service.msg(params[0], '오징어 IRC 네트워크에 오신 것을 환영합니다! 서비스봇 사용을 위해서는 \x02/msg {0} 도움말\x02 을 입력해보세요.', self.service.name)
        self.service.msg(params[0], '오징어의 새 서비스봇인 ika는 현재 시범적으로 \x02오징오징어\x02 를 대체하고 있습니다. ㅇㅈㅇ는 앞으로 대체될 예정에 있습니다.')
        self.service.msg(params[0], 'ika는 오픈소스로 개발되고 있으며 소스코드는 https://github.com/devunt/ika 에서 보실 수 있습니다. 많은 기여와 이슈 제보 부탁드립니다. 감사합니다.')
