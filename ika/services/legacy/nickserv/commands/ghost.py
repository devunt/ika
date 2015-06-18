from ika.classes import Command, Legacy

from ika.services.ozinger.commands.ghost import Ghost


class Ghost(Command, Legacy):
    name = 'GHOST'
