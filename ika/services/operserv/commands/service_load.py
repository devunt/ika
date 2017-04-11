from ika.service import Command, Permission


class ServiceLoad(Command):
    name = 'LOADSERVICE'
    aliases = (
    )
    syntax = '<서비스명>'
    regex = r'(?P<service_name>\S+)'
    permission = Permission.OPERATOR
    description = (
        '지정된 서비스를 로드합니다.',
    )

    async def execute(self, user, service_name):
        self.server.register_service(service_name, [])
        self.server.register_service_irc_bot(service_name)
        self.msg(user, f'Service \x02{service_name}\x02 loaded.')
