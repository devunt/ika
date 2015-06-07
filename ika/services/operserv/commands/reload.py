import asyncio

from ika.classes import Command
from ika.enums import Permission


class Reload(Command):
    name = 'RELOAD'
    aliases = (
    )
    permission = Permission.OPERATOR
    description = (
        '설정을 다시 읽어들이고 서비스봇 모듈들을 새로운 파일로 갱신합니다.',
    )

    @asyncio.coroutine
    def execute(self, user):
        self.service.server.reload_services()
        self.service.msg(user, 'Reload complete')
