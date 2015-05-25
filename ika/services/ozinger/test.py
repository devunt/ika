import asyncio

from ika.classes import Command


class Test(Command):
    name = "test"
    aliases = [
        "테스트",
    ]

    @asyncio.coroutine
    def execute(self, future, *params):
        future.set_result(' '.join(params))
        # Just repeat the lines
