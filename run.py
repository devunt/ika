#!/usr/bin/env python3.6

import asyncio
import os
import sys
from django.core.wsgi import get_wsgi_application
from django.core.management import execute_from_command_line

from ika.logger import logger
from ika.server import Server


os.environ.setdefault("DJANGO_SETTINGS_MODULE", "ika.conf")
application = get_wsgi_application()


def main():
    if len(sys.argv) > 1:
        if sys.argv[1] == 'makemigrations' or sys.argv[1] == 'migrate':
            execute_from_command_line(sys.argv)
            return

    loop = asyncio.get_event_loop()

    ika = Server()
    ika.register_services()

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
