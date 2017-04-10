import subprocess

from ika.service import Command, Permission


class GitPull(Command):
    name = 'PULL'
    aliases = (
    )
    permission = Permission.OPERATOR
    description = (
        'GitHub 저장소에서 최신 버전 소스코드를 받아옵니다.',
    )

    async def execute(self, user):
        self.msg(user, 'Pulling start')
        proc = subprocess.run(['git', 'pull'])
        self.msg(user, f'Pulling complete (command returned {proc.returncode})')
