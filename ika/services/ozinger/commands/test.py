import asyncio

from ika.classes import Command


class Test(Command):
    name = "테스트"
    aliases = [
        "test",
    ]
    description = [
        "테스트 명령입니다.",
    ]

    @asyncio.coroutine
    def execute(self, uid, *params):
        self.service.msg(uid, ' '.join(params))
        # Just repeat the lines
