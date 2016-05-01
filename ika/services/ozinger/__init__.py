from ika.classes import Service


class Ozinger(Service):
    name = '^^'
    aliases = (
        '오징어',
    )
    description = (
        '통합 서비스봇입니다.',
        '채널, 계정(닉네임) 관리 등을 할 수 있습니다.',
        ' ',
        '현재 개발중에 있으며 시범적으로 기존 서비스봇을 대체하여 운영중입니다.',
        '닉네임은 최종적으로 정해진 닉네임이 아니며, 기존 \x02오징오징어\x02와 \x02ㅇㅈㅇ\x02는',
        '하위호환성 유지를 위해 사용하지 못하고 남겨둬야 하는 점 양해 부탁드립니다',
        '소스코드: https://github.com/devunt/ika',
    )
    joined_channels = list()

    def join_channel(self, channel):
        self.writeserverline('FJOIN {} {} +{} :ao,{}',
            channel.name, channel.timestamp, channel.modes, self.uid)
        self.joined_channels.append(channel.name.lower())

    def part_channel(self, channel, reason=None):
        self.writesvsuserline('PART {} :{}', channel, reason or 'No reason was specified')
        self.joined_channels.remove(channel.lower())
