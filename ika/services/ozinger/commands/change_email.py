import asyncio
from datetime import datetime

from ika.classes import Command
from ika.enums import Permission
from ika.database import Nick, Account, Session


class ChangeEmail(Command):
    name = '이메일변경'
    aliases = (
        '이메일바꾸기',
    )
    syntax = '<현재 비밀번호> <새 이메일>'
    regex = r'(?P<password>\S+) (?P<new_email>\S+)'
    permission = Permission.LOGIN_REQUIRED
    description = (
        '현재 오징어 IRC 네트워크에 로그인되어 있는 계정의 이메일을 변경합니다.',
        ' ',
        '이 명령을 사용할 시 현재 로그인되어 있는 계정의 이메일을 변경합니다.',
    )

    @asyncio.coroutine
    def execute(self, uid, password, new_email):
        user = self.service.server.users[uid]
        accountname = user.metadata.get('accountname')
        session = Session()
        account = session.query(Account).filter(Nick.name == accountname).first()
        if account.password == password:
            account.email = new_email
            session.commit()
            self.service.msg(uid, '\x02{}\x02 계정의 이메일이 \x02{}\x02 로 변경되었습니다.', account.name.name, new_email)
        else:
            self.service.msg(uid, '\x02{}\x02 계정의 비밀번호와 일치하지 않습니다.', account.name.name)
