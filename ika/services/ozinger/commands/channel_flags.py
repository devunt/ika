import asyncio
from datetime import datetime

from ika.classes import Command
from ika.database import Channel, Flag, Session
from ika.enums import Flags, Permission


class ChannelFlags(Command):
    name = '채널등록'
    aliases = (
        '새채널',
        'NEWCHANNEL',
        'REGISTERCHANNEL',
    )
    syntax = '<#채널명>'
    regex = r'(?P<name>#\S+)'
    permission = Permission.LOGIN_REQUIRED
    description = (
        '오징어 IRC 네트워크에 채널을 등록합니다.',
        ' ',
        '이 명령을 사용할 시 오징어 IRC 네트워크에 해당 이름의 채널을 등록하며,',
        '그 뒤로 네트워크에서 제공하는 여러 편의 기능등을 이용하실 수 있습니다.',
        '채널 등록은 해당 채널에 옵이 있는 사용자만 할 수 있습니다.',
    )

    @asyncio.coroutine
    def execute(self, user, name):
        session = Session()

        real_channel = self.service.server.channels.get(name)
        if not real_channel:
            self.service.msg(user, '해당 채널 \x02{}\x02 가 존재하지 않습니다.', name)
            return

        if 'o' not in real_channel.usermodes[user.uid]:
            self.service.msg(user, '해당 채널 \x02{}\x02 에 \x02{}\x02 유저에 대한 옵이 없습니다.', name, user.nick)
            return

        if Channel.find_by_name(name):
            self.service.msg(user, '해당 채널 \x02{}\x02 은 이미 오징어 IRC 네트워크에 등록되어 있습니다.', name)
            return

        channel = Channel()
        channel.name = name

        flag = Flag()
        flag.channel = channel
        flag.target = user.account.name.name
        flag.type = Flags.OWNER

        session.add(flag)
        session.commit()

        self.service.msg(user, '해당 채널 \x02{}\x02 의 등록이 완료되었습니다.', name)

        self.service.join_channel(real_channel)
        self.service.writesvsuserline('FMODE {} {} +{} {}', name, real_channel.timestamp, 'q', user.uid)