from ika.service import Command, Permission


class ServiceUnload(Command):
    name = 'UNLOADSERVICE'
    aliases = (
    )
    syntax = '<서비스명>'
    regex = r'(?P<service_name>\S+)'
    permission = Permission.OPERATOR
    description = (
        '지정된 서비스를 언로드합니다.',
    )

    async def execute(self, user, service_name):
        self.server.unload_service(service_name)
        self.msg(user, f'Service \x02{service_name}\x02 unloaded.')
