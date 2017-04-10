from ika.service import Command, Permission


class Reload(Command):
    name = 'RELOAD'
    aliases = (
    )
    permission = Permission.OPERATOR
    description = (
        '설정을 다시 읽어들이고 서비스봇 모듈들을 새로운 파일로 갱신합니다.',
    )

    async def execute(self, user):
        self.server.reload_services()
        self.msg(user, 'Reload complete')
