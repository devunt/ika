import asyncio
from ika.classes import Service


class Ozinger(Service):
    name = 'ㅇㅈㅇ'

    @asyncio.coroutine
    def execute(self, future, line):
        command, *params = line.split()
