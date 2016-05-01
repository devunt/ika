import asyncio

from ika.classes import Command
from ika.database import Channel, Flag, Session
from ika.enums import Flags, Permission


class ChannelFlags(Command):
    name = '채널권한'
    aliases = (
        '권한',
        'CHANNELFLAGS',
        'FLAGS',
    )
    syntax = '<#채널명>'
    regex = r'(?P<name>#\S+)'
    permission = Permission.LOGIN_REQUIRED
    description = (
        '오징어 IRC 네트워크에 등록되어 있는 채널의 권한을 보거나 설정합니다,'
        ' ',
        '이 명령을 사용할 시 오징어 IRC 네트워크에 등록되어 있는 채널의 이용 권한을 보거나 설정하며,',
        '개설자(파운더), 주인, 보호된 사용자, 관리자(옵), 부관리자(하프옵), 발언권(보이스) 등의 권한이 설정 가능합니다.',
    )

    flagmap = {
        Flags.OWNER: 'Q',
        Flags.FOUNDER: 'F',
        Flags.PROTECT: 'A',
        Flags.OP: 'O',
        Flags.HALFOP: 'H',
        Flags.VOICE: 'V',
    }

    @asyncio.coroutine
    def execute(self, user, name):
        #session = Session()

        channel = Channel.find_by_name(name)

        if (channel is None) or (channel.get_flags_by_user(user) & Flags.OWNER) == 0:
            if user.is_operator:
                self.service.msg(user, '해당 채널 \x02{}\x02 은 오징어 IRC 네트워크에 등록되어 있지 않습니다.', name)
            else:
                self.service.msg(user, '해당 명령을 실행할 권한이 없습니다.')
            return

        self.service.msg(user, '\x02=== {} 채널 권한 정보 ===\x02', channel.name)
        self.service.msg(user, ' ')
        self.service.msg(user, '\x02{:32}{:32}{}\x02', '계정명 또는 마스크', '권한', '변경된 시각')

        for flag in channel.flags:
            flags = ''.join(map(lambda x: x[1] if (flag.type & x[0]) != 0 else '', self.flagmap.items()))
            self.service.msg(user, '{:32}{:32}{}', flag.target, flags, flag.created_on)