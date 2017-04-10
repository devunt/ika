import logging

from ika.conf import settings


logging.basicConfig(format='[%(asctime)s] {%(levelname)s} %(message)s')

if settings.logging.sentry.dsn is not None:
    from raven import Client
    from raven.conf import setup_logging
    from raven.handlers.logging import SentryHandler

    client = Client(dsn=settings.logging.sentry.dsn, auto_log_stacks=True)
    handler = SentryHandler(client)
    handler.setLevel(getattr(logging, settings.logging.sentry.level))
    setup_logging(handler)

logger = logging.getLogger('ika')
logger.setLevel(getattr(logging, settings.logging.console.level))
