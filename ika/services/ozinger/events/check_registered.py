import asyncio

from ika.classes import Listener
from ika.database import Session
from ika.database import Nick


class CheckRegistered(Listener):
    def check(self, uid, name):
        session = Session()
        nick = session.query(Nick).filter_by(name=name).first()
        if nick and (nick.account or nick.account_alias):
            self.service.msg(uid, '이 닉네임은 이미 오징어 IRC 네트워크에 등록되어 있는 닉네임입니다. 계정의 주인이시라면 \x02/msg {} 로그인\x02 을, 주인이 아니시라면 지금 닉네임을 다른 것으로 바꿔 주세요.', self.service.name)

    @asyncio.coroutine
    def NICK(self, user, *params):
        if user.account is None:
            self.check(user.uid, params[0])

    @asyncio.coroutine
    def UID(self, server, *params):
        self.check(params[0], params[2])
