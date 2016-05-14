from ika.classes import Legacy

from ika.services.ozinger.commands.ghost import Ghost


class Ghost(Ghost, Legacy):
    name = 'GHOST'
    aliases = (
        '고스트',
    )
