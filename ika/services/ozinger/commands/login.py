# from datetime import datetime

from ika.service import Command
from ika.models import Account


class Login(Command):
    name = '로그인'
    aliases = (
        '인증',
        'LOGIN',
        'IDENTIFY',
        'ID',
    )
    syntax = '[계정명] <비밀번호>'
    regex = r'((?P<name>\S+) )?(?P<password>\S+)'
    description = (
        '오징어 IRC 네트워크에 로그인합니다.',
        ' ',
        '이 명령을 사용할 시 오징어 IRC 네트워크에 이미 등록되어 있는 계정으로 로그인하며,',
        '그 뒤로 네트워크에서 제공하는 여러 편의 기능등을 이용하실 수 있습니다.',
        '네트워크에 새로운 계정을 등록하는 방법에 대해서는 \x02등록\x02 명령을 참고해주세요.',
    )

    async def execute(self, user, name, password):
        if user.account is not None:
            self.err(user, f'이미 \x02{user.account.name}\x02 계정으로 로그인되어 있습니다.')

        account = Account.get(name or user.nick)
        if (account is None) or (not account.check_password(password)):
            self.err(user, '등록되지 않은 계정이거나 잘못된 비밀번호입니다. 계정명이나 비밀번호를 모두 제대로 입력했는지 다시 한번 확인해주세요.')

        # nick.last_use = datetime.now()
        # account.last_login = datetime.now()
        self.msg(user, f'환영합니다! \x02{account.name}\x02 계정으로 로그인되었습니다.')
        self.writeserverline('METADATA', user.uid, 'accountname', account.name)
        if account.vhost is not None:
            self.writesvsuserline('CHGHOST', user.uid, account.vhost)
