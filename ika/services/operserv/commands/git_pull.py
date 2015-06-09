import asyncio
import subprocess

from ika.classes import Command
from ika.enums import Permission


class GitPull(Command):
    name = 'PULL'
    aliases = (
    )
    permission = Permission.OPERATOR
    description = (
        'GitHub 저장소에서 최신 버전 소스코드를 받아옵니다.',
    )

    @asyncio.coroutine
    def execute(self, user):
        self.service.msg(user, 'pulling start')
        ret = subprocess.call(('git', 'pull'))
        self.service.msg(user, 'pulling complete (command returned {})', ret)
