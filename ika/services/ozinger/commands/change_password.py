import asyncio
from datetime import datetime

from ika.classes import Command
from ika.database import Nick, Account, Session


class ChangePassword(Command):
    name = '비밀번호변경'
    aliases = (
        '비밀번호바꾸기',
        '비번변경',
        '비번바꾸기',
    )
    syntax = '<현재 비밀번호> <새 비밀번호>'
    regex = r'(?P<password>\S+) (?P<new_password>\S+)'
    description = (
        '현재 오징어 IRC 네트워크에 로그인되어 있는 계정의 비밀번호를 변경합니다.',
        ' ',
        '이 명령을 사용할 시 현재 로그인되어 있는 계정의 비밀번호를 변경합니다.',
    )

    @asyncio.coroutine
    def execute(self, uid, password, new_password):
        user = self.service.server.users[uid]
        accountname = user.metadata.get('accountname')
        if accountname is None:
            self.service.msg(uid, '로그인되어 있지 않습니다. \x02/msg {} 로그인\x02 명령을 이용해 로그인해주세요.', self.service.name)
            return
        session = Session()
        account = session.query(Account).filter(Nick.name == accountname).first()
        if account.password == password:
            account.password = new_password
            session.commit()
            self.service.msg(uid, '\x02{}\x02 계정의 비밀번호가 \x02{}\x02 로 변경되었습니다.', account.name.name, new_password)
        else:
            self.service.msg(uid, '\x02{}\x02 계정의 비밀번호와 일치하지 않습니다.', account.name.name)
