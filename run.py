#!/usr/bin/env python3

import asyncio

from ika.database import Base, engine
from ika.server import Server


def main():
    loop = asyncio.get_event_loop()

    ika = Server()
    ika.register_services()
    Base.metadata.create_all(engine)

    loop.run_until_complete(ika.connect())
    loop.close()


if __name__ == '__main__':
    main()
