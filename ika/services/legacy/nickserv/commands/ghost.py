from ika.service import Legacy
from ika.services.ozinger.commands.ghost import Ghost as _Ghost


class Ghost(Legacy, _Ghost):
    name = 'GHOST'
    aliases = (
        '고스트',
    )
