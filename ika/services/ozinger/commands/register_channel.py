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
        if not irc_channel:
            self.err(user, f'해당 채널 \x02{cname}\x02 가 존재하지 않습니다.')

        if 'o' not in irc_channel.usermodes.get(user.uid, set()):
            self.err(user, f'해당 채널 \x02{cname}\x02 에 \x02{user.nick}\x02 유저에 대한 옵이 없습니다.')

        if Channel.get(cname):
            self.err(user, f'해당 채널 \x02{cname}\x02 은 이미 오징어 IRC 네트워크에 등록되어 있습니다.')

        channel = Channel()
        channel.name = cname
        channel.save()

        flag = Flag()
        flag.channel = channel
        flag.target = user.account.name
        flag.type = int(Flags.OWNER)
        flag.save()

        self.msg(user, f'해당 채널 \x02{cname}\x02 의 등록이 완료되었습니다.')

        self.service.join_channel(irc_channel)
        self.writesvsuserline('FMODE', cname, irc_channel.timestamp, '+q', user.uid)
