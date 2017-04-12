from ika.service import Command, Permission


class Stop(Command):
    name = 'STOP'
    aliases = (
    )
    syntax = '[이유]'
    regex = r'(?P<reason>.+)?'
    permission = Permission.OPERATOR
    description = (
        '서비스봇을 종료합니다.',
        ' ',
        '이 명령을 사용한 뒤 서비스봇을 다시 켜기 위해서는 콘솔 접근 권한이 필요합니다.',
    )

    async def execute(self, user, reason):
        self.msg(user, '장비를 정지합니다.')
        self.server.disconnect('Manually interrupted by operator command ({})'.format(reason or 'No reason was specified'))
