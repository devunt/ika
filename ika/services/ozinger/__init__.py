from ika.service import Service
from ika.utils import unixtime


class Ozinger(Service):
    name = '^^'
    aliases = (
    )
    description = (
        '통합 서비스봇입니다.',
        '채널, 계정(닉네임) 관리 등을 할 수 있습니다.',
        ' ',
        '현재 개발중에 있으며 시범적으로 기존 서비스봇을 대체하여 운영중입니다.',
        '기존 \x02오징오징어\x02와 \x02ㅇㅈㅇ\x02는 하위호환성 유지를 위해 일부 명령에 한해 동작하고 있습니다.',
        '소스코드: https://github.com/devunt/ika',
    )

    def join_channel(self, cname):
        irc_channel = self.server.channels.get(cname)
        timestamp, modestring = (irc_channel.timestamp, irc_channel.modestring) if irc_channel else (unixtime(), '+')
        self.writeserverline('FJOIN', cname, timestamp, modestring, f'o,{self.uid}')

    def part_channel(self, cname, reason=None):
        self.writesvsuserline('PART', cname, reason or 'Never left without saying goodbye')
