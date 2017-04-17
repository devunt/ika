from ika.service import Command, Permission


class ChangeEmail(Command):
    name = '이메일변경'
    aliases = (
        '이메일바꾸기',
        'CHANGEEMAIL',
    )
    syntax = '<현재 비밀번호> <새 이메일>'
    regex = r'(?P<password>\S+) (?P<new_email>\S+)'
    permission = Permission.LOGIN_REQUIRED
    description = (
        '현재 오징어 IRC 네트워크에 로그인되어 있는 계정의 이메일을 변경합니다.',
        ' ',
        '이 명령을 사용할 시 현재 로그인되어 있는 계정의 이메일을 변경합니다.',
    )

    async def execute(self, user, password, new_email):
        if user.account.check_password(password):
            account = user.account
            account.email = new_email
            account.save()
            self.msg(user, f'\x02{user.account}\x02 계정의 이메일이 \x02{new_email}\x02 로 변경되었습니다.')
        else:
            self.err(user, f'\x02{user.account}\x02 계정의 비밀번호와 일치하지 않습니다.')
