from ika.service import Command, Permission


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
        'PRIVMSG를 이용해 채널 라인으로 출력하므로 주의하십시오.',
        '명령을 실행하는 순간 발송하므로 명령을 실행하기 전 다시 한번 공지사항의 내용을 확인해주세요.',
    )

    async def execute(self, user, text):
        count = len(self.server.channels)
        self.msg(user, f'{count}개 채널에 공지사항을 발송합니다.')
        for cname in self.server.channels.keys():
            self.writesvsuserline(f'PRIVMSG {cname} : \x02[공지]\x02 {text}')
        self.msg(user, f'{count}개 채널에 공지사항을 발송했습니다.')
