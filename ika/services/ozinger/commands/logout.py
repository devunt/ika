import asyncio

from ika.classes import Command
from ika.enums import Permission


class Logout(Command):
    name = '로그아웃'
    aliases = (
        '인증해제',
        'LOGOUT',
    )
    permission = Permission.LOGIN_REQUIRED
    description = (
        '오징어 IRC 네트워크에서 로그아웃합니다.',
        ' ',
        '이 명령을 사용할 시 오징어 IRC 네트워크에서 로그아웃합니다.',
    )

    @asyncio.coroutine
    def execute(self, user):
        self.service.writeserverline('METADATA {} accountname :', user.uid)
        del user.metadata['accountname']
        self.service.msg(user, '로그아웃했습니다.')
