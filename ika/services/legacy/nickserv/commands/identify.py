from ika.classes import Legacy

from ika.services.ozinger.commands.login import Login


class Identify(Login, Legacy):
    name = 'IDENTIFY'
    aliases = (
        'ID',
    )
