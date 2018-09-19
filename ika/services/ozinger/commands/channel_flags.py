import re

from ika.service import Command, Permission
from ika.models import Account, Channel, Flag
from ika.utils import tokenize_modestring
from ika.enums import Flags, FlagsDefinition
from ika.format import Color, colorize


class ChannelFlags(Command):
    name = '채널권한'
    aliases = (
        '권한',
        'CHANNELFLAGS',
        'FLAGS',
    )
    syntax = '<#채널명> [<대상> <권한>]'
    regex = r'(?P<cname>#\S+)( (?P<target>\S+) (?P<flagstring>[A-Za-z\+\-]+))?'
    permission = Permission.LOGIN_REQUIRED
    description = (
        '오징어 IRC 네트워크에 등록되어 있는 채널의 권한을 보거나 설정합니다.'
        ' ',
        '이 명령을 사용할 시 오징어 IRC 네트워크에 등록되어 있는 채널의 이용 권한을 보거나 설정할 수 있습니다.',
        '권한 설정시 대상은 \x02이카\x02 (로그인 계정명) 혹은 \x02이카*!*@*\x02 (마스크) 형식으로 설정이 가능하며,',
        '로그인 계정명을 대상으로 설정시 해당 계정으로 로그인 되어있는 유저가 \x02현재 해당 채널에 접속\x02해 있어야 합니다.'
        '권한은 \x02+OV-A\x02 (옵과 보이스 권한을 추가, 동시에 프로텍트 권한을 제거) 등으로 설정이 가능합니다.',
        ' ',
        '\x02현재 지원되는 권한의 목록은 다음과 같습니다:\x02',
        ' ',
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        descriptions = list()
        for k, v in FlagsDefinition.MAP.items():
            description = f'  {colorize(v.character, v.color):<16} {colorize(v.name, v.color):<32}'
            if not v.mutable:
                description += colorize('(설정 불가)', Color.RED)
            descriptions.append(description)
        self.description += tuple(descriptions)

    async def execute(self, user, cname, target, flagstring):
        channel = Channel.get(cname)

        if channel is None:
            if user.is_operator:
                self.err(user, f'해당 채널 \x02{cname}\x02 은 오징어 IRC 네트워크에 등록되어 있지 않습니다.')
            else:
                self.err(user, '해당 명령을 실행할 권한이 없습니다.')

        if Flags.OWNER not in channel.get_flags_by_user(user):
            if not user.is_operator:
                self.err(user, '해당 명령을 실행할 권한이 없습니다.')

        if (target is None) or (flagstring is None):
            self.msg(user, f'\x02=== {channel} 채널 권한 정보 ===\x02')
            self.msg(user, ' ')

            for flag in channel.flags.all():
                self.msg(user, f'  \x02{flag.target:<32}\x02 {flag.flags.coloredstring:<16} ({flag.updated_on.strftime("%Y-%m-%d %H:%M:%S")}에 마지막으로 변경됨)')
        else:
            irc_channel = self.server.channels.get(cname)

            if not re.match(r'\S+!\S+@\S+', target):
                account = Account.get(target)
                if account and irc_channel:
                    for irc_user in irc_channel.users.values():
                        if irc_user.account == account:
                            target = irc_user.account
                            break
                if not isinstance(target, Account):
                    self.err(user, f'\x02{channel}\x02 채널에 \x02{target}\x02 계정으로 로그인중인 유저가 존재하지 않습니다.')

            flag = Flag.get(channel, target)
            if flag is None:
                flag = Flag(channel=channel, type=0)
                flag.target = target

            flags = flag.flags
            adds, removes = tokenize_modestring(dict(D=Flags.get_all_characters()), flagstring)
            for c in adds.keys():
                flags |= Flags.get_by_character_for_mutation(c)
            for c in removes.keys():
                flags &= ~Flags.get_by_character_for_mutation(c)

            if flags == flag.flags:
                self.err(user, '설정될 수 있는 권한이 없습니다.')

            flag.flags = flags
            flag.save()

            if flags:
                self.msg(user, f'\x02{channel}\x02 채널의 \x02{flag.target}\x02 대상에게 해당 권한을 설정했습니다.')
            else:
                self.msg(user, f'\x02{channel}\x02 채널의 \x02{flag.target}\x02 대상의 권한을 제거했습니다.')

            if irc_channel:
                if isinstance(target, Account):
                    modestring = irc_channel.generate_synchronizing_modestring(account=target)
                else:
                    modestring = irc_channel.generate_synchronizing_modestring(mask=target)
                if modestring:
                    self.writesvsuserline('FMODE', irc_channel.name, irc_channel.timestamp, modestring)
