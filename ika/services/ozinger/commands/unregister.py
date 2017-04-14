from ika.service import Command, Permission
from ika.enums import Flags


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
        '계정에 \x02F\02 (개설자) 권한이 있는 채널이 있을 경우 등록을 해제할 수 없습니다.',
        '실수로 명령을 실행하는 것을 방지하기 위해 명령 맨 뒤에 \x02YES\x02 를 붙여야 합니다.',
    )

    async def execute(self, user, confirmed):
        if confirmed != 'YES':
            return

        name = user.account.name

        for flag in user.account.channel_flags.all():
            if Flags.FOUNDER in flag.flags:
                self.err(user, f'\x02{flag.channel}\x02 채널에 \x02F\x02 (개설자) 권한이 있어 해당 계정 \x02{name}\x02 의 등록을 해제할 수 없습니다.')

        user.account.delete()
        self.writeserverline('METADATA', user.uid, 'accountname', '')

        self.msg(user, f'해당 계정 \x02{name}\x02 의 등록이 해제되었습니다.')
