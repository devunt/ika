from ika.service import Command, Permission
from ika.conf import settings


class Reload(Command):
    name = 'RELOAD'
    aliases = (
    )
    syntax = '[서비스명]'
    regex = r'(?P<service_name>\S+)?'
    permission = Permission.OPERATOR
    description = (
        '지정된 서비스의 모듈들을 리로드합니다.',
        ' ',
        '인자가 제공되지 않았을 경우 전체 서비스의 모듈들을 리로드합니다.'
    )

    async def execute(self, user, service_name):
        settings.reload()
        if service_name:
            self.server.reload_service_module(service_name)
            self.msg(user, f'Service \x02{service_name}\x02 modules reloaded.')
        else:
            self.server.reload_service_modules()
            self.msg(user, 'Service modules reloaded.')
