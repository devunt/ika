# from datetime import datetime

from ika.service import Command
from ika.models import Account, Nickname


class Register(Command):
    name = '등록'
    aliases = (
        '가입',
        'REGISTER',
        'SIGNUP',
    )
    syntax = '<이메일 주소> <비밀번호>'
    regex = r'(?P<email>\S+) (?P<password>\S+)'
    description = (
        '오징어 IRC 네트워크에 계정을 등록합니다.',
        ' ',
        '이 명령을 사용할 시 오징어 IRC 네트워크에 현재 사용중인 닉네임을 계정으로 등록하며,',
        '그 뒤로 네트워크에서 제공하는 여러 편의 기능등을 이용하실 수 있습니다.',
        '입력하신 비밀번호는 서버에 bcrypt를 이용해 안전하게 저장되나,',
        '자동로그인을 위해 클라이언트에 자주 저장되는 비밀번호의 특성상 유출이 쉽게 가능하기 때문에',
        '\x1f기존에 다른 곳에서 사용하지 않는 비밀번호의 사용을 권장\x1f합니다.',
    )

    async def execute(self, user, email, password):
        if Nickname.get(user.nick) is not None:
            self.err(user, '해당 닉네임 \x02{}\x02 은 이미 오징어 IRC 네트워크에 등록되어 있습니다.', user.nick)

        if Account.objects.filter(email__iexact=email).exists():
            self.err(user, '해당 이메일 \x02{}\x02 은 이미 오징어 IRC 네트워크에 등록되어 있습니다.', email)

        account = Account()
        account.email = email
        account.set_password(password)
        # account.last_login = datetime.now()
        account.save()

        nick = Nickname()
        nick.name = user.nick
        nick.account = account
        nick.is_account_name = True
        # nick.last_use = datetime.now()
        nick.save()

        self.msg(user, f'해당 닉네임 \x02{nick.name}\x02 의 계정 등록이 완료되었습니다. '
                       f'앞으로 \x02/msg {self.service.name} 로그인 {password}\x02 명령을 통해 로그인할 수 있습니다. 지금 로그인 해보세요.')
