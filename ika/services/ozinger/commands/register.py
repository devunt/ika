import asyncio
from datetime import datetime

from ika.classes import Command
from ika.database import Account, Nick, Session


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

    @asyncio.coroutine
    def execute(self, user, email, password):
        session = Session()

        if Nick.find_by_name(user.nick):
            self.service.msg(user, '해당 닉네임 \x02{}\x02 은 이미 오징어 IRC 네트워크에 등록되어 있습니다.', user.nick)
            return

        if session.query(Account).filter(Account.email == email).exists():
            self.service.msg(user, '해당 이메일 \x02{}\x02 은 이미 오징어 IRC 네트워크에 등록되어 있습니다.', email)
            return

        nick = Nick()
        nick.name = user.nick
        nick.last_use = datetime.now()

        account = Account()
        account.email = email
        account.name = nick
        account.password = password
        account.last_login = datetime.now()

        session.add(account)
        session.commit()

        self.service.msg(user, '해당 닉네임 \x02{}\x02 의 계정 등록이 완료되었습니다. 앞으로 \x02/msg {} 로그인 {}\x02 명령을 통해 로그인할 수 있습니다. 지금 로그인 해보세요.', nick.name, self.service.name, password)
