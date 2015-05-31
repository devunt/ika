import asyncio
from datetime import datetime

from ika.classes import Command
from ika.database import Nick, User, Session


class Register(Command):
    name = '로그인'
    aliases = (
        '인증',
    )
    syntax = '[닉네임] <비밀번호>'
    description = (
        '오징어 IRC 네트워크에 로그인합니다.',
        ' ',
        '이 명령을 사용할 시 오징어 IRC 네트워크에 이미 등록되어 있는 닉네임으로 로그인하며,',
        '그 뒤로 네트워크에서 제공하는 여러 편의 기능등을 이용하실 수 있습니다.',
        '네트워크에 새로운 닉네임을 등록하는 방법에 대해서는 \x02등록\x02 명령을 참고해주세요.',
    )

    @asyncio.coroutine
    def execute(self, uid, *params):
        user = self.service.server.users[uid]
        if 'accountname' in user.metadata:
            self.service.msg(uid, '이미 \x02{}\x02 닉네임으로 로그인되어 있습니다.', user.metadata['accountname'])
            return
        if len(params) == 1:
            name = user.nick
            password = params[0]
        else:
            name = params[0]
            password = params[1]
        session = Session()
        nick = session.query(Nick).filter_by(name=name).first()
        if nick:
            user = nick.user or nick.user_alias
            if user.password == password:
                nick.last_use = datetime.now()
                (nick.user or nick.user_alias).last_login = datetime.now()
                session.commit()
                self.service.msg(uid, '환영합니다! \x02{}\x02 닉네임으로 로그인되었습니다.', nick.user.name.name)
                self.service.server.writeserverline('METADATA {} accountname :{}', uid, nick.user.name.name)
                self.service.server.users[uid].metadata['accountname'] = nick.user.name.name
                return
        self.service.msg(uid, '등록되지 않은 닉네임이거나 잘못된 비밀번호입니다. 닉네임이나 비밀번호를 모두 제대로 입력했는지 다시 한번 확인해주세요.')
