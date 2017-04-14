from ika.service import Command, Permission
from ika.enums import Flags


class Invite(Command):
    name = '초대'
    aliases = (
        '채널초대',
        'INVITE',
        'INVITECHANNEL'
    )
    syntax = '<채널명>'
    regex = r'(?P<cname>#\S+)'
    permission = Permission.LOGIN_REQUIRED
    description = (
        '오징어 IRC 네트워크에 등록되어 있는 채널에 초대를 요청합니다.',
        ' ',
        '이 명령을 사용할 시 오징어 IRC 네트워크에 등록되어 있는 채널에 초대를 요청합니다.',
        '이 명령을 사용하기 위해서는 해당 채널에 1명 이상이 있어 서버에 채널이 존재하고 있어야 합니다.'
        '또한 해당 채널에 \x02F\x02 (개설자), \x02Q\x02 (주인), \x02A\x02 (보호), \x02O\x02 (관리자), \x02H\x02 (부관리자) 중 하나의 권한이 등록되어 있어야 합니다.',
    )

    usable_flags = Flags.FOUNDER | Flags.OWNER | Flags.PROTECT | Flags.OP | Flags.HALFOP

    async def execute(self, user, cname):
        irc_channel = self.server.channels.get(cname)
        if (not irc_channel) or (not irc_channel.channel) or (not (self.usable_flags & irc_channel.channel.get_flags_by_user(user))):
            self.err(user, f'해당 채널 \x02{cname}\x02 가 존재하지 않거나, 해당 채널의 \x02{user.account}\x02 계정에 필요한 권한이 등록되어 있지 않습니다.')

        if user.uid in irc_channel.users:
            self.err(user, f'해당 채널 \x02{irc_channel.name}\x02 에 이미 접속해있습니다.')

        self.msg(user, f'해당 채널 \x02{irc_channel.name}\x02 에 초대되었습니다.')
        self.writesvsuserline('INVITE', user.uid, cname, 0)
