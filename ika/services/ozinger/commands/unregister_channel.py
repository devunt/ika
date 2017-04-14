from ika.service import Command, Permission
from ika.models import Channel, Flag
from ika.enums import Flags


class UnregisterChannel(Command):
    name = '채널등록해제'
    aliases = (
        'UNREGISTERCHANNEL',
    )
    syntax = '<#채널명>'
    regex = r'(?P<cname>#\S+)'
    permission = Permission.LOGIN_REQUIRED
    description = (
        '오징어 IRC 네트워크에 등록되어 있는 채널의 등록을 해제합니다.',
        ' ',
        '이 명령을 사용할 시 오징어 IRC 네트워크에 등록되어 있는 채널의 등록을 해제하며,',
        '그 뒤로는 네트워크에서 제공하는 여러 편의 기능등을 이용하실 수 없습니다.',
        '채널 등록 해제는 해당 채널에 F (개설자) 권한이 있는 사용자만 할 수 있습니다.',
    )

    async def execute(self, user, cname):
        channel = Channel.get(cname)
        if not channel:
            self.err(user, f'해당 채널 \x02{cname}\x02 은 오징어 IRC 네트워크에 등록되어 있지 않습니다.')

        if Flags.FOUNDER not in channel.get_flags_by_user(user):
            self.err(user, f'해당 채널 \x02{cname}\x02 의 \x02{user.nick}\x02 유저에 F (개설자) 권한이 없습니다.')

        channel.delete()

        self.msg(user, f'해당 채널 \x02{cname}\x02 의 등록이 해제되었습니다.')

        self.writesvsuserline('PART', cname, 'Never left without saying goodbye')
