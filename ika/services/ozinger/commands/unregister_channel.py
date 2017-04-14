from ika.service import Command, Permission
from ika.models import Channel
from ika.enums import Flags


class UnregisterChannel(Command):
    name = '채널등록해제'
    aliases = (
        'UNREGISTERCHANNEL',
    )
    syntax = '<#채널명> <YES>'
    regex = r'(?P<cname>#\S+) (?P<confirmed>YES)'
    permission = Permission.LOGIN_REQUIRED
    description = (
        '오징어 IRC 네트워크에 등록되어 있는 채널의 등록을 해제합니다.',
        ' ',
        '이 명령을 사용할 시 오징어 IRC 네트워크에 등록되어 있는 채널의 \x02등록을 해제\x02하며,',
        '그 뒤로는 네트워크에서 제공하는 여러 편의 기능등을 이용하실 수 없습니다.',
        '채널 등록 해제는 해당 채널에 \x02F\x02 (개설자) 권한이 있는 사용자만 할 수 있습니다.',
        '실수로 명령을 실행하는 것을 방지하기 위해 명령 맨 뒤에 \x02YES\x02 를 붙여야 합니다.',
    )

    async def execute(self, user, cname, confirmed):
        if confirmed != 'YES':
            return

        channel = Channel.get(cname)
        if (not channel) or (Flags.FOUNDER not in channel.get_flags_by_user(user)):
            self.err(user, f'해당 채널 \x02{cname}\x02 의 \x02{user.nick}\x02 유저에 \x02F\x02 (개설자) 권한이 없습니다.')

        channel.delete()

        self.msg(user, f'해당 채널 \x02{cname}\x02 의 등록이 해제되었습니다.')

        self.service.part_channel(cname)
