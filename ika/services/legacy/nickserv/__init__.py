from ika.classes import Legacy, Service


class NickServ(Legacy, Service):
    name = '오징오징어'
    aliases = (
        'NickServ',
    )
    description = (
        '과거에 닉네임 서비스 봇이었습니다.',
        '하위호환을 위해 자주 쓰였던 닉섭 명령들을 새 통합 서비스봇으로 넘겨주는 역할을 합니다.',
    )
