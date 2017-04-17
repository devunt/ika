from ika.service import Command, Permission


class ChangePassword(Command):
    name = '비밀번호변경'
    aliases = (
        '비밀번호바꾸기',
        '비번변경',
        '비번바꾸기',
        'CHANGEPASSWORD',
        'CHANGEPASS',
    )
    syntax = '<현재 비밀번호> <새 비밀번호>'
    regex = r'(?P<password>\S+) (?P<new_password>\S+)'
    permission = Permission.LOGIN_REQUIRED
    description = (
        '현재 오징어 IRC 네트워크에 로그인되어 있는 계정의 비밀번호를 변경합니다.',
        ' ',
        '이 명령을 사용할 시 현재 로그인되어 있는 계정의 비밀번호를 변경합니다.',
    )

    async def execute(self, user, password, new_password):
        if user.account.check_password(password):
            account = user.account
            account.set_password(new_password)
            account.save()
            self.msg(user, f'\x02{user.account}\x02 계정의 비밀번호가 \x02{new_password}\x02 로 변경되었습니다.')
        else:
            self.err(user, f'\x02{user.account}\x02 계정의 비밀번호와 일치하지 않습니다.')
