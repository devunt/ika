from ika.service import Command, Permission
from ika.models import Nickname
from ika.services.ozinger.commands.group import Group


class ChangeName(Command):
    name = '계정명변경'
    aliases = (
        '계정명바꾸기',
        '이름변경',
        '이름바꾸기',
        'CHANGENAME',
    )
    syntax = '<새 계정명>'
    regex = r'(?P<new_name>\S+)'
    permission = Permission.LOGIN_REQUIRED
    description = (
        '현재 오징어 IRC 네트워크에 로그인되어 있는 계정의 이름을 변경합니다.',
        ' ',
        '이 명령을 사용할 시 현재 로그인되어 있는 계정의 이름을 변경합니다.',
        f'기존 계정에 이미 \x02그룹\x02 명령을 이용해 추가가 완료되어 있는 닉네임중 하나를 선택할 수 있습니다.',
        '계정 이름이 바뀐 후에는 기존 계정명이 보조 계정명(그룹)으로 자동으로 바뀌게 됩니다',
    )

    async def execute(self, user, new_name):
        cur_name = user.account.name
        if cur_name == new_name:
            self.err(user, f'\x02{cur_name}\x02 계정의 대표 닉네임이 이미 \x02{new_name}\x02 입니다.')

        nickname = Nickname.get(new_name)
        if (nickname is None) or (nickname.account != user.account):
            self.err(user, f'\x02{cur_name}\x02 계정에 \x02{new_name}\x02 닉네임이 존재하지 않습니다. '
                           f'{self.refer_command(Group)} 명령을 이용해 해당 닉네임을 계정에 추가해보세요.')

        user.account.nicknames.update(is_account_name=False)

        nickname.is_account_name = True
        nickname.save()

        self.writeserverline('METADATA', user.uid, 'accountname', new_name)
        self.msg(user, f'\x02{cur_name}\x02 계정의 대표 닉네임이 \x02{new_name}\x02 로 변경되었습니다.')
