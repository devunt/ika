import asyncio

from ika.classes import Command
from ika.enums import Permission


class Announce(Command):
    name = 'ANNOUNCE'
    aliases = (
        'ANN',
        '공지',
    )
    syntax = '<내용>'
    regex = r'(?P<text>.+)'
    permission = Permission.OPERATOR
    description = (
        '모든 IRC 채널에 공지사항을 출력합니다.',
        '^^ 명의의 PRIVMSG를 이용해 채널 라인으로 출력하므로 주의하십시오.',
        '명령을 실행하는 순간 발송하므로 명령을 실행하기 전 다시 한번 공지사항의 내용을 확인해주세요.',
    )

    @asyncio.coroutine
    def execute(self, user, text):
        channelcount = len(self.service.server.channels)
        self.service.msg(user, '{}개 채널에 공지사항을 발송합니다.', channelcount)
        for channelname in self.service.server.channels.keys():
            self.service.writesvsuserline('PRIVMSG {} : \x02[공지]\x02 {}', channelname, text)
        self.service.msg(user, '{}개 채널에 공지사항을 발송했습니다.', channelcount)
