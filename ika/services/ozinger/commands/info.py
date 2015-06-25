import asyncio

from ika.classes import Command
from ika.enums import Flags, Permission
from ika.database import Account, Channel


class Information(Command):
    name = '정보'
    aliases = (
    )
    syntax = '[계정명 또는 채널명]'
    regex = r'(?P<name>\S+)?'
    permission = Permission.LOGIN_REQUIRED
    description = (
        '오징어 IRC 네트워크에 등록되어 있는 계정 또는 채널의 정보를 확인합니다.',
        ' ',
        '이 명령을 사용할 시 오징어 IRC 네트워크에 이미 등록되어 있는 계정 또는 채널에 대한 정보를 확인할 수 있습니다.',
        '계정명 또는 채널명을 생략할 경우 현재 로그인되어 있는 계정의 정보를 보여줍니다.',
        '자신의 계정이나 자신이 주인으로 등록되어 있는 채널 외 대상의 정보를 보기 위해서는 오퍼레이터 인증이 필요합니다.',
    )

    @asyncio.coroutine
    def execute(self, user, name):
        if name is None:
            account = user.account
        else:
            if name.startswith('#'):
                channel = Channel.find_by_name(name)
                if user.is_operator:
                    if channel is None:
                        self.service.msg(user, '등록되지 않은 채널입니다.')
                        return
                else:
                    if channel is not None:
                        if (channel.get_flags_by_user(user) & Flags.OWNER) == 0:
                            self.service.msg(user, '권한이 없습니다.')
                            return
                    else:
                        self.service.msg(user, '권한이 없습니다.')
                        return
                self.service.msg(user, '\x02=== {} 채널 정보 ===\x02', channel.name)
                self.service.msg(user, '채널 등록일: {}', channel.created_on)
            else:
                if user.is_operator:
                    account = Account.find_by_nick(name)
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
                self.service.msg(user, '계정 등록일: {}', account.created_on)
                self.service.msg(user, '마지막 로그인: {}', account.last_login)
