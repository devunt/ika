import asyncio

from ika.classes import Command
from ika.enums import Permission
from ika.database import Session


class ChangeEmail(Command):
    name = '이메일변경'
    aliases = (
        '이메일바꾸기',
        'CHANGEEMAIL',
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
    def execute(self, user, password, new_email):
        session = Session()
        if user.account.password == password:
            account = user.account
            account.email = new_email
            session.commit()
            self.service.msg(user, '\x02{}\x02 계정의 이메일이 \x02{}\x02 로 변경되었습니다.', user.account.name.name, new_email)
        else:
            self.service.msg(user, '\x02{}\x02 계정의 비밀번호와 일치하지 않습니다.', user.account.name.name)
