from ika.service import Command, Permission
from ika.conf import settings


class ServiceReload(Command):
    name = 'RELOADSERVICE'
    aliases = (
    )
    syntax = '[서비스명]'
    regex = r'(?P<service_name>\S+)?'
    permission = Permission.OPERATOR
    description = (
        '지정된 서비스를 리로드합니다.',
        ' ',
        '인자가 제공되지 않았을 경우 전체 서비스를 리로드합니다.'
    )

    async def execute(self, user, service_name):
        settings.reload()
        if service_name:
            self.msg(user, f'Service \x02{service_name}\x02 will be reloaded now.')
            self.server.reload_service(service_name)
        else:
            self.msg(user, 'Services will be reloaded now.')
            self.server.reload_services()
