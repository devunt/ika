from ika.service import Legacy
from ika.services.ozinger.commands.login import Login as _Login


class Identify(Legacy, _Login):
    name = 'IDENTIFY'
    aliases = (
        'ID',
        '인증',
        '로그인',
    )
