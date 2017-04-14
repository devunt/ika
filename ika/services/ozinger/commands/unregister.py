from ika.service import Command, Permission


class Unregister(Command):
    name = '등록해제'
    aliases = (
        '탈퇴',
        'UNREGISTER',
    )
    syntax = '<YES>'
    regex = r'(?P<confirmed>YES)'
    permission = Permission.LOGIN_REQUIRED
    description = (
        '오징어 IRC 네트워크에 등록되어 있는 계정의 등록을 해제합니다.',
        ' ',
        '이 명령을 사용할 시 오징어 IRC 네트워크에 등록되어 있는 계정의 등록을 해제하며,',
        '그 뒤로는 네트워크에서 제공하는 여러 편의 기능등을 이용하실 수 없습니다.',
    )

    async def execute(self, user, confirmed):
        if confirmed != 'YES':
            return

        user.account.delete()

        self.msg(user, f'해당 계정 \x02{cname}\x02 의 등록이 해제되었습니다.')

        self.writeserverline('METADATA', 'accountname', '')
