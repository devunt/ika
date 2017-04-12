from ika.service import Listener


class Welcome(Listener):
    async def uid(self, sid, uid, timestamp, nick, host, dhost, ident, ipaddress, signon, *modes_n_gecos):
        self.msg(uid, f'오징어 IRC 네트워크에 오신 것을 환영합니다! '
                      f'서비스봇 사용을 위해서는 \x02/msg {self.service.name} 도움말\x02 또는 \x02/s ?\x02 등을 입력해보세요.')
