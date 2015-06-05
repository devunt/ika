import asyncio

from ika.classes import Command

from ika.services.ozinger import Ozinger
from ika.services.ozinger.commands.ghost import Ghost


class Identify(Command):
    name = 'GHOST'
    syntax = '<닉네임>'
    regex = r'(?P<nick>\S+)'
    description = (
        '오징어 IRC 네트워크에 등록된 계정에 연결된 닉네임을 사용중인 사용자의 연결을 강제로 끊습니다.',
        ' ',
        '\x02이 명령은 호환성을 위한 레거시 명령입니다. 아래 명령을 이용해주세요.\x02',
        '\x02/msg {} {} {}\x02'.format(Ozinger.name, Ghost.name, Ghost.syntax),
    )

    @asyncio.coroutine
    def execute(self, user, nick):
        ozinger = tuple(filter(lambda x: isinstance(x, Ozinger), self.service.server.services_instances))[0]
        ghost = tuple(filter(lambda x: isinstance(x, Ghost), ozinger.commands.values()))[0]
        asyncio.async(Ghost.execute(ghost, user, nick))
