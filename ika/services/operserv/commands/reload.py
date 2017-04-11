from ika.service import Command, Permission
from ika.conf import settings


class Reload(Command):
    name = 'RELOAD'
    aliases = (
    )
    syntax = '[FULL?]'
    regex = r'(?P<full>FULL)?'
    permission = Permission.OPERATOR
    description = (
        '설정을 다시 읽어들이고 서비스봇 모듈들을 새로운 파일로 갱신합니다.',
    )

    async def execute(self, user, full):
        settings.reload()
        if full:
            self.msg(user, 'Will be reloaded now')
            self.server.full_reload_services()
        else:
            self.server.reload_services()
            self.msg(user, 'Reload complete')
