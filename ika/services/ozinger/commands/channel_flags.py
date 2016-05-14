import asyncio
from sqlalchemy import func

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
    syntax = '<#채널명> [대상] [권한]'
    regex = r'(?P<name>#\S+)( (?P<target)\S+) (?P<flags>[+-][QFAOHV]+[+-QFAOHV]*))'
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

    flagmap = {
        Flags.OWNER: '\x0306Q\x03',
        Flags.FOUNDER: '\x0306F\x03',
        Flags.PROTECT: '\x0304A\x03',
        Flags.OP: '\x0309O\x03',
        Flags.HALFOP: '\x0311H\x03',
        Flags.VOICE: '\x0307V\x03',
    }
    reverse_flagmap = {
        'Q': Flags.OWNER,
        'F': Flags.FOUNDER,
        'A': Flags.PROTECT,
        'O': Flags.OP,
        'H': Flags.HALFOP,
        'V': Flags.VOICE,
    }

    @asyncio.coroutine
    def execute(self, user, name, target, flags):
        session = Session()

        channel = Channel.find_by_name(name)

        if channel is None:
            if user.is_operator:
                self.service.msg(user, '해당 채널 \x02{}\x02 은 오징어 IRC 네트워크에 등록되어 있지 않습니다.', name)
            else:
                self.service.msg(user, '해당 명령을 실행할 권한이 없습니다.')
            return

        if (channel.get_flags_by_user(user) & Flags.OWNER) == 0:
            if not user.is_operator:
                self.service.msg(user, '해당 명령을 실행할 권한이 없습니다.')
                return

        if (target is None) or (flags is None):
            self.service.msg(user, '\x02=== {} 채널 권한 정보 ===\x02', channel.name)
            self.service.msg(user, ' ')

            for flag in channel.flags:
                flags_str = ''.join(map(lambda x: x[1] if (flag.type & x[0]) != 0 else '', self.flagmap.items()))
                self.service.msg(user, '  \x02{:<32}\x02 {:<16} ({} 에 마지막으로 변경됨)', flag.target, flags_str, flag.created_on)
        else:
            flag = channel.flags.filter(func.lower(Flag.target) == func.lower(target)).first()

            if flag is None:
                flag = Flag()
                flag.channel = channel
                flag.target = target

            for _flag in flags:
                if _flag == '+':
                    is_adding = True
                elif _flag == '-':
                    is_adding = False
                else:
                    flagnum = int(self.reverse_flagmap[_flag])
                    if is_adding:
                        flag.type |= flagnum
                    else:
                        flag.type &= ~flagnum

            flag.created_on = func.now()

            session.add(flag)
            session.commit()

            self.service.msg(user, '\x02{}\x02 채널의 \x02{}\x02 대상에게 해당 권한을 설정했습니다.', name, target)
