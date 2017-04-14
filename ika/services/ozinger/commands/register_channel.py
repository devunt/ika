from ika.service import Command, Permission
from ika.models import Channel, Flag
from ika.enums import Flags


class RegisterChannel(Command):
    name = '채널등록'
    aliases = (
        '새채널',
        'NEWCHANNEL',
        'REGISTERCHANNEL',
    )
    syntax = '<#채널명>'
    regex = r'(?P<cname>#\S+)'
    permission = Permission.LOGIN_REQUIRED
    description = (
        '오징어 IRC 네트워크에 채널을 등록합니다.',
        ' ',
        '이 명령을 사용할 시 오징어 IRC 네트워크에 해당 이름의 채널을 등록하며,',
        '그 뒤로 네트워크에서 제공하는 여러 편의 기능등을 이용하실 수 있습니다.',
        '채널 등록은 해당 채널에 옵이 있는 사용자만 할 수 있습니다.',
    )

    async def execute(self, user, cname):
        irc_channel = self.server.channels.get(cname)
        if (not irc_channel) or ('o' not in irc_channel.usermodes.get(user.uid, set())) or Channel.get(cname):
            self.err(user, f'명령을 실행할 권한이 없습니다. 해당 채널 \x02{cname}\x02 이 아직 등록되지 않았고 \x02{user.nick}\x02 유저에 대한 옵이 존재하는지 확인해주세요.')

        channel = Channel()
        channel.name = cname
        channel.save()

        flag = Flag(channel=channel, type=Flags.FOUNDER | Flags.OWNER | Flags.OP)
        flag.target = user.account
        flag.save()

        self.service.join_channel(cname)
        modestring = irc_channel.generate_synchronizing_modestring()
        if modestring:
            self.writesvsuserline('FMODE', irc_channel.name, irc_channel.timestamp, modestring)

        self.msg(user, f'해당 채널 \x02{cname}\x02 의 등록이 완료되었습니다.')
