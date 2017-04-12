from ika.service import Command, Permission
from ika.models import Channel, Flag
from ika.utils import tokenize_modestring
from ika.enums import Flags


class ChannelFlags(Command):
    name = '채널권한'
    aliases = (
        '권한',
        'CHANNELFLAGS',
        'FLAGS',
    )
    syntax = '<#채널명> [대상] [권한]'
    regex = r'(?P<cname>#\S+)( (?P<target>\S+) (?P<flags>[+-][QFAOHV]+[+-FAOHV]*))?'
    permission = Permission.LOGIN_REQUIRED
    description = (
        '오징어 IRC 네트워크에 등록되어 있는 채널의 권한을 보거나 설정합니다,'
        ' ',
        '이 명령을 사용할 시 오징어 IRC 네트워크에 등록되어 있는 채널의 이용 권한을 보거나 설정하며,',
        '개설자(파운더), 주인(오너), 보호된 사용자(프로텍트), 관리자(옵), 부관리자(하프옵), 발언권(보이스) 등의 권한이 설정 가능합니다.',
        '권한 설정시 대상은 \x02이카\x02 (로그인 계정명) 혹은 \x02이카*!*@*\x02 (마스크) 형식으로 설정이 가능하며,',
        '권한은 \x02+OV-A\x02 (옵과 보이스 권한을 추가, 동시에 프로텍트 권한을 제거) 등으로 설정이 가능합니다.',
        '권한 설정시 Q 권한은 이 명령을 이용해 지정이 불가능합니다.',
    )

    async def execute(self, user, cname, target, flags):
        channel = Channel.get(cname)

        if channel is None:
            if user.is_operator:
                self.err(user, f'해당 채널 \x02{cname}\x02 은 오징어 IRC 네트워크에 등록되어 있지 않습니다.')
            else:
                self.err(user, '해당 명령을 실행할 권한이 없습니다.')

        if (channel.get_flags_by_user(user) & Flags.OWNER) == 0:
            if not user.is_operator:
                self.err(user, '해당 명령을 실행할 권한이 없습니다.')

        if (target is None) or (flags is None):
            self.msg(user, f'\x02=== {channel.name} 채널 권한 정보 ===\x02')
            self.msg(user, ' ')

            for flag in channel.flags.all():
                _flag = Flags(flag.type)
                self.msg(user, f'  \x02{flag.target:<32}\x02 {_flag.coloredstring:<16} ({flag.updated_on} 에 마지막으로 변경됨)')
        else:
            flag = Flag.get(channel, target)
            if flag is None:
                types = 0
            else:
                types = flag.type

            adds, removes = tokenize_modestring(dict(D=Flags.get_all_characters()), flags)
            for f in adds:
                types |= int(Flags.get(f))
            for f in removes:
                types &= ~int(Flags.get(f))

            if types == 0:
                if flag is not None:
                    flag.delete()
                    self.msg(user, f'\x02{channel.name}\x02 채널의 \x02{target}\x02 대상의 권한을 제거했습니다.')
                else:
                    self.err(user, '설정될 수 있는 권한이 없습니다.')
            else:
                if flag is None:
                    flag = Flag()
                    flag.channel = channel
                    flag.target = target
                flag.type = types
                flag.save()

                self.msg(user, f'\x02{channel.name}\x02 채널의 \x02{target}\x02 대상에게 해당 권한을 설정했습니다.')