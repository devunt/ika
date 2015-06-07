#!/usr/bin/env python3

import asyncio

from ika.database import Base, engine
from ika.logger import logger
from ika.server import Server


def main():
    loop = asyncio.get_event_loop()

    ika = Server()
    ika.register_services()
    Base.metadata.create_all(engine)

    try:
        loop.run_until_complete(ika.connect())
    except KeyboardInterrupt:
        ika.disconnect('Manually interrupted by console access')
    except:
        logger.exception('Exception has occured in the main loop')
    finally:
        loop.close()


if __name__ == '__main__':
    main()
