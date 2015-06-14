from ika.classes import Legacy

from ika.services.ozinger.commands.login import Login


class Identify(Legacy, Login):
    name = 'IDENTIFY'
    aliases = (
        'ID',
    )
