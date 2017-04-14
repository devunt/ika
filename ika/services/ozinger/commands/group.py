from datetime import datetime

from ika.service import Command, Permission
from ika.models import Nickname


class Group(Command):
    name = '그룹'
    aliases = (
        '닉네임추가',
        '닉추가',
        'GROUP',
    )
    permission = Permission.LOGIN_REQUIRED
    description = (
        '현재 오징어 IRC 네트워크에 로그인되어 있는 계정에 현재 사용중인 닉네임을 추가합니다.',
        ' ',
        '이 명령을 사용할 시 현재 로그인되어 있는 계정에 현재 사용중인 닉네임을 추가합니다.',
        '계정 1개에는 최대 5개의 닉네임을 추가적으로 등록할 수 있습니다.',
    )

    async def execute(self, user):
        if len(user.account.aliases) >= 5:
            self.err(user, f'\x02{user.account.name}\x02 계정에 등록할 수 있는 닉네임 제한을 초과했습니다 (5개).')
        if Nickname.get(user.nick):
            self.err(user, '이미 등록되어 있는 닉네임입니다.')
        nickname = Nickname(name=user.nick, account=user.account)
        nickname.save()
        self.msg(user, f'\x02{user.account.name}\x02 계정에 \x02{nickname.name}\x02 닉네임을 추가했습니다.')
