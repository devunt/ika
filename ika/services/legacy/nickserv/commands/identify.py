import asyncio

from ika.classes import Command

from ika.services.ozinger import Ozinger
from ika.services.ozinger.commands.login import Login


class Identify(Command):
    name = 'IDENTIFY'
    aliases = (
        'ID',
    )
    syntax = '[계정명] <비밀번호>'
    regex = r'((?P<name>\S+) )?(?P<password>\S+)'
    description = (
        '오징어 IRC 네트워크에 로그인합니다.',
        ' ',
        '\x02이 명령은 호환성을 위한 레거시 명령입니다. 아래 명령을 이용해주세요.\x02',
        '\x02/msg {} {} {}\x02'.format(Ozinger.name, Login.name, Login.syntax),
    )

    @asyncio.coroutine
    def execute(self, user, name, password):
        ozinger = tuple(filter(lambda x: isinstance(x, Ozinger), self.service.server.services_instances))[0]
        login = tuple(filter(lambda x: isinstance(x, Login), ozinger.commands.values()))[0]
        asyncio.async(Login.execute(login, user, name, password))
