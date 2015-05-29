import asyncio
from ika.classes import Service


class Ozinger(Service):
    name = 'ika'
    description = [
        '통합 서비스봇입니다.',
        '채널, 계정(닉네임) 관리 등을 할 수 있습니다.',
    ]
