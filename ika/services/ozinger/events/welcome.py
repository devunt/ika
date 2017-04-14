from ika.service import Listener
from ika.services.help import Help


class Welcome(Listener):
    async def uid(self, sid, uid, timestamp, nick, host, dhost, ident, ipaddress, signon, *modes_n_gecos):
        self.msg(uid, f'오징어 IRC 네트워크에 오신 것을 환영합니다! '
                      f'서비스봇 사용을 위해서는 {self.refer_command(Help)} 혹은 \x02/s ?\x02 등을 입력해보세요.')
