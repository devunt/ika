import asyncio

from ika.classes import Command


class Test(Command):
    name = "test"
    aliases = [
        "테스트",
    ]

    @asyncio.coroutine
    def execute(self, uid, *params):
        self.service.msg(uid, ' '.join(params))
        # Just repeat the lines
