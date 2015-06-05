import asyncio

from ika.classes import Command
from ika.enums import Permission
from ika.database import Account, Nick, Session


class Information(Command):
    name = '정보'
    aliases = (
    )
    syntax = '[계정명]'
    regex = r'(?P<name>\S+)?'
    permission = Permission.LOGIN_REQUIRED
    description = (
        '오징어 IRC 네트워크에 등록되어 있는 계정의 정보를 확인합니다.',
        ' ',
        '이 명령을 사용할 시 오징어 IRC 네트워크에 이미 등록되어 있는 계정에 대한 정보를 확인할 수 있습니다.',
        '계정명을 생략할 경우 현재 로그인되어 있는 계정의 정보를 보여줍니다.',
        '계정명을 따로 지정해 다른 계정의 정보를 보기 위해서는 오퍼레이터 권한이 필요합니다.',
    )

    @asyncio.coroutine
    def execute(self, user, name):
        if name is None:
            account = user.account
        else:
            if user.is_operator:
                session = Session()
                account = session.query(Account).filter(Nick.name == name).first()
                if account is None:
                    self.service.msg(user, '등록되지 않은 계정입니다.')
                    return
            else:
                self.service.msg(user, '권한이 없습니다. 오퍼레이터 인증을 해 주세요.')
                return
        self.service.msg(user, '\x02=== {} 계정 정보 ===\x02', account.name.name)
        self.service.msg(user, '이메일: {}', account.email)
        self.service.msg(user, '대표 계정명: {}', account.name.name)
        self.service.msg(user, '보조 계정명: {}', (', '.join([nick.name for nick in account.aliases])) or '없음')
        self.service.msg(user, '가상 호스트: {}', account.vhost or '없음')
        self.service.msg(user, '마지막 로그인: {}', account.last_login)
