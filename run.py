#!/usr/bin/env python3.6

import asyncio
import os
import sys
from django.core.wsgi import get_wsgi_application
from django.core.management import call_command, execute_from_command_line
from django.db import DEFAULT_DB_ALIAS, connections

from ika.logger import logger
from ika.server import Server


os.environ.setdefault("DJANGO_SETTINGS_MODULE", "ika.conf")
application = get_wsgi_application()


def main():
    if len(sys.argv) == 1:
        print("Usage: ./run.py run")
        return

    if sys.argv[1] in ('makemigrations', 'runserver',):
        execute_from_command_line(sys.argv)
    elif sys.argv[1] == 'run':
        from django.db.migrations.executor import MigrationExecutor

        connection = connections[DEFAULT_DB_ALIAS]
        connection.prepare_database()
        executor = MigrationExecutor(connection)
        plan = executor.migration_plan(executor.loader.graph.leaf_nodes())

        if len(plan) > 0:
            print('Synchronizing database schemas...')
            call_command('migrate')
            print()
            print('Starting application...')

        loop = asyncio.get_event_loop()

        ika = Server()
        ika.register_services()

        try:
            loop.run_until_complete(ika.connect())
        except KeyboardInterrupt:
            ika.disconnect('Manually interrupted by console access')
        except:
            ika.disconnect('Exception has occured in the main loop')
            logger.exception('Exception has occured in the main loop')
        finally:
            loop.close()

if __name__ == '__main__':
    main()
