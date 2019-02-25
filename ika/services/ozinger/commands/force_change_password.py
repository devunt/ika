from ika.service import Command, Permission
from ika.models import Account


class ChangePassword(Command):
    name = '강제비밀번호변경'
    aliases = (
        'FPASSWORD',
    )
    syntax = '<계정명> <새 비밀번호>'
    regex = r'(?P<name>\S+) (?P<new_password>\S+)'
    permission = Permission.OPERATOR
    description = (
        '현재 오징어 IRC 네트워크에 로그인되어 있는 계정의 비밀번호를 강제로 변경합니다.',
        ' ',
        '이 명령을 사용할 시 현재 로그인되어 있는 계정의 비밀번호를 강제로 변경합니다.',
    )

    async def execute(self, user, name, new_password):
        account = Account.get(name)
        if account is None:
            self.err(user, '등록되지 않은 계정입니다.')
        account.set_password(new_password)
        account.save()
        self.msg(user, f'\x02{account}\x02 계정의 비밀번호가 \x02{new_password}\x02 로 변경되었습니다.')
