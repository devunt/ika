from ika.service import Command, Permission
from ika.enums import Flags
from ika.models import Account, Channel


class Information(Command):
    name = '정보'
    aliases = (
        'INFO',
    )
    syntax = '[계정명 또는 채널명]'
    regex = r'(?P<name>\S+)?'
    permission = Permission.LOGIN_REQUIRED
    description = (
        '오징어 IRC 네트워크에 등록되어 있는 계정 또는 채널의 정보를 확인합니다.',
        ' ',
        '이 명령을 사용할 시 오징어 IRC 네트워크에 이미 등록되어 있는 계정 또는 채널에 대한 정보를 확인할 수 있습니다.',
        '자신의 계정이나 자신이 주인으로 등록되어 있는 채널 외 대상의 정보를 보기 위해서는 오퍼레이터 인증이 필요합니다.',
        '아무 인자도 없이 실행했을 경우 현재 로그인되어 있는 계정의 정보를 확인합니다.',
    )

    async def execute(self, user, name):
        if (name is not None) and name.startswith('#'):
            channel = Channel.get(name)
            if user.is_operator:
                if channel is None:
                    self.err(user, f'해당 채널 \x02{name}\x02 은 오징어 IRC 네트워크에 등록되어 있지 않습니다.')
            else:
                if channel is not None:
                    if (channel.get_flags_by_user(user) & Flags.OWNER) == 0:
                        self.err(user, '해당 명령을 실행할 권한이 없습니다.')
                else:
                    # 채널이 존재하지 않으나 권한이 없는 이용자에게는 채널의 존재 여부를 알려줄 수 없음
                    self.err(user, '해당 명령을 실행할 권한이 없습니다.')
            self.msg(user, '\x02=== {} 채널 정보 ===\x02', channel.name)
            self.msg(user, '채널 설립자: {}', ', '.join(map(lambda x: x.target, filter(lambda x: (x.type & Flags.FOUNDER) != 0, channel.flags))))
            self.msg(user, '채널 주인: {}', ', '.join(map(lambda x: x.target, filter(lambda x: (x.type & Flags.OWNER) != 0, channel.flags))))
            self.msg(user, '채널 등록일: {}', channel.created_on)
        else:
            if name is None:
                account = user.account
            else:
                account = Account.get(name)
            if (not user.is_operator) and (account != user.account):
                self.err(user, '해당 명령을 실행할 권한이 없습니다.')
            if account is None:
                self.err(user, f'해당 계정 \x02{name}\x02 은 오징어 IRC 네트워크에 등록되어 있지 않습니다.')
            self.msg(user, '\x02=== {} 계정 정보 ===\x02', account.name)
            self.msg(user, '이메일: {}', account.email)
            self.msg(user, '대표 계정명: {}', account.name)
            self.msg(user, '보조 계정명: {}', (', '.join(account.aliases)) or '없음')
            self.msg(user, '가상 호스트: {}', account.vhost or '없음')
            self.msg(user, '계정 등록일: {}', account.created_on)
            self.msg(user, '마지막 로그인: {}', account.authenticated_on)
