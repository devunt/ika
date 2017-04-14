from ika.service import Listener
from ika.models import Account
from ika.services.ozinger.commands.login import Login


class CheckRegistered(Listener):
    def _check(self, uid, name):
        account = Account.get(name)
        if account and (self.server.users[uid].account != account):
            self.msg(uid, f'이 닉네임은 이미 오징어 IRC 네트워크에 등록되어 있는 닉네임입니다. '
                          f'계정의 주인이시라면 {self.refer_command(Login)} 을, '
                          f'주인이 아니시라면 지금 닉네임을 다른 것으로 바꿔 주세요.')

    async def nick(self, uid, nick, timestamp):
        self._check(uid, nick)

    async def uid(self, sid, uid, timestamp, nick, host, dhost, ident, ipaddress, signon, *modes_n_gecos):
        self._check(uid, nick)
