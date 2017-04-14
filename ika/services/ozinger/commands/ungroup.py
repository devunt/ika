from ika.service import Command, Permission
from ika.models import Nickname
from ika.services.ozinger.commands.change_name import ChangeName


class Ungroup(Command):
    name = '그룹해제'
    aliases = (
        '닉네임제거',
        '닉제거',
        'UNGROUP',
    )
    syntax = '[제거할 닉네임]'
    regex = r'(?P<name>\S+)?'
    permission = Permission.LOGIN_REQUIRED
    description = (
        '현재 오징어 IRC 네트워크에 로그인되어 있는 계정에서 닉네임을 제거합니다.',
        ' ',
        '이 명령을 사용할 시 현재 로그인되어 있는 계정에서 닉네임을 제거할 수 있습니다.',
        '제거할 닉네임이 지정되지 않을 시 현재 사용중인 닉네임으로 시도합니다.',
    )

    async def execute(self, user, name):
        nickname = Nickname.get(name or user.nick)
        if (nickname is None) or (nickname.account != user.account):
            self.err(user, f'\x02{user.account}\x02 계정에 \x02{name or user.nick}\x02 닉네임이 등록되어 있지 않습니다.')

        if nickname.is_account_name:
            self.err(user, f'\x02{nickname}\x02 닉네임이 해당 계정의 기본 닉네임으로 지정되어 있어 제거할 수 없습니다. '
                           f'{self.refer_command(ChangeName)} 명령을 이용해 기본 닉네임을 수정해주세요.')

        nickname.delete()
        self.msg(user, f'\x02{user.account}\x02 계정에서 \x02{nickname}\x02 닉네임을 제거했습니다.')
