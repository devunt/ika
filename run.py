#!/usr/bin/env python3

import asyncio

from ika.server import Server


def main():
    loop = asyncio.get_event_loop()

    ika = Server()
    ika.register_services()

    asyncio.async(ika.connect())
    loop.run_forever()


if __name__ == '__main__':
    main()
