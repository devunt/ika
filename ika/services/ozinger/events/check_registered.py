from ika.service import Listener
from ika.models import Account


class CheckRegistered(Listener):
    def _check(self, uid, name):
        if Account.get(name):
            self.msg(uid, f'이 닉네임은 이미 오징어 IRC 네트워크에 등록되어 있는 닉네임입니다. '
                          f'계정의 주인이시라면 \x02/msg {self.service.name} 로그인\x02 을, '
                          f'주인이 아니시라면 지금 닉네임을 다른 것으로 바꿔 주세요.')

    async def nick(self, uid, nick):
        if self.server.users[uid].account is None:
            self._check(uid, nick)

    async def uid(self, uid, timestamp, nick, host, dhost, ident, ipaddress, signon, modes, gecos):
        self._check(uid, nick)
